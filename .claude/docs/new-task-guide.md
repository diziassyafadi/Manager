# /new-task — Usage Guide

Interactively create a new task file and optionally push it to GitHub Issues.

---

## Usage

```
/new-task [task name]
```

| Form | Behavior |
|---|---|
| `/new-task` | Asks for task name first, then proceeds |
| `/new-task Fix ingress timeout on glchat-be` | Skips the name question, starts from goal |

---

## Interactive Questions

Claude asks these **one at a time**:

| # | Question | Required | Notes |
|---|----------|----------|-------|
| 1 | Task name | Yes | Skipped if passed as argument |
| 2 | Goal / description | Yes | What needs to be done and why |
| 3 | Action items | No | Skip → Claude generates 3–5 suggestions |
| 4 | Due date | No | Format: `YYYY-MM-DD` |

---

## What gets created

A task file at `tasks/YYYY-MM-DD-<slug>.md`:

```yaml
---
title: Fix ingress timeout on glchat-be
status: backlog
created: 2026-03-22
completed: null
due: 2026-03-28
issue: null
parent: null
type: Task
---

**Labels** :
-

# Description and Contexts
<your goal>

# Action Item
- [ ] <your items or AI-generated suggestions>

# Current Issue / Blocker
N/A

# Dependencies (Optional)
N/A

## Result
N/A
```

The slug is derived from the task name: lowercased, spaces replaced with hyphens.

---

## AI-generated action items

If Dizi skips the action items question, Claude generates 3–5 SRE-oriented steps based on the goal. They are marked clearly:

```markdown
<!-- AI-generated — adjust as needed -->
- [ ] Identify the root cause by checking ingress controller logs
- [ ] Update timeout values in the ingress manifest
- [ ] Apply changes to staging and verify
- [ ] Apply to production after confirmation
```

Dizi edits these directly in the file before starting work.

---

## GitHub push prompt

After creating the file, Claude asks:

> Task file created: `tasks/2026-03-22-fix-ingress-timeout.md`
> Do you want to push this to GitHub Issues now? (yes/no)

- **Yes** → Claude runs the `/push-issue` logic inline. Issue is created and `issue:` is written back.
- **No** → Claude reminds Dizi to run `/push-issue <filename>` when ready.

---

## Examples

```
# Start from scratch
/new-task

# Pre-fill the task name
/new-task Update glchat-be replica count for peak traffic

# After creation, push manually later
/push-issue 2026-03-22-update-glchat-be-replica-count.md
```

---

## Notes

- Status always starts as `backlog` — change it when work begins.
- `issue:` and `parent:` are `null` by default; set `parent:` before pushing if this is a sub-issue.
- The session memory (`.claude/.claude-memory.md`) is updated automatically after creation.
