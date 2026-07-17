# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- (no unreleased changes yet)

## [v0.4.0] - 2026-07-17

### Added
- GitHub Pages docsify documentation site with automated deployment workflow
- Open in Codespaces badge in README (English and Japanese)
- OpenSSF Scorecard CI workflow + badge
- Documentation badge linking to GitHub Pages
- "Generated from loop-engineering-template" badge auto-insertion in project-bootstrapper
- AGENTS.md Star Support section (English + Japanese)
- GitHub Discussions enabled

### Changed
- README badges: 6 → 9 (added Scorecard, Docs, Codespaces)
- CI/CD pipeline tables: added Scorecard + Pages entries
- project-bootstrapper: Step 5 new (badge insertion), Steps 6-9 renumbered

## [v0.3.0] - 2026-07-16

### Added
- feat: complete loop engineering implementation (6 building blocks)
- Sub-agent system: provider-agnostic explorer/implementer/verifier roles
- Automation schedules: .agents/config/schedules.yaml with 4 schedule definitions
- Triage skill: automation-callable CI triage with inbox routing
- Triage inbox: unresolvable items routed to human review
- State spine: STATE.md for cross-session progress tracking
- Worktree isolation pattern for single-repo sub-agent execution
- /goal run-until-done loop with separate verifier stop-condition check
- Quickstart guide: 15-minute setup from zero to first loop
- Safety warnings in all 9 skills
- Linear + Slack MCP connector configs
- Config validation: scripts/validate-configs.py + CI integration

### Changed
- agent-harness.yml: added scheduled cron trigger (weekdays 07:00 UTC)
- All 8 skills: added Loop Safety sections
- CI: added validate-configs step
- README/AGENTS.md: updated for new components

## [v0.2.0] - 2026-07-16

### Added
- Initial template release with 7 skills
- Git Flow branching strategy
- CI/CD workflows (CI, CodeQL, Dependency Review, Release)
- AGENTS.md with loop engineering rules
- ADR system with decision-recorder skill
- pre-commit hooks configuration
- CONTRIBUTING.md with full Git Flow guide
- SECURITY.md with vulnerability reporting SLA
- project-bootstrapper skill for new project creation
- project-manager skill for multi-project task management
- Dev Container configuration
- MCP (Model Context Protocol) configuration
- Skill evaluation harness with run-evals.py
- test-policy skill for enforcing test coverage
- Makefile with development and Git Flow targets

### Fixed
- Removed duplicate version fields in decision-recorder, session-reviewer, project-bootstrapper
- Missing evals/evals.json for project-bootstrapper, project-manager, skill-crafter, test-policy

## [v0.1.0] - 2026-07-10

### Added
- Initial scaffold of the loop-engineering-template repository
- Directory structure and foundational configuration
