---
name: project-bootstrapper
version: 3.0.0
category: management
tags: [bootstrap, setup, initialization, github]
description: Bootstraps new projects from this template - creates GitHub repo, clones locally, guides language/framework setup through interactive dialog, and registers in project registry. Language-agnostic — supports any programming language or framework.
compatibility: 'Hermes Agent (gh CLI required), Opencode, Claude Code'
metadata:
  depends_on: [loop-engineer]
---

# Project Bootstrapper

> **English:** Bootstraps a brand new project from the loop-engineering-template — creates GitHub repo, clones locally, configures language/framework, and registers in project registry.
>
> このスキルは loop-engineering-template から**新しいプロジェクト**をゼロから立ち上げます。
プロセス（ループエンジニアリングの仕組み）はテンプレートから継承し、
言語・フレームワーク固有の設定は対話型セットアップで動的に生成します。

実行が完了すると、自分自身の SKILL.md を削除する**セルフデストラクト**機能を持ちます。

## 前提条件

- `gh` CLI がインストールされ、認証済みであること
- 環境変数 `$PROJECTS_DIR` が未設定の場合、`$HOME/project` をデフォルトとして使用する

## 使用方法

```
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
3. **言語・フレームワークの詳細（自由選択）**
   - 言語: 任意（Python / TypeScript / Rust / Go / Java / Kotlin / Swift / C# / その他）
   - フレームワーク: 該当するもの（例：Next.js, FastAPI, Actix, Spring Boot, なし など）
   - ビルドツール / パッケージマネージャ: （例：uv / npm / cargo / gradle / mix など）
   - テストフレームワーク: （例：pytest / vitest / cargo-test / JUnit / など）
4. **プロジェクトの説明 / 作りたいもの**
   - 自由記述。READMEや初期コミットメッセージに反映します。

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

### Step 4: プロジェクトの初期化（言語・フレームワークに応じて動的生成）

テンプレートからループエンジニアリングのプロセス基盤（スキル群、AGENTS.md、
Git Flow設定、CI設定など）は自動的に継承されます。

言語・フレームワーク固有の設定は、Step 1 で収集した情報に基づき
**動的に生成**します。以下の手順を状況に応じて適用します：

#### 4a. プロジェクト基本構成

`src/` と `tests/` ディレクトリを作成します（内容は言語に応じて後続処理で生成）：

```bash
PROJECTS_DIR="${PROJECTS_DIR:-$HOME/project}"
cd "$PROJECTS_DIR/<name>/repo-<name>"
mkdir -p src tests
```

#### 4b. CI 設定の生成

`.github/workflows/ci.yml` に、選択された言語・フレームワークに応じた
`build-and-test` ジョブを追記します。

**Python (pytest):**
```yaml
  build-and-test:
    name: Build and Test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install ".[dev]"
      - run: python -m pytest tests/ --cov=src --cov-fail-under=80
```

**TypeScript (vitest):**
```yaml
  build-and-test:
    name: Build and Test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: npm ci
      - run: npm test
```

**Rust (cargo):**
```yaml
  build-and-test:
    name: Build and Test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cargo build
      - run: cargo test
```

**その他の言語:** ユーザーが指定したビルドツール・テストフレームワークに合わせて
適切な CI ジョブを生成します。不明な場合はユーザーに確認します。

#### 4c. プロジェクト初期化（必要な場合）

言語ネイティブのプロジェクト初期化ツールがある場合は実行します：

- **Python**: `uv init` / `poetry init`
- **TypeScript**: `npm init` / `npm create vite@latest`
- **Rust**: `cargo init`
- **Go**: `go mod init`
- **その他**: 該当する言語のツールを使用

該当するツールがない場合やユーザーが手動初期化を希望する場合はスキップします。

#### 4d. .gitignore の設定

選択された言語に適した `.gitignore` テンプレートを
GitHub のリポジトリから取得して設定します：

```bash
# 例: Python の場合
curl -sL "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore" >> .gitignore
```

該当するテンプレートがない場合は、汎用的な `.gitignore` を設定します。

#### 4e. 初期化確認

```bash
cd "$PROJECTS_DIR/<name>/repo-<name>"
ls -la src/ tests/
git status
```

生成された内容をユーザーに確認し、必要に応じて修正します。

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
  build_tool: <build-tool>
  test_framework: <test-framework>
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
   ローカル:   ${PROJECTS_DIR:-$HOME/project}/<name>/repo-<name>
   言語:       <language>
   フレームワーク: <framework>
   ビルドツール:   <build-tool>
   テストFW:       <test-framework>
   可視性:     <public|private>
   説明:       <description>

プロジェクトのブートストラップスキルはセルフデストラクト済みです。
```

## 注意事項

- `gh` CLI がインストールされ、認証済みであることを前提とします。
- テンプレートリポジトリは自動検出されますが、`gh repo view` で確認可能です。
- プロジェクトのルートディレクトリは `${PROJECTS_DIR:-$HOME/project}/<name>/repo-<name>` です。`$PROJECTS_DIR` 環境変数で上書き可能です。
- セルフデストラクトは新しいプロジェクト内のファイルのみ削除します。テンプレート本体には影響しません。
- プロジェクト名が既に `repo-registry.yaml` に存在する場合は上書き確認を行います。
- **言語・フレームワークは自由選択です。** このテンプレートは特定の言語に依存しません。
  未サポートの言語の場合は、適宜ユーザーと相談しながら CI 設定を調整してください。