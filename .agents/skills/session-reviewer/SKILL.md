---
name: session-reviewer
description: セッション終了時に振り返りを行い、学び・改善点・アクションアイテムを抽出する。Use at the end of every session to close the loop engineering cycle.
version: 1.0.0
tags: [review, retrospective, improvement]
category: meta
compatibility: 'Hermes Agent, Opencode'
metadata:
  version: '1.1.0'
  hermes:
    tags: [review, retrospective, improvement]
---

# session-reviewer

セッション終了時にトリガーされ、そのセッションの振り返りを実施する。

## 開始時

1. **過去レビューの確認** — `learnings/` 内の `session-review-*.md` ファイルを全て読み込め。日付降順でソートし、直近の改善点を把握せよ。
2. **セッションログの収集** — このセッションで実行したツールコール・作成したファイル・変更したファイルの一覧を可能な限り取得せよ。

## 実行中

以下の観点でセッションをレビューし、`learnings/session-review-YYYY-MM-DD.md` に保存せよ。

### レビュー項目

#### 1. 達成内容（Accomplished）

- このセッションで何を達成したか？
- 完了したタスク・未完了のタスクは何か？
- 想定より進んだ・遅れた点はあるか？

#### 2. 学び（Learned）

- 新しく得た知識・気づきは何か？
- 予想外の発見・問題はあったか？
- プロジェクトやコードベースに関する理解の変化は？

#### 3. 改善点（Improvements）

- 効率を妨げた要因はあったか？
- コミュニケーション・ツール・プロセスの問題点は？
- 次回同じ状況で最適な振る舞いは何か？

#### 4. アクションアイテム（Action Items）

- 次回セッションで最初に取り組むべきタスクは？
- 具体的で実行可能な ToDo を箇条書きで列挙せよ
- 各アイテムに優先度（High/Medium/Low）を付与せよ

#### 5. 自動化パターン（Automation Patterns）

- このセッションで **3回以上** 繰り返された操作・パターンはあるか？
- そのパターンをスキルとして抽出する価値があるか？（→ `skill-crafter` に依頼すべきか評価せよ）
- 定型化できる手作業は残っているか？

#### 6. knowledge-harvest 漏れチェック

- 複雑なタスク（ツールコール5回以上）を完了したにも関わらず `knowledge-harvest` が実行されていない場合、未実行であることを明示的にフラグせよ
- フラグした内容はアクションアイテムに含めよ

## 出力ファイル形式

```
learnings/session-review-YYYY-MM-DD.md
```

### ファイル構成

```markdown
# Session Review: YYYY-MM-DD

## Accomplished
...

## Learned
...

## Improvements
...

## Action Items
- [ ] (High) ...
- [ ] (Medium) ...
- [ ] (Low) ...

## Automation Patterns
...

## Knowledge Harvest Flags
...
```

## 終了時

- 作成したレビューファイルへのパスを報告せよ
- アクションアイテムが存在する場合、次回セッションに向けて要約を提示せよ
- `learnings/` ディレクトリが存在しない場合は作成せよ

## Gotchas

- Run at END of session, not during
- Always assign priority to action items (High/Medium/Low)
- If knowledge-harvest was skipped, flag it but do NOT run it from within the reviewer
- Archive old review files if learnings/ grows large
