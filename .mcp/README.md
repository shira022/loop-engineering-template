# Model Context Protocol (MCP) Configuration

This directory contains MCP server configurations for connecting your agent
to external tools and services.

## Available Configs

| File | Service | Purpose in the Loop |
|------|---------|---------------------|
| `filesystem.json` | Local file access | Read/write project files from sub-agents |
| `github.json` | GitHub API | Create PRs, review issues, manage repos |
| `sqlite.json` | SQLite database | Persistent state storage |
| `linear.json` | Linear | Update tickets when PRs are created |
| `slack.json` | Slack | Notify channels of triage results and PRs |

## Usage

### How MCP Fits in the Loop

MCP connectors let the loop **act** in your environment instead of telling you what it would do:

| Phase | Connector | Action |
|-------|-----------|--------|
| Triage finds a bug | GitHub MCP | Opens an issue |
| Implementer fixes it | Filesystem MCP | Reads/writes code in worktree |
| Verifier approves | GitHub MCP | Creates PR |
| PR is created | Linear MCP | Updates ticket status |
| PR is ready | Slack MCP | Posts notification to channel |

### Setup

Each MCP server requires environment variables:

```bash
cp .mcp/example-config.json .mcp/local.json
```

Set required environment variables:

```bash
export GITHUB_TOKEN="ghp_..."
export LINEAR_API_KEY="lin_api_..."
export SLACK_BOT_TOKEN="xoxb-..."
export SLACK_TEAM_ID="T..."
```

### Provider Integration

| Platform | How to load MCP configs |
|----------|------------------------|
| **Claude Code** | Reads `.mcp/*.json` automatically |
| **Codex** | Reads `.mcp/*.json` automatically |
| **Hermes** | Configured in `config.yaml` under `mcp_servers` |
| **Opencode** | Configured in `.opencode/config.yaml` |

## Security Notes

- **Never commit credentials** to the repository
- Use `.mcp/*.local.json` for local overrides (gitignored)
- Each MCP server runs with the permissions of its configured token
- Review what each MCP server can access before adding it
