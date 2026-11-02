import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
TOOLS_DIR = Path(__file__).resolve().parents[2]
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from agent_eval import adapters, checks


class TempDirTestCase(unittest.TestCase):
    def setUp(self):
        self._temp = tempfile.TemporaryDirectory(
            prefix=".agent-eval-test-", dir=str(ROOT)
        )
        self.tmp = Path(self._temp.name)

    def tearDown(self):
        self._temp.cleanup()

    def write_json(self, path, data):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def run_cli(self, args, env=None):
        merged = os.environ.copy()
        if env:
            merged.update(env)
        return subprocess.run(
            [sys.executable, str(TOOLS_DIR / "agent_eval" / "run_eval.py"), *args],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            env=merged,
        )

    def make_cases(self, name, cases):
        return self.write_json(self.tmp / name, {"suite": "test", "cases": cases})


class ReplayAdapterTests(TempDirTestCase):
    def test_replay_returns_content_and_tool_calls(self):
        replay_dir = self.tmp / "replay"
        self.write_json(
            replay_dir / "case-one.json",
            {
                "content": "hello",
                "tool_calls": [
                    {"name": "search", "arguments": {"query": "x"}}
                ],
                "latency_ms": 7.5,
            },
        )

        result = adapters.replay_adapter("case-one", replay_dir)

        self.assertEqual(result["content"], "hello")
        self.assertEqual(
            result["tool_calls"],
            [{"name": "search", "arguments": {"query": "x"}}],
        )
        self.assertEqual(result["latency_ms"], 7.5)
        self.assertIn("raw", result)

    def test_replay_manifest_fallback(self):
        replay_dir = self.tmp / "replay"
        self.write_json(
            replay_dir / "example.json",
            {"responses": {"case-two": {"content": "from manifest"}}},
        )

        result = adapters.replay_adapter("case-two", replay_dir)

        self.assertEqual(result["content"], "from manifest")
        self.assertIsNone(result["latency_ms"])

    def test_missing_replay_fixture_is_case_error(self):
        replay_dir = self.tmp / "replay"
        replay_dir.mkdir()

        with self.assertRaises(adapters.AdapterError) as caught:
            adapters.replay_adapter("missing", replay_dir)

        self.assertEqual(caught.exception.status, "error")
        self.assertIn("no replay fixture", caught.exception.message)

    def test_missing_replay_fixture_makes_cli_case_fail(self):
        cases_file = self.make_cases(
            "cases.json",
            [
                {
                    "id": "missing",
                    "prompt": "hi",
                    "checks": [{"type": "contains", "value": "hi"}],
                }
            ],
        )
        replay_dir = self.tmp / "replay"
        replay_dir.mkdir()
        out_dir = self.tmp / "out"

        proc = self.run_cli(
            [
                "--cases",
                str(cases_file),
                "--adapter",
                "replay",
                "--replay-dir",
                str(replay_dir),
                "--out",
                str(out_dir),
            ]
        )

        self.assertEqual(proc.returncode, 1)
        report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["cases"][0]["status"], "error")
        self.assertEqual(report["summary"]["errored"], 1)
        self.assertEqual(report["summary"]["passed"], 0)


class CommandAdapterTests(TempDirTestCase):
    def test_prompt_is_sent_on_stdin(self):
        result = adapters.command_adapter("prompt from test", "cat", 5)

        self.assertEqual(result["content"], "prompt from test")
        self.assertEqual(result["tool_calls"], [])
        self.assertIsInstance(result["latency_ms"], float)

    def test_timeout_is_case_failure(self):
        with self.assertRaises(adapters.AdapterError) as caught:
            adapters.command_adapter("ignored", "sleep 2", 0.2)

        self.assertEqual(caught.exception.status, "fail")
        self.assertIn("timed out", caught.exception.message)

    def test_nonzero_exit_is_case_failure(self):
        with self.assertRaises(adapters.AdapterError) as caught:
            adapters.command_adapter("ignored", "exit 7", 5)

        self.assertEqual(caught.exception.status, "fail")
        self.assertIn("7", caught.exception.message)

    def test_cli_command_adapter(self):
        cases_file = self.make_cases(
            "cases.json",
            [
                {
                    "id": "echo",
                    "prompt": "round-trip",
                    "checks": [{"type": "contains", "value": "round-trip"}],
                }
            ],
        )
        out_dir = self.tmp / "out"

        proc = self.run_cli(
            [
                "--cases",
                str(cases_file),
                "--adapter",
                "command",
                "--cmd",
                "cat",
                "--timeout",
                "5",
                "--out",
                str(out_dir),
            ]
        )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["summary"]["passed"], 1)


class OpenAIAdapterTests(TempDirTestCase):
    def test_maps_content_and_tool_calls_without_leaking_key(self):
        payload = {
            "choices": [
                {
                    "message": {
                        "content": "answer",
                        "tool_calls": [
                            {
                                "function": {
                                    "name": "search",
                                    "arguments": "{\"q\": \"x\"}",
                                }
                            }
                        ],
                    }
                }
            ]
        }

        class FakeResponse:
            def read(self):
                return json.dumps(payload).encode("utf-8")

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        with mock.patch.object(
            adapters.urllib.request, "urlopen", return_value=FakeResponse()
        ) as urlopen:
            result = adapters.openai_adapter(
                "question", "http://example.test/v1/", "test-model", "super-secret", 5
            )

        self.assertEqual(result["content"], "answer")
        self.assertEqual(
            result["tool_calls"],
            [{"name": "search", "arguments": {"q": "x"}}],
        )
        self.assertNotIn("super-secret", json.dumps(result["raw"]))
        request = urlopen.call_args[0][0]
        self.assertEqual(
            request.get_header("Authorization"), "Bearer super-secret"
        )

    def test_http_error_is_case_failure(self):
        error = adapters.urllib.error.HTTPError(
            "http://example.test/v1/chat/completions", 500, "boom", None, None
        )
        with mock.patch.object(
            adapters.urllib.request, "urlopen", side_effect=error
        ):
            with self.assertRaises(adapters.AdapterError) as caught:
                adapters.openai_adapter(
                    "question", "http://example.test/v1", "m", "secret", 5
                )

        self.assertEqual(caught.exception.status, "fail")
        self.assertIn("500", caught.exception.message)


class CheckTests(unittest.TestCase):
    def run_one(self, check, **result):
        base = {"content": "", "tool_calls": [], "latency_ms": 1.0}
        base.update(result)
        return checks.run_check(check, base)

    def test_json_valid_plain(self):
        outcome = self.run_one({"type": "json_valid"}, content='{"a": 1}')
        self.assertEqual(outcome["status"], "pass")

    def test_json_valid_strips_code_fences(self):
        content = "```json\n{\"answer\":\"OK\"}\n```"
        outcome = self.run_one({"type": "json_valid"}, content=content)
        self.assertEqual(outcome["status"], "pass")

    def test_json_valid_rejects_bad_json(self):
        outcome = self.run_one({"type": "json_valid"}, content="not json")
        self.assertEqual(outcome["status"], "fail")

    def test_json_schema_required_violation(self):
        check = {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "required": ["answer"],
                "properties": {"answer": {"type": "string"}},
            },
        }
        outcome = self.run_one(check, content='{"other": 1}')
        self.assertEqual(outcome["status"], "fail")
        self.assertIn("answer", outcome["detail"])

    def test_json_schema_enum_and_items(self):
        check = {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "required": ["status", "items"],
                "properties": {
                    "status": {"type": "string", "enum": ["ok"]},
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["id"],
                            "properties": {"id": {"type": "integer"}},
                        },
                    },
                },
            },
        }
        good = self.run_one(
            check, content='{"status":"ok","items":[{"id":1}]}'
        )
        bad = self.run_one(
            check, content='{"status":"bad","items":[{"id":"x"}]}'
        )
        self.assertEqual(good["status"], "pass")
        self.assertEqual(bad["status"], "fail")

    def test_contains_and_not_contains(self):
        self.assertEqual(
            self.run_one({"type": "contains", "value": "OK"}, content="OK!")[
                "status"
            ],
            "pass",
        )
        self.assertEqual(
            self.run_one({"type": "contains", "value": "ok"}, content="OK!")[
                "status"
            ],
            "fail",
        )
        self.assertEqual(
            self.run_one(
                {"type": "not_contains", "value": "TODO"}, content="OK!"
            )["status"],
            "pass",
        )
        self.assertEqual(
            self.run_one(
                {"type": "not_contains", "value": "TODO"}, content="TODO"
            )["status"],
            "fail",
        )

    def test_regex_and_flags(self):
        check = {"type": "regex", "pattern": "^hello.*world$", "flags": "is"}
        outcome = self.run_one(check, content="Hello\nWorld")
        self.assertEqual(outcome["status"], "pass")
        missing = self.run_one(check, content="goodbye")
        self.assertEqual(missing["status"], "fail")

    def test_tool_calls_subset(self):
        check = {"type": "tool_calls", "mode": "subset", "expected": ["search"]}
        self.assertEqual(
            self.run_one(
                check,
                tool_calls=[
                    {"name": "search", "arguments": {}},
                    {"name": "extra", "arguments": {}},
                ],
            )["status"],
            "pass",
        )
        self.assertEqual(
            self.run_one(check, tool_calls=[{"name": "other"}])["status"],
            "fail",
        )

    def test_tool_calls_exact(self):
        check = {
            "type": "tool_calls",
            "mode": "exact",
            "expected": ["lookup", "summarize"],
        }
        self.assertEqual(
            self.run_one(
                check,
                tool_calls=[
                    {"name": "lookup"},
                    {"name": "summarize"},
                ],
            )["status"],
            "pass",
        )
        self.assertEqual(
            self.run_one(check, tool_calls=[{"name": "lookup"}])["status"],
            "fail",
        )
        self.assertEqual(
            self.run_one(
                check,
                tool_calls=[
                    {"name": "lookup"},
                    {"name": "summarize"},
                    {"name": "extra"},
                ],
            )["status"],
            "fail",
        )

    def test_tool_calls_none(self):
        check = {"type": "tool_calls", "mode": "none", "expected": []}
        self.assertEqual(
            self.run_one(check, tool_calls=[])["status"], "pass"
        )
        self.assertEqual(
            self.run_one(check, tool_calls=[{"name": "search"}])["status"],
            "fail",
        )

    def test_max_latency(self):
        check = {"type": "max_latency_ms", "value": 100}
        self.assertEqual(
            self.run_one(check, latency_ms=99.9)["status"], "pass"
        )
        self.assertEqual(
            self.run_one(check, latency_ms=100.1)["status"], "fail"
        )

    def test_unknown_check_type_is_config_error(self):
        with self.assertRaises(checks.ConfigError):
            checks.validate_check({"type": "does_not_exist"})

    def test_unknown_schema_type_is_config_error(self):
        with self.assertRaises(checks.ConfigError):
            checks.validate_check(
                {"type": "json_schema", "schema": {"type": "widget"}}
            )


class CliBehaviourTests(TempDirTestCase):
    def test_unknown_check_type_exits_2(self):
        cases_file = self.make_cases(
            "cases.json",
            [
                {
                    "id": "bad-check",
                    "prompt": "hi",
                    "checks": [{"type": "no-such-check"}],
                }
            ],
        )
        proc = self.run_cli(
            [
                "--cases",
                str(cases_file),
                "--adapter",
                "replay",
                "--out",
                str(self.tmp / "out"),
            ]
        )

        self.assertEqual(proc.returncode, 2)
        self.assertIn("unknown check type", proc.stderr)

    def test_all_pass_exits_0_and_writes_reports(self):
        cases_file = self.make_cases(
            "cases.json",
            [
                {
                    "id": "one",
                    "prompt": "a",
                    "checks": [{"type": "contains", "value": "OK"}],
                },
                {
                    "id": "two",
                    "prompt": "b",
                    "checks": [{"type": "json_valid"}],
                },
            ],
        )
        replay_dir = self.tmp / "replay"
        self.write_json(
            replay_dir / "one.json",
            {"content": "OK", "tool_calls": [], "latency_ms": 1},
        )
        self.write_json(
            replay_dir / "two.json",
            {"content": '{"ok": true}', "tool_calls": [], "latency_ms": 2},
        )
        out_dir = self.tmp / "out"

        proc = self.run_cli(
            [
                "--cases",
                str(cases_file),
                "--adapter",
                "replay",
                "--replay-dir",
                str(replay_dir),
                "--out",
                str(out_dir),
            ]
        )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((out_dir / "report.json").is_file())
        self.assertTrue((out_dir / "report.md").is_file())
        report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(
            report["summary"],
            {
                "total": 2,
                "passed": 2,
                "failed": 0,
                "errored": 0,
                "score": 1.0,
            },
        )
        self.assertIsNone(report["regressions"]["compared_to"])

    def test_failure_exits_1(self):
        cases_file = self.make_cases(
            "cases.json",
            [
                {
                    "id": "one",
                    "prompt": "a",
                    "checks": [{"type": "contains", "value": "OK"}],
                }
            ],
        )
        replay_dir = self.tmp / "replay"
        self.write_json(
            replay_dir / "one.json",
            {"content": "BAD", "tool_calls": [], "latency_ms": 1},
        )

        proc = self.run_cli(
            [
                "--cases",
                str(cases_file),
                "--adapter",
                "replay",
                "--replay-dir",
                str(replay_dir),
                "--out",
                str(self.tmp / "out"),
            ]
        )

        self.assertEqual(proc.returncode, 1)

    def test_json_flag_prints_report(self):
        cases_file = self.make_cases(
            "cases.json",
            [
                {
                    "id": "one",
                    "prompt": "a",
                    "checks": [{"type": "contains", "value": "OK"}],
                }
            ],
        )
        replay_dir = self.tmp / "replay"
        self.write_json(
            replay_dir / "one.json",
            {"content": "OK", "tool_calls": [], "latency_ms": 1},
        )

        proc = self.run_cli(
            [
                "--cases",
                str(cases_file),
                "--adapter",
                "replay",
                "--replay-dir",
                str(replay_dir),
                "--out",
                str(self.tmp / "out"),
                "--json",
            ]
        )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        printed = json.loads(proc.stdout)
        self.assertEqual(printed["summary"]["passed"], 1)
        self.assertEqual(printed["suite"], "test")

    def test_bundled_example_suite_passes(self):
        out_dir = self.tmp / "out"
        proc = self.run_cli(
            [
                "--cases",
                str(ROOT / "tools/agent_eval/cases/example.json"),
                "--adapter",
                "replay",
                "--out",
                str(out_dir),
            ]
        )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["summary"]["total"], 8)
        self.assertEqual(report["summary"]["passed"], 8)
        self.assertEqual(report["summary"]["score"], 1.0)


class RegressionTests(TempDirTestCase):
    def _baseline(self, statuses):
        return {
            "suite": "test",
            "cases": [
                {"id": case_id, "status": status, "checks": [], "failure_reasons": []}
                for case_id, status in statuses.items()
            ],
        }

    def test_previous_pass_to_fail_is_new_failure(self):
        cases_file = self.make_cases(
            "cases.json",
            [
                {
                    "id": "regressed",
                    "prompt": "a",
                    "checks": [{"type": "contains", "value": "OK"}],
                }
            ],
        )
        replay_dir = self.tmp / "replay"
        self.write_json(
            replay_dir / "regressed.json",
            {"content": "BAD", "tool_calls": [], "latency_ms": 1},
        )
        baseline_file = self.write_json(
            self.tmp / "baseline.json", self._baseline({"regressed": "pass"})
        )
        out_dir = self.tmp / "out"

        proc = self.run_cli(
            [
                "--cases",
                str(cases_file),
                "--adapter",
                "replay",
                "--replay-dir",
                str(replay_dir),
                "--baseline",
                str(baseline_file),
                "--fail-on-regression",
                "--out",
                str(out_dir),
            ]
        )

        self.assertEqual(proc.returncode, 1)
        report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["regressions"]["new_failures"], ["regressed"])
        self.assertEqual(report["regressions"]["new_cases"], [])
        self.assertEqual(report["regressions"]["new_case_failures"], [])

    def test_new_case_failure_is_not_a_regression(self):
        cases_file = self.make_cases(
            "cases.json",
            [
                {
                    "id": "old",
                    "prompt": "a",
                    "checks": [{"type": "contains", "value": "OK"}],
                },
                {
                    "id": "new",
                    "prompt": "b",
                    "checks": [{"type": "contains", "value": "OK"}],
                },
            ],
        )
        replay_dir = self.tmp / "replay"
        self.write_json(
            replay_dir / "old.json",
            {"content": "OK", "tool_calls": [], "latency_ms": 1},
        )
        self.write_json(
            replay_dir / "new.json",
            {"content": "BAD", "tool_calls": [], "latency_ms": 1},
        )
        baseline_file = self.write_json(
            self.tmp / "baseline.json", self._baseline({"old": "pass"})
        )
        out_dir = self.tmp / "out"

        proc = self.run_cli(
            [
                "--cases",
                str(cases_file),
                "--adapter",
                "replay",
                "--replay-dir",
                str(replay_dir),
                "--baseline",
                str(baseline_file),
                "--fail-on-regression",
                "--out",
                str(out_dir),
            ]
        )

        self.assertEqual(proc.returncode, 1)
        report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["regressions"]["new_failures"], [])
        self.assertEqual(report["regressions"]["new_cases"], ["new"])
        self.assertEqual(report["regressions"]["new_case_failures"], ["new"])

    def test_fixed_case_is_reported(self):
        cases_file = self.make_cases(
            "cases.json",
            [
                {
                    "id": "recovered",
                    "prompt": "a",
                    "checks": [{"type": "contains", "value": "OK"}],
                }
            ],
        )
        replay_dir = self.tmp / "replay"
        self.write_json(
            replay_dir / "recovered.json",
            {"content": "OK", "tool_calls": [], "latency_ms": 1},
        )
        baseline_file = self.write_json(
            self.tmp / "baseline.json", self._baseline({"recovered": "fail"})
        )
        out_dir = self.tmp / "out"

        proc = self.run_cli(
            [
                "--cases",
                str(cases_file),
                "--adapter",
                "replay",
                "--replay-dir",
                str(replay_dir),
                "--baseline",
                str(baseline_file),
                "--out",
                str(out_dir),
            ]
        )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["regressions"]["fixed"], ["recovered"])

    def test_missing_baseline_exits_2(self):
        cases_file = self.make_cases(
            "cases.json",
            [
                {
                    "id": "one",
                    "prompt": "a",
                    "checks": [{"type": "contains", "value": "OK"}],
                }
            ],
        )

        proc = self.run_cli(
            [
                "--cases",
                str(cases_file),
                "--adapter",
                "replay",
                "--baseline",
                str(self.tmp / "does-not-exist.json"),
                "--out",
                str(self.tmp / "out"),
            ]
        )

        self.assertEqual(proc.returncode, 2)


class ReportDetailTests(TempDirTestCase):
    def test_failure_report_truncates_long_output(self):
        long_content = "X" * 800
        cases_file = self.make_cases(
            "cases.json",
            [
                {
                    "id": "long",
                    "prompt": "a",
                    "checks": [{"type": "contains", "value": "OK"}],
                }
            ],
        )
        replay_dir = self.tmp / "replay"
        self.write_json(
            replay_dir / "long.json",
            {"content": long_content, "tool_calls": [], "latency_ms": 1},
        )
        out_dir = self.tmp / "out"

        proc = self.run_cli(
            [
                "--cases",
                str(cases_file),
                "--adapter",
                "replay",
                "--replay-dir",
                str(replay_dir),
                "--out",
                str(out_dir),
            ]
        )

        self.assertEqual(proc.returncode, 1)
        markdown = (out_dir / "report.md").read_text(encoding="utf-8")
        self.assertIn("X" * 500, markdown)
        self.assertNotIn("X" * 501, markdown)


if __name__ == "__main__":
    unittest.main()
