# Loop Engineering Rules

This project implements **Loop Engineering** — an AI-agent-driven software development methodology
[defined by Addy Osmani (Google)](https://addyosmani.com/blog/loop-engineering/)
([also covered by The New Stack](https://thenewstack.io/loop-engineering/)).

## Core Rules

- **Before starting work**, read `learnings/` (most recent first) and `docs/adr/` to understand context
- **After complex tasks** (5+ tool calls), run `knowledge-harvest` to extract learnings
- **Record architecture decisions** using `decision-recorder` skill as ADRs in `docs/adr/`
- **When a pattern appears 3+ times**, use `skill-crafter` to create a reusable skill
- **At session end**, run `session-reviewer` for retrospective and action items

## Available Skills

- `.agents/skills/loop-engineer` — Core orchestrator for the loop lifecycle
- `.agents/skills/knowledge-harvest` — Extract learnings from completed tasks
- `.agents/skills/skill-crafter` — Auto-create skills from repeated patterns
- `.agents/skills/decision-recorder` — Record Architecture Decision Records
- `.agents/skills/session-reviewer` — End-of-session retrospectives
- `.agents/skills/project-bootstrapper` — Bootstrap new projects (first session only)
- `.agents/skills/project-manager` — Cross-project task management
- `.agents/skills/triage` — Scheduled CI triage and automation dispatch

## The Loop Building Blocks

This template implements the 6 building blocks of loop engineering:

| Block | What It Does | Where |
|-------|-------------|-------|
| **Automations** | Scheduled execution — heartbeat of the loop | `.agents/config/schedules.yaml`, `agent-harness.yml` (schedule trigger) |
| **Worktrees** | Isolated checkouts for parallel sub-agents | `project-manager` skill, `git worktree` |
| **Skills** | Project knowledge codification | `.agents/skills/*/SKILL.md` (9 skills) |
| **Plugins & Connectors** | Real tool access via MCP + distribution bundles | `.mcp/*.json` (GitHub, Linear, Slack, etc.) |
| **Sub-agents** | Maker/checker split for quality | `.agents/agents/*.yaml` (explorer, implementer, verifier) |
| **State** | Cross-session memory | `learnings/`, `docs/adr/`, `traces/` |

For a full walkthrough of how these compose, see [docs/loop-patterns.md](docs/loop-patterns.md).

## ⚠️ Loop Engineering Warnings

Before running automated loops, understand these risks:

1. **Verification is still on you** — A loop running unattended is also making mistakes unattended
2. **Comprehension debt** — The faster the loop ships code, the bigger the gap between what exists and what you understand
3. **Cognitive surrender** — When the loop runs itself, it's tempting to stop having an opinion

## Agent Compatibility

This `.agents/skills/` format follows the [agentskills.io](https://agentskills.io) standard, compatible with:

- Hermes Agent
- Opencode
- Claude Code
- Gemini CLI
- Cursor
- GitHub Copilot

## ⭐ Support

If you find this template useful, consider:
- ⭐ **Starring** the [GitHub repository](https://github.com/shira022/loop-engineering-template) to help others discover it
- 🐛 Reporting bugs via [Issues](https://github.com/shira022/loop-engineering-template/issues)
- 💡 Sharing improvement ideas

---

## 🇯🇵 日本語

### 基本ルール

- 作業開始前に `learnings/` と `docs/adr/` を確認する
- 複雑なタスク完了後は knowledge-harvest スキルを実行する
- 重要なアーキテクチャ判断は decision-recorder でADRに記録する
- 同じパターンが3回以上出現したら skill-crafter でスキル化する
- セッション終了時は session-reviewer で振り返る

### スキル一覧

- `.agents/skills/loop-engineer` — ループエンジニアリング中核オーケストレーター
- `.agents/skills/knowledge-harvest` — タスク完了後の学び抽出
- `.agents/skills/skill-crafter` — 繰り返しパターンから自動スキル化
- `.agents/skills/decision-recorder` — ADR記録
- `.agents/skills/session-reviewer` — セッション終了時の振り返り
- `.agents/skills/project-bootstrapper` — 新規プロジェクト作成（初回のみ）
- `.agents/skills/project-manager` — 複数プロジェクトのタスク管理
- `.agents/skills/triage` — 定期CIトリアージと自動化ディスパッチ

### ループ構成要素

| 要素 | 役割 | 配置 |
|------|------|------|
| **Automations** | 定時実行（ループの心臓） | `.agents/config/schedules.yaml` |
| **Worktrees** | 並列作業の分離 | `project-manager` スキル |
| **Skills** | プロジェクト知識のコード化 | `.agents/skills/*/SKILL.md` |
| **Plugins & Connectors** | 外部ツール連携 (MCP) + 配布バンドル | `.mcp/*.json` |
| **Sub-agents** | メーカー/チェッカー分離 | `.agents/agents/*.yaml` |
| **State** | セッション間状態管理 | `learnings/`, `docs/adr/` |

### ⚠️ Loop Engineering の警告

1. **検証は依然としてあなたの責任** — 無人ループは無人で間違いも作る
2. **理解債務（Comprehension debt）** — ループが早くコードを出せば出すほど、理解のギャップは拡大する
3. **認知放棄（Cognitive surrender）** — ループに任せきりで判断力を失わないこと

### 対応エージェント

この `.agents/skills/` 形式は agentskills.io 標準に準拠しており、
Hermes Agent、Opencode、Claude Code、Gemini CLI、Cursor、GitHub Copilot 等で利用可能です。

### ⭐ サポート

このテンプレートが役立つと思ったら、以下の方法でサポートをお願いします：
- ⭐ **スター** を付けて他の人にも見つけてもらいやすくする
- 🐛 バグ報告は [Issues](https://github.com/shira022/loop-engineering-template/issues) へ
- 💡 改善アイデアの共有
