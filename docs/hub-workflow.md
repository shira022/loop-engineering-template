# Hub Workflow: Multi-Project Setup

> *"A hub repo that references the template via symlinks, managing multiple application projects under `project/`."*

This document describes how to use the loop-engineering-template as a **central hub** that manages multiple projects, rather than cloning it as a standalone project. This is the pattern used by `hermes-project/` — one hub repo, many application repos, shared skills.

## Architecture

```
hub-repo/                        # Your hub repository
├── AGENTS.md                    # Hub-level rules (loads learnings/ + docs/adr/)
├── .agents/skills/ → symlinks   # Symlinks to template's .agents/skills/
├── project/
│   ├── repo-registry.yaml       # Registry of all projects
│   ├── app-1/repo-app-1/        # Project created from template
│   │   ├── src/
│   │   └── tests/
│   └── app-2/repo-app-2/        # Another project
│       ├── src/
│       └── tests/
├── learnings/                   # Hub-level cross-project learnings
├── docs/adr/                    # Hub-level architecture decisions
└── loop-engineering-template/   # Cloned template (the origin of skills)
    └── .agents/skills/          # Real skill files live here
```

## Why Use a Hub?

| Scenario | Hub | Standalone Clone |
|----------|-----|-----------------|
| Single project | Overkill ✗ | Simple ✓ |
| 2–3 related projects | Shared skills ✓ | Duplicated skills ✗ |
| 5+ microservices | Central triage + cross-project analytics ✓ | Inconsistent versions ✗ |
| Team of agents | One source of truth for skills ✓ | Skill drift ✗ |

## Setup

### Step 1: Create the Hub

```bash
mkdir my-hub && cd my-hub
git init
mkdir -p project learnings docs/adr
```

### Step 2: Add the Template as a Subdirectory

```bash
git clone https://github.com/shira022/loop-engineering-template.git
# or: gh repo clone shira022/loop-engineering-template
```

### Step 3: Symlink Skills from Template

```bash
# Link each skill (or all at once)
mkdir -p .agents
ln -s ../loop-engineering-template/.agents/skills .agents/skills
ln -s ../loop-engineering-template/.agents/agents .agents/agents
ln -s ../loop-engineering-template/.agents/config .agents/config
ln -s ../loop-engineering-template/scripts scripts
ln -s ../loop-engineering-template/Makefile Makefile
```

### Step 4: Create Hub AGENTS.md

```markdown
# Hub Rules

- `.agents/skills/` — symlinked from `loop-engineering-template/.agents/skills/`
- New projects go under `project/` and get registered in `project/repo-registry.yaml`
- Hub-level learnings in `learnings/`, per-project learnings in each repo
- Architecture decisions in `docs/adr/`
- Before starting work, check `learnings/` (most recent first) and `docs/adr/`
```

### Step 5: Add Projects

```bash
# Create a new project from template
cd project
gh repo create my-app --template shira022/loop-engineering-template --public
git clone https://github.com/your-org/my-app.git
cd my-app
# Run bootstrap via your agent
```

Then register it:

```yaml
# project/repo-registry.yaml
- name: my-app
  path: /path/to/hub/project/my-app/repo-my-app
  visibility: public
  language: typescript
  framework: next.js
  build_tool: npm
  test_framework: vitest
  created_at: "2026-07-17T12:00:00"
  description: "Web application with auth"
```

## Daily Workflow

```bash
# 1. Navigate to hub root
cd /path/to/hub

# 2. Run hub-level triage (checks all registered projects)
bash scripts/daily-triage.sh

# 3. Work on a specific project
cd project/my-app/repo-my-app
# ... develop, commit, push ...

# 4. Update hub state
cd /path/to/hub
# Update learnings/ and STATE.md manually as needed
```

## Sub-Agent Dispatching Across Projects

With `project-manager` skill and `repo-registry.yaml`, you can dispatch agents to any registered project:

```bash
# Using project-manager
# "Dispatch a verifier to my-app to review PR #42"
```

## ⚠️ Warnings

1. **Symlinks break** if the template directory is moved or deleted. Keep it stable.
2. **Git history is separate** — the hub, the template, and each project are independent repos.
3. **Skill updates** — to update skills, `git pull` inside `loop-engineering-template/`.
4. **Not for CI** — GitHub Actions workflows live per-project, not in the hub.

---

## 🇯🇵 日本語

ハブ運用は、テンプレートリポジトリをシンボリックリンクで参照し、`project/` 配下に複数のアプリケーションプロジェクトを管理する方式です。スキルはテンプレートに一元管理され、全プロジェクトで共有されます。テンプレートの更新は `git pull` で全プロジェクトに即座に反映されます。
