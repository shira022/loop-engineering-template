---
name: loop-engineer
description: Core orchestrator for the loop engineering lifecycle — manages knowledge harvesting, skill crafting, and session review across every session.
tags: [core, loop-engineering, automation]
category: development
compatibility: 'Hermes Agent, Opencode, Claude Code, Gemini CLI, Cursor, GitHub Copilot'
version: '2.0.0'
metadata:
  version: '2.0.0'
  depends_on: [knowledge-harvest, skill-crafter, session-reviewer]
  hermes:
    tags: [core, loop-engineering, automation]
---

# loop-engineer

The core orchestrator for the Loop Engineering lifecycle. Manages session start, in-session execution, and session teardown by coordinating all other skills.

ループエンジニアリングサイクルの統括オーケストレーター。セッションの開始・実行・終了を管理し、全スキルを連携させる。

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

## 実行トレース

セッションの開始時に `traces/` ディレクトリに実行トレースファイルを作成せよ：

```json
{
  "session_id": "<unique-id>",
  "started_at": "<ISO-8601>",
  "skills_loaded": ["loop-engineer", ...],
  "tool_calls": 0,
  "tokens_used": 0,
  "files_created": [],
  "files_modified": []
}
```

セッション中はツールコール数をトレースファイルに記録し、終了時に `session-reviewer` がファイナライズする。

## Trace Management

> **English:** Create a trace file at session start recording session_id, started_at, and skills_loaded. During the session, increment the tool_calls counter. At session end, finalize with completed_at timestamp. Traces enable quantitative metrics via `scripts/analyze-traces.py`.

## ⚠️ Loop Safety

このスキルを使用する際は以下の警告を理解した上で実装せよ：

### 1. Verification is Still On You
Loop engineering automates execution, not accountability. A verifier sub-agent reduces mistakes but does NOT eliminate them. Always review generated output before considering it final. "Done" is a claim, not a proof.

### 2. Comprehension Debt
The faster the loop ships code you did not write, the bigger the gap between what exists and what you understand. Read the loop's output regularly — especially the learnings/, traces/, and generated code.

### 3. Cognitive Surrender
When the loop runs itself, it's tempting to stop having an opinion. Designing the loop is the cure when done with judgment, and the accelerant when done to avoid thinking. Stay engaged.

### 4. Token Cost Awareness
Each sub-agent call, knowledge-harvest run, and session review consumes tokens. Monitor your usage. This skill's typical cost: ~500-2000 tokens per invocation depending on context size.

## Gotchas

- Do NOT run knowledge-harvest for trivial tasks (under 5 tool calls)
- session-reviewer may not exist on first session; skip gracefully
- AGENTS.md rules take precedence over skill instructions
