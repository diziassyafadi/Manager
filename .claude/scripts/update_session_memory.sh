#!/usr/bin/env bash
# update_session_memory.sh — Hook: upsert a task entry in .claude/.claude-memory.md
# Triggered after any Write to tasks/*.md
#
# Claude Code hook env vars used:
#   CLAUDE_FILE_PATHS — space-separated list of files written in this tool call
#
# Usage (manual): update_session_memory.sh tasks/2026-03-25-some-task.md

set -euo pipefail

MEMORY_FILE=".claude/.claude-memory.md"

# Determine file list: prefer hook env var, fall back to $1
if [[ -n "${CLAUDE_FILE_PATHS:-}" ]]; then
    IFS=' ' read -ra FILES <<< "$CLAUDE_FILE_PATHS"
else
    FILES=("${1:-}")
fi

for TASK_FILE in "${FILES[@]}"; do
    # Only process files under tasks/ with .md extension
    [[ "$TASK_FILE" =~ ^tasks/[^/]+\.md$ ]] || continue
    [[ -f "$TASK_FILE" ]] || continue

    # Parse frontmatter fields
    title=$(grep -m1 '^title:' "$TASK_FILE" | sed 's/^title: *//' | xargs)
    status=$(grep -m1 '^status:' "$TASK_FILE" | sed 's/^status: *//' | xargs)
    issue=$(grep -m1 '^issue:' "$TASK_FILE" | sed 's/^issue: *//' | xargs)

    [[ -n "$title" && -n "$status" ]] || continue

    filename=$(basename "$TASK_FILE")

    # Build the entry line
    if [[ "$issue" == "null" || -z "$issue" ]]; then
        entry="- [${filename}](${TASK_FILE}) — ${title} (\`${status}\`)"
    else
        entry="- [${filename}](${TASK_FILE}) — ${title} (\`${status}\`, #${issue})"
    fi

    # Ensure memory file and Active Tasks section exist
    if [[ ! -f "$MEMORY_FILE" ]]; then
        printf '# Claude Session Memory\n\n## Active Tasks\n\n' > "$MEMORY_FILE"
    fi
    if ! grep -q '^## Active Tasks' "$MEMORY_FILE"; then
        printf '\n## Active Tasks\n\n' >> "$MEMORY_FILE"
    fi

    # Remove stale entry for this filename (if any), then insert fresh one
    # Use a temp file to avoid in-place sed portability issues
    tmpfile=$(mktemp)
    grep -v "\[${filename}\]" "$MEMORY_FILE" > "$tmpfile"

    # Insert after "## Active Tasks" header
    awk -v entry="$entry" '
        /^## Active Tasks/ { print; print entry; next }
        { print }
    ' "$tmpfile" > "$MEMORY_FILE"

    rm -f "$tmpfile"
done
