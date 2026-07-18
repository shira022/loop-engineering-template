---
name: project-bootstrapper
version: 3.0.0
category: management
tags: [bootstrap, setup, initialization, github, questionnaire]
description: >
  Bootstraps new projects from the loop-engineering-template.
  Uses an interactive questionnaire (questions.yaml) to customize the project
  to the user's needs, then generates and executes an implementation task list.
  Features: user-level-adaptive questions, Git Flow setup, connector config,
  skill management (copy vs symlink), loop automation scheduling.
compatibility: 'Hermes Agent (gh CLI + clarify tool required), Opencode, Claude Code, Codex'
metadata:
  depends_on: [loop-engineer]
  references:
    - questions.yaml  # 質問定義ファイル（このスキルの心臓部）
---

# Project Bootstrapper — 次世代ブートストラップ

> **English:** Bootstraps a brand new project from the loop-engineering-template.
> Uses a structured questionnaire (questions.yaml) to gather user intent, then
> generates a customized project with the right template features enabled.
>
> このスキルは loop-engineering-template から**新しいプロジェクト**を
> ゼロから立ち上げます。旧バージョンからの主な改善点：
>
> 1. **質問漏れゼロ** — questions.yaml で全質問を定義
> 2. **ユーザーレベル適応** — 初心者には丁寧に、上級者には最小限の説明で
> 3. **実装リスト自動生成** — 回答から coarse/fine タスクリストを生成
> 4. **テンプレ設定のカスタマイズ** — Git Flow/Pages/Connectors等を選択可能
> 5. **中級者ゲート質問** — 詳細設定を見せるかどうかをユーザー自身に選択させる

実行が完了すると、自分自身の SKILL.md を削除する**セルフデストラクト**機能を持ちます。

## 前提条件

- `gh` CLI がインストールされ認証済みであること
- プロジェクトの配置先ディレクトリはユーザーへのヒアリングで決定する
  （`$PROJECTS_DIR` 環境変数がある場合はデフォルト候補として提示する）

## 使用方法

```
# エージェントに以下のように指示：
# 「このテンプレートを使って新しいプロジェクトをブートストラップして」
```

## ワークフロー概要

```
[Phase 0] ユーザーレベル把握  ──→  detail_level 決定
     ↓
[Phase 1-4] 質問実行          ──→  questions.yaml に従って順次質問
     ↓
[タスク生成] 回答→実装リスト   ──→  coarseタスク + fineサブタスク
     ↓
[タスク実行] T1 → T2 → ... T11  ──→  順次実装
     ↓
[完了] 初期コミット → 報告 → セルフデストラクト
```

## Step 0: 事前準備

作業を開始する前に、以下の情報を確認・準備せよ：

1. **テンプレートリポジトリを特定**: このスキル自身が含まれているリポジトリが
   テンプレートである。`gh repo view --json nameWithOwner` で確認できる。
2. **questions.yaml を読み込め**: このファイルと同じディレクトリにある
   `questions.yaml` を読み込み、全質問・タスク・ルールを把握せよ。
3. **ユーザーのコンテキストを確認**: Hermes Agentの場合は session_search で
   過去の会話履歴を検索し、ユーザーの好みや環境を把握することを検討せよ。

## Step 1: Phase 0 — ユーザーレベル把握（1〜2問）

questions.yaml の `phase: user-level` に定義された質問を最初に提示する。

**重要なルール:**
- まず `experience_level` を1問だけ提示する。その回答を見てから次の質問を決める
- 初心者（beginner）の場合、`loop_familiarity` はスキップしてよい
- 中級者以上の場合は両方の質問を提示する

**回答後の動作:**

| 回答 | detail_level | 以降の振る舞い |
|------|-------------|----------------|
| beginner | verbose | 各質問を丁寧に説明。`question_phrasing_examples` の beginner 例を参照 |
| intermediate | concise | 簡潔な説明 |
| advanced | minimal | 設定名のみ。詳細説明は不要 |

**エージェント向けヒント:**
- 選択式質問は、Hermes Agentの `clarify` ツールの `choices` パラメータで
  ワンタッチ選択させることで、ユーザーのタイプ負荷を減らせる
- 選択肢が多い質問は、画面上で見やすく整形すること（改行・インデント）

## Step 2: Phase 1-4 — 質問の順次実行

questions.yaml の `phases[1-4]` を順次進行する。

### 質問の進行ルール

1. **フェーズごとに区切って提示**: 全質問を一度に投げず、フェーズ単位で
   区切って提示する。各フェーズの前に `label` と `description` を表示する。

2. **依存関係の解決**: 各質問の `depends_on` を確認し、条件を満たさない
   質問はスキップする。例えば `repo_visibility` が `private` の場合、
   `pages_enabled` はスキップされる（privateリポではPagesが制限されるため）。

3. **デフォルト値の活用**: 各質問に `default` がある場合、ユーザーが答えを
   明示しない場合はデフォルト値を採用してよい。ユーザーに「デフォルトの〜で
   進めますか？」と確認する方式が効率的。

4. **質問の言い換え**: `question_phrasing_examples` セクションを参照し、
   `detail_level` に応じた語彙・説明長で質問すること。

5. **Phase 3 のゲート質問**: `show_advanced_settings` の回答が No/false の場合、
   Phase 4 はスキップする。その場合、Phase 4 の各項目はデフォルト値が適用される。

6. **フリーテキスト質問**: バリデーションルール（`validation`）が設定されている
   場合、ユーザーの回答がパターンにマッチするか確認すること。

### Hermes Agent での質問実装パターン

**単一選択（single_choice）:**
```python
from hermes_tools import clarify
# choices パラメータに選択肢を渡す
response = clarify(
    question="使用する技術スタックを選択してください",
    choices=["Python", "TypeScript/JavaScript", "Rust", "Go", "Java/Kotlin", "その他"]
)
# response の値を questions.yaml の choices.value と照合する
```

**複数選択（multi_choice）:**
```python
# Hermes Agent の clarify は複数選択に対応していない場合、
# 「カンマ区切りで入力してください」と指示するか、1つずつ個別に質問する
# 例: 「GitHub MCPを有効にしますか？」→「Linearは？」→「Slackは？」
```

**Yes/No（yes_no）:**
```python
response = clarify(
    question="Git Flow を有効にしますか？",
    choices=["はい（推奨）", "いいえ"]
)
```

## Step 3: 実装タスクリストの生成

全質問の回答が出揃ったら、以下の手順で実装タスクリストを生成する：

1. questions.yaml の `tasks` セクションを走査する
2. 各タスクの `always: true` または `condition` を評価する
3. 条件を満たすタスクのみを含めたリストを生成する
4. 各タスクの `sub_tasks` を展開する（condition付きのsub_taskも評価する）
5. タスクID順（T1→T11）にソートする

**生成例（Git Flow有効・Pages無効・独立コピーの場合）:**
```
実装タスクリスト:
  T1: GitHubリポジトリ作成
    - gh repo create ...
    - git clone ...
  T2: README・ドキュメントのカスタマイズ
    - README.md のタイトル置換
    - AGENTS.md の置換
    - CHANGELOG.md のリセット
  T3: Git Flow セットアップ
    - developブランチ作成
    - デフォルトブランチ変更
  T5: スキル管理方式の設定（確認のみ）
  T6: ループ自動化の設定（fullの場合）
  T8: プロジェクトコードの初期スキャフォールド
  T9: MCPコネクター設定
  T10: 初期コミット・プッシュ
```

**ユーザーへの確認:**
実装タスクリストを生成したら、ユーザーに一覧を提示して確認を取ること。
「以上のタスクを実行します。よろしいですか？」と聞く。
ユーザーが特定タスクのスキップや追加を希望する場合はそれに従う。

## Step 4: タスクの実行

確認が取れたら、生成されたタスクリストを順番に実行する。

### 各タスクの実行ガイドライン

- **T1 リポジトリ作成**: `gh repo create` を使用。テンプレートリポジトリは
  このスキルが存在するリポジトリを自動的に使用する。
- **T2 ドキュメントカスタマイズ**: README.md / AGENTS.md / CONTRIBUTING.md の
  テンプレート固有の記述をプロジェクト用に書き換える。特にバッジのURL、
  コントリビュート先、スターのお願い等に注意。
- **T3 Git Flow**: developブランチを作成後、GitHub上でデフォルトブランチを
  developに変更する。これによりデフォルトのPR先がdevelopになる。
- **T5 スキル管理**: symlink_hub が選択された場合、.agents/skills/ の各スキル
  を削除してシンボリックリンクに置き換える。
- **T8 コードスキャフォールド**: 選択された技術スタックに応じたコードの雛形を
  生成する。CIのbuild-and-testジョブもこのスタックに合わせて生成する。
- **T10 初期コミット**: 必ず最初のコミットメッセージは絵文字付きで
  意味のある内容にすること。

### エラーハンドリング

| エラー | 対処 |
|--------|------|
| `gh repo create` で名前重複 | ユーザーに別の名前を提案するか、既存リポジトリの削除確認 |
| git操作の失敗 | ネットワークと認証状態を確認 |
| スキルのsymlink作成失敗 | リンク先パスが正しいか確認 |
| ユーザーが途中で中断 | STATE.md に現在の進行状態を記録してから終了 |

## Step 5: 完了報告 & セルフデストラクト

### 完了報告

すべてのタスクが完了したら、以下の内容をユーザーに報告する：

```
✅ プロジェクト「{project_name}」のブートストラップが完了しました。

📦 リポジトリ: https://github.com/{user}/{project_name}
📁 ローカル:   {local_path}
🔧 スタック:   {tech_stack} / {framework}
🌐 可視性:     {repo_visibility}
🔄 Git Flow:  {gitflow_enabled ? '有効' : '無効'}
📄 Pages:     {pages_enabled ? '有効' : '無効'}

📋 実装したタスク:
   {完了したタスクのリスト}

💡 次のステップ:
   1. cd {local_path}
   2. エージェントで「Bootstrap this project」と指示してアプリ開発を開始
   3. または直接コードを編集
```

### セルフデストラクト

新しいプロジェクト内の `project-bootstrapper` スキルを削除する：

```bash
# 新しいプロジェクトのディレクトリ内で実行
rm -f ".agents/skills/project-bootstrapper/SKILL.md"
rm -f ".agents/skills/project-bootstrapper/questions.yaml"
```

これは**テンプレート側のファイルには影響しない**。テンプレートは再利用可能なまま残る。

## ⚠️ Loop Safety

### 1. 本スキルは初回セッションのみ使用すること
2回目の実行は重複設定やレジストリエントリの重複を引き起こす。
再ブートストラップが必要な場合は手動でレジストリをクリーンアップすること。

### 2. トークンコスト
本スキルはテンプレート中で最もトークン消費が大きい（〜5000〜20000 tokens）。
質問が多いほどコストが増加するため、`detail_level: beginner` の場合は
特に `explanation_style: verbose` による追加トークンに注意すること。

### 3. 検証
自動スキャフォールディングはあなたの意図と完全に一致しない可能性がある。
生成された設定はコミット前にレビューすること。セルフデストラクトは
生成されたプロジェクトの検証は行わない。

### 4. 質問のバランス
「網羅的な質問」と「質問疲れ」のバランスに注意。
- 技術スタックのベストプラクティスが明確なものは質問せずデフォルト採用してよい
- ユーザーの認識と差異が発生しそうなものは必ず質問する
- Phase 3 のゲート質問（show_advanced_settings）はこのバランスを取るための仕組み

## 参考: questions.yaml の構造理解

このスキルの動作の大部分は `questions.yaml` に定義されている。
同ファイルを参照し、以下の構造を理解してから質問を開始すること：

```
phases[].questions[] → 質問の定義（type/prompt/choices/depends_on）
tasks[] → 実装タスクの定義（condition/sub_tasks）
question_phrasing_examples → レベル別の言い回し例
rules.detail_levels → 説明スタイルの定義
```
