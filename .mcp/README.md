# MCP (Model Context Protocol) 設定

このディレクトリは MCP サーバー設定を管理します。
MCP は AI エージェントが外部ツール（データベース、API、ファイルシステム）と安全に連携するための標準プロトコルです。

## 対応エージェント

- Hermes Agent (MCP対応)
- Claude Code (MCP対応)
- Gemini CLI (MCP対応)

## セットアップ

```bash
# Hermes Agent の場合
hermes config set mcp.enabled true

# Claude Code の場合
claude mcp add ...
```

## 利用可能なツール例

| ツール | 説明 | デフォルト設定 |
|--------|------|---------------|
| Filesystem | ファイル読み書き操作 | 組み込み |
| GitHub | リポジトリ管理・PR作成 | `.mcp/github.json` |
| Database | SQLクエリ実行 | `.mcp/database.json` |

## 注意事項

- 認証情報を含む設定は `.mcp/*.local.json` に記述し、`.gitignore` に追加してください
- MCP サーバーは必要に応じてエージェントが自動起動します
