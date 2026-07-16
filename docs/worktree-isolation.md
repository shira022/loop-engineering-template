# Worktree Isolation for Sub-Agents

> *"Two agents writing the same file is the same headache as two engineers committing to the same lines and nobody talked to each other first."* — Addy Osmani

This document describes how to use **git worktree** for sub-agent isolation within a **single repository**. This is distinct from the multi-project worktree pattern in `project-manager` — this is for isolating sub-agents working on the same repo in parallel.

## The Pattern

```
main repo/
├── .git/                    # Shared git history
├── src/                     # Main working directory (develop branch)
├── worktrees/
│   ├── feature/auth-fix/    # Isolated checkout for sub-agent A
│   │   └── src/             # Sub-agent A works here
│   └── feature/bug-fix/     # Isolated checkout for sub-agent B
│       └── src/             # Sub-agent B works here
└── .agents/                 # Shared across all worktrees
```

Each worktree is on its own branch, shares the same git history, but has its own working directory. Sub-agents cannot collide because they are literally editing different directories.

## Setup

### 1. Create a worktrees directory

```bash
mkdir -p worktrees
echo "worktrees/" >> .gitignore
```

### 2. Standard isolation workflow

```bash
# From the main repo
git fetch origin

# Create branch from develop
BRANCH="fix/auth-token-$(date +%s)"
git branch "$BRANCH" origin/develop

# Create isolated worktree
git worktree add "worktrees/$BRANCH" "$BRANCH"

# Now a sub-agent can work safely:
cd "worktrees/$BRANCH"
# ... make changes, run tests, commit ...
git add -A
git commit -m "fix: auth token expiry"
git push origin "$BRANCH"

# Clean up when done
cd /path/to/main/repo
git worktree remove "worktrees/$BRANCH"
git branch -d "$BRANCH"
```

### 3. Sub-agent integration

When dispatching a sub-agent from a triage finding:

```bash
# In the triage skill or automation:
BRANCH="fix/$(echo "$FINDING" | slugify)-$(date +%s)"
git branch "$BRANCH" origin/develop
git worktree add "worktrees/$BRANCH" "$BRANCH"

# Dispatch implementer in the worktree
cd "worktrees/$BRANCH"
opencode --task "Fix: $FINDING. Write tests. Do NOT review your own work."

# Dispatch verifier in the worktree
cd "worktrees/$BRANCH"
opencode --task "Review the fix for $FINDING. Run tests. Check security."

# If verifier passes:
git add -A && git commit -m "fix: $FINDING"
git push origin "$BRANCH"
gh pr create --base develop --head "$BRANCH" --title "fix: $FINDING"

# Cleanup
cd /path/to/main/repo
git worktree remove "worktrees/$BRANCH"
```

## Provider-Specific Setups

### Claude Code

```bash
# Claude Code supports isolation: worktree on subagents
# In .claude/agents/implementer.md:
# isolation: worktree
# This creates an automatic worktree for each sub-agent invocation.

claude --agent implementer --task "Fix $FINDING"
```

### Codex

```bash
# Codex has built-in worktree per thread.
# Each thread gets its own worktree automatically.
```

### Hermes

```bash
# Manual worktree management (or via project-manager skill)
# The delegate_task runs in its own session; pair with manual git worktree.
```

### DIY (any agent)

```bash
# Explicit worktree creation before agent invocation (as shown above)
# Guaranteed isolation regardless of agent capabilities.
```

## Benefits

| Aspect | Without Worktree | With Worktree |
|--------|-----------------|---------------|
| Parallel sub-agents | File collisions guaranteed | Complete isolation |
| Failed experiment | Dirty working directory | Delete worktree, branch gone |
| Multiple fixes at once | Context switching hell | Each fix in its own directory |
| Main branch safety | Risk of accidental commits | Worktree branch only |
| CI for sub-agent work | Manual branch management | Push from worktree → CI runs |

## ⚠️ Warnings

1. **Disk space** — Each worktree is a full checkout (~50-200MB). Clean up after completion.
2. **Branch name collisions** — Always include a timestamp in branch names.
3. **Orphaned worktrees** — If a sub-agent crashes, its worktree remains. Add a cleanup cron job.
4. **.gitignore** — Make sure `worktrees/` is in `.gitignore` so worktrees are never committed.

## Worktree Commands Reference

```bash
# List all worktrees
git worktree list

# Create worktree
git worktree add <path> <branch>

# Remove worktree (must not have uncommitted changes)
git worktree remove <path>

# Force remove (discard changes)
git worktree remove --force <path>

# Prune stale worktree references
git worktree prune

# Create branch and worktree in one command
git worktree add -b <new-branch> <path> <base-branch>
```
