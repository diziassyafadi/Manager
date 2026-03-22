#!/usr/bin/env bash
# validate-task.sh — Validates a task file before pushing to GitHub Issues
# Usage: validate-task.sh <path-to-task-file>
# Exit 0: valid. Exit 1: invalid (prints error).

set -euo pipefail

TASK_FILE="${1:-}"

if [[ -z "$TASK_FILE" ]]; then
  echo "ERROR: No task file provided." >&2
  echo "Usage: validate-task.sh <path-to-task-file>" >&2
  exit 1
fi

if [[ ! -f "$TASK_FILE" ]]; then
  echo "ERROR: File not found: $TASK_FILE" >&2
  exit 1
fi

ERRORS=()

# Check frontmatter delimiter
if ! head -1 "$TASK_FILE" | grep -q '^---$'; then
  ERRORS+=("Missing opening frontmatter delimiter (---)")
fi

# Required frontmatter fields
for field in title status created; do
  if ! grep -q "^${field}:" "$TASK_FILE"; then
    ERRORS+=("Missing required frontmatter field: '${field}'")
  fi
done

# Validate status value
STATUS=$(grep '^status:' "$TASK_FILE" | head -1 | sed 's/status: *//' | tr -d '"'"'" | xargs)
VALID_STATUSES="backlog ready in-progress in-review done on-hold"
if [[ -n "$STATUS" ]] && ! echo "$VALID_STATUSES" | grep -qw "$STATUS"; then
  ERRORS+=("Invalid status '${STATUS}'. Must be one of: ${VALID_STATUSES}")
fi

# Required body sections
for section in "# Description and Contexts" "# Action Item" "# Current Issue / Blocker"; do
  if ! grep -qF "$section" "$TASK_FILE"; then
    ERRORS+=("Missing required section: '${section}'")
  fi
done

# Report
if [[ ${#ERRORS[@]} -gt 0 ]]; then
  echo "VALIDATION FAILED: $TASK_FILE" >&2
  for err in "${ERRORS[@]}"; do
    echo "  - $err" >&2
  done
  exit 1
fi

echo "OK: $TASK_FILE"
exit 0
