# 🔒 Path Leak Guard

Committing a user-specific absolute path to a repository leaks the machine's
directory layout and the OS user name. A path such as `/home/<user>/project`
or `C:\Users\<user>\project` tells anyone who reads the repository how the
author's machine is organized and who the author is. This is a privacy leak
that survives rebases, mirrors and forks, so it is cheaper to block it than to
scrub it later.

The template ships **two layers** that work together:

| Layer | Where it runs | What it protects |
|-------|---------------|------------------|
| **Local pre-commit guard** | On the developer's machine, before a commit | Local commits, regardless of how the code was edited |
| **GitHub-side reusable workflow** | In CI, on every push and pull request | PRs, web edits, and commits made on other machines |

## Layer 1 — Local pre-commit guard (machine-local)

The local guard is provided by the machine-local **`pii-guard`** tool. It is
installed outside the repository and is deliberately **never copied into the
repository** — the scanner is not project code, and shipping it inside every
project would only create more surface to maintain.

Install it once per repository with:

```bash
pii-guard install <repo>
```

This sets the repository's `git config core.hooksPath` to a hooks directory
owned by the tool. From then on, `git commit` runs the guard and refuses
commits that contain user-specific absolute paths. Because the hook lives
outside the working tree, it is not tracked, not distributed, and cannot be
committed by accident.

## Layer 2 — GitHub-side reusable workflow

GitHub cannot see the local hooks of contributors, so this repository also
ships a reusable workflow:

- **File:** `.github/workflows/path-leak-check.yml`
- **Trigger:** `workflow_call` (reusable) and `workflow_dispatch` (manual)
- **What it does:** scans the **tracked text files** of the calling repository
  with `git grep`, and fails if it finds a user-specific absolute path.

It detects these patterns (POSIX ERE):

| Pattern | Meaning |
|---------|---------|
| `/home/<name>/` | Linux home |
| `/Users/<name>/` | macOS home |
| `C:\Users\<name>\` | Windows home (case-insensitive) |
| `/mnt/<drive>/Users/<name>/` | WSL mount |
| `\\wsl.localhost\<distro>\home\<name>\` | WSL UNC |
| `\\wsl$\<distro>\home\<name>\` | WSL UNC (legacy) |

Generated directories (`node_modules`, `dist`, `build`, `vendor`, `target`)
and non-text files are skipped, and so are the workflow itself and this
document — otherwise the patterns in those files would trip the check.

### Allowlist

The check never fails on obvious placeholders, including:

`<user>`, `<u>`, `<name>`, `user`, `username`, `youruser`, `example`,
`alice`, `bob`, `runner`, `vscode`, `node`, `nonroot`, `$HOME`, `${HOME}`,
`%USERNAME%`, `%USERPROFILE%`, `<%= ... %>`, `{{ ... }}`, `xxxx`, `xxxxx`.

### Opt-out marker

Some documentation must show a realistic example. Add the marker
`path-leak-check:allow` to that line and the line is skipped:

```text
default_home=/home/<user>/project  path-leak-check:allow
```

Use the marker only for documentation that genuinely needs to display an
example. A real path in a real config file is still a leak.

## Opting in from another project

Add this caller workflow to the consuming repository:

```yaml
# .github/workflows/path-leak-guard.yml in the consuming repository
name: Path Leak Guard
on: [push, pull_request]
jobs:
  scan:
    uses: shira022/loop-engineering-template/.github/workflows/path-leak-check.yml@main
```

The reusable workflow is self-contained: the caller does **not** need any
script file, only the snippet above.

> **Until this change is merged**, point the `uses:` ref at the feature
> branch instead of `main`:
> `shira022/loop-engineering-template/.github/workflows/path-leak-check.yml@feature/path-leak-guard`

New projects bootstrapped from this template get the caller workflow
automatically as `.github/workflows/path-leak-guard.yml`, and their local
guard is installed with `pii-guard install <repo>`.

> [← CI/CD Pipelines](ci-cd.md) | [⚡ Quick Reference →](quick-reference.md)
