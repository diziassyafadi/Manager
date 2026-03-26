---
name: sync-issue
description: Sync a local task file to GitHub Issues in gdp-admin/SRE-task. Creates if issue is null, updates if set. Supports comments and PR attachment. Trigger on "push issue", "update issue", "sync issue", "create issue".
---

Sync a task file to GitHub Issues. Auto-detects **create** (`issue: null`) vs **update** (`issue` set).

**Argument:** `$ARGUMENTS` — parse for these optional parts:
- `<filename>` — task file to sync (without `tasks/` prefix)
- `comment: <text>` — post a comment on the issue
- `pr: <url_or_number>` — attach a PR as "Resolved by" comment
- No argument → resolve active task from `.claude/.claude-memory.md`; stop if none found

## Steps

### 1. Parse and validate

```bash
python3 .claude/skills/sync-issue/scripts/parse_task_file.py tasks/<filename>
```

Outputs JSON: `title`, `status`, `due`, `issue`, `parent`, `type`, `state`, `body`, `filename`.

If `issue` is null (new issue), also run: `.claude/scripts/validate-task.sh tasks/<filename>` — stop on failure.

### 2. Create or update issue

Read `.claude/.env` for `GITHUB_ISSUE_ASSIGNEES`.

**Create** (`issue` is null) → `mcp__github__issue_write` method `create`:
  owner=`gdp-admin`, repo=`SRE-task`, title, body, type from JSON, assignees from env.
  Then write `issue: <number>` back to the task file frontmatter.

**Update** (`issue` is set) → `mcp__github__issue_write` method `update`:
  Same fields + `issue_number` + `state` from JSON.
  If status=`done`, also set `completed: <today>` in task file frontmatter.

### 3. Sync project fields

```bash
python3 .claude/skills/sync-issue/scripts/sync_project.py <issue_number> <status> [--due <date>] [--parent <issue_number>]
```

Syncs to GitHub Projects v2: status, due date, and parent field (if configured in config JSON).

### 4. Link sub-issue (optional, if using GitHub issue links)

If organizing via GitHub issue links (separate from Projects field sync):
Use `node_id` from step 3 output.
`mcp__github__sub_issue_write` method `add`: owner=`gdp-admin`, repo=`SRE-task`, issue_number=`<parent>`, sub_issue_id=`<node_id>`, replace_parent=true.

### 5. Post comment (if `comment:` in args)

`mcp__github__add_issue_comment`: owner=`gdp-admin`, repo=`SRE-task`, issue_number, body=comment text.

### 6. Attach PR (if `pr:` in args)

Full URL → use as-is. Number only → ask Dizi for full URL.
`mcp__github__add_issue_comment` body: `Resolved by: [PR #<N>](<url>)`

### 7. Confirm

```
✓ Issue #<N> <created|updated> → https://github.com/gdp-admin/SRE-task/issues/<N>
  ↳ Project: Status=<status>, Due=<due or "not set">, Parent=<parent or "not set">
  ↳ Comment posted             ← if applicable
  ↳ PR attached: <url>         ← if applicable
```
