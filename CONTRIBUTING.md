# コントリビューションガイド

loop-engineering-template へのコントリビューションを歓迎します！

## 開発の流れ

1. **Issue を作成** — 機能リクエストやバグ報告はまず Issue で議論してください
2. **Fork & ブランチ作成** — `main` から feature/fix ブランチを作成
3. **変更を実装** — 以下のガイドラインに従ってください
4. **Pull Request を作成** — テンプレートに従い詳細を記述

## ガイドライン

### コードスタイル

- Markdown は `markdownlint` に準拠
- YAML は整形式であること
- スキル (SKILL.md) は agentskills.io 標準フォーマットに準拠

### スキル追加時のルール

- `.agents/skills/<name>/SKILL.md` に配置
- YAML frontmatter に `name`, `description`, `tags`, `category` を必須とする
- 説明は具体的で実行可能な手順であること
- 可能な限り多言語での利用を考慮した記述に

### CI パイプライン

- 全ての PR は CI をパスする必要があります
- スキルバリデーション（YAML frontmatter チェック）を含みます
- lint / format チェックを含みます

### コミットメッセージ

[Conventional Commits](https://www.conventionalcommits.org/) を推奨します:

```
feat: add new skill for ...
fix: correct adr template format
docs: update readme with usage examples
chore: update dependencies
```

## 質問・議論

- Issue で質問してください
- 大きな変更は事前に Issue で提案し、フィードバックを得てから実装してください

## 行動規範

このプロジェクトに参加する全ての人は、 respectful で包括的な態度を守ることに同意したものとみなします。
