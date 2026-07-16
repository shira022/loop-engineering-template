---
name: triage
description: Scheduled CI triage — reads CI failures, open issues, and recent commits; categorizes findings; writes actionable triage report; dispatches fixable items to sub-agents; routes unresolvable items to the triage inbox for human review.
tags: [automation, triage, ci, maintenance]
category: development
compatibility: 'Hermes Agent, Opencode, Claude Code, Codex'
metadata:
  version: '1.0.0'
  depends_on: [loop-engineer, project-manager]
---

# Triage

> **English:** Scheduled triage skill — the automation heartbeat. Called by schedules.yaml or cron to discover, categorize, and dispatch findings.
>
> このスキルは定期実行されるトリアージ処理の実体。CI結果・Issue・コミットを分析し、対処可能な項目をサブエージェントに発行し、処理できない項目をトリアージインボックスに送る。

## When This Skill Runs

Called by an automation schedule (`.agents/config/schedules.yaml`), typically via:
- **GitHub Actions**: `agent-harness.yml` schedule trigger → runs triage prompt
- **cron + agent**: `0 7 * * 1-5` → `opencode --skill triage`
- **Codex Automations**: configured in Automations tab, calls `$triage`
- **Claude Code**: `claude --schedule "0 7 * * 1-5" --skill triage`

## Triage Process

### Step 1: Gather Data

Collect the current state from three sources:

```bash
# 1. CI status
gh run list --branch main --limit 5 --json conclusion,headBranch,createdAt,displayTitle

# 2. Open issues
gh issue list --limit 20 --json number,title,labels,createdAt

# 3. Recent commits
git log --since="24 hours ago" --oneline --no-decorate
```

### Step 2: Categorize Findings

Classify each finding into one of three categories:

| Category | Definition | Action |
|----------|-----------|--------|
| **🔴 Critical** | Blocking issue, security vulnerability, broken CI | Flag for immediate human review → triage inbox |
| **🟡 Fixable** | Clear root cause, known fix pattern | Dispatch to sub-agent (implementer + verifier) |
| **ℹ️ Info** | Minor, cosmetic, non-blocking | Log in state file, no immediate action |

### Step 3: Write Triage Report

Write to `learnings/triage-YYYY-MM-DD.md`:

```markdown
# Triage Report: YYYY-MM-DD

## CI Health
- main: ✅ / ❌ (last run: <time>)
- develop: ✅ / ❌ (last run: <time>)

## New Issues (since last triage)
- #123: Auth token expiry — 🟡 Fixable
- #124: Rate limiting bug — 🔴 Critical → INBOX

## Recent Commits
- abc1234: fix auth middleware (2h ago)
- def5678: update dependencies (5h ago)

## Dispatched
- [ ] Auth token fix → implementer + verifier dispatched
- [ ] Rate limiting → INBOX (needs human architecture decision)

## State Update
- Previous open items: 3
- Resolved this run: 1
- New items this run: 2
- Inbox total: 1
```

### Step 4: Dispatch Fixable Items

For each 🟡 Fixable item, trigger the maker/checker pipeline:

```bash
# Create isolated worktree
git worktree add "worktrees/fix-<slug>" "fix/<slug>-$(date +%s)"

# Run implementer sub-agent
# (in worktree) implementer: fix the issue, write tests

# Run verifier sub-agent
# (in worktree) verifier: review fix, run tests, check coverage

# If verifier passes → create PR, update state
# If verifier fails → loop back to implementer
```

### Step 5: Route Unresolvable Items to Inbox

For each 🔴 Critical item (or items that need human judgment):

1. Create a file in `inbox/YYYY-MM-DD-<slug>.md`
2. Include context: what was found, why it couldn't be automated, what decision is needed
3. Update the state file to mark this item as `INBOX`

### Step 6: Update State File

Update `STATE.md` (or `AGENTS.md` state section) with:

```markdown
## Triage State
Last run: YYYY-MM-DDTHH:MM:SSZ
| Item | Status | Assigned To | Since |
|------|--------|-------------|-------|
| Auth token expiry | ✅ Done | implementer | 2026-07-16 |
| Rate limiting | 📥 Inbox | human | 2026-07-17 |
| EOL dependency | ⏳ Open | triage (next run) | 2026-07-17 |
```

## ⚠️ Loop Safety

### 1. Triage is a filter, not a solution
Triage discovers and categorizes. It does NOT fix complex problems. Items that need architecture decisions, cross-cutting changes, or human judgment go to the inbox.

### 2. Token Cost
Typical triage run: ~3000-8000 tokens depending on CI/issue volume. Each dispatched sub-agent adds its own cost. Budget accordingly.

### 3. Triage Inbox Debt
An inbox that grows without review is worse than no inbox. Set a regular cadence to process the inbox (e.g., daily human review of new inbox items).

### 4. Verification
Triage categorization is automated heuristics, not guarantees. A 🔴 Critical item might slip through as 🟡 Fixable. The verifier sub-agent catches some of these; human review catches the rest.

## Gotchas

- gh CLI must be authenticated for CI/issue data
- The triage report is the source of truth for the automation run
- If no issues found, write "clean" report and skip dispatch
- Triage inbox files are NOT gitignored — they are part of the project's permanent record
- State file enables the compounding effect: each run picks up where the last stopped
