# 📁 Directory Structure

```
.
├── .agents/skills/           # 8 agentskills.io-compatible skills
│   ├── loop-engineer/        # Core session orchestrator
│   ├── knowledge-harvest/    # Extract learnings from completed tasks
│   ├── skill-crafter/        # Auto-create skills from repeated patterns
│   ├── decision-recorder/    # Architecture Decision Records
│   ├── session-reviewer/     # End-of-session retrospectives
│   ├── project-bootstrapper/ # Bootstrap new projects from this template
│   ├── project-manager/      # Cross-project task management
│   ├── test-policy/          # Enforce comprehensive test coverage
│   └── triage/               # Scheduled CI triage and automation dispatch
├── .agents/agents/           # Generic sub-agent definitions
├── .agents/config/           # Automation schedule files
├── .devcontainer/            # VS Code / Codespaces dev container
├── .github/workflows/        # CI / CodeQL / Dependabot / Agent Harness / Release / Pages / Scorecard
├── .mcp/                     # Model Context Protocol configuration
├── docs/                     # Documentation (GitHub Pages)
├── inbox/                    # Triage inbox
├── learnings/                # Session learnings
├── scripts/                  # Utility scripts
├── traces/                   # Agent execution traces
├── AGENTS.md                 # Agent-facing rules
├── CONTRIBUTING.md           # Contribution guidelines
├── Makefile                  # Task runner
├── STATE.md                  # Loop state
├── TESTING.md                # Testing policy
└── SECURITY.md               # Security vulnerability reporting
```

> [← Getting Started](getting-started.md) | [🛠️ Built-in Skills →](skills.md)
