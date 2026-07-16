# MCP Connectors

> *Model Context Protocol (MCP) servers give your agents real tool access — creating PRs, updating tickets, sending notifications.*

This directory contains MCP server configuration files. Each `.json` file defines a connector that your agent can use to interact with external services.

## Available Connectors

| File | Service | Purpose |
|------|---------|---------|
| `github.json` | GitHub | Create PRs, review issues, manage repos, list runs |
| `linear.json` | Linear | Update tickets when PRs are created |
| `slack.json` | Slack | Notify channels of triage results |
| `database.json` | SQLite | Local database access for sub-agents |
| `example-config.json` | — | Template with documentation comments |

## Setup

### Prerequisites

Each connector needs authentication. The method varies by service.

### GitHub MCP

1. Create a [GitHub Personal Access Token](https://github.com/settings/tokens) (classic) with scope: `repo`, `workflow`
2. Set the token as an environment variable:

```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
```

3. The `github.json` config reads `GITHUB_TOKEN` from the environment:

```json
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": {
    "GITHUB_TOKEN": "${GITHUB_TOKEN}"
  }
}
```

### Linear MCP

1. Create a [Linear API key](https://linear.app/settings/api)
2. Set the environment variable:

```bash
export LINEAR_API_KEY="lin_api_xxxxxxxxxxxxxxxxxxxx"
```

### Slack MCP

1. Create a [Slack App](https://api.slack.com/apps) with `chat:write` and `channels:read` scopes
2. Install the app to your workspace
3. Set the bot token:

```bash
export SLACK_BOT_TOKEN="xoxb-xxxxxxxxxxxxxxxxxxxx"
```

## Usage

Once configured, your agent can use the connectors automatically. Example agent prompts:

```
"Create a PR from branch fix/auth to develop with title 'fix: auth token expiry'"
"Update Linear ticket ENG-123 status to 'In Review'"
"Post to #engineering channel: 'PR #42 is ready for review'"
```

## Adding a New Connector

1. Find the MCP server package (npm, pip, or binary)
2. Create a new `.json` file in this directory:

```json
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-something"],
  "env": {
    "API_KEY": "${SOMETHING_API_KEY}"
  }
}
```

3. Document required environment variables in this README
4. Add the config to `.gitignore` if it contains default credentials

## Testing

```bash
# Verify MCP config syntax
python3 scripts/validate-configs.py
```

## ⚠️ Warnings

1. **Credentials** — Never commit real tokens. Use environment variables or `.env` files.
2. **Rate limits** — GitHub API has rate limits. Connectors that make many calls may hit them.
3. **Cost** — Some MCP servers (e.g., Slack) are free. Others may have usage costs.
4. **Security** — Connectors give agents real write access. Review what each connector can do.

---

## 🇯🇵 日本語

MCPコネクタはエージェントに外部サービスへのアクセス権限を与えます。各 `.json` ファイルが一つのMCPサーバー設定を定義します。認証情報は環境変数で管理し、リポジトリにコミットしないでください。
