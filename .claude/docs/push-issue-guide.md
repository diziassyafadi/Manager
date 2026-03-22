# /push-issue — Usage Guide

Sync a local task file to GitHub Issues in `gdp-admin/SRE-task`.

---

## Usage

```
/push-issue [filename]
```

| Form | Behavior |
|---|---|
| `/push-issue` | Uses the active task from `.claude/.claude-memory.md` |
| `/push-issue 2026-03-22-fix-ingress.md` | Uses the specified task file |

The filename is relative to `tasks/` — just the filename, no path needed.

---

## What it does

1. Validates the task file structure
2. Creates a new GitHub issue if the task has no `issue:` field yet
3. Updates the existing issue if `issue:` is already set
4. Writes the issue number back to the task file (`issue: 3456`)
5. Links the issue as a sub-issue if `parent:` is set

---

## Task File Frontmatter

```yaml
---
title: Fix ingress timeout on glchat-be
status: in-progress
created: 2026-03-22
completed: null
issue: null        # auto-filled by /push-issue on first run
parent: null       # set to a GitHub issue number to make this a sub-issue
type: Task         # Task | Bug | Feature  (default: Task)
---
```

### Field reference

| Field    | Who sets it | Notes |
|----------|-------------|-------|
| `title`  | Dizi / Claude | Required. Becomes the issue title |
| `status` | Claude | Drives GitHub state + label |
| `issue`  | `/push-issue` | Never edit manually |
| `parent` | Dizi | Set before first push to link as sub-issue |
| `type`   | Dizi | Defaults to `Task` if omitted |

---

## Status → GitHub Mapping

| Task status   | GitHub state | Label      |
|---------------|-------------|------------|
| `backlog`     | open        | `backlog`  |
| `ready`       | open        | `ready`    |
| `in-progress` | open        | `in-progress` |
| `in-review`   | open        | `in-review` |
| `done`        | closed      | —          |
| `on-hold`     | open        | `on-hold`  |

Running `/push-issue` after changing status from `in-progress` to `done` will close the issue automatically.

---

## Parent / Sub-issue

To make a task a sub-issue of an existing parent issue:

1. Set `parent: <issue-number>` in the task frontmatter before the first push:
   ```yaml
   parent: 3430
   ```
2. Run `/push-issue` — Claude creates the issue and links it under issue #3430.

To create a parent issue first:
1. Create and push the parent task (no `parent` field).
2. Note its issue number from the confirmation output.
3. Create child tasks with `parent: <that number>`.

---

## Examples

```
# Push active task (from memory)
/push-issue

# Push a specific task by filename
/push-issue 2026-03-22-fix-ingress-timeout.md

# After updating status to done in the file, sync to close the issue
/push-issue 2026-03-22-fix-ingress-timeout.md
```

---

## Validation

The skill runs `.claude/scripts/validate-task.sh` before touching GitHub. It checks:
- File exists
- Required frontmatter: `title`, `status`, `created`
- Valid status value
- Required body sections: `# Description and Contexts`, `# Action Item`, `# Current Issue / Blocker`

Fix any reported errors before re-running.

---

## Notes

- The `## Result` section in the task file is **never pushed** to GitHub — it's local context only.
- Re-running `/push-issue` on an already-pushed task is safe — it updates the issue in place.
- `parent` linking only runs once (on create). To re-link, do it manually on GitHub.
