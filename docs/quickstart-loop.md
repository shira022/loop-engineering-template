# Quickstart: Your First Loop

> *"Developers can start with a single scheduled triage automation and a verifier sub-agent, capturing most of the value at a fraction of the token spend."* — The New Stack

This guide gets you from zero to a running loop in **15 minutes**, with just two components: **triage automation** + **verifier sub-agent**. This is the minimum viable loop — you can add worktrees, connectors, and the explorer role later.

## Step 1: Setup (2 min)

```bash
# Clone the template
gh repo create my-project --template shira022/loop-engineering-template --public
cd my-project

# Verify prerequisites
which gh git opencode  # or: claude, hermes
gh auth status
```

## Step 2: Configure Triage Automation (3 min)

Edit `.github/workflows/agent-harness.yml` — the schedule trigger is already configured:

```yaml
on:
  schedule:
    - cron: '0 7 * * 1-5'  # Weekdays at 07:00 UTC (already present)
```

Or set up a local cron job:

```bash
# crontab -e
0 7 * * 1-5 cd /path/to/my-project && bash scripts/daily-triage.sh
```

Test the triage script manually:

```bash
bash scripts/daily-triage.sh
cat learnings/triage-$(date +%F).md
```

## Step 3: Configure Your First Sub-Agent — The Verifier (3 min)

The verifier is the most important sub-agent. It catches mistakes the implementer missed.

**Option A: Native (if your agent supports it)**

```bash
# Claude Code: The verifier definition is already in .agents/agents/verifier.yaml
# Translate it to Claude's format:
mkdir -p .claude/agents
cat > .claude/agents/verifier.md << 'EOF'
You are a verifier agent. Your job is to review code changes critically.
Do NOT write code.
Rules:
1. Assume the implementer made mistakes until proven otherwise
2. Run all tests
3. Check: correctness, security, edge cases, error handling
4. Output verdict: PASS / FAIL / NEEDS_WORK
EOF
```

**Option B: CLI (works with any agent)**

```bash
# Use the verifier as a prompt template:
alias verify='opencode --task "Review the following changes: $(git diff --cached). Run tests. Do NOT write code."'
```

**Option C: Hermes delegate_task**

```python
# In your Hermes session:
from hermes_tools import delegate_task
verdict = delegate_task(
    goal="Verify changes for correctness",
    context="Review the implementer's changes. Run tests. Be skeptical."
)
```

## Step 4: Run a Manual Triage (2 min)

Simulate what the automation will do daily:

```bash
# 1. Run triage
bash scripts/daily-triage.sh

# 2. If it found something fixable:
git worktree add worktrees/fix-issue-123 fix/issue-123-$(date +%s)
cd worktrees/fix-issue-123
opencode --task "Fix the issue identified in triage report"
opencode --task "Verify the fix: run tests, check coverage, review"
cd ../..
git worktree remove worktrees/fix-issue-123
```

## Step 5: Walk Away (3 min)

The next morning, the automation runs automatically:

1. CI triage runs → generates `learnings/triage-YYYY-MM-DD.md`
2. If issues found → dispatched to sub-agents
3. If sub-agents can't resolve → items go to `inbox/`
4. State updates in `STATE.md`
5. You review the results

## Step 6: Iterate (2 min)

Review what happened:

```bash
# What did the loop find?
cat learnings/triage-$(date +%F).md

# What's in the inbox?
ls -la inbox/

# What's the state?
cat STATE.md

# Any PRs created?
gh pr list --author "@me"
```

## What You Have After 15 Minutes

```
✅ Scheduled CI triage (runs weekdays at 07:00)
✅ Verifier sub-agent (reviews before PR)
✅ Triage reports (learnings/triage-*.md)
✅ Triage inbox (items the loop can't handle)
✅ State file (remembers what's open)
```

## What to Add Next

| When | Add | Why |
|------|-----|-----|
| Week 2 | **Explorer sub-agent** | Better investigation before implementation |
| Week 3 | **Worktree isolation** | Run multiple sub-agents in parallel |
| Week 4 | **MCP connectors** | Auto-create PR, update tickets, notify Slack |
| Week 5 | **/goal pattern** | Run-until-done for complex tasks |
| Ongoing | **Skills compound** | Each new skill = less re-explaining |

## Reference: The Minimal Loop Files

After setup, your project has these loop-specific files:

```
.agents/
├── agents/
│   ├── verifier.yaml        # Your first sub-agent
│   └── README.md            # How to use sub-agents
├── config/
│   └── schedules.yaml       # What runs when
└── skills/
    ├── triage/SKILL.md       # The automation skill
    ├── loop-engineer/        # Session orchestrator
    └── ... (other skills)

.github/workflows/
└── agent-harness.yml        # Scheduled execution

scripts/
├── daily-triage.sh          # Triage implementation
└── goal-loop.sh             # /goal implementation

learnings/                   # Triage reports land here
inbox/                       # Unresolvable items land here
STATE.md                     # The spine of the loop
```
