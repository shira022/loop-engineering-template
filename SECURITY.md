# SECURITY POLICY

## Supported Branches

| Branch | Security Fixes | Status |
|--------|---------------|--------|
| `main` | ✅ 常に受け付け | ✅ Active |
| `develop` | ✅ 次のリリースで対応 | ⚠️ Active |
| `release/*` | ✅ リリース前に修正 | ✅ Active |
| `hotfix/*` | 🚨 緊急対応 | ⚡ On-demand |
| Older tags | ❌ サポート対象外 | ❌ EOL |

## Reporting a Vulnerability

**Do NOT** report security vulnerabilities via public GitHub Issues.

Instead, please report them via one of the following methods:

### 1. Email (推奨)
Send details to the project maintainer. If no dedicated email is listed in the repository profile, open a **private security advisory** on GitHub:

### 2. GitHub Private Advisory
1. Go to the repository on GitHub
2. Click **Security** tab
3. Click **Report a vulnerability** (in the "Advisories" section)
4. Fill in the details

### What to include
- Type of vulnerability (XSS, SQL injection, remote code execution, etc.)
- Steps to reproduce
- Affected versions / branches
- Potential impact
- Suggested fix (if available)

### Response SLA

| Severity | Initial Response | Patch Target |
|----------|-----------------|--------------|
| 🔴 Critical | Within 24 hours | 7 days |
| 🟠 High | Within 48 hours | 14 days |
| 🟡 Medium | Within 5 days | 30 days |
| 🔵 Low | Within 14 days | Next release |

## Disclosure Policy

- We follow **coordinated disclosure**: please allow us time to fix before public disclosure
- We will acknowledge receipt within the SLA above
- We will keep you informed of progress
- Once a fix is released, we welcome public disclosure

## Security Related Configurations

### Branch Protection
See [CONTRIBUTING.md](CONTRIBUTING.md#-ブランチ保護ルール-main--develop) for branch protection rules.

### Pre-commit Hooks
This repository uses pre-commit hooks that include:
- `detect-private-key` — prevents accidental commit of keys/tokens
- `check-merge-conflict` — catches unresolved conflict markers
- `check-added-large-files` — prevents large file commits (DoS vector)

### Dependency Management
- Dependabot is configured for GitHub Actions
- Dependency Review action checks for vulnerable dependencies on every PR
- CodeQL analysis runs on every push to protected branches

## Threat Model

This project is a **template repository** for loop engineering with AI agents.
The main security considerations are:

1. **Agent instruction injection** — skills/AGENTS.md contain instructions executed by LLM agents
2. **GitHub token exposure** — CI workflows may process PRs from forks
3. **Supply chain** — dependencies of the template itself
4. **Secret leakage** — users may accidentally commit secrets while testing the template

Reviewers should be vigilant about injected instructions in `.md` files, YAML workflow files, and skill definitions.
