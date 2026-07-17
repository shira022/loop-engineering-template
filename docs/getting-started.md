# 🚀 Getting Started

Choose your level. Each builds on the previous — start wherever matches your confidence.

## Lv0 — Create a Project from the Template (2 min)

```bash
gh repo create my-project --template shira022/loop-engineering-template --public
git clone https://github.com/your-org/my-project.git
cd my-project
```

**Private repo?**
```bash
gh repo create my-project --template shira022/loop-engineering-template --private
```

> ✅ Done. You now have a project with CI/CD, Git Flow config, and 9 agent skills.

## Lv1 — Run Manual Triage (+5 min)

```bash
bash scripts/daily-triage.sh
cat learnings/triage-$(date +%F).md
cat STATE.md
```

## Lv2 — Add a Verifier Sub-agent (+10 min)

```bash
alias verify='opencode --task "Review changes: $(git diff --cached). Run tests. No code."'
```

## Lv3 — Set Up Automation (+5 min)

**GitHub Actions** (shipped in `.github/workflows/agent-harness.yml`):
```yaml
on:
  schedule:
    - cron: '0 7 * * 1-5'
```

## Lv4 — Full One Loop (+15 min)

All 6 building blocks working together:

```
07:00  Automation triggers
       ↓
07:01  Explorer sub-agent reads CI + issues + commits
       ↓
07:05  Triage report → learnings/triage-YYYY-MM-DD.md
       ↓
07:06  Fixable items → git worktree isolation
       ↓
07:10  Implementer drafts fix in worktree
       ↓
07:15  Verifier reviews + runs tests
       ↓
07:20  PASS → Connectors create PR, update tickets, notify Slack
       ↓
07:25  STATE.md updated → next run picks up where this stopped
```

### Prerequisites

| Tool | Required | Purpose |
|------|----------|---------|
| `git` | ✅ | Version control |
| `gh` CLI | ✅ | GitHub repository creation |
| `python3` | ✅ Recommended | Validation scripts |
| AI Agent | ✅ | Hermes, Opencode, Claude Code, or any agentskills.io-compatible agent |

---

> [← Back to Overview](/) | [📁 Directory Structure →](directory-structure.md)
