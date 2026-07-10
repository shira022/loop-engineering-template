# Loop Engineering Project Template

A project template for **Loop Engineering** — an AI-agent-assisted software development methodology.

The core idea is to establish a **Work → Learn → Improve** cycle that continuously enhances agent performance across sessions.

## What is Loop Engineering?

Loop Engineering is a methodology where AI agents:

1. **Work** — execute development tasks (coding, testing, documenting)
2. **Learn** — extract structured knowledge from completed tasks
3. **Improve** — persist knowledge as reusable skills for future sessions

This creates a flywheel effect: each session makes the next one more efficient.

## Directory Structure

```
.
├── .agents/skills/       # agentskills.io-compatible skill definitions
│   ├── loop-engineer/    # Core loop engineering orchestrator
│   ├── knowledge-harvest/# Extract learnings from completed tasks
│   ├── skill-crafter/    # Auto-create skills from repeated patterns
│   ├── decision-recorder/# Architecture Decision Records
│   ├── session-reviewer/ # End-of-session retrospectives
│   ├── project-bootstrapper/ # Bootstrap new projects from this template
│   └── project-manager/  # Cross-project task management
├── docs/adr/             # Architecture Decision Records
├── learnings/            # Session learnings and knowledge
├── AGENTS.md             # Agent-facing rules and conventions
├── CONTRIBUTING.md       # Contribution guidelines
└── .github/workflows/    # CI / Agent Harness
```

## Getting Started

```bash
# Create a new project from this template
gh repo create my-project --template shira022/loop-engineering-template --public
git clone https://github.com/your-org/my-project.git
cd my-project

# Or use the project-bootstrapper skill via your agent:
# "Bootstrap a new project from this template"
```

Once cloned, run the **project-bootstrapper** skill (first session only) to customize language, framework, and CI settings.

## Agent Compatibility

This template uses the `.agents/skills/` format standard defined by [agentskills.io](https://agentskills.io), compatible with:

- Hermes Agent
- Opencode
- Claude Code
- Gemini CLI
- Cursor
- GitHub Copilot

## License

MIT
