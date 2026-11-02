# tools/agent_eval

A small, standard-library-only regression harness for an application's LLM
outputs and tool calls. It is separate from `scripts/run-evals.py`, which
validates this template's skills. `agent_eval` runs case JSON against the LLM
(or agent) you are testing.

## Quick start

```bash
cd "$(git rev-parse --show-toplevel)"

# Run the bundled replay sample (all 8 cases should pass).
python3 tools/agent_eval/run_eval.py \
  --cases tools/agent_eval/cases/example.json \
  --adapter replay \
  --out .tmp-eval-out
echo "exit=$?"
cat .tmp-eval-out/report.md
rm -rf .tmp-eval-out
```

## CLI

```text
python3 tools/agent_eval/run_eval.py --cases <file.json> \
  --adapter replay|command|openai \
  [--replay-dir DIR] \
  [--cmd "..."] [--timeout 60] \
  [--base-url URL] [--model NAME] [--api-key-env VAR] \
  [--out DIR] [--baseline BASELINE.json] [--fail-on-regression] [--json]
```

| Option | Meaning |
| --- | --- |
| `--cases` | Cases JSON file (required). |
| `--adapter` | `replay`, `command`, or `openai` (required). |
| `--replay-dir` | Fixture directory. Default: `tools/agent_eval/fixtures/replay/`. |
| `--cmd` | Shell command for the `command` adapter. The prompt is written to stdin. |
| `--timeout` | Adapter timeout in seconds. Default: `60`. |
| `--base-url` | OpenAI-compatible base URL (for `openai`). |
| `--model` | Model name (for `openai`). |
| `--api-key-env` | Environment variable containing the API key. Default: `OPENAI_API_KEY`. |
| `--out` | Output directory. Default: `tools/agent_eval/out/<UTC timestamp>/`. |
| `--baseline` | Previous `report.json` used for regression comparison. |
| `--fail-on-regression` | Exit `1` if a case that passed in the baseline now fails. |
| `--json` | Print the `report.json` object to stdout. |

Exit codes:

| Code | Meaning |
| --- | --- |
| `0` | All cases passed. |
| `1` | At least one case failed or errored. |
| `2` | Configuration or input error (bad cases file, unknown check type, missing baseline, missing API key, etc.). |

## Case file

```json
{
  "suite": "deskspawn-smoke",
  "cases": [
    {
      "id": "json-mode",
      "prompt": "Return {\"answer\":\"OK\"} as JSON.",
      "tags": ["json"],
      "checks": [
        {"type": "json_valid"},
        {
          "type": "json_schema",
          "schema": {
            "type": "object",
            "required": ["answer"],
            "properties": {"answer": {"type": "string"}}
          }
        },
        {"type": "contains", "value": "OK"},
        {"type": "not_contains", "value": "TODO"},
        {"type": "regex", "pattern": "^\\{.*\\}$", "flags": "s"},
        {"type": "tool_calls", "mode": "subset", "expected": ["search"]},
        {"type": "max_latency_ms", "value": 60000}
      ]
    }
  ]
}
```

`id` must be unique and must not contain path separators. `prompt` is a string.
`tags` is optional. An unknown check `type` is a configuration error
(exit `2`), never a silent pass.

## Check types

| Type | Behaviour |
| --- | --- |
| `json_valid` | The whole response parses as JSON. One surrounding Markdown code fence is stripped first. |
| `json_schema` | Minimal JSON Schema subset: `type`, `required`, `properties`, `items`, `enum`. No `jsonschema` package. |
| `contains` | Case-sensitive substring is present. |
| `not_contains` | Case-sensitive substring is absent. |
| `regex` | `re.search` with `flags` built from `s`, `m`, and/or `i`. |
| `tool_calls` | Compare tool names. `subset`: all expected names present. `exact`: same set. `none`: zero calls. |
| `max_latency_ms` | Adapter-reported latency must be less than or equal to `value`. |

## Adapters

Every adapter returns:

```json
{
  "content": "...",
  "tool_calls": [{"name": "search", "arguments": {}}],
  "latency_ms": 1.2,
  "raw": {}
}
```

### `replay`

Reads `<replay-dir>/<case_id>.json`. If that file is absent, the adapter falls
back to a manifest named `example.json` in the same directory:

```json
{
  "responses": {
    "case-id": {
      "content": "response text",
      "tool_calls": [{"name": "search", "arguments": {"q": "x"}}],
      "latency_ms": 4.2
    }
  }
}
```

A missing fixture makes that case an `error` (and the run exits `1`).

### `command`

Runs `--cmd` with `subprocess.run(shell=True, input=prompt, text=True,
timeout=--timeout)`. stdout becomes `content`; `tool_calls` is empty. A timeout
or a non-zero exit code fails that case with a reason. It does not crash the
whole run.

```bash
python3 tools/agent_eval/run_eval.py \
  --cases tools/agent_eval/cases/example.json \
  --adapter command \
  --cmd "cat" \
  --timeout 5
```

### `openai`

Posts to `{base_url}/chat/completions` with a single user message and
`Authorization: Bearer $API_KEY`. The key is read from `--api-key-env` and is
never written to logs or reports. `choices[0].message.content` and
`choices[0].message.tool_calls` are mapped to the common result shape. HTTP
errors fail the individual case.

```bash
export OPENAI_API_KEY="..."
python3 tools/agent_eval/run_eval.py \
  --cases tools/agent_eval/cases/example.json \
  --adapter openai \
  --base-url https://api.openai.com/v1 \
  --model gpt-4o-mini \
  --api-key-env OPENAI_API_KEY
```

The test suite does not make network calls; the OpenAI adapter is mocked.

## Reports

`--out` receives:

- `report.json` — suite metadata, per-case status/checks/failure reasons,
  summary counts, and regression information.
- `report.md` — summary table, case table, failure details, and regression
  notes. Long outputs are truncated to the first 500 characters.

On `--baseline`, `regressions.new_failures` contains cases that were `pass` in
the baseline and are now `fail`/`error`. Cases that did not exist in the
baseline are listed separately in `new_cases` / `new_case_failures`; their
failures are **not** counted as regressions. `regressions.fixed` lists cases
that moved from failing to passing.

## Tests

```bash
cd "$(git rev-parse --show-toplevel)"
python3 -m unittest discover -s tools/agent_eval/tests -v
```

Tests use only `unittest` and the standard library. Temporary files are created
inside the worktree and removed automatically.
