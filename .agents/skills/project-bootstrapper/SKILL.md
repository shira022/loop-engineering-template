---
name: project-bootstrapper
version: 2.0.0
category: management
tags: [bootstrap, setup, initialization]
description: このテンプレートから新規プロジェクトをブートストラップし、GitHubリポジトリ作成、クローン、言語初期化、レジストリ登録までを自動化します。
---

# Project Bootstrapper

このスキルは loop-engineering-template から**新しいプロジェクト**をゼロから立ち上げます。
実行が完了すると、自分自身の SKILL.md を削除する**セルフデストラクト**機能を持ちます。

## 前提条件

- `gh` CLI がインストールされ、認証済みであること
- 環境変数 `$PROJECTS_DIR` が未設定の場合、`$HOME/project` をデフォルトとして使用する

## 使用方法

```bash
# エージェントに以下のように指示してください：
# 「このテンプレートを使って新しいプロジェクトをブートストラップして」
```

## ワークフロー

### Step 1: 対話型プロジェクト設定

以下の情報をユーザーにヒアリングします：

1. **プロジェクト名**（例：`my-awesome-app`）
   - 命名規則: 小文字 + ハイフン区切りを推奨
2. **リポジトリの公開設定**
   - `public` または `private` の選択
3. **言語・フレームワークの詳細**
   - 言語: Python / TypeScript / Rust / Go / その他
   - フレームワーク: 該当するもの（例：Next.js, FastAPI, Actix など）
   - テストフレームワーク: pytest / vitest / cargo-test / など
4. **プロジェクトの説明 / 作りたいもの**
   - 自由記述。後述のREADMEや初期コミットメッセージに反映します。

### Step 2: GitHub リポジトリ作成

テンプレートリポジトリから新しいリポジトリを作成します：

```bash
gh repo create <project-name> --template <template-repo> --<public|private>
```

- `<template-repo>` は現在のテンプレートリポジトリ（自動検出）
- 公開設定は Step 1 で選択した値を使用

### Step 3: ローカルへのクローン

以下のディレクトリ構成でクローン・セットアップを行います：

```
${PROJECTS_DIR:-$HOME/project}/<name>/
├── repo-<name>          # メインリポジトリ（クローン先）
└── worktrees/           # git worktree 格納ディレクトリ
```

```bash
PROJECTS_DIR="${PROJECTS_DIR:-$HOME/project}"
mkdir -p "$PROJECTS_DIR/<name>"
git clone <clone-url> "$PROJECTS_DIR/<name>/repo-<name>"
mkdir -p "$PROJECTS_DIR/<name>/worktrees/"
```

### Step 4: 言語に応じたプロジェクト初期化

選択された言語/フレームワークに基づき、以下の処理を実行します。

#### Python
- `src/` ディレクトリを作成し `__init__.py` を配置
- `tests/` ディレクトリを作成し `__init__.py` と `conftest.py` を配置
- `.github/workflows/ci.yml` に Python 用の CI 設定を記述（pytest + ruff）

#### TypeScript
- `src/` ディレクトリを作成
- `tests/` ディレクトリを作成
- `.github/workflows/ci.yml` に TypeScript 用の CI 設定を記述（vitest / jest + tsc）

#### Rust
- `src/` ディレクトリは `cargo init` で生成
- `tests/` ディレクトリは `cargo test` の構成に合わせて配置
- `.github/workflows/ci.yml` に Rust 用の CI 設定を記述（cargo build + cargo test + clippy）

#### Go
- `src/` は Go のモジュール構成に合わせて `cmd/` と `internal/` を作成
- `tests/` は `*_test.go` パターンに従う
- `.github/workflows/ci.yml` に Go 用の CI 設定を記述（go build + go test + golangci-lint）

### Step 5: 初期コミット & プッシュ

```bash
PROJECTS_DIR="${PROJECTS_DIR:-$HOME/project}"
cd "$PROJECTS_DIR/<name>/repo-<name>"
git add -A
git commit -m "🎉 Initial commit: <project-name> - <description>"
git push origin main
```

### Step 6: プロジェクトレジストリへの登録

`${PROJECTS_DIR:-$HOME/project}/repo-registry.yaml` に以下のフォーマットでプロジェクト情報を追記します：

```yaml
- name: <project-name>
  path: ${PROJECTS_DIR:-$HOME/project}/<name>/repo-<name>
  visibility: <public|private>
  language: <language>
  framework: <framework>
  created_at: <YYYY-MM-DDTHH:MM:SS>
  description: <description>
```

### Step 7: セルフデストラクト

**自分自身の SKILL.md を削除します。**

削除対象: `.agents/skills/project-bootstrapper/SKILL.md`

これは新しく作成されたプロジェクトのテンプレート由来のブートストラップスキルを削除する処理です。
（テンプレート側のファイルには影響しません。）

```bash
PROJECTS_DIR="${PROJECTS_DIR:-$HOME/project}"
rm "$PROJECTS_DIR/<name>/repo-<name>/.agents/skills/project-bootstrapper/SKILL.md"
```

### Step 8: 完了報告

以下の内容をユーザーに報告します：

```
✅ プロジェクト <name> のブートストラップが完了しました。
   リポジトリ: <clone-url>
   ローカル:  ${PROJECTS_DIR:-$HOME/project}/<name>/repo-<name>
   言語:      <language>
   可視性:    <public|private>
   説明:      <description>

プロジェクトのブートストラップスキルはセルフデストラクト済みです。
```

## 注意事項

- `gh` CLI がインストールされ、認証済みであることを前提とします。
- テンプレートリポジトリは自動検出されますが、`gh repo view` で確認可能です。
- プロジェクトのルートディレクトリは `${PROJECTS_DIR:-$HOME/project}/<name>/repo-<name>` です。`$PROJECTS_DIR` 環境変数で上書き可能です。
- セルフデストラクトは新しいプロジェクト内のファイルのみ削除します。テンプレート本体には影響しません。
- プロジェクト名が既に `repo-registry.yaml` に存在する場合は上書き確認を行います。
