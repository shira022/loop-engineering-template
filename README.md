# Loop Engineering プロジェクトテンプレート

[![CI](https://github.com/shira022/loop-engineering-template/actions/workflows/ci.yml/badge.svg)](https://github.com/shira022/loop-engineering-template/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![agentskills.io](https://img.shields.io/badge/agentskills.io-compatible-blue)](https://agentskills.io)

## ループエンジニアリングとは

ループエンジニアリングは、AIエージェントを活用したソフトウェア開発手法です。
**作業 → 学習 → 改善** のサイクルを繰り返すことで、エージェントのパフォーマンスが
継続的に向上する仕組みを提供します。

### コアサイクル

1. **Work** — 開発タスクを実行（コーディング、テスト、ドキュメント作成）
2. **Learn** — 完了したタスクから構造化された知識を抽出
3. **Improve** — 知識を再利用可能なスキルとして蓄積し、次回セッションに活用

## ディレクトリ構造

```
.
├── .agents/skills/           # agentskills.io 準拠のスキル定義
│   ├── loop-engineer/        # ループエンジニアリング中核オーケストレーター
│   ├── knowledge-harvest/    # タスク完了後の学び抽出
│   ├── skill-crafter/        # 繰り返しパターンから自動スキル化
│   ├── decision-recorder/    # Architecture Decision Records
│   ├── session-reviewer/     # セッション終了時の振り返り
│   ├── project-bootstrapper/ # 新規プロジェクト作成（初回のみ）
│   └── project-manager/      # 複数プロジェクトのタスク管理
├── docs/adr/                 # Architecture Decision Records
├── learnings/                # セッションから抽出した学び・知見
├── src/                      # サンプルコード
├── tests/                    # サンプルテスト
├── scripts/                  # ユーティリティスクリプト
├── AGENTS.md                 # エージェント向けルール定義
├── CONTRIBUTING.md           # コントリビューションガイド
├── Makefile                  # タスクランナー
└── .github/workflows/        # CI / Agent Harness / Release
```

## クイックスタート

```bash
# テンプレートから新規プロジェクト作成
gh repo create my-project --template shira022/loop-engineering-template --public
git clone https://github.com/your-org/my-project.git
cd my-project

# 初回のみ project-bootstrapper を実行（対話型セットアップ）
# エージェントに「このテンプレートを使って新しいプロジェクトを
# ブートストラップして」と指示
```

## 組み込みワークフロー

| ワークフロー | トリガー | 説明 |
|:---|:---|:---|
| **CI** | push / PR | スキルバリデーション + マルチ言語テスト |
| **Agent Harness** | 手動 (workflow_dispatch) | エージェント（Hermes/Opencode/Claude）によるタスク実行 |
| **Release** | タグ `v*.*.*` プッシュ | GitHub Release 自動作成 |

## 対応エージェント

この `.agents/skills/` 形式は [agentskills.io](https://agentskills.io) 標準に準拠しており、
以下のエージェントで利用可能です：

- Hermes Agent
- Opencode
- Claude Code
- Gemini CLI
- Cursor
- GitHub Copilot

## コントリビューション

コントリビューションを歓迎します！[CONTRIBUTING.md](CONTRIBUTING.md) をご覧ください。

## ライセンス

MIT
