<h1 align="center">🔄 Loop Engineering Template</h1>

<p align="center">
  <em>The AI-Agent-Driven Software Development Methodology</em>
</p>

<p align="center">
  <a href="https://github.com/shira022/loop-engineering-template/actions/workflows/ci.yml">
    <img src="https://github.com/shira022/loop-engineering-template/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <a href="https://github.com/shira022/loop-engineering-template/actions/workflows/codeql.yml">
    <img src="https://github.com/shira022/loop-engineering-template/actions/workflows/codeql.yml/badge.svg" alt="CodeQL">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
  </a>
  <a href="https://agentskills.io">
    <img src="https://img.shields.io/badge/agentskills.io-compatible-blue" alt="agentskills.io">
  </a>
  <a href="https://github.com/shira022/loop-engineering-template/stargazers">
    <img src="https://img.shields.io/github/stars/shira022/loop-engineering-template?style=social" alt="Stars">
  </a>
  <a href="https://github.com/shira022/loop-engineering-template/network/members">
    <img src="https://img.shields.io/github/forks/shira022/loop-engineering-template?style=social" alt="Forks">
  </a>
</p>

<p align="center">
  <b>Hermes Agent</b> · 
  <b>Opencode</b> · 
  <b>Claude Code</b> · 
  <b>Gemini CLI</b> · 
  <b>Cursor</b> · 
  <b>GitHub Copilot</b>
</p>

---

## 📖 Overview

**Loop Engineering** is a methodology where AI agents follow a continuous **Work → Learn → Improve** cycle. With each session, the agent becomes more effective by persisting knowledge as reusable **skills**.

This template gives you everything you need to start a new project with loop engineering built in — from the skill orchestration system to CI/CD, branching strategy, and security policies.

```mermaid
graph LR
    A[🛠️ Work] --> B[📚 Learn]
    B --> C[⚡ Improve]
    C --> A
    style A fill:#4a9eff,stroke:#333,color:#fff
    style B fill:#50c878,stroke:#333,color:#fff
    style C fill:#ff6b6b,stroke:#333,color:#fff
```

---

## ✨ Features

### 🧠 Agent-First Architecture
- **9 built-in skills** — orchestrator, knowledge harvester, skill crafter, decision recorder, session reviewer, project bootstrapper, project manager, test policy, triage
- **agentskills.io compatible** — works with every major AI coding agent
- **Skill auto-creation** — repeated patterns are automatically detected and codified
- **Provider-agnostic sub-agents** — explorer, implementer, verifier roles in neutral YAML format
- **Automation-ready** — pre-configured schedules, triage skill, and /goal loop
- **State spine** — STATE.md tracks what's tried, what passed, what's open across sessions
- **Triage inbox** — items the loop can't handle get routed for human review

### 🔄 The Loop Cycle

| Phase | Skill | What Happens |
|-------|-------|-------------|
| 🛠️ **Work** | `loop-engineer` | Orchestrates the session, loads past context |
| 📚 **Learn** | `knowledge-harvest` | Extracts structured knowledge from complex tasks |
| ⚡ **Improve** | `skill-crafter` | Auto-creates skills from 3× repeated patterns |
| 📝 **Record** | `decision-recorder` | Captures architecture decisions as ADRs |
| 🔍 **Review** | `session-reviewer` | Retrospectives with action items for next session |

### 🤖 Sub-Agent System (Maker/Checker Split)
- **3 generic roles** — explorer (read-only), implementer (writes code), verifier (reviews)
- **Provider-agnostic YAML format** — works with Claude Code, Codex, Hermes, Opencode
- **Different models** for different roles catches different mistake types
- **No hard dependency** on any specific agent platform

### ⏰ Automations
- **Scheduled CI triage** — `agent-harness.yml` runs weekdays at 07:00 UTC
- **Configurable schedules** — `.agents/config/schedules.yaml` defines daily/weekly/event-driven tasks
- **Triage script** — `scripts/daily-triage.sh` analyzes CI, issues, and commits
- **Manual dispatch** still available via `workflow_dispatch`

### 🔌 Connectors (MCP)
- **GitHub MCP** — create PRs, review issues, manage repos
- **Linear MCP** — update tickets when PRs are created
- **Slack MCP** — notify channels of triage results
- **Filesystem MCP** — local file access for sub-agents
- **Extensible** — add any MCP-compatible server

### 🏗️ Project Infrastructure
- **Git Flow** — `main` / `develop` / `feature/*` / `release/*` / `hotfix/*`
- **CI/CD** — 5 GitHub Actions workflows (CI, CodeQL, Dependency Review, Agent Harness, Release)
- **Security** — SECURITY.md with SLA, pre-commit hooks, CODEOWNERS, branch protection
- **Dev Container** — ready-to-use VS Code / GitHub Codespaces setup
- **MCP Support** — Model Context Protocol configuration for filesystem, GitHub, database

### 🌐 Language Agnostic
This template doesn't lock you into any language. The `project-bootstrapper` skill guides you through setup for:

`Python` · `TypeScript` · `Rust` · `Go` · `Java` · `Kotlin` · `Swift` · `C#` · and more

---

## 🚀 Getting Started

### Option 1: Use the template directly

```bash
# Create a new repository from this template
gh repo create my-project --template shira022/loop-engineering-template --public
git clone https://github.com/your-org/my-project.git
cd my-project

# Launch your AI agent and tell it:
# "Bootstrap this project using the project-bootstrapper skill"
```

### Option 2: Quickstart script

```bash
# Download and run the quickstart (coming soon)
curl -sL https://raw.githubusercontent.com/shira022/loop-engineering-template/main/scripts/quickstart.sh | bash
```

### Prerequisites

| Tool | Required | Purpose |
|------|----------|---------|
| `git` | ✅ Yes | Version control |
| `gh` CLI | ✅ Yes | GitHub repository creation |
| AI Agent | ✅ Yes | Hermes, Opencode, Claude Code, or any agentskills.io-compatible agent |

---

## 📁 Directory Structure

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
│   └── triage/               # Scheduled CI triage & automation dispatch
├── .agents/agents/           # Generic sub-agent definitions (explorer, implementer, verifier)
├── .agents/config/           # Automation schedule and configuration files
├── .devcontainer/            # VS Code / Codespaces dev container
├── .github/workflows/        # CI / CodeQL / Dependabot / Agent Harness / Release
├── .mcp/                     # Model Context Protocol configuration (GitHub, Linear, Slack, SQLite)
├── docs/
│   ├── adr/                  # Architecture Decision Records
│   ├── eval-harness.md       # Skill evaluation framework docs
│   ├── architecture.md       # System architecture documentation
│   ├── loop-patterns.md      # "One Loop" complete workflow guide
│   ├── quickstart-loop.md    # 15-minute start with triage + verifier
│   ├── triage-inbox.md       # Triage inbox pattern documentation
│   └── worktree-isolation.md # Worktree isolation for sub-agents
├── inbox/                    # Triage inbox — items the loop can't handle
├── learnings/                # Session learnings and knowledge
├── scripts/                  # Utility scripts (validate, eval, triage, goal-loop)
├── traces/                   # Agent execution traces
├── AGENTS.md                 # Agent-facing rules and conventions
├── CONTRIBUTING.md           # Contribution guidelines
├── Makefile                  # Task runner
├── STATE.md                  # Loop state — the spine of the system
├── TESTING.md                # Testing policy
└── SECURITY.md               # Security vulnerability reporting
```

---

## 🛠️ Built-in Skills

| Skill | Description | Trigger |
|-------|-------------|---------|
| **loop-engineer** | Session orchestrator — loads context, coordinates skills, manages counters | Every session start |
| **knowledge-harvest** | Extracts structured learnings to `learnings/` | After 5+ tool calls |
| **skill-crafter** | Creates new skills when patterns repeat 3× | On pattern threshold |
| **decision-recorder** | Writes ADRs for architectural decisions | On significant decisions |
| **session-reviewer** | Conducts end-of-session retrospectives | Session end |
| **triage** | Scheduled CI triage & automation dispatch | Daily schedule or manual |
| **project-bootstrapper** | Scaffolds new projects from this template | First session only (self-destructs) |
| **project-manager** | Manages tasks across multiple git worktrees | On task dispatch |
| **test-policy** | Enforces 80%+ test coverage across all code | Every PR / commit |

---

## 🤖 Agent Compatibility

This template uses the `.agents/skills/` format defined by [agentskills.io](https://agentskills.io), making it compatible with:

| Agent | Status | Notes |
|-------|--------|-------|
| **Hermes Agent** | ✅ Fully supported | Native agentskills.io support |
| **Opencode** | ✅ Fully supported | Use `opencode --task` with skills loaded |
| **Claude Code** | ✅ Compatible | Loads `.agents/skills/` automatically |
| **Gemini CLI** | ✅ Compatible | agentskills.io format supported |
| **Cursor** | ✅ Compatible | `.cursorrules` equivalent |
| **GitHub Copilot** | ✅ Compatible | Reads `AGENTS.md` instructions |

---

## 📊 CI/CD Pipelines

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **CI** | push + PR (protected branches) | Skill validation, lint, eval harness |
| **CodeQL** | push + PR + weekly | Security vulnerability scanning |
| **Dependency Review** | PR | Dependency vulnerability check |
| **Agent Harness** | `workflow_dispatch` | Run agents in GitHub Actions |
| **Release** | Tag `v*.*.*` | Automatic GitHub Release creation |
| **Dependabot** | Weekly | Automated dependency updates |

---

## 📝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Git Flow branch strategy
- Branch naming conventions
- PR requirements
- Code style guidelines
- Security vulnerability reporting

### Quick Start for Contributors

```bash
# Clone and set up
git clone https://github.com/shira022/loop-engineering-template.git
cd loop-engineering-template
make setup    # Install dev dependencies
make lint     # Run lint checks
make validate # Validate all skills
```

---

## 🔒 Security

See [SECURITY.md](SECURITY.md) for our security policy and vulnerability reporting process. Key points:

- **Private disclosure**: Report vulnerabilities via GitHub Private Advisory
- **Response SLA**: Critical within 24h, High within 48h
- **Coordinated disclosure**: We fix before public disclosure

---

## 📄 License

MIT © [shira022](https://github.com/shira022)

---

## 🌟 Support

- ⭐ Star this repository if you find it useful
- 🐛 [Report bugs](https://github.com/shira022/loop-engineering-template/issues/new?labels=bug&template=bug_report.md)
- 💡 [Suggest features](https://github.com/shira022/loop-engineering-template/issues/new?labels=enhancement&template=feature_request.md)
- 💬 [Start a discussion](https://github.com/shira022/loop-engineering-template/discussions)

---

## 🇯🇵 日本語

Loop Engineering は、AIエージェントが **Work（作業）→ Learn（学習）→ Improve（改善）** のサイクルを繰り返すことで、セッションを重ねるごとにパフォーマンスが向上するソフトウェア開発手法です。

このテンプレートは、Loop Engineering を実践するために必要な全スキル・CI/CD・セキュリティポリシー・ブランチ戦略をパッケージ化しています。

詳細は [README.ja.md](README.ja.md) をご覧ください。
