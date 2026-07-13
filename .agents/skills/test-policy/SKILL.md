---
name: test-policy
version: 1.0.0
category: testing
tags: [testing, coverage, quality, ci]
description: >
  Enforces comprehensive test coverage across the project.
  When a PR or feature branch is created, this skill ensures tests
  exist for all new code, coverage meets the 80% threshold, and
  edge/error cases are covered.
metadata:
  version: "1.0.0"
---

# Test Policy

## 役割

このスキルは新規コードが必ずテストされることを保証します。
全てのプロジェクトはこのポリシーに従う必要があります。

## ルール

1. **必須テスト**: 新規コードには必ずテストを書く
2. **カバレッジ**: ラインカバレッジ80%以上（CIで強制）
3. **テスト種類**:
   - ユニットテスト: 全ての関数/モジュール
   - エッジケース: 空入力、null/None、境界値
   - エラーパス: 例外、エラーリターン、失敗状態
   - 結合テスト: 外部サービス連携、DB操作（該当する場合）

## 言語別テスト設定

### Python (pytest)
- 設定: `pyproject.toml` の `[tool.pytest.ini_options]`
- カバレッジ: `--cov=src --cov-fail-under=80`
- 配置: `tests/test_*.py`

### TypeScript (vitest)
- 設定: `vitest.config.ts`
- カバレッジ: `vitest --coverage`
- 配置: `tests/**/*.test.ts`

### Rust
- 設定: `Cargo.toml`
- テスト: `#[cfg(test)]` + `#[test]`
- 配置: インラインテスト + `tests/`

### Go
- 設定: 標準 testing パッケージ
- テスト: `go test ./...`
- 配置: `*_test.go`

## CIでの強制

CIパイプライン (`build-and-test` job) は以下の場合に失敗します:
- テストが見つからない（exit code 1）
- カバレッジが80%未満
- テストが失敗する

## 参照

- `TESTING.md` — 完全なテストポリシー
- `tests/test_example.py` — Pythonテスト例
- `tests/ts/example.test.ts` — TypeScriptテスト例
