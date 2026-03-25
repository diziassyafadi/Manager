---
name: new-task
description: Create a new task file in `tasks/` by collecting information from Dizi interactively. Trigger when Dizi says "new task", "create task", "add task", or wants to log a piece of work.
---

Create a new BAU task file in `tasks/` by collecting information from Dizi interactively.

**Argument:** `$ARGUMENTS` (optional — if provided, use it as the task name and skip asking for it)

---

## Steps

### 1. Collect information

Ask Dizi the following questions **one at a time**, waiting for each answer before proceeding.

**Q1 — Task name** (skip if provided as `$ARGUMENTS`):
> What is the task name?

**Q2 — Goal:**
> What is the rough goal of this task? (What needs to be done and why?)

**Q3 — Action items** (optional):
> Are there any specific action items? (Press Enter to skip — Claude will generate them)

**Q4 — Due date** (optional):
> What is the due date? (Format: YYYY-MM-DD, or press Enter to skip)

---

### 2. Generate action items (if Q3 was skipped)

Based on Q2, generate 3–5 concrete SRE-oriented action items:
```
<!-- AI-generated — adjust as needed -->
- [ ] <action item 1>
- [ ] <action item 2>
...
```

---

### 3. Create the task file

Pipe action items to stdin:

```bash
printf '<action items, one per line>' | \
python3 .claude/skills/new-task/scripts/create_task_file.py \
  --title "<title>" \
  --description "<goal from Q2>" \
  [--due <YYYY-MM-DD>]
```

Prints the created file path (e.g. `tasks/2026-03-25-fix-something.md`).

---

### 4. Ask about GitHub sync

> Task file created: `tasks/<filename>`
> Do you want to sync this to GitHub Issues now? (yes/no)

- If **yes**: execute `/sync-issue` inline.
- If **no**: remind Dizi they can run `/sync-issue <filename>` anytime later.
