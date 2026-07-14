# Eval Harness

このプロジェクトは agentskills.io の評価フレームワークに対応しています。
各スキルに `evals/evals.json` が配置されており、スキルの品質を自動検証できます。

## 構成

```
.agents/skills/<skill-name>/
├── SKILL.md
└── evals/
    └── evals.json        # テストケース定義
```

## テストケースの構造

```json
{
  "skill_name": "skill-name",
  "evals": [
    {
      "id": 1,
      "prompt": "ユーザー入力を模したプロンプト",
      "expected_output": "期待される出力の説明",
      "files": ["evals/files/sample.csv"],
      "assertions": [
        "検証可能な表明1",
        "検証可能な表明2"
      ]
    }
  ]
}
```

## ローカル実行

```bash
# 全スキルの評価を実行
python3 scripts/run-evals.py

# 特定スキルのみ
python3 scripts/run-evals.py --skill knowledge-harvest
```

## CI での実行

`.github/workflows/ci.yml` で全スキルの評価が自動実行されます。
評価に失敗した場合は CI が失敗します。

## アサーションの書き方

良いアサーション:
- `"Output file is valid JSON"` — プログラムで検証可能
- `"Report includes at least 3 recommendations"` — 計測可能

弱いアサーション:
- `"Output is good"` — 曖昧すぎる
- `"Output uses exactly 'Total: $X'"` — 脆すぎる
