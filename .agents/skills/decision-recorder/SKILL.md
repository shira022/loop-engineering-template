---
name: decision-recorder
description: アーキテクチャ上の重要な決定をADR（Architecture Decision Record）として記録・管理する。
version: 1.1.0
tags: [architecture, decision, documentation, adr]
category: documentation
compatibility: 'Hermes Agent, Opencode, Claude Code, Gemini CLI, Cursor, GitHub Copilot'
metadata:
  depends_on: [loop-engineer]
  hermes:
    tags: [architecture, decision, documentation, adr]
---

# decision-recorder

> **English:** Creates and updates Architecture Decision Records (ADRs) when important architectural decisions are made.
>
> アーキテクチャ上の重要な決定が行われた際に、ADR（Architecture Decision Record）を作成・更新する。

## 開始時

1. **既存ADRの読み込み** — `docs/adr/` 内の全 `.md` ファイルを読み込み、既存の決定を把握せよ。番号順にソートし、最新の番号（`NNN`）を特定せよ。
2. **テンプレートの確認** — `docs/adr/_template.md` が存在するか確認せよ。存在しない場合、標準テンプレートを使用して作成せよ。

## 実行中

### ADRの作成

以下の条件のいずれかに該当する場合、ADRを作成せよ：

- アーキテクチャ全体に影響を与える決定を行ったとき
- 技術スタック・フレームワーク・ライブラリを選定したとき
- 重要なトレードオフを伴う設計判断を下したとき
- 既存のADRで規定された方針を変更するとき

### ADRの命名規則

```
NNN-title-in-kebab-case.md
```

- `NNN`：既存の最大番号 + 1（ゼロ埋め3桁）
- タイトルは簡潔で説明的なkebab-caseとする

### ADRの構成

テンプレートに従いつつ、以下のセクションを必ず含めよ：

| セクション | 内容 |
|---|---|
| **Title** | 決定のタイトル（簡潔に） |
| **Status** | `proposed` / `accepted` / `superseded` |
| **Context** | この決定に至った背景・問題・制約 |
| **Decision** | 採用した解決策とその理由 |
| **Consequences** | 決定による影響（良い面・悪い面・トレードオフ） |

### ステータス管理

- 作成時は **`proposed`** に設定せよ
- チーム内で合意が得られたら **`accepted`** に更新せよ
- 別のADRに置き換わる場合は、旧ADRのステータスを **`superseded`** に変更し、置き換え先のADR番号を追記せよ

### 関連性の記録

- 既存ADRに関連する決定の場合、本文中に `Supersedes ADR-XXX` や `Related to ADR-XXX` のように明示的に参照せよ
- 同じトピックの連続した決定は、Previous/Next リンクを末尾に付与するとよい

### 新規ファイル作成時の注意

- ファイル作成後、ユーザーに内容を確認させよ
- `docs/adr/` ディレクトリが存在しない場合は作成せよ

## 終了時

- 今回作成・更新したADRの一覧を簡潔に報告せよ

## ⚠️ Loop Safety

### 1. Decision Debt
Every ADR is a commitment. Recording too many trivial decisions creates noise that obscures truly important ones. Recording too few creates undocumented context that future sessions must re-derive.

### 2. Token Cost
Loading existing ADRs consumes context on every session start. Keep ADRs concise — prefer a clear decision/consequences paragraph over verbose context rehashing.

### 3. Verification
ADRs reflect the decision at a point in time. Revisit accepted ADRs periodically — they may be superseded by experience even if no formal superseding ADR exists.

## Gotchas

- ADR files are tracked in git; ensure accuracy
- Status field must be one of: proposed, accepted, superseded, deprecated
- When superseding an ADR, update old ADR status and add Superseded-By link
- Do NOT record trivial decisions
