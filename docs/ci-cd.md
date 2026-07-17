# 📊 CI/CD Pipelines

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **CI** | push + PR | Skill validation, lint, eval harness |
| **CodeQL** | push + PR + weekly | Security vulnerability scanning |
| **Dependency Review** | PR | Dependency vulnerability check |
| **Agent Harness** | workflow_dispatch | Run agents in GitHub Actions |
| **Release** | Tag v*.*.* | Automatic GitHub Release creation |
| **Dependabot** | Weekly | Automated dependency updates |
| **Scorecard** | push + weekly | OpenSSF security scorecard |
| **Pages** | push to main | Deploy documentation to GitHub Pages |

> [← Built-in Skills](skills.md) | [⚡ Quick Reference →](quick-reference.md)
