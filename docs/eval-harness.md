# Skill Evaluation Harness

This project supports the [agentskills.io](https://agentskills.io) evaluation framework. Each skill has an `evals/evals.json` file that defines automated test cases for validating skill quality.

## Structure

```
.agents/skills/<skill-name>/
├── SKILL.md
└── evals/
    └── evals.json        # Test case definitions
```

## Test Case Format

```json
{
  "skill_name": "skill-name",
  "evals": [
    {
      "id": 1,
      "prompt": "Simulated user prompt for the skill",
      "expected_output": "Description of expected output",
      "assertions": [
        "Verifiable assertion 1",
        "Verifiable assertion 2"
      ]
    }
  ]
}
```

## Running Locally

```bash
# Run all skill evaluations
python3 scripts/run-evals.py

# Run a specific skill
python3 scripts/run-evals.py --skill knowledge-harvest
```

## CI Integration

The `.github/workflows/ci.yml` workflow automatically runs all skill evaluations on every push and PR. Failed evaluations cause the CI to fail.

## Writing Good Assertions

### Good assertions:
- `"Output path starts with docs/adr/"` — programmatically verifiable
- `"Content contains heading for status"` — measurable
- `"Skill learns from learnings/ directory"` — testable behavior

### Weak assertions:
- `"Output is good"` — too vague
- `"Output uses exactly 'Total: $X'"` — too brittle

## Current Evaluation Coverage

| Skill | Evals | Status |
|-------|-------|--------|
| loop-engineer | 1 | ✅ |
| knowledge-harvest | 1 | ✅ |
| decision-recorder | 1 | ✅ |
| session-reviewer | 1 | ✅ |
| skill-crafter | 2 | ✅ |
| project-bootstrapper | 2 | ✅ |
| project-manager | 2 | ✅ |
| test-policy | 2 | ✅ |

---

## 🇯🇵 日本語

各スキルに `evals/evals.json` が配置されており、スキルの品質を自動検証できます。`scripts/run-evals.py` でローカル実行、CIで自動検証。
