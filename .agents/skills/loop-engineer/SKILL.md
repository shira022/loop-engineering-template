---
name: loop-engineer
description: Core orchestrator for the loop engineering lifecycle — manages knowledge harvesting, skill crafting, and session review across every session.
tags: [core, loop-engineering, automation]
category: development
compatibility: 'Hermes Agent, Opencode, Claude Code, Gemini CLI, Cursor, GitHub Copilot'
version: '2.0.0'
---

# loop-engineer

このスキルは、セッション全体を通じてループエンジニアリングサイクルを統括する。

## 開始時

1. **過去知識の確認** — `learnings/` 内の全 `.md` ファイルを読み込め。日付降順でソートし、直近の知見を把握せよ。
2. **アーキテクチャコンテキストの確認** — `docs/adr/` に `.md` ファイルが存在する場合、全て読み込め。存在しなければスキップしてよい。
3. **セッションコンテキストの初期化** — このセッションのツールコール数を内部的にカウントし始めよ。

## 実行中

- 同一パターンが **3回以上** 出現した場合、直ちに `skill-crafter` スキルに通知せよ。
- 複雑なタスク（ツールコールが5回以上）を完了したら、`knowledge-harvest` スキルを実行せよ。

## 終了時

- セッション終了前に `session-reviewer` を実行せよ。`session-reviewer` が存在しない場合（まだ作成されていない場合）はスキップしてよい。
- 全てのカウンターをリセットせよ。

## Gotchas

- Do NOT run knowledge-harvest for trivial tasks (under 5 tool calls)
- session-reviewer may not exist on first session; skip gracefully
- AGENTS.md rules take precedence over skill instructions
