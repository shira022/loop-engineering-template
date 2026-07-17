# ⚡ Quick Reference

## Hub Workflow (Multi-Project)

```
hermes-project/
├── AGENTS.md
├── .agents/skills/ -> symlinks to template
├── project/
│   ├── repo-registry.yaml
│   └── app-1/repo-app-1/
└── loop-engineering-template/
```

## Makefile Targets

| Target | Description |
|--------|-------------|
| `make setup` | Install dev dependencies |
| `make lint` | Run lint checks |
| `make validate` | Validate all skills |
| `make git-flow-init` | Initialize Git Flow |

> [← Back to Overview](/)
