---
name: project-manager
version: 2.0.0
category: management
tags: [management, orchestration, worktree]
description: 複数プロジェクトと git worktree を横断してタスクを管理・実行します。タスク実行、ステータス報告、キャンセル処理を統合的に行います。
---

# Project Manager

このスキルは、プロジェクトレジストリと git worktree を活用して、複数プロジェクトにまたがるタスクの実行・監視・キャンセルを統合管理します。

## 前提条件

- 環境変数 `$PROJECTS_DIR` が未設定の場合、`$HOME/project` をデフォルトとして使用する
- `gh` CLI がインストールされ、認証済みであること

## 使用方法

```bash
# タスク実行
# 「project-manager で <project-name> に <task-description> を実行して」

# ステータス確認
# 「project-manager で全プロジェクトのステータスを表示して」

# タスクキャンセル
# 「project-manager で <project-name> のタスクをキャンセルして」
```

## ワークフロー

### 1. タスク実行

#### 1-a. プロジェクト情報の取得

`${PROJECTS_DIR:-$HOME/project}/repo-registry.yaml` を読み込み、指定されたプロジェクト名で情報を検索します。

```yaml
# repo-registry.yaml フォーマット例
- name: my-app
  path: ${PROJECTS_DIR:-$HOME/project}/my-app/repo-my-app
  visibility: public
  language: typescript
  framework: next.js
  created_at: "2025-06-01T10:00:00"
  description: "Web application"
```

該当プロジェクトが見つからない場合はエラーを返します。

#### 1-b. Git Worktree の作成

対象プロジェクトのリポジトリ内で、タスク用のブランチを作成し worktree を追加します：

```bash
PROJECTS_DIR="${PROJECTS_DIR:-$HOME/project}"
cd "$PROJECTS_DIR/<name>/repo-<name>"

# 最新の main を取得
git fetch origin

# タスク用ブランチを作成
BRANCH="task/<task-slug>-$(date +%s)"
git branch "$BRANCH" origin/main

# worktree を作成
WORKTREE_PATH="$PROJECTS_DIR/<name>/worktrees/$BRANCH"
git worktree add "$WORKTREE_PATH" "$BRANCH"
```

`<task-slug>` はタスク内容から生成する短いスラッグ（例：`add-auth`, `fix-bug-123`）です。

#### 1-c. エージェントの起動とタスク実行

作成した worktree ディレクトリで、適切なエージェントを起動してタスクを実行します：

**Opencode を使用する場合：**
```bash
cd "$WORKTREE_PATH"
opencode --task "<task-description>" --output /tmp/opencode-task-<name>-<timestamp>.log &
```

**Hermes を使用する場合：**
```bash
cd "$WORKTREE_PATH"
hermes run "<task-description>" --log /tmp/hermes-task-<name>-<timestamp>.log &
```

エージェントの PID を記録し、後続の監視・キャンセルに備えます。

#### 1-d. 進捗監視と報告

エージェントの実行中、以下の方法で進捗を監視します：

1. プロセスが生存しているか定期的に確認（例：10秒間隔）
2. ログファイルの最新行を取得し内容を報告
3. 以下の情報をユーザーに提示：
   ```
   プロジェクト: <name>
   ブランチ:     <branch>
   ステータス:   実行中 / 完了 / エラー
   経過時間:     <elapsed>
   最終ログ:     <last-log-line>
   ```

#### 1-e. PR 作成（タスク完了時）

エージェントのプロセスが正常終了した場合、自動で Pull Request を作成します：

```bash
PROJECTS_DIR="${PROJECTS_DIR:-$HOME/project}"
cd "$WORKTREE_PATH"
git add -A
git commit -m "<task-description>"
git push origin "$BRANCH"

gh pr create \
  --repo "$PROJECTS_DIR/<name>/repo-<name>" \
  --base main \
  --head "$BRANCH" \
  --title "<task-description>" \
  --body "Automated task by project-manager skill.\n\n**Project:** <name>\n**Branch:** $BRANCH\n**Description:** <task-description>"
```

#### 1-f. Worktree のクリーンアップ

PR 作成完了後、worktree を削除します：

```bash
PROJECTS_DIR="${PROJECTS_DIR:-$HOME/project}"
cd "$PROJECTS_DIR/<name>/repo-<name>"
git worktree remove "$WORKTREE_PATH"
git branch -d "$BRANCH"
```

> **注意**: PR 作成後もブランチはリモートに残ります。ローカルのブランチと worktree のみ削除します。

### 2. ステータス報告

全プロジェクトのアクティブな worktree とタスク状況を一覧表示します：

```bash
PROJECTS_DIR="${PROJECTS_DIR:-$HOME/project}"
# 全プロジェクトの worktree 一覧を取得
for repo in "$PROJECTS_DIR"/*/repo-*; do
  echo "=== $(basename "$(dirname "$repo")") ==="
  git -C "$repo" worktree list
  echo ""
done
```

出力例：

```
=== my-app ===
$PROJECTS_DIR/my-app/repo-my-app  main (detached)
$PROJECTS_DIR/my-app/worktrees/task/add-auth-1717200000  task/add-auth-1717200000

=== api-server ===
$PROJECTS_DIR/api-server/repo-api-server  main (detached)
$PROJECTS_DIR/api-server/worktrees/task/fix-timeout-1717300000  task/fix-timeout-1717300000
```

**アクティブなエージェントプロセス**も確認し、以下を表示します：

| プロジェクト | ブランチ | ステータス | 経過時間 | PID |
|:---|:---|:---|:---|:---|
| my-app | task/add-auth-... | 実行中 | 5m 32s | 12345 |
| api-server | task/fix-timeout-... | 完了待ち | 完了 | - |

### 3. タスクキャンセル

実行中のタスクをキャンセルする場合、以下の手順を実行します：

#### 3-a. エージェントプロセスの強制終了

記録してある PID に対して SIGTERM を送信します：

```bash
kill -TERM <pid> 2>/dev/null
sleep 3
kill -KILL <pid> 2>/dev/null  # それでも終了しない場合
```

#### 3-b. Worktree の削除

```bash
PROJECTS_DIR="${PROJECTS_DIR:-$HOME/project}"
cd "$PROJECTS_DIR/<name>/repo-<name>"
git worktree remove --force "$WORKTREE_PATH"
git branch -D "$BRANCH" 2>/dev/null
```

#### 3-c. キャンセル報告

ユーザーにキャンセル完了を報告します：

```
🛑 タスクをキャンセルしました。
   プロジェクト: <name>
   ブランチ:     <branch>
   キャンセル時刻: <YYYY-MM-DDTHH:MM:SS>
   状態:         worktree 削除済 / ブランチ削除済 / プロセス終了済
```

## エラーハンドリング

| エラー種別 | 対応 |
|:---|:---|
| プロジェクト未登録 | `repo-registry.yaml` に該当プロジェクトがない旨を報告 |
| Worktree 作成失敗 | ブランチが既に存在する場合は `task/...` の別名を試行 |
| エージェント起動失敗 | エラーを報告し worktree を即座にクリーンアップ |
| PR 作成失敗 | コードはプッシュ済みのため、手動作業を促すメッセージを表示 |
| タイムアウト | 30分経過でプロセスをキャンセル扱いにする（設定可能） |

## 設定

| パラメータ | デフォルト値 | 説明 |
|:---|:---|:---|
| `timeout_minutes` | 30 | タスクの最大実行時間（分） |
| `poll_interval_seconds` | 10 | 進捗監視のポーリング間隔 |
| `agent_type` | opencode | 使用するエージェント（opencode / hermes） |
| `log_dir` | /tmp | エージェントログの出力先 |
