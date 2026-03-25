---
name: import-github-issue
description: Imports a GitHub Issue into a local task file in tasks/. Triggers when Dizi says "import issue", "pull issue from GitHub", "create local task from issue", provides a GitHub issue number, URL, or assignee username.
---

Import a GitHub issue into `tasks/` as a local task file.

**Argument:** issue number (e.g. `3435`), full GitHub URL, or assignee username (e.g. `diziassyafadi`).

---

## Workflow

### 1. Parse argument

- Full URL → extract number from path (`.../issues/<number>`)
- Plain number → use directly
- Assignee username → run [Assignee flow](#assignee-flow) below
- No argument → ask: "Which issue number do you want to import?"

### 2. Check for duplicate

```bash
grep -rl "issue: <number>" tasks/
```

If found, ask: "Issue #<number> already exists as `<filename>`. Overwrite? (yes/no)" — stop if no.

### 3. Fetch issue

```bash
python3 .claude/skills/import-github-issue/scripts/fetch_issue.py <number>
```

Outputs JSON with: `number`, `title`, `body`, `state`, `status`, `type`, `node_id`, `owner`, `repo`.

### 4. Parse body

```bash
python3 .claude/skills/import-github-issue/scripts/fetch_issue.py <number> \
  | python3 .claude/skills/import-github-issue/scripts/parse_issue_body.py \
  > /tmp/issue_parsed.json
```

Adds: `description`, `action_item`, `blocker`, `dependencies`, `labels`, `due`.

### 5. Write task file

```bash
python3 .claude/skills/import-github-issue/scripts/generate_task_file.py \
  < /tmp/issue_parsed.json
```

Prints the created file path (e.g. `tasks/2026-03-24-<slug>.md`).

### 6. Update session memory

Add to `.claude/.claude-memory.md` under **Active Tasks**:
```
- [<filename>](tasks/<filename>) — <title> (`<status>`, #<issue>)
```

### 7. Confirm

```
✓ Issue #<number> imported → tasks/<filename>
  Title:  <title>
  Status: <status>
  Due:    <due or "not set">
```

---

## Assignee flow

```bash
python3 .claude/skills/import-github-issue/scripts/list_issues.py <username>
```

Outputs a JSON array of `{ number, title, state, labels }`. Present as a numbered list and ask which issue to import, then resume from step 3.

---

## Config & env

- Config: `.claude/config/github-projects.json` — owner, repo, project_number, status option IDs
- Env: `.claude/.env` — `GITHUB_PAT`, `GITHUB_ISSUE_REPO` (config key, e.g. `SRE-task`), `GITHUB_ORG`
- Scripts default to `GITHUB_ISSUE_REPO` for the config key — pass `--repo <key>` to override
