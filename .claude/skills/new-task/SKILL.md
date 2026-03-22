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

### 2. Generate the slug and filename

- Slug: lowercase task name, spaces → hyphens, strip special characters
  - Example: "Fix ingress timeout on glchat-be" → `fix-ingress-timeout-on-glchat-be`
- Filename: `<today's date>-<slug>.md`
  - Example: `2026-03-22-fix-ingress-timeout-on-glchat-be.md`
- Path: `tasks/<filename>`

---

### 3. Generate action items (if Q3 was skipped)

Based on the goal from Q2, generate 3–5 concrete, SRE-oriented action items as a checklist. These are suggestions — Dizi will adjust them manually if needed.

Label them clearly:
```
<!-- AI-generated — adjust as needed -->
- [ ] <action item 1>
- [ ] <action item 2>
...
```

---

### 4. Create the task file

Write the file to `tasks/<filename>` using this exact template:

```markdown
---
title: <task name from Q1>
status: backlog
created: <today's date YYYY-MM-DD>
completed: null
due: <due date from Q4, or null>
issue: null
parent: null
type: Task
---

**Labels** :
- 

# Description and Contexts
<goal from Q2>

# Action Item
<action items from Q3, or AI-generated items from step 3>

# Current Issue / Blocker
N/A

# Dependencies (Optional)
N/A

## Result
N/A
```

---

### 5. Update session memory

Add the new task to `.claude/.claude-memory.md` under **Active Tasks**:
```
- [<filename>](tasks/<filename>) — <title> (`backlog`)
```

---

### 6. Ask about GitHub push

After confirming the file was created, ask:

> Task file created: `tasks/<filename>`
> Do you want to push this to GitHub Issues now? (yes/no)

- If **yes**: execute the `/push-issue` skill logic inline (do not ask Dizi to run it separately).
- If **no**: remind Dizi they can run `/push-issue <filename>` anytime later.
