---
description: How Claude manages tasks in tasks/ and updates .claude/.claude-memory.md
globs: *
---

## Task Workflow

Dizi tracks operation(BAU) and project tasks as markdown files in `tasks/`.

### File Naming Convention

Flat structure with date prefix: `YYYY-MM-DD-<slug>.md`

Example: `2026-03-22-update-glchat-replicas.md`

### Task File Template

```markdown
---
title: <task title>
status: backlog | ready | in-progress | in-review | done | on-hold
created: YYYY-MM-DD
completed: YYYY-MM-DD | null
due: YYYY-MM-DD | null  # Due date — shown in GitHub issue body
issue: null             # GitHub issue number — written back by /push-issue
parent: null            # GitHub issue number of the parent issue (for sub-issues)
type: Task              # Task | Bug | Feature
---

**Labels** :
<!-- Tags related to the task (e.g. project name, service, domain) -->
- some_label

# Description and Contexts
<!-- What needs to be done and why -->
<description>

# Action Item
<!-- Required steps as a checklist -->
- [ ] some_action

# Current Issue / Blocker
<!-- Active blockers or issues. Put N/A if none -->
N/A

# Dependencies (Optional)
<!-- Related issues, PRs, or tasks. Put N/A if none -->
N/A

## Result
<!-- Outcome and how it was verified — NOT pushed to GitHub, local only -->
N/A
```

### Frontmatter Fields

| Field       | Required | Description |
|-------------|----------|-------------|
| `title`     | Yes      | Task title — becomes GitHub issue title |
| `status`    | Yes      | Current status (see mapping below) |
| `created`   | Yes      | Creation date |
| `completed` | Yes      | Completion date or `null` |
| `due`       | No       | Due date — shown in GitHub issue body |
| `issue`     | No       | Written by `/push-issue` after creation |
| `parent`    | No       | Parent issue number — links this as a sub-issue |
| `type`      | No       | Issue type: `Task` (default), `Bug`, `Feature` |

### Status → GitHub Mapping

| Status       | GitHub State | Label applied  |
|-------------|--------------|----------------|
| `backlog`   | open         | `backlog`      |
| `ready`     | open         | `ready`        |
| `in-progress` | open       | `in-progress`  |
| `in-review` | open         | `in-review`    |
| `done`      | closed       | _(none)_       |
| `on-hold`   | open         | `on-hold`      |

### Claude's Responsibilities

- When Dizi assigns a task, Claude creates a task file in `tasks/` before starting work
- Claude updates the task file as work progresses (status, action items, blockers)
- Claude marks the task `done` and fills in the Result section upon completion
- Claude keeps `.claude/.claude-memory.md` in sync with active/completed tasks
- Claude never modifies the `issue` field manually — it is written back by `/push-issue`
