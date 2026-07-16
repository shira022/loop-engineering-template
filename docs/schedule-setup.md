# Schedule Setup: Platform Translation Guide

> *"Translate abstract schedule definitions into your platform's scheduler."*

The template defines schedules abstractly in `.agents/config/schedules.yaml`. This document shows how to implement those schedules on each supported platform.

## Schedule Definitions

All schedules are defined in `.agents/config/schedules.yaml`:

```yaml
schedules:
  - id: "daily-ci-triage"
    name: "Daily CI Health Triage"
    cadence: "0 7 * * 1-5"       # Weekdays at 07:00 UTC
    agent: "triage"
    prompt: "Run the daily triage workflow..."

  - id: "weekly-skill-health"
    name: "Weekly Skill Health Check"
    cadence: "0 9 * * 1"          # Mondays at 09:00 UTC
    agent: "loop-engineer"
    prompt: "Run weekly skill maintenance..."
```

## Platform Implementations

### GitHub Actions (shipped)

The template ships `.github/workflows/agent-harness.yml` with the daily triage schedule pre-configured:

```yaml
on:
  schedule:
    - cron: '0 7 * * 1-5'   # Weekdays 07:00 UTC
  workflow_dispatch:          # Manual trigger always available
```

**To add the weekly skill health check:**

Create `.github/workflows/skill-health.yml`:

```yaml
name: Skill Health Check
on:
  schedule:
    - cron: '0 9 * * 1'     # Mondays 09:00 UTC
  workflow_dispatch:

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python3 scripts/validate-skills.py
      - run: python3 scripts/run-evals.py
      - run: |
          echo "## Skill Health Report" > learnings/skill-health-$(date +%F).md
          python3 scripts/validate-skills.py >> learnings/skill-health-$(date +%F).md
```

### Local cron (Linux / macOS)

```bash
# Edit crontab
crontab -e

# Daily triage at 07:00 UTC weekdays
0 7 * * 1-5 cd /path/to/repo && bash scripts/daily-triage.sh

# Weekly skill health at 09:00 UTC Mondays
0 9 * * 1 cd /path/to/repo && python3 scripts/validate-skills.py && python3 scripts/run-evals.py

# Log output to file (optional)
0 7 * * 1-5 cd /path/to/repo && bash scripts/daily-triage.sh >> /var/log/loop-triage.log 2>&1
```

### Hermes Agent cron

```bash
# Daily triage
hermes cron create \
  --name "Daily CI Triage" \
  --schedule "0 7 * * 1-5" \
  --skill triage \
  --prompt "Run the daily triage workflow"

# Weekly skill health
hermes cron create \
  --name "Weekly Skill Health" \
  --schedule "0 9 * * 1" \
  --skill loop-engineer \
  --prompt "Run weekly skill maintenance: validate skills, run evals, archive old traces"
```

### Claude Code

```bash
# Claude Code supports scheduled execution via CLI
claude --schedule "0 7 * * 1-5" \
       --task "Run daily CI triage: check CI status, open issues, recent commits"
```

### Opencode

Opencode doesn't have a built-in scheduler. Use system cron:

```bash
# In crontab:
0 7 * * 1-5 cd /path/to/repo && opencode --task "Run daily CI triage. Use the triage skill."
```

## Cadence Reference

| Expression | Meaning |
|------------|---------|
| `0 7 * * 1-5` | Weekdays at 07:00 UTC |
| `0 9 * * 1` | Mondays at 09:00 UTC |
| `0 */6 * * *` | Every 6 hours |
| `30 8 * * *` | Daily at 08:30 UTC |
| `0 0 * * 0` | Sundays at midnight |
| `*/15 * * * *` | Every 15 minutes (use sparingly) |
| `0 7 1 * *` | 1st of every month at 07:00 UTC |

## Per-PR (Event-Driven)

Some schedules are event-driven (`cadence: "on-pr"`). These don't use cron — they use platform webhooks:

**GitHub Actions** — the `ci.yml` workflow already runs on PR. Add a separate workflow:

```yaml
name: PR Review Gate
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          echo "Running PR review gate..."
          # Your review logic here
```

## Monitoring

Check if your scheduled runs are working:

```bash
# GitHub Actions
gh run list --workflow agent-harness.yml

# Local cron
grep loop-triage /var/log/syslog  # or check /var/log/cron

# Hermes
hermes cron list
```

## ⚠️ Warnings

1. **Time zones** — GitHub Actions uses UTC. Local cron uses system timezone. Adjust accordingly.
2. **Token costs** — Each scheduled agent run consumes tokens. Monitor usage, especially for `implementer` tasks.
3. **Idempotency** — Schedules should be safe to run multiple times. Design prompts to detect and skip already-done work.
4. **Logging** — Always log cron output. Silent failures are hard to debug.

---

## 🇯🇵 日本語

`.agents/config/schedules.yaml` で定義された抽象スケジュールを、各プラットフォーム（GitHub Actions / crontab / Hermes cron / Claude Code）の実際のスケジューラーに変換する方法を説明します。テンプレートには daily CI triage の GitHub Actions 設定が同梱されています。
