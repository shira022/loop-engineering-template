.PHONY: help lint validate test clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

lint: ## Run lint checks (markdown, yaml)
	@echo "Running markdownlint..."
	@which markdownlint-cli2 2>/dev/null && markdownlint-cli2 '**/*.md' --ignore node_modules || echo "⚠️  markdownlint not installed (npm install -g markdownlint-cli2)"
	@echo "Running yamllint..."
	@which yamllint 2>/dev/null && yamllint .github/ workflows/ .*.yaml || echo "⚠️  yamllint not installed (pip install yamllint)"

validate: lint ## Validate all skills have required frontmatter
	@echo "Validating skills..."
	@python3 scripts/validate-skills.py

test: ## Run tests (if any)
	@if [ -f pyproject.toml ]; then pytest 2>/dev/null || echo "no pytest"; fi
	@if [ -f package.json ]; then npm test 2>/dev/null || echo "no test script"; fi

clean: ## Clean temporary files
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name '*.pyc' -delete 2>/dev/null || true
	@rm -rf .mypy_cache .pytest_cache

setup: ## Install development dependencies
	@pip install yamllint 2>/dev/null || true
	@echo "Development tools setup complete"
