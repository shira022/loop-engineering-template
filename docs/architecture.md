# Loop Engineering Architecture

## System Overview

Loop Engineering implements a **procedural memory** system for AI agents. Instead of starting each session from scratch, agents progressively build a reusable knowledge base of skills, learnings, and decisions. The system is built on **6 core building blocks** that compose into autonomous loops.

## The 6 Building Blocks

| Block | Role | Location |
|-------|------|----------|
| **Automations** | Scheduled execution — the heartbeat of the loop | `.agents/config/schedules.yaml`, `.github/workflows/agent-harness.yml` |
| **Worktrees** | Isolated environments for parallel sub-agents | `project-manager` skill, `git worktree` |
| **Skills** | Codified project knowledge and conventions | `.agents/skills/*/SKILL.md` |
| **Plugins & Connectors** | Real tool access via MCP servers + distribution bundles | `.mcp/*.json` |
| **Sub-agents** | Maker/checker split for quality | `.agents/agents/*.yaml` |
| **State** | Cross-session memory of what's done and next | `learnings/`, `docs/adr/`, `traces/` |

```mermaid
graph TD
    subgraph "The Loop"
        A[Automations<br/>Schedule] --> B[Triage<br/>Discover & Prioritize]
        B --> C[Sub-agents<br/>Maker/Checker Split]
        C --> D[Worktrees<br/>Isolated Execution]
        D --> E[Plugins & Connectors<br/>PR + Ticket + Notify]
        E --> F[State<br/>learnings/ + traces/]
        F --> A
    end
    
    subgraph "Foundation"
        S[Skills<br/>.agents/skills/]
        C -->|reads| S
        F -->|persists| S
    end
```

## Session Lifecycle

```mermaid
graph TD
    subgraph Session
        LE[loop-engineer] --> KH[knowledge-harvest]
        LE --> DR[decision-recorder]
        LE --> SR[session-reviewer]
        KH --> SC[skill-crafter]
    end

    subgraph Storage
        L[learnings/]
        A[docs/adr/]
        S[.agents/skills/]
        T[traces/]
    end

    KH -->|writes| L
    DR -->|writes| A
    SC -->|creates| S
    LE -->|writes| T

    L -.->|next session loads| LE
    A -.->|next session loads| LE
    S -.->|available to all| LE
```

## The Loop Lifecycle

### Session Start

```mermaid
sequenceDiagram
    participant Agent as AI Agent
    participant LE as loop-engineer
    participant FS as File System

    Agent->>LE: Start session
    LE->>FS: Read learnings/ (recent first)
    LE->>FS: Read docs/adr/
    LE->>LE: Initialize tool-call counter
    LE-->>Agent: Context loaded, ready
```

### During Session

```mermaid
flowchart LR
    A[Agent works] --> B{5+ tool calls?}
    B -->|Yes| C[knowledge-harvest]
    B -->|No| A
    C --> D{Pattern 3×?}
    D -->|Yes| E[skill-crafter]
    D -->|No| A
    E --> A
```

### Session End

```mermaid
sequenceDiagram
    participant Agent as AI Agent
    participant LE as loop-engineer
    participant SR as session-reviewer
    participant FS as File System

    Agent->>LE: End session
    LE->>SR: Run retrospective
    SR->>FS: Write learnings/session-review-*.md
    SR->>FS: Check for skipped knowledge-harvest
    SR-->>Agent: Review complete, action items ready
    LE->>LE: Reset counters
```

## Skill Dependencies

```mermaid
graph LR
    LE[loop-engineer] --> KH[knowledge-harvest]
    LE --> DR[decision-recorder]
    LE --> SR[session-reviewer]
    KH --> SC[skill-crafter]
    PB[project-bootstrapper] --> PM[project-manager]
    PM --> TP[test-policy]

    style LE fill:#4a9eff,stroke:#333,color:#fff
    style KH fill:#50c878,stroke:#333,color:#fff
    style SC fill:#ff6b6b,stroke:#333,color:#fff
    style DR fill:#ffa500,stroke:#333,color:#fff
    style SR fill:#da70d6,stroke:#333,color:#fff
    style PB fill:#20b2aa,stroke:#333,color:#fff
    style PM fill:#20b2aa,stroke:#333,color:#fff
    style TP fill:#f0e68c,stroke:#333,color:#000
```

## Data Flow

| Artifact | Created By | Used By | Format |
|----------|-----------|---------|--------|
| `learnings/*.md` | knowledge-harvest | loop-engineer (next session) | Markdown with frontmatter |
| `docs/adr/NNN-*.md` | decision-recorder | loop-engineer (next session) | Markdown with status |
| `.agents/skills/*/SKILL.md` | skill-crafter | All agents | agentskills.io YAML+Markdown |
| `traces/YYYY-MM-DD-*.json` | loop-engineer | analyze-traces.py | JSON metrics |
| `learnings/session-review-*.md` | session-reviewer | loop-engineer (next session) | Markdown with action items |

## Tool Implementation Mapping

Each of the 6 building blocks is implemented in both major coding agents. The names differ slightly; the capability is the same:

| Block | Claude Code | Notes |
|-------|-------------|-------|
| **Automations** | Scheduled tasks, cron, `/loop` (cadence), `/goal` (run-until-done), hooks, GitHub Actions | Both tools support `/goal` — a separate model checks the stop condition |
| **Worktrees** | `git worktree`, `--worktree` flag, `isolation: worktree` on subagents | Isolated checkouts so parallel agents don't collide |
| **Skills** | Agent Skills (`SKILL.md`) — loaded automatically or invoked explicitly | Same SKILL.md format across both tools |
| **Plugins & Connectors** | MCP servers + plugins. Lifecycle hooks fire shell commands at agent lifecycle points | MCP is the shared protocol; plugins are the distribution mechanism |
| **Sub-agents** | Task subagents in `.claude/agents/`, agent teams | Maker/checker split; different models catch different mistakes |
| **State** | Markdown (AGENTS.md, STATE.md, progress files), Linear via MCP | *"The model forgets between runs. The repo doesn't."* |

## CI Pipeline Architecture

```mermaid
graph LR
    subgraph "Pull Request"
        BP[Branch Policy] --> LINT[Lint & Validate]
        LINT --> EVAL[Eval Harness]
        EVAL --> CQ[CodeQL]
        CQ --> DR[Dependency Review]
        DR --> MERGE{Merge}
    end

    subgraph "Release"
        TAG[Tag v*.*.*] --> RELEASE[GitHub Release]
    end

    subgraph "Scheduled"
        SCHED[Weekly] --> CQ
        SCHED --> DEP[Dependabot]
    end
```

## Project Registry

The `repo-registry.yaml` (created by project-bootstrapper) tracks all projects created from this template:

```yaml
- name: my-app
  path: ${PROJECTS_DIR}/my-app/repo-my-app
  visibility: public
  language: typescript
  framework: next.js
  build_tool: npm
  test_framework: vitest
  created_at: "2026-07-16T10:00:00"
  description: "Web application with auth"
```

This is used by `project-manager` to dispatch tasks to the correct project worktrees.
