#!/usr/bin/env bash
# =============================================================================
# /goal: Run-Until-Done Loop
# =============================================================================
# Implements the /goal pattern described in loop engineering:
#   "keeps working across turns until a verifiable stopping condition holds,
#    with a separate verifier checking the stop condition."
#
# Usage:
#   bash scripts/goal-loop.sh \
#     --goal "Make all tests in test/auth pass" \
#     --stop-condition "All tests in test/auth pass and lint is clean" \
#     --max-iterations 10 \
#     --work-dir .
#
# The implementer and verifier are called through the configured agent.
# The verifier uses a SEPARATE check (implementer cannot grade itself).
# =============================================================================

set -euo pipefail

# ---- Defaults ----
MAX_ITERATIONS=10
WORK_DIR="."
AGENT_CMD="opencode"
VERIFIER_CMD="opencode"
ITERATION=0
STATE_FILE=""

# ---- Parse args ----
while [[ $# -gt 0 ]]; do
    case "$1" in
        --goal) GOAL="$2"; shift 2 ;;
        --stop-condition) STOP_CONDITION="$2"; shift 2 ;;
        --max-iterations) MAX_ITERATIONS="$2"; shift 2 ;;
        --work-dir) WORK_DIR="$2"; shift 2 ;;
        --agent) AGENT_CMD="$2"; shift 2 ;;
        --verifier) VERIFIER_CMD="$2"; shift 2 ;;
        --state-file) STATE_FILE="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

if [[ -z "${GOAL:-}" || -z "${STOP_CONDITION:-}" ]]; then
    echo "Usage: $0 --goal <goal> --stop-condition <condition> [--max-iterations N] [--work-dir DIR]"
    echo "  --goal              What to achieve (e.g., 'Make all tests pass')"
    echo "  --stop-condition    Verifiable condition that ends the loop"
    echo "  --max-iterations    Max loop iterations (default: 10)"
    echo "  --work-dir          Working directory (default: .)"
    echo "  --agent             Agent command (default: opencode)"
    echo "  --verifier          Verifier command (default: opencode)"
    echo "  --state-file        Optional: file path to persist state between runs"
    exit 1
fi

STATE_FILE="${STATE_FILE:-$(pwd)/STATE.md}"

echo "=============================================="
echo "  /goal Loop"
echo "=============================================="
echo "  Goal:           $GOAL"
echo "  Stop condition: $STOP_CONDITION"
echo "  Max iterations: $MAX_ITERATIONS"
echo "  Work dir:       $WORK_DIR"
echo "  Agent:          $AGENT_CMD"
echo "  Verifier:       $VERIFIER_CMD"
echo "  State file:     $STATE_FILE"
echo "=============================================="

cd "$WORK_DIR"

while [[ $ITERATION -lt $MAX_ITERATIONS ]]; do
    ITERATION=$((ITERATION + 1))
    echo ""
    echo "--- Iteration $ITERATION/$MAX_ITERATIONS ---"

    # ---- Step 1: Check if already done ----
    if [[ -f "$STATE_FILE" ]]; then
        echo "Checking state file for previous progress..."
    fi

    # ---- Step 2: Implementer takes the next step ----
    echo "[implementer] Working toward goal..."
    $AGENT_CMD --task "
    Goal: $GOAL
    
    Current iteration: $ITERATION of $MAX_ITERATIONS
    
    Stop condition (do NOT check this — the verifier will):
    $STOP_CONDITION
    
    Take the next logical step toward the goal. Do NOT check the stop
    condition — a separate verifier agent will determine when done.
    Write tests. Check for regressions.
    " 2>&1 || echo "[implementer] warning: exit code $?"

    # ---- Step 3: Verifier checks the stop condition ----
    echo ""
    echo "[verifier] Checking stop condition..."
    VERIFIER_OUTPUT=$($VERIFIER_CMD --task "
    Check whether this stop condition is TRUE or FALSE:
    
    $STOP_CONDITION
    
    Investigate thoroughly:
    1. Run all relevant tests
    2. Check lint/format
    3. Verify the condition literally
    
    Respond with EXACTLY one line at the end:
    VERDICT: PASS (if condition is met)
    VERDICT: FAIL (if condition is NOT met)
    
    If FAIL, explain what's still needed.
    " 2>&1 || true)
    
    echo "$VERIFIER_OUTPUT"
    
    # ---- Step 4: Check verdict ----
    if echo "$VERIFIER_OUTPUT" | grep -q "VERDICT: PASS"; then
        echo ""
        echo "=============================================="
        echo "  ✅ GOAL ACHIEVED after $ITERATION iteration(s)"
        echo "=============================================="
        
        # Update state file
        if [[ -f "$STATE_FILE" ]]; then
            sed -i "s/Last updated:.*/Last updated: $(date -u '+%Y-%m-%dT%H:%M:%SZ')/" "$STATE_FILE"
            sed -i "s/\*\*Open items:\*\*.*/**Open items:** 0/" "$STATE_FILE"
        fi
        
        exit 0
    fi
    
    # ---- Step 5: Check for max iterations ----
    if [[ $ITERATION -ge $MAX_ITERATIONS ]]; then
        echo ""
        echo "=============================================="
        echo "  ⚠️  MAX ITERATIONS ($MAX_ITERATIONS) REACHED"
        echo "  Goal was NOT fully achieved."
        echo "=============================================="
        echo ""
        echo "What was accomplished:"
        echo "  (review the output above)"
        echo ""
        echo "What remains:"
        echo "$VERIFIER_OUTPUT" | grep -A 10 "VERDICT: FAIL" || true
        
        # Inbox the item
        INBOX_DIR="$(dirname "$STATE_FILE")/inbox"
        mkdir -p "$INBOX_DIR"
        INBOX_FILE="$INBOX_DIR/goal-unfinished-$(date +%F).md"
        cat > "$INBOX_FILE" <<- EOF
# $(date +%F): /goal unfinished after $MAX_ITERATIONS iterations

## Goal
$GOAL

## Stop Condition
$STOP_CONDITION

## What was achieved
See iteration logs above.

## What remains
$(echo "$VERIFIER_OUTPUT" | grep -A 10 "VERDICT: FAIL" || echo "Check verifier output")

## Suggested next step
Investigate why the stop condition was not met and consider:
1. Breaking the goal into smaller sub-goals
2. Providing more context to the implementer
3. Fixing the issue manually
EOF
        echo "📥 Unfinished goal sent to inbox: $INBOX_FILE"
        exit 1
    fi
    
    echo ""
    echo "[verifier] Condition not yet met. Starting next iteration..."
    echo ""
done
