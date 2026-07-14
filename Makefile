.PHONY: help lint validate test clean setup \
        git-flow-init git-feature-start git-feature-finish \
        git-release-start git-release-finish \
        git-hotfix-start git-hotfix-finish

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-32s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------------------
# Development tools
# ---------------------------------------------------------------------------

lint: ## Run lint checks (markdown, yaml, pre-commit)
	@echo "Running pre-commit hooks..."
	@pre-commit run --all-files 2>/dev/null || echo "pre-commit not installed (pip install pre-commit && pre-commit install)"
	@echo "Running yamllint..."
	@which yamllint 2>/dev/null && yamllint .github/ workflows/ .*.yaml || echo "yamllint not installed (pip install yamllint)"

validate: lint ## Validate all skills have required frontmatter
	@echo "Validating skills..."
	@python3 scripts/validate-skills.py

test: ## Run project tests (language-agnostic)
	@echo "Running tests using project's test runner..."
	@if command -v pytest >/dev/null 2>&1 && [ -f pyproject.toml ]; then \
		python -m pytest tests/ -v; \
	elif command -v npm >/dev/null 2>&1 && [ -f package.json ]; then \
		npm test; \
	elif command -v cargo >/dev/null 2>&1 && [ -f Cargo.toml ]; then \
		cargo test; \
	elif command -v go >/dev/null 2>&1; then \
		go test ./...; \
	else \
		echo "No recognized test runner found. Use your language's native test command."; \
	fi

clean: ## Clean temporary files
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name '*.pyc' -delete 2>/dev/null || true
	@rm -rf .mypy_cache .pytest_cache .ruff_cache node_modules target

setup: ## Install development dependencies
	@pip install yamllint pre-commit 2>/dev/null || true
	@pre-commit install 2>/dev/null || true
	@echo "Development tools setup complete"

# ---------------------------------------------------------------------------
# Git Flow helpers
# ---------------------------------------------------------------------------

git-flow-init: ## Initialize Git Flow in this repository
	@if ! git flow init -d 2>/dev/null; then \
		echo "git-flow not installed. Using defaults:"; \
		git config gitflow.branch.master main; \
		git config gitflow.branch.develop develop; \
		git config gitflow.prefix.feature feature/; \
		git config gitflow.prefix.release release/; \
		git config gitflow.prefix.hotfix hotfix/; \
		git config gitflow.prefix.bugfix bugfix/; \
		echo "Git Flow config set (config only, no branch creation)."; \
		echo "Run 'make git-flow-init' again after installing git-flow for full init."; \
	fi

git-feature-start: ## Start a new feature: make git-feature-start NAME=my-feature
	@if [ -z "$(NAME)" ]; then \
		echo "Usage: make git-feature-start NAME=feature-name"; \
		exit 1; \
	fi
	@git flow feature start $(NAME) || (echo "git-flow not found. Run instead:"; echo "  git checkout develop && git pull && git checkout -b feature/$(NAME)")

git-feature-finish: ## Finish current feature: make git-feature-finish NAME=my-feature
	@if [ -z "$(NAME)" ]; then \
		echo "Usage: make git-feature-finish NAME=feature-name"; \
		echo "Consider creating a PR instead of finishing locally."; \
		exit 1; \
	fi
	@echo "To finish feature/$(NAME):"
	@echo "  1. Create a PR: feature/$(NAME) -> develop"
	@echo "  2. After merge, delete the local branch:"
	@echo "     git branch -d feature/$(NAME)"

git-release-start: ## Start a new release: make git-release-start VERSION=1.0.0
	@if [ -z "$(VERSION)" ]; then \
		echo "Usage: make git-release-start VERSION=1.0.0"; \
		exit 1; \
	fi
	@git flow release start $(VERSION) 2>/dev/null || \
		(git checkout develop && git pull && git checkout -b release/$(VERSION) && \
		 echo "Created release/$(VERSION) from develop")

git-release-finish: ## Finish current release: make git-release-finish VERSION=1.0.0
	@if [ -z "$(VERSION)" ]; then \
		echo "Usage: make git-release-finish VERSION=1.0.0"; \
		echo "Consider creating PRs instead of finishing locally."; \
		exit 1; \
	fi
	@echo "To finish release/$(VERSION):"
	@echo "  1. Create PR: release/$(VERSION) -> main"
	@echo "  2. Create PR: release/$(VERSION) -> develop"
	@echo "  3. After merge, tag the main merge commit:"
	@echo "     git tag -a v$(VERSION) -m 'Release v$(VERSION)' && git push origin v$(VERSION)"

git-hotfix-start: ## Start a hotfix: make git-hotfix-start VERSION=1.0.1
	@if [ -z "$(VERSION)" ]; then \
		echo "Usage: make git-hotfix-start VERSION=1.0.1"; \
		exit 1; \
	fi
	@git flow hotfix start $(VERSION) 2>/dev/null || \
		(git checkout main && git pull && git checkout -b hotfix/$(VERSION) && \
		 echo "Created hotfix/$(VERSION) from main")

git-hotfix-finish: ## Finish hotfix: make git-hotfix-finish VERSION=1.0.1
	@if [ -z "$(VERSION)" ]; then \
		echo "Usage: make git-hotfix-finish VERSION=1.0.1"; \
		echo "Consider creating PRs instead of finishing locally."; \
		exit 1; \
	fi
	@echo "To finish hotfix/$(VERSION):"
	@echo "  1. Create PR: hotfix/$(VERSION) -> main  (urgent review)"
	@echo "  2. Create PR: hotfix/$(VERSION) -> develop"
	@echo "  3. After merge, tag the main merge commit:"
	@echo "     git tag -a v$(VERSION) -m 'Hotfix v$(VERSION)' && git push origin v$(VERSION)"
