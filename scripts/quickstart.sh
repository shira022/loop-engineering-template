#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# Loop Engineering Template — Quickstart
# =============================================================================
# This script guides you through creating a new project from the
# loop-engineering-template.
#
# Usage:
#   curl -sL https://raw.githubusercontent.com/shira022/loop-engineering-template/main/scripts/quickstart.sh | bash
#
# Or locally:
#   bash scripts/quickstart.sh
# =============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}${BOLD}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}${BOLD}║   🔄 Loop Engineering Template — Quickstart   ║${NC}"
echo -e "${BLUE}${BOLD}╚═══════════════════════════════════════════════╝${NC}"
echo ""

# --- Prerequisites Check ---

echo -e "${YELLOW}Checking prerequisites...${NC}"

check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "  ${RED}❌ $1 not found${NC}"
        return 1
    else
        echo -e "  ${GREEN}✅ $1 found: $($1 --version 2>&1 | head -1)${NC}"
        return 0
    fi
}

PREREQ_OK=true
check_command git || PREREQ_OK=false
check_command gh || PREREQ_OK=false

if [ "$PREREQ_OK" = false ]; then
    echo ""
    echo -e "${RED}❌ Missing required tools. Please install:${NC}"
    echo "  - git: https://git-scm.com/downloads"
    echo "  - gh:  https://cli.github.com/"
    exit 1
fi

# Check gh auth
if ! gh auth status 2>&1 | grep -q "Logged in"; then
    echo -e "  ${RED}❌ gh CLI not authenticated. Run: gh auth login${NC}"
    exit 1
else
    echo -e "  ${GREEN}✅ gh CLI authenticated${NC}"
fi

echo ""
echo -e "${GREEN}✅ All prerequisites met!${NC}"
echo ""

# --- Project Configuration ---

echo -e "${YELLOW}Let's configure your new project.${NC}"
echo ""

read -r -p "$(echo -e "${BOLD}Project name${NC} (e.g., my-awesome-app): ")" PROJECT_NAME
if [ -z "$PROJECT_NAME" ]; then
    echo -e "${RED}❌ Project name is required.${NC}"
    exit 1
fi

read -r -p "$(echo -e "${BOLD}Visibility${NC} (public/private, default: public): ")" VISIBILITY
VISIBILITY="${VISIBILITY:-public}"

read -r -p "$(echo -e "${BOLD}Description${NC} (optional): ")" DESCRIPTION

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}Creating project:${NC}"
echo "  Name:        $PROJECT_NAME"
echo "  Visibility:  $VISIBILITY"
echo "  Description: $DESCRIPTION"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# --- GitHub Repository Creation ---

echo -e "${YELLOW}Creating GitHub repository...${NC}"

TEMPLATE_REPO="shira022/loop-engineering-template"

if [ -n "$DESCRIPTION" ]; then
    gh repo create "$PROJECT_NAME" \
        --template "$TEMPLATE_REPO" \
        --"$VISIBILITY" \
        --description "$DESCRIPTION" \
        --clone
else
    gh repo create "$PROJECT_NAME" \
        --template "$TEMPLATE_REPO" \
        --"$VISIBILITY" \
        --clone
fi

echo -e "${GREEN}✅ Repository created and cloned!${NC}"
echo ""

# --- Next Steps ---

echo -e "${BLUE}${BOLD}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}${BOLD}║   ✅ Project Created Successfully!            ║${NC}"
echo -e "${BLUE}${BOLD}╚═══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Repository: ${GREEN}https://github.com/$(gh api user --jq '.login')/${PROJECT_NAME}${NC}"
echo -e "Local path: ${GREEN}$(pwd)/${PROJECT_NAME}${NC}"
echo ""
echo -e "${BOLD}Next steps:${NC}"
echo ""
echo "  1. cd $PROJECT_NAME"
echo ""
echo "  2. Launch your AI agent and run:"
echo -e "     ${BOLD}\"Bootstrap this project using the project-bootstrapper skill\"${NC}"
echo ""
echo "  3. Or open in VS Code:"
echo "     code $PROJECT_NAME"
echo ""
echo -e "${YELLOW}💡 Tip: Star the template repo if you find it useful!${NC}"
echo -e "${YELLOW}   https://github.com/shira022/loop-engineering-template${NC}"
echo ""
