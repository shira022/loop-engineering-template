# Loop Engineering Rules

This project implements **Loop Engineering** — an AI-agent-driven software development methodology.

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

## Agent Compatibility

This `.agents/skills/` format follows the [agentskills.io](https://agentskills.io) standard, compatible with:

- Hermes Agent
- Opencode
- Claude Code
- Gemini CLI
- Cursor
- GitHub Copilot

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

### 対応エージェント

この `.agents/skills/` 形式は agentskills.io 標準に準拠しており、
Hermes Agent、Opencode、Claude Code、Gemini CLI、Cursor、GitHub Copilot 等で利用可能です。
