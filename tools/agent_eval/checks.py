"""Assertion checks and case validation for tools.agent_eval.

Only the Python standard library is used.  The JSON Schema support is a
deliberately small subset: ``type``, ``required``, ``properties``, ``items``
and ``enum``.
"""

from __future__ import annotations

import json
import re

CHECK_TYPES = (
    "json_valid",
    "json_schema",
    "contains",
    "not_contains",
    "regex",
    "tool_calls",
    "max_latency_ms",
)

_TOOL_CALL_MODES = ("subset", "exact", "none")
_SCHEMA_TYPES = {
    "object",
    "array",
    "string",
    "number",
    "integer",
    "boolean",
    "null",
}
_FLAG_MAP = {
    "s": re.DOTALL,
    "m": re.MULTILINE,
    "i": re.IGNORECASE,
}
_DEFAULT_EXCERPT_LIMIT = 500


class ConfigError(Exception):
    """Raised for invalid case configuration or CLI input (exit code 2)."""


def excerpt(value, limit=_DEFAULT_EXCERPT_LIMIT):
    """Return a printable, length-limited excerpt of *value*."""
    text = "" if value is None else str(value)
    if len(text) <= limit:
        return text
    return text[:limit] + "...(truncated)"


def strip_code_fences(text):
    """Remove one surrounding Markdown code fence, if present."""
    stripped = text.strip()
    match = re.match(r"^```[^\n`]*\n(.*?)\n?```$", stripped, re.DOTALL)
    if match:
        return match.group(1).strip()
    return stripped


def parse_json_content(text):
    """Parse *text* as JSON after stripping optional code fences."""
    return json.loads(strip_code_fences(text))


def _check_result(check_type, ok, detail):
    return {
        "type": check_type,
        "status": "pass" if ok else "fail",
        "detail": detail,
    }


def _json_type_name(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if isinstance(value, str):
        return "string"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    return type(value).__name__


def _matches_type(value, expected):
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    raise ConfigError(f"unsupported JSON Schema type: {expected!r}")


def _validate_schema(schema, path="$"):
    """Validate a (subset) JSON Schema definition itself."""
    if not isinstance(schema, dict):
        raise ConfigError(f"{path}: schema must be an object")

    if "type" in schema:
        types = schema["type"]
        if isinstance(types, str):
            types = [types]
        if not isinstance(types, list) or not types:
            raise ConfigError(f"{path}.type: expected a string or non-empty list")
        for type_name in types:
            if type_name not in _SCHEMA_TYPES:
                raise ConfigError(f"{path}.type: unsupported type {type_name!r}")

    if "enum" in schema and not isinstance(schema["enum"], list):
        raise ConfigError(f"{path}.enum: expected a list")

    if "required" in schema:
        required = schema["required"]
        if not isinstance(required, list) or not all(
            isinstance(item, str) for item in required
        ):
            raise ConfigError(f"{path}.required: expected a list of strings")

    if "properties" in schema:
        properties = schema["properties"]
        if not isinstance(properties, dict):
            raise ConfigError(f"{path}.properties: expected an object")
        for key, sub_schema in properties.items():
            _validate_schema(sub_schema, f"{path}.properties.{key}")

    if "items" in schema:
        _validate_schema(schema["items"], f"{path}.items")


def _validate_value(value, schema, path, errors):
    if "type" in schema:
        types = schema["type"]
        if isinstance(types, str):
            types = [types]
        if not any(_matches_type(value, type_name) for type_name in types):
            expected = "/".join(types)
            errors.append(
                f"{path}: expected type {expected}, got {_json_type_name(value)}"
            )
            return

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value {value!r} is not in enum {schema['enum']!r}")

    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}.{key}: required property is missing")
        for key, sub_schema in schema.get("properties", {}).items():
            if key in value:
                _validate_value(value[key], sub_schema, f"{path}.{key}", errors)

    if isinstance(value, list) and "items" in schema:
        for index, item in enumerate(value):
            _validate_value(item, schema["items"], f"{path}[{index}]", errors)


def _validate_flags(flags):
    if flags is None:
        return ""
    if not isinstance(flags, str):
        raise ConfigError("regex flags must be a string")
    for flag in flags:
        if flag not in _FLAG_MAP:
            raise ConfigError(
                f"unsupported regex flag {flag!r}; expected a combination of s/m/i"
            )
    return flags


def validate_check(check):
    """Validate a single check definition, raising ConfigError on problems."""
    if not isinstance(check, dict):
        raise ConfigError("each check must be an object")

    check_type = check.get("type")
    if check_type not in CHECK_TYPES:
        raise ConfigError(f"unknown check type: {check_type!r}")

    if check_type in ("contains", "not_contains"):
        if not isinstance(check.get("value"), str):
            raise ConfigError(f"{check_type}: 'value' must be a string")

    elif check_type == "regex":
        pattern = check.get("pattern")
        if not isinstance(pattern, str):
            raise ConfigError("regex: 'pattern' must be a string")
        flags = _validate_flags(check.get("flags"))
        try:
            re.compile(pattern, _flags_value(flags))
        except re.error as exc:
            raise ConfigError(f"regex: invalid pattern: {exc}") from exc

    elif check_type == "tool_calls":
        mode = check.get("mode")
        if mode not in _TOOL_CALL_MODES:
            raise ConfigError(
                f"tool_calls: 'mode' must be one of {', '.join(_TOOL_CALL_MODES)}"
            )
        expected = check.get("expected", [])
        if not isinstance(expected, list) or not all(
            isinstance(item, str) for item in expected
        ):
            raise ConfigError("tool_calls: 'expected' must be a list of strings")
        if mode in ("subset", "exact") and not expected:
            raise ConfigError(f"tool_calls: 'expected' is required for mode {mode!r}")

    elif check_type == "max_latency_ms":
        value = check.get("value")
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ConfigError("max_latency_ms: 'value' must be a number")

    elif check_type == "json_schema":
        schema = check.get("schema")
        if not isinstance(schema, dict):
            raise ConfigError("json_schema: 'schema' must be an object")
        _validate_schema(schema)


def validate_case(case):
    """Validate a case definition, raising ConfigError on problems."""
    if not isinstance(case, dict):
        raise ConfigError("each case must be an object")

    case_id = case.get("id")
    if not isinstance(case_id, str) or not case_id:
        raise ConfigError("case 'id' must be a non-empty string")
    if "/" in case_id or "\\" in case_id or case_id in (".", ".."):
        raise ConfigError(f"case 'id' must not contain path separators: {case_id!r}")

    if not isinstance(case.get("prompt"), str):
        raise ConfigError(f"case {case_id!r}: 'prompt' must be a string")

    tags = case.get("tags")
    if tags is not None and (
        not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags)
    ):
        raise ConfigError(f"case {case_id!r}: 'tags' must be a list of strings")

    case_checks = case.get("checks")
    if not isinstance(case_checks, list):
        raise ConfigError(f"case {case_id!r}: 'checks' must be a list")
    for check in case_checks:
        try:
            validate_check(check)
        except ConfigError as exc:
            raise ConfigError(f"case {case_id!r}: {exc}") from exc


def _flags_value(flags):
    result = 0
    for flag in flags:
        result |= _FLAG_MAP[flag]
    return result


def _check_json_valid(check_type, content):
    try:
        parse_json_content(content)
    except (json.JSONDecodeError, TypeError) as exc:
        return _check_result(
            check_type,
            False,
            f"response is not valid JSON: {exc}. actual: {excerpt(content)}",
        )
    return _check_result(check_type, True, "response parsed as JSON")


def _check_json_schema(check, content):
    try:
        value = parse_json_content(content)
    except (json.JSONDecodeError, TypeError) as exc:
        return _check_result(
            "json_schema",
            False,
            f"response is not valid JSON: {exc}. actual: {excerpt(content)}",
        )

    errors = []
    _validate_value(value, check["schema"], "$", errors)
    if errors:
        return _check_result(
            "json_schema",
            False,
            "schema validation failed: "
            + "; ".join(errors[:10])
            + f". actual: {excerpt(content)}",
        )
    return _check_result("json_schema", True, "response matches schema")


def _check_tool_calls(check, result):
    actual_calls = result.get("tool_calls") or []
    if not isinstance(actual_calls, list):
        return _check_result(
            "tool_calls",
            False,
            f"adapter returned non-list tool_calls: {type(actual_calls).__name__}",
        )

    actual_names = [
        call.get("name", "")
        for call in actual_calls
        if isinstance(call, dict)
    ]
    expected = check.get("expected", [])
    mode = check["mode"]
    actual_set = set(actual_names)
    expected_set = set(expected)

    if mode == "none":
        ok = not actual_names
        detail = (
            "no tool calls were made"
            if ok
            else f"expected no tool calls, actual: {sorted(actual_names)}"
        )
    elif mode == "subset":
        missing = sorted(expected_set - actual_set)
        ok = not missing
        detail = (
            f"all expected tool calls present: {sorted(expected_set)}"
            if ok
            else f"missing expected tool calls: {missing}; actual: {sorted(actual_names)}"
        )
    else:  # exact
        missing = sorted(expected_set - actual_set)
        extra = sorted(actual_set - expected_set)
        ok = actual_set == expected_set
        detail = (
            f"tool calls exactly match: {sorted(expected_set)}"
            if ok
            else f"expected exactly {sorted(expected_set)}, actual: {sorted(actual_names)}"
            f" (missing: {missing}, unexpected: {extra})"
        )

    return _check_result("tool_calls", ok, detail)


def run_check(check, result):
    """Run one check against an adapter result and return a report dict."""
    check_type = check["type"]
    content = result.get("content", "")
    if not isinstance(content, str):
        content = "" if content is None else str(content)

    if check_type == "json_valid":
        return _check_json_valid(check_type, content)

    if check_type == "json_schema":
        return _check_json_schema(check, content)

    if check_type == "contains":
        value = check["value"]
        ok = value in content
        detail = (
            f"found substring {value!r}"
            if ok
            else f"substring {value!r} not found. actual: {excerpt(content)}"
        )
        return _check_result(check_type, ok, detail)

    if check_type == "not_contains":
        value = check["value"]
        ok = value not in content
        detail = (
            f"substring {value!r} is absent"
            if ok
            else f"unexpected substring {value!r} found. actual: {excerpt(content)}"
        )
        return _check_result(check_type, ok, detail)

    if check_type == "regex":
        flags = _validate_flags(check.get("flags"))
        try:
            match = re.search(check["pattern"], content, _flags_value(flags))
        except re.error as exc:  # defensive: validate_check normally catches this
            raise ConfigError(f"regex: invalid pattern: {exc}") from exc
        ok = match is not None
        detail = (
            f"pattern {check['pattern']!r} matched"
            if ok
            else f"pattern {check['pattern']!r} did not match. actual: {excerpt(content)}"
        )
        return _check_result(check_type, ok, detail)

    if check_type == "tool_calls":
        return _check_tool_calls(check, result)

    if check_type == "max_latency_ms":
        latency = result.get("latency_ms")
        if latency is None:
            return _check_result(
                check_type, False, "adapter did not report latency_ms"
            )
        limit = check["value"]
        ok = latency <= limit
        detail = (
            f"latency {latency:.3f}ms is within limit {limit}ms"
            if ok
            else f"latency {latency:.3f}ms exceeds limit {limit}ms"
        )
        return _check_result(check_type, ok, detail)

    # validate_check prevents this, but keep the failure explicit.
    raise ConfigError(f"unknown check type: {check_type!r}")
