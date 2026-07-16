#!/usr/bin/env bash
# =============================================================================
# Agent Runner — Execute agent tasks in CI
# =============================================================================
# This script executes agent tasks using the specified agent backend.
# It's used by the Agent Harness workflow and can also be used locally.
#
# Usage:
#   bash scripts/agent-runner.sh <agent-type> <task-description>
#
# Examples:
#   bash scripts/agent-runner.sh opencode "Run knowledge-harvest"
#   bash scripts/agent-runner.sh hermes "Create a new skill from pattern X"
# =============================================================================
set -euo pipefail

AGENT="${1:-}"
TASK="${2:-}"

if [ -z "$AGENT" ] || [ -z "$TASK" ]; then
    echo "Usage: $0 <agent-type> <task-description>"
    echo "  agent-type: opencode, hermes, claude, stub"
    exit 1
fi

BRANCH="agent/$(whoami)/$(date +%s)"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_FILE="/tmp/agent-runner-${TIMESTAMP}.log"

echo "╔═══════════════════════════════════════════════╗"
echo "║   🤖 Agent Runner                            ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""
echo "  Agent:      $AGENT"
echo "  Task:       $TASK"
echo "  Branch:     $BRANCH"
echo "  Log file:   $LOG_FILE"
echo ""

# Create task description file
mkdir -p .agent
cat > ".agent/task-${TIMESTAMP}.md" << TASKEOF
# Agent Task

$TASK

## Rules
- Follow the project's AGENTS.md rules
- Run knowledge-harvest after complex tasks
- Record ADR for architectural decisions
- Update learnings/ with new insights
TASKEOF

echo "  ✅ Task file created at .agent/task-${TIMESTAMP}.md"

# Create branch
git checkout -b "$BRANCH" 2>&1 | tail -1
echo "  ✅ Branch created: $BRANCH"

# Run the agent
case "$AGENT" in
    opencode)
        echo "  🚀 Running Opencode..."
        if command -v opencode &> /dev/null; then
            opencode --task "$TASK" --output "$LOG_FILE" 2>&1 | tee -a "$LOG_FILE"
            EXIT_CODE=$?
        else
            echo "  ⚠️  Opencode not installed. Running in stub mode."
            echo "  [STUB] Would run: opencode --task \"$TASK\"" >> "$LOG_FILE"
            EXIT_CODE=0
        fi
        ;;

    hermes)
        echo "  🚀 Running Hermes Agent..."
        if command -v hermes &> /dev/null; then
            hermes run "$TASK" --log "$LOG_FILE" 2>&1 | tee -a "$LOG_FILE"
            EXIT_CODE=$?
        else
            echo "  ⚠️  Hermes not installed. Running in stub mode."
            echo "  [STUB] Would run: hermes run \"$TASK\"" >> "$LOG_FILE"
            EXIT_CODE=0
        fi
        ;;

    claude)
        echo "  🚀 Running Claude Code..."
        if command -v claude &> /dev/null; then
            claude "$TASK" 2>&1 | tee -a "$LOG_FILE"
            EXIT_CODE=$?
        else
            echo "  ⚠️  Claude Code not installed. Running in stub mode."
            echo "  [STUB] Would run: claude \"$TASK\"" >> "$LOG_FILE"
            EXIT_CODE=0
        fi
        ;;

    stub)
        echo "  🚀 Running in stub mode (no agent backend required)..."
        echo "  [STUB] Simulating agent execution for: $TASK" >> "$LOG_FILE"
        echo "  [STUB] Completed successfully." >> "$LOG_FILE"
        EXIT_CODE=0
        ;;

    *)
        echo "  ❌ Unknown agent type: $AGENT"
        echo "     Supported: opencode, hermes, claude, stub"
        exit 1
        ;;
esac

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "  ✅ Agent completed successfully (exit code: $EXIT_CODE)"
else
    echo "  ❌ Agent failed (exit code: $EXIT_CODE)"
    tail -20 "$LOG_FILE"
    exit $EXIT_CODE
fi

# Show summary
echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║   ✅ Agent Run Complete                       ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""
echo "  Agent:      $AGENT"
echo "  Task:       $TASK"
echo "  Branch:     $BRANCH"
echo "  Log:        $LOG_FILE"
echo "  Status:     $([ $EXIT_CODE -eq 0 ] && echo '✅ Success' || echo '❌ Failed')"
echo ""
