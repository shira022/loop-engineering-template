"""Adapters that produce the common result shape for agent_eval.

Every adapter returns::

    {"content": str, "tool_calls": [{"name": str, "arguments": dict}],
     "latency_ms": float, "raw": dict}

Adapters deliberately avoid third-party dependencies.  The OpenAI adapter is
implemented with :mod:`urllib`; tests mock the network call.
"""

from __future__ import annotations

import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

from .checks import ConfigError, excerpt


class AdapterError(Exception):
    """A case-level adapter failure.

    ``status`` is either ``"fail"`` (the target ran but failed) or
    ``"error"`` (the fixture/input needed by the adapter is missing or bad).
    """

    def __init__(self, message, status="fail"):
        super().__init__(message)
        self.message = message
        self.status = status


def _normalise_result(data, source):
    if not isinstance(data, dict):
        raise AdapterError(f"replay fixture must be an object: {source}", "error")

    content = data.get("content")
    if not isinstance(content, str):
        raise AdapterError(
            f"replay fixture is missing a string 'content': {source}", "error"
        )

    tool_calls = data.get("tool_calls", [])
    if tool_calls is None:
        tool_calls = []
    if not isinstance(tool_calls, list) or not all(
        isinstance(call, dict) for call in tool_calls
    ):
        raise AdapterError(
            f"replay fixture 'tool_calls' must be a list of objects: {source}", "error"
        )

    latency = data.get("latency_ms")
    if latency is not None:
        try:
            latency = float(latency)
        except (TypeError, ValueError) as exc:
            raise AdapterError(
                f"replay fixture 'latency_ms' must be numeric: {source}", "error"
            ) from exc

    return {
        "content": content,
        "tool_calls": tool_calls,
        "latency_ms": latency,
        "raw": data,
    }


def _read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise AdapterError(f"cannot read replay fixture {path}: {exc}", "error") from exc
    except json.JSONDecodeError as exc:
        raise AdapterError(f"invalid JSON in replay fixture {path}: {exc}", "error") from exc


def _from_manifest(manifest_path, case_id):
    """Look up *case_id* in an ``example.json`` style replay manifest."""
    if not manifest_path.is_file():
        return None
    data = _read_json(manifest_path)
    if not isinstance(data, dict):
        return None
    for key in ("responses", "cases"):
        bucket = data.get(key)
        if isinstance(bucket, dict) and case_id in bucket:
            return bucket[case_id]
    if case_id in data and isinstance(data[case_id], dict):
        return data[case_id]
    return None


def replay_adapter(case_id, replay_dir):
    """Read a fixture for *case_id* from *replay_dir*.

    The primary form is ``<replay_dir>/<case_id>.json``.  As a convenience for
    the bundled sample, a missing per-case file falls back to a manifest named
    ``example.json`` (``{"responses": {"<case_id>": {...}}}``).
    """
    directory = Path(replay_dir)
    case_path = directory / f"{case_id}.json"

    if case_path.is_file():
        data = _read_json(case_path)
        source = case_path
    else:
        data = _from_manifest(directory / "example.json", case_id)
        if data is None:
            raise AdapterError(
                f"no replay fixture for case {case_id!r} in {directory}", "error"
            )
        source = directory / "example.json"

    return _normalise_result(data, source)


def command_adapter(prompt, cmd, timeout):
    """Run a shell command, feeding *prompt* on stdin."""
    if not cmd:
        raise ConfigError("--cmd is required for the command adapter")

    started = time.perf_counter()
    try:
        completed = subprocess.run(
            cmd,
            shell=True,
            input=prompt,
            text=True,
            timeout=timeout,
            capture_output=True,
        )
    except subprocess.TimeoutExpired:
        raise AdapterError(f"command timed out after {timeout:g}s", "fail")
    latency_ms = (time.perf_counter() - started) * 1000.0

    if completed.returncode != 0:
        message = f"command exited with code {completed.returncode}"
        stderr_excerpt = excerpt(completed.stderr, 300)
        if stderr_excerpt:
            message += f": {stderr_excerpt}"
        raise AdapterError(message, "fail")

    return {
        "content": completed.stdout,
        "tool_calls": [],
        "latency_ms": latency_ms,
        "raw": {
            "returncode": completed.returncode,
            "stderr": completed.stderr,
        },
    }


def openai_adapter(prompt, base_url, model, api_key, timeout):
    """Call an OpenAI-compatible ``/chat/completions`` endpoint.

    The API key is never placed in an exception message or returned in ``raw``.
    """
    if not api_key:
        raise ConfigError("OpenAI adapter requires a non-empty API key")
    if not base_url:
        raise ConfigError("--base-url is required for the openai adapter")
    if not model:
        raise ConfigError("--model is required for the openai adapter")

    url = base_url.rstrip("/") + "/chat/completions"
    body = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload_bytes = response.read()
    except urllib.error.HTTPError as exc:
        raise AdapterError(
            f"HTTP error {exc.code} from {url}", "fail"
        ) from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise AdapterError(f"request to {url} failed: {exc}", "fail") from exc
    latency_ms = (time.perf_counter() - started) * 1000.0

    try:
        payload = json.loads(payload_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AdapterError(f"invalid JSON response from {url}: {exc}", "fail") from exc

    try:
        message = payload["choices"][0]["message"]
    except (KeyError, IndexError, TypeError) as exc:
        raise AdapterError(
            f"response from {url} has no choices[0].message", "fail"
        ) from exc

    content = message.get("content") or ""
    if not isinstance(content, str):
        content = str(content)

    tool_calls = []
    for call in message.get("tool_calls") or []:
        if not isinstance(call, dict):
            continue
        function = call.get("function") or {}
        if not isinstance(function, dict):
            function = {}
        arguments = function.get("arguments", {})
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                arguments = {}
        if not isinstance(arguments, dict):
            arguments = {}
        tool_calls.append(
            {"name": function.get("name", ""), "arguments": arguments}
        )

    return {
        "content": content,
        "tool_calls": tool_calls,
        "latency_ms": latency_ms,
        "raw": payload,
    }
