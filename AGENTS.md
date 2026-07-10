# Loop Engineering Rules

このプロジェクトはループエンジニアリングを実践します。

## 基本ルール
- 作業開始前に必ず `learnings/` と `docs/adr/` を確認する
- 複雑なタスク完了後は knowledge-harvest スキルを実行する
- 重要なアーキテクチャ判断は decision-recorder でADRに記録する
- 同じパターンが3回以上出現したら skill-crafter でスキル化する
- セッション終了時は session-reviewer で振り返る

## スキル一覧
- `.agents/skills/loop-engineer` - ループエンジニアリング中核
- `.agents/skills/knowledge-harvest` - 学びの抽出
- `.agents/skills/skill-crafter` - 自動スキル化
- `.agents/skills/decision-recorder` - ADR記録
- `.agents/skills/session-reviewer` - 振り返り
- `.agents/skills/project-bootstrapper` - 新規プロジェクト作成（初回のみ）
- `.agents/skills/project-manager` - タスク管理

## 対応エージェント
この `.agents/skills/` 形式は agentskills.io 標準に準拠しており、
Hermes Agent、Opencode、Claude Code、Gemini CLI、Cursor、GitHub Copilot 等で利用可能です。
