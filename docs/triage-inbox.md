# Triage Inbox

> *"Anything the loop can not handle lands in the triage inbox for me."* — Addy Osmani

This directory is the **human interface** of the loop engineering system. When the automated loop encounters items it cannot resolve — architecture decisions, cross-cutting changes, security incidents, ambiguous requirements — it writes them here for human review.

## How It Works

```
Automation runs → finds items → can it be automated?
    ├── ✅ Yes → dispatch sub-agent + track in state
    └── ❌ No  → write to inbox/ for human review
```

Each inbox item is a markdown file with:

```markdown
# YYYY-MM-DD: <Brief Title>

## Context
What the loop found, why it couldn't handle it.

## What's Needed
- [ ] Decision: <what needs deciding>
- [ ] Action: <what needs doing>
- [ ] Assignee: <who should handle>

## Supporting Data
- CI run: <link>
- Issue: <link>
- Findings: <summary of what was investigated>

## Priority
🔴 Critical / 🟡 Needs Attention / ℹ️ Info
```

## Inbox File Lifecycle

| Status | Description | Location |
|--------|-------------|----------|
| **📥 New** | Just triaged, needs human review | `inbox/<date>-<slug>.md` |
| **👁️ Reviewing** | Human has started working on it | Same file, header updated |
| **✅ Resolved** | Human completed the action | Moved to `inbox/archive/<date>-<slug>.md` |

## Processing the Inbox

Recommended cadence: **daily** (as part of the morning triage review).

```bash
# List all open inbox items
ls -la inbox/*.md 2>/dev/null

# Read the most critical one
cat inbox/*.md | head -20

# Archive a resolved item
mv inbox/2026-07-17-rate-limiting.md inbox/archive/
```

## When to Inbox an Item

| Situation | Inbox? | Reason |
|-----------|--------|--------|
| Security vulnerability found | ✅ YES | Needs human triage and severity assessment |
| Architecture decision needed | ✅ YES | Cannot be automated |
| Ambiguous bug report | ✅ YES | Needs human to clarify |
| Cross-cutting refactor | ✅ YES | Risk of breaking changes |
| Simple CI fix (known pattern) | ❌ NO | Sub-agent can handle |
| Dependency update with known fix | ❌ NO | Sub-agent can handle |
| Test failure with clear cause | ❌ NO | Sub-agent can handle |

## ⚠️ Warnings

1. **Inbox ≠ Black hole** — Items in the inbox must be reviewed and acted on, not accumulated. Set a regular review cadence.
2. **Triage quality** — If the loop inboxes everything, it's not doing useful triage. If it inboxes nothing, it's likely missing critical items.
3. **Token cost** — Writing an inbox file costs ~500 tokens. Better to inbox than to guess wrong.

## Initial Setup

```bash
mkdir -p inbox/archive
touch inbox/.gitkeep
echo "*.local.md" >> .gitignore  # optional: keep local analysis private
```
