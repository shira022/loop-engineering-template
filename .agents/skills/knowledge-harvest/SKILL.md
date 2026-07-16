---
name: knowledge-harvest
description: Extracts structured learnings from completed complex tasks and persists them to the learnings/ directory for future sessions. Use after solving a non-trivial problem or debugging session to preserve reusable knowledge.
tags: [learning, knowledge, documentation]
category: development
compatibility:
  - 'Hermes Agent'
  - 'Opencode'
  - 'Claude Code'
  - 'Gemini CLI'
  - 'Cursor'
  - 'GitHub Copilot'
metadata:
  version: '1.1.0'
  depends_on: [loop-engineer, skill-crafter]
---

# knowledge-harvest

> **English:** Extracts structured learnings from completed complex tasks and persists them to `learnings/` for future sessions.
>
> このスキルは、完了した複雑なタスクから学びを抽出し、`learnings/` に保存する。

## トリガー条件

- `loop-engineer` から呼び出されたとき（目安：ツールコール5回以上のタスク完了後）
- または、エージェントが明示的に「知見を記録すべき」と判断したとき

## 実行手順

1. **学びの構造化** — 以下のフォーマットで知見を整理せよ：
   - **What I learned**: 何を学んだか（1〜3文）
   - **Pattern**: 再利用可能なパターンの説明
   - **Reusable for**: この知見が将来どのような状況で再利用できるか

2. **ファイル保存** — `learnings/` ディレクトリに、以下の命名規則で保存せよ：
   ```
   learnings/YYYY-MM-DD-<brief-slug>.md
   ```
   例: `learnings/2025-06-15-api-error-handling.md`

3. **パターン重複検出** — `learnings/` 内の既存ファイルを全て読み込み、今回抽出したパターンと類似するものがないか確認せよ。
   - 同一パターンが **3回以上** 出現した場合、`skill-crafter` スキルに通知せよ。

4. **フォーマット例**:
   ```markdown
   # YYYY-MM-DD: <タイトル>

   ## What I learned
   <学びの内容>

   ## Pattern
   <パターンの説明>

   ## Reusable for
   <再利用できる状況>
   ```

## Gotchas

- Update the active trace file's `files_created` array when saving learnings
- Set the `source` field in learning frontmatter to enable traceability

- Only trigger for complex tasks (5+ tool calls)
- Do not overwrite existing learnings files; always create new dated files
- learnings/ files are tracked in git; avoid committing sensitive information
