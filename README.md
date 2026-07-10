# Loop Engineering プロジェクトテンプレート

## ループエンジニアリングとは

ループエンジニアリングは、AIエージェントを活用したソフトウェア開発手法です。
作業 → 学習 → 改善 のサイクルを繰り返すことで、エージェントのパフォーマンスが
継続的に向上する仕組みを提供します。

## ディレクトリ構造

```
.
├── .agents/skills/       # agentskills.io 準拠のスキル定義
├── docs/adr/             # Architecture Decision Records
├── learnings/            # セッションから抽出した学び・知見
├── AGENTS.md             # エージェント向けルール定義
└── .github/workflows/    # CI / エージェントハーネス
```

## 使い方

```bash
git clone https://github.com/your-org/loop-engineering-template.git my-project
cd my-project
# 初回のみ project-bootstrapper を実行
```

プロジェクト固有の設定を追加したら、最初のADR（ADR-001）を参考にカスタマイズしてください。

## 対応エージェント

- Hermes Agent
- Opencode
- Claude Code
- Gemini CLI
- Cursor
- GitHub Copilot

## ライセンス

MIT
