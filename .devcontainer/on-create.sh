#!/bin/bash
set -e
echo "🔧 Loop Engineering Dev Container Setup"
git config --global user.name "${GIT_USER_NAME:-Developer}"
git config --global user.email "${GIT_USER_EMAIL:-dev@example.com}"
git config --global init.defaultBranch main
if [ -f pyproject.toml ]; then pip install -e ".[dev]" 2>/dev/null || true; fi
pre-commit install 2>/dev/null || true
if command -v gh &> /dev/null; then gh auth status 2>/dev/null || echo "⚠️  gh CLI not authenticated"; fi
echo "✅ Dev Container setup complete!"
