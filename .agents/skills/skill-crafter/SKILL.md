---
name: skill-crafter
description: Automates the creation of new agentskills.io-compatible skills when repeated patterns are detected across sessions.
tags: [automation, skill-creation, meta]
category: meta
---

# skill-crafter

このスキルは、繰り返し出現するパターンから新しい `.agents/skills/<name>/SKILL.md` を作成する。

## トリガー条件

- `loop-engineer` または `knowledge-harvest` から「同一パターンが3回以上出現した」という通知を受けたとき

## 実行手順

1. **パターン分析** — 通知に含まれるパターン情報と、`learnings/` 内の関連ファイルを読み込み、新しいスキルに必要な動作を特定せよ。

2. **スキル作成** — 以下のテンプレートに従い、`.agents/skills/<name>/SKILL.md` を作成せよ：
   ```markdown
   ---
   name: <半角英数ケバブケース>
   description: <1〜2文の説明>
   tags: [<関連タグ>]
   category: development|meta|testing|documentation
   ---

   # <name>

   ## 概要
   <このスキルが何をするかの説明>

   ## トリガー条件
   <どのような状況でこのスキルが呼び出されるか>

   ## 実行手順
   1. <ステップ1>
   2. <ステップ2>
   3. <ステップ3>
   ```

3. **セルフレビュー** — 作成した SKILL.md を再度読み込み、以下を確認せよ：
   - 必須フィールド（name, description, tags, category）が全て存在する
   - `name` が半角英数ケバブケースである
   - 説明が具体的で実行可能な手順になっている
   - agentskills.io の標準フォーマットに準拠している

4. **品質問題がある場合** — 上記レビューで問題が見つかった場合は修正せよ。問題がなければ完了とする。

## ブートストラップ完了時の注意

全スキルのブートストラップが完了したら（＝ループエンジニアリングに必要な全スキルが出揃ったら）、この `skill-crafter` スキル自身を削除してもよい。これはブートストラッパーパターンに従い、自身の役割が不要になった段階でプロジェクトから除去することを意味する。
