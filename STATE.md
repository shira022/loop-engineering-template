# Loop State

> *"The state file is the spine of the whole thing, it remembers what got tried, what passed, what is still open, so tomorrow morning the run picks up where today stopped."* — Addy Osmani

This file tracks the ongoing state of the loop engineering cycle. It is both read and written by automated runs. The format is designed to be machine-parseable and human-readable.

## Current State

**Last updated:** YYYY-MM-DDTHH:MM:SSZ
**Last triage run:** YYYY-MM-DD (see `learnings/triage-YYYY-MM-DD.md`)
**Open items:** 0

| Item | Status | Source | Assigned To | Since | Updated |
|------|--------|--------|-------------|-------|---------|
| _(no open items)_ | | | | | |

## Inbox Summary

| Date | Item | Priority | Status |
|------|------|----------|--------|
| _(no inbox items)_ | | | | |

## Recent Resolutions

| Date | Item | Outcome | PR |
|------|------|---------|----|
| _(none yet — reset for template release)_ | | | |

## Skill Count

| Skill | Created | Last Used | Evals |
|-------|---------|-----------|-------|
| loop-engineer | bootstrap | every session | ✅ |
| triage | bootstrap | daily | — |
| _(skills compound here as new ones are created)_ | | | |

---

## State File Rules

1. **Always update `Last updated`** with the current timestamp after any change
2. **Move items** from Open → Inbox → Resolved as they progress
3. **Never delete** a resolved item — archive it in "Recent Resolutions"
4. **Prefix status** with emoji for quick scanning:
   - ⏳ Open — being worked on by the loop
   - 📥 Inbox — waiting for human
   - 👁️ Reviewing — human is looking at it
   - ✅ Done — resolved
   - ❌ Failed — attempted but could not resolve
5. **The state file is NOT gitignored** — it is the project's persistent memory

## How Triage Updates This File

After each triage run, the triage skill updates STATE.md:

```diff
+ ## Current State
+ **Last updated:** YYYY-MM-DDTHH:MM:SSZ
+ **Last triage run:** YYYY-MM-DD
+ **Open items:** 2
+ 
+ | Item | Status | Source | Assigned To | Since |
+ |------|--------|--------|-------------|-------|
+ | Auth token expiry | ⏳ Open | triage YYYY-MM-DD | implementer | YYYY-MM-DD |
+ | Rate limiting | 📥 Inbox | triage YYYY-MM-DD | human | YYYY-MM-DD |
```

## Compounding Effect

Over time, the state file demonstrates the compounding value of skills:

```markdown
## Skill Count
| Skill | Created | Last Used | Evals |
|-------|---------|-----------|-------|
| loop-engineer | Day 1 | every session | ✅ |
| triage | Day 1 | daily | ✅ |
| docker-setup | Day 5 | weekly | ✅ |
| api-test-pattern | Day 12 | per PR | ✅ |
| deploy-checklist | Day 19 | per release | ✅ |
```

Each new skill makes the loop more effective without re-deriving knowledge from scratch.
