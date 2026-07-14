---
name: test-policy
version: 2.0.0
category: testing
tags: [testing, coverage, quality, ci]
description: >
  Enforces comprehensive test coverage across the project.
  This policy is language-agnostic — it applies regardless of the
  programming language or framework chosen for the project.
metadata:
  version: "2.0.0"
---

# Test Policy

## 役割

このスキルは新規コードが必ずテストされることを保証します。
全てのプロジェクトはこのポリシーに従う必要があります。
このポリシーは特定の言語やフレームワークに依存しません。

## ルール

1. **必須テスト**: 新規コードには必ずテストを書く
2. **カバレッジ**: ラインカバレッジ80%以上（CIで強制）
3. **テスト種類**:
   - ユニットテスト: 全ての関数/モジュール
   - エッジケース: 空入力、null/None、境界値
   - エラーパス: 例外、エラーリターン、失敗状態
   - 結合テスト: 外部サービス連携、DB操作（該当する場合）

## テスト設定の生成

プロジェクト作成時（`project-bootstrapper`）の対話型セットアップで
選択した言語・フレームワークに基づき、テスト設定は動的に生成されます。

```yaml
# project-bootstrapper で生成される設定 (実際の値は選択に依存)
language: <user-selected-language>
framework: <user-selected-framework>
test_framework: <user-selected-test-framework>
```

生成される設定内容:
- テストフレームワーク設定ファイル
- CI の build-and-test ジョブ
- カバレッジ閾値設定
- テストディレクトリ構成

## CIでの強制

CIパイプラインは以下の場合に失敗します:
- テストが見つからない（exit code 1）
- カバレッジが80%未満
- テストが失敗する

## 言語別の実装例（参考）

プロジェクト作成後に以下のような構成となります（選択した言語に依存）:

### 例: Python
- 設定: `pyproject.toml` の `[tool.pytest.ini_options]`
- カバレッジ: `--cov=src --cov-fail-under=80`
- 配置: `tests/test_*.py`

### 例: TypeScript
- 設定: `vitest.config.ts`
- カバレッジ: `vitest --coverage`
- 配置: `tests/**/*.test.ts`

### 例: Rust
- 設定: `Cargo.toml`
- テスト: `#[cfg(test)]` + `#[test]`
- 配置: インラインテスト + `tests/`

### 例: Go
- 設定: 標準 testing パッケージ
- テスト: `go test ./...`
- 配置: `*_test.go`

> **Note:** 上記は参考例です。実際の設定はプロジェクト作成時に選択した内容に基づき生成されます。

## エージェントへの指示

テストポリシーを適用する際は:
1. プロジェクトで使用されている言語・フレームワークを確認する
2. 対応するテスト設定を `project-bootstrapper` が生成した内容に従う
3. ポリシー（80%カバレッジ、全テスト種別）を強制する

## 参照

- `TESTING.md` — 完全なテストポリシー
- `project-bootstrapper` スキル — プロジェクト作成時のテスト設定生成
