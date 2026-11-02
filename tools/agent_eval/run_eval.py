"""CLI entry point for the agent LLM regression evaluation harness.

Usage::

    python3 tools/agent_eval/run_eval.py \
        --cases tools/agent_eval/cases/example.json --adapter replay

Exit codes: 0 = all cases pass, 1 = one or more failures/errors,
2 = configuration or input error.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_eval import checks
from agent_eval.adapters import (
    AdapterError,
    command_adapter,
    openai_adapter,
    replay_adapter,
)


TOOL_DIR = Path(__file__).resolve().parent
DEFAULT_REPLAY_DIR = TOOL_DIR / "fixtures" / "replay"
DEFAULT_OUT_DIR = TOOL_DIR / "out"


def _utc_timestamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_cases(path):
    cases_path = Path(path)
    try:
        text = cases_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise checks.ConfigError(f"cannot read cases file {cases_path}: {exc}") from exc

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise checks.ConfigError(f"invalid JSON in cases file {cases_path}: {exc}") from exc

    if not isinstance(data, dict):
        raise checks.ConfigError("cases file must contain a JSON object")

    suite = data.get("suite", "default")
    if not isinstance(suite, str):
        raise checks.ConfigError("'suite' must be a string")

    cases = data.get("cases")
    if not isinstance(cases, list):
        raise checks.ConfigError("'cases' must be a list")

    seen = set()
    for case in cases:
        checks.validate_case(case)
        case_id = case["id"]
        if case_id in seen:
            raise checks.ConfigError(f"duplicate case id: {case_id!r}")
        seen.add(case_id)

    return suite, cases


def load_baseline(path):
    baseline_path = Path(path)
    try:
        data = json.loads(baseline_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise checks.ConfigError(
            f"cannot read baseline {baseline_path}: {exc}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise checks.ConfigError(
            f"invalid JSON in baseline {baseline_path}: {exc}"
        ) from exc

    if not isinstance(data, dict) or not isinstance(data.get("cases"), list):
        raise checks.ConfigError("baseline must be a report.json with a 'cases' list")

    statuses = {}
    for case in data["cases"]:
        if not isinstance(case, dict):
            raise checks.ConfigError("baseline cases must be objects")
        case_id = case.get("id")
        status = case.get("status")
        if not isinstance(case_id, str) or not isinstance(status, str):
            raise checks.ConfigError("baseline cases require string 'id' and 'status'")
        statuses[case_id] = status
    return statuses


def evaluate_case(case, adapter, options):
    started = time.perf_counter()
    case_id = case["id"]

    try:
        if adapter == "replay":
            result = replay_adapter(case_id, options["replay_dir"])
        elif adapter == "command":
            result = command_adapter(
                case["prompt"], options["cmd"], options["timeout"]
            )
        elif adapter == "openai":
            result = openai_adapter(
                case["prompt"],
                options["base_url"],
                options["model"],
                options["api_key"],
                options["timeout"],
            )
        else:
            raise checks.ConfigError(f"unknown adapter: {adapter!r}")
    except AdapterError as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        return {
            "id": case_id,
            "status": exc.status,
            "latency_ms": round(elapsed_ms, 3),
            "checks": [],
            "failure_reasons": [exc.message],
        }

    elapsed_ms = (time.perf_counter() - started) * 1000.0
    latency_ms = result.get("latency_ms")
    if latency_ms is None:
        latency_ms = elapsed_ms

    check_results = []
    failure_reasons = []
    for check in case.get("checks", []):
        outcome = checks.run_check(check, result)
        check_results.append(outcome)
        if outcome["status"] != "pass":
            failure_reasons.append(f"{check['type']}: {outcome['detail']}")

    return {
        "id": case_id,
        "status": "pass" if not failure_reasons else "fail",
        "latency_ms": round(float(latency_ms), 3),
        "checks": check_results,
        "failure_reasons": failure_reasons,
    }


def build_summary(case_results):
    total = len(case_results)
    passed = sum(1 for result in case_results if result["status"] == "pass")
    failed = sum(1 for result in case_results if result["status"] == "fail")
    errored = sum(1 for result in case_results if result["status"] == "error")
    score = round(passed / total, 4) if total else 1.0
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "errored": errored,
        "score": score,
    }


def build_regressions(case_results, baseline_path, baseline_statuses):
    if baseline_statuses is None:
        return {
            "compared_to": None,
            "new_failures": [],
            "fixed": [],
            "new_cases": [],
            "new_case_failures": [],
        }

    new_failures = []
    fixed = []
    new_cases = []
    new_case_failures = []

    for result in case_results:
        case_id = result["id"]
        status = result["status"]
        if case_id not in baseline_statuses:
            new_cases.append(case_id)
            if status in ("fail", "error"):
                new_case_failures.append(case_id)
            continue
        previous = baseline_statuses[case_id]
        if previous == "pass" and status in ("fail", "error"):
            new_failures.append(case_id)
        elif previous in ("fail", "error") and status == "pass":
            fixed.append(case_id)

    return {
        "compared_to": str(baseline_path),
        "new_failures": new_failures,
        "fixed": fixed,
        "new_cases": new_cases,
        "new_case_failures": new_case_failures,
    }


def _markdown_table(headers, rows):
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)


def render_markdown(report):
    summary = report["summary"]
    regressions = report["regressions"]
    lines = [
        f"# agent_eval report — {report['suite']}",
        "",
        f"- Adapter: `{report['adapter']}`",
        f"- Started: {report['started_at']}",
        f"- Duration: {report['duration_ms']} ms",
        "",
        "## Summary",
        "",
        _markdown_table(
            ["Total", "Passed", "Failed", "Errored", "Score"],
            [
                [
                    summary["total"],
                    summary["passed"],
                    summary["failed"],
                    summary["errored"],
                    summary["score"],
                ]
            ],
        ),
        "",
        "## Cases",
        "",
    ]

    case_rows = []
    for result in report["cases"]:
        failed_checks = [
            check["type"]
            for check in result["checks"]
            if check["status"] != "pass"
        ]
        case_rows.append(
            [
                f"`{result['id']}`",
                result["status"],
                result["latency_ms"],
                ", ".join(failed_checks) if failed_checks else "-",
            ]
        )
    lines.append(_markdown_table(["ID", "Status", "Latency (ms)", "Failed checks"], case_rows))

    failing_cases = [result for result in report["cases"] if result["status"] != "pass"]
    lines.extend(["", "## Failures", ""])
    if not failing_cases:
        lines.append("No failures.")
    else:
        for result in failing_cases:
            lines.extend([f"### `{result['id']}` — {result['status']}", ""])
            if result["failure_reasons"]:
                for reason in result["failure_reasons"]:
                    lines.append(f"- {reason}")
            else:
                lines.append("- No failure reason recorded.")
            for check in result["checks"]:
                if check["status"] != "pass":
                    lines.append(f"  - `{check['type']}`: {check['detail']}")
            lines.append("")

    lines.extend(["## Regressions", ""])
    if regressions["compared_to"] is None:
        lines.append("No baseline provided.")
    else:
        lines.append(f"- Compared to: `{regressions['compared_to']}`")
        new_failures = regressions["new_failures"]
        lines.append(
            "- New failures: "
            + (", ".join(f"`{case_id}`" for case_id in new_failures) if new_failures else "none")
        )
        fixed = regressions["fixed"]
        lines.append(
            "- Fixed: "
            + (", ".join(f"`{case_id}`" for case_id in fixed) if fixed else "none")
        )
        new_cases = regressions["new_cases"]
        lines.append(
            "- New cases (not regressions): "
            + (", ".join(f"`{case_id}`" for case_id in new_cases) if new_cases else "none")
        )
        new_case_failures = regressions["new_case_failures"]
        lines.append(
            "- New case failures (not regressions): "
            + (
                ", ".join(f"`{case_id}`" for case_id in new_case_failures)
                if new_case_failures
                else "none"
            )
        )

    return "\n".join(lines) + "\n"


def write_reports(report, out_dir):
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    json_path = output / "report.json"
    markdown_path = output / "report.md"
    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, markdown_path


def _build_parser():
    parser = argparse.ArgumentParser(
        prog="tools/agent_eval/run_eval.py",
        description="Run LLM/tool-call regression cases against an adapter.",
    )
    parser.add_argument("--cases", required=True, help="Cases JSON file")
    parser.add_argument(
        "--adapter", required=True, choices=("replay", "command", "openai")
    )
    parser.add_argument(
        "--replay-dir",
        default=str(DEFAULT_REPLAY_DIR),
        help="Directory containing replay fixtures (default: %(default)s)",
    )
    parser.add_argument("--cmd", help="Shell command for the command adapter")
    parser.add_argument(
        "--timeout", type=float, default=60.0, help="Adapter timeout in seconds"
    )
    parser.add_argument("--base-url", help="OpenAI-compatible base URL")
    parser.add_argument("--model", help="Model name for the openai adapter")
    parser.add_argument(
        "--api-key-env",
        default="OPENAI_API_KEY",
        help="Environment variable holding the API key (default: %(default)s)",
    )
    parser.add_argument(
        "--out", help="Output directory (default: tools/agent_eval/out/<UTC timestamp>/)"
    )
    parser.add_argument("--baseline", help="Previous report.json for regression comparison")
    parser.add_argument(
        "--fail-on-regression",
        action="store_true",
        help="Exit 1 when a previously passing case now fails",
    )
    parser.add_argument(
        "--json", action="store_true", help="Print report.json content to stdout"
    )
    return parser


def _run(args):
    suite, cases = load_cases(args.cases)

    if args.timeout <= 0:
        raise checks.ConfigError("--timeout must be greater than zero")

    api_key = None
    if args.adapter == "command":
        if not args.cmd:
            raise checks.ConfigError("--cmd is required for the command adapter")
    elif args.adapter == "openai":
        if not args.base_url:
            raise checks.ConfigError("--base-url is required for the openai adapter")
        if not args.model:
            raise checks.ConfigError("--model is required for the openai adapter")
        api_key = os.environ.get(args.api_key_env)
        if not api_key:
            raise checks.ConfigError(
                f"environment variable {args.api_key_env!r} is not set"
            )

    baseline_statuses = load_baseline(args.baseline) if args.baseline else None

    out_dir = Path(args.out) if args.out else DEFAULT_OUT_DIR / _utc_timestamp()
    started_at = datetime.now(timezone.utc).isoformat()
    started = time.perf_counter()

    options = {
        "replay_dir": args.replay_dir,
        "cmd": args.cmd,
        "timeout": args.timeout,
        "base_url": args.base_url,
        "model": args.model,
        "api_key": api_key,
    }
    case_results = [
        evaluate_case(case, args.adapter, options) for case in cases
    ]
    duration_ms = round((time.perf_counter() - started) * 1000.0, 3)

    report = {
        "suite": suite,
        "started_at": started_at,
        "duration_ms": duration_ms,
        "adapter": args.adapter,
        "cases": case_results,
        "summary": build_summary(case_results),
        "regressions": build_regressions(
            case_results, args.baseline, baseline_statuses
        ),
    }

    write_reports(report, out_dir)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.fail_on_regression and report["regressions"]["new_failures"]:
        return 1

    summary = report["summary"]
    if summary["failed"] or summary["errored"]:
        return 1
    return 0


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        return _run(args)
    except checks.ConfigError as exc:
        print(f"agent_eval: error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"agent_eval: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
