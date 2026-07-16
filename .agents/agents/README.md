# Generic Sub-Agent System

This directory defines **provider-agnostic sub-agent configurations** for the maker/checker split pattern — the single most important structural element in loop engineering.

## Why Generic?

Codex uses `.codex/agents/` (TOML), Claude Code uses `.claude/agents/` (Markdown), Hermes uses `delegate_task()`, Opencode uses `--task`. Rather than shipping platform-specific configs for just one tool, this directory provides:

1. **The canonical definition** in YAML — readable by humans and parsable by tools
2. **Provider mappings** — how to translate each generic agent into native format
3. **A consistent mental model** — explorer → implementer → verifier — for any agent

## The Three Core Roles

| Role | Does | Does NOT | Access |
|------|------|----------|--------|
| **Explorer** | Investigates, searches, reads, traces bugs | Write code or modify files | Read-only |
| **Implementer** | Writes code, creates tests, makes changes | Review its own work | Read + Write |
| **Verifier** | Reviews, tests, checks security, validates | Write new code | Read + Test-run |

```
┌──────────┐     ┌──────────────┐     ┌──────────┐     ┌─────────┐
│ Explorer │────>│ Implementer  │────>│ Verifier │────>│  Human  │
│ (reads)  │     │ (writes)     │     │ (checks) │     │ (reviews)│
└──────────┘     └──────────────┘     └──────────┘     └─────────┘
     │                  │                   │
     └──────────────────┴───────────────────┘
                    ↑ feedback loop (if verifier rejects)
```

## How to Use

### Option A: Native sub-agent support

Translate YAML definitions into your platform's format:

| Platform | Location | Format | Invocation |
|----------|----------|--------|------------|
| **Claude Code** | `.claude/agents/<name>.md` | Markdown | `claude --agent <name>` |
| **Codex** | `.codex/agents/<name>.toml` | TOML | `@<name>` in prompt |
| **Hermes** | In-session `delegate_task()` | Python | See below |
| **Opencode** | `opencode --task` | CLI arg | `opencode --task "<instructions>"` |

### Option B: DIY with any agent

```bash
# Step 1: Explore — read only
opencode --task "Explore the codebase to understand how auth works. Do NOT write code."

# Step 2: Implement — write code
opencode --task "Implement the auth fix based on exploration findings. Write tests."

# Step 3: Verify — review only
opencode --task "Review the changes. Run tests. Report issues."
```

### Option C: Hermes delegate_task pattern

```python
# Phase 1: Explore
findings = delegate_task(
    goal="Explore the codebase for X and report findings",
    context="Read-only investigation requested"
)

# Phase 2: Implement
changes = delegate_task(
    goal="Implement the fix based on exploration findings",
    context=f"Explorer report: {findings}"
)

# Phase 3: Verify
verdict = delegate_task(
    goal="Review the implementer's changes for correctness",
    context=f"Changes: {changes}"
)
```

## Creating Custom Agents

Copy `_template.yaml` and fill in the fields:

```yaml
name: "my-custom-agent"
role: "custom"
description: "..."
instructions: |
  ...
```

## Design Principles

1. **Provider independence** — define once, use everywhere
2. **Clear separation** — explorer never writes, implementer never reviews, verifier never implements
3. **Different models** — use different providers for different roles (catches different bug types)
4. **Fail fast** — verifier rejects early, before human review
5. **Token-aware** — explorers are cheapest, implementers balanced, verifiers discerning
