# Dev Container

このディレクトリは Dev Container 設定を管理します。
Dev Container を使用することで、チーム全員が統一された開発環境で作業できます。

## 対応エディタ

- VS Code (Remote - Containers 拡張機能が必要)
- GitHub Codespaces
- JetBrains IDE (Gateway 経由)

## セットアップ

### VS Code
1. Remote - Containers 拡張機能をインストール
2. Ctrl+Shift+P → "Reopen in Container"
3. コンテナビルド完了まで待機

### GitHub Codespaces
1. リポジトリページで "Code" → "Codespaces" → "Create codespace on main"
2. 自動的に Dev Container が適用される

## 含まれるツール

| ツール | バージョン | 用途 |
|--------|-----------|------|
| Python | 3.12 | メイン言語 |
| Node.js | 20 | Node.js プロジェクト |
| Rust | latest | Rust プロジェクト |
| Go | 1.22 | Go プロジェクト |
| pre-commit | latest | Git フック管理 |
| yamllint | latest | YAML リント |
| gh CLI | latest | GitHub CLI |
