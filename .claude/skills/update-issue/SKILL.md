---
name: update-issue
description: Sync a local task file to its GitHub Issue and optionally add a comment. Trigger when Dizi says "update issue", "sync issue", "add comment to issue", or "update GitHub issue".
---

Sync the task file to its GitHub Issue (body + project fields) and optionally post a comment or attach a resolving PR.

**Argument:** `$ARGUMENTS`

Argument forms:
- No argument → sync active task from `.claude/.claude-memory.md`
- `<filename>` → sync that specific task file
- `<filename> comment: <text>` → sync + post the given text as a comment
- `comment: <text>` → post comment on active task's issue (skip body sync)
- `<filename> pr: <pr_url_or_number>` → sync + attach PR as a "Resolved by" comment
- `pr: <pr_url_or_number>` → attach PR to active task's issue (skip body sync)
- Arguments can be combined: `<filename> comment: <text> pr: <pr_url_or_number>`

---

## Configuration

- **Project config:** `.claude/config/github-projects.json` — project IDs and field IDs
- **Auth:** `.claude/.env` — `GITHUB_PAT`. Read at start, never log.

---

## Steps

### 1. Load config and credentials

- Read `.claude/config/github-projects.json` and load the `SRE-task` entry.
- Read `.claude/.env` and extract `GITHUB_PAT` as `PAT`.

### 2. Resolve the task file

- If no filename in argument: read `.claude/.claude-memory.md` to find the active task filename.
- Stop and tell Dizi if no active task is found and no filename was given.
- Confirm the task has an `issue:` number set. If not, tell Dizi to run `/push-issue` first.

### 3. Parse the task file

Same fields as `/push-issue`:
- Frontmatter: `title`, `status`, `due`, `issue`, `parent`, `type`
- Body sections: `**Labels** :`, `# Description and Contexts`, `# Action Item`, `# Current Issue / Blocker`, `# Dependencies (Optional)`
- Do NOT push the `## Result` section.

### 4. Determine mode from argument

Parse the argument for the following optional components:
- `comment: <text>` → extract comment text; flag `HAS_COMMENT = true`
- `pr: <value>` → extract PR value (URL or number); flag `HAS_PR = true`
- Remaining token (if any) → task filename

Modes:
- **Sync mode** (default when a filename is given, or no special prefix): perform steps 5 and 6.
- **Comment-only mode** (`comment:` with no filename and no `pr:`): skip to step 7.
- **PR-only mode** (`pr:` with no filename and no `comment:`): skip to step 8.
- Any combination of sync + comment + PR runs all applicable steps.

### 5. Sync issue body and state

Call `mcp__github__issue_write` with method `update`:
- `owner`: `gdp-admin`
- `repo`: `SRE-task`
- `issue_number`: from frontmatter
- `title`: from frontmatter
- `body`: rebuild using the same format as `/push-issue` step 5
- `state`: `open` or `closed` per status mapping (status is managed in Projects v2 — never via labels)
- `assignees`: from config

| Task status   | GitHub state |
|---------------|-------------|
| `backlog`     | open        |
| `ready`       | open        |
| `in-progress` | open        |
| `in-review`   | open        |
| `done`        | closed      |
| `on-hold`     | open        |

If status changed to `done`, also set `completed: <today's date>` in the task file frontmatter.

### 6. Sync GitHub Project fields

Using `PAT` and project config:

**6a. Get issue node ID:**
```bash
curl -s https://api.github.com/repos/GDP-ADMIN/SRE-task/issues/<issue_number> \
  -H "Authorization: bearer <PAT>" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['node_id'])"
```

**6b. Add to project (idempotent — safe to call even if already in project):**
```bash
curl -s -X POST https://api.github.com/graphql \
  -H "Authorization: bearer <PAT>" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"mutation { addProjectV2ItemById(input: {projectId: \\\"<project_id>\\\", contentId: \\\"<ISSUE_NODE_ID>\\\"}) { item { id } } }\"}"
```
Extract `data.addProjectV2ItemById.item.id` → `ITEM_ID`.

**6c. Set Status field** (look up option ID from `config.fields.status.options[<task_status>]`):
```bash
curl -s -X POST https://api.github.com/graphql \
  -H "Authorization: bearer <PAT>" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"mutation { updateProjectV2ItemFieldValue(input: {projectId: \\\"<project_id>\\\", itemId: \\\"<ITEM_ID>\\\", fieldId: \\\"<status_field_id>\\\", value: {singleSelectOptionId: \\\"<status_option_id>\\\"}}) { projectV2Item { id } } }\"}"
```

**6d. Set Due Date** (only if `due` is set):
```bash
curl -s -X POST https://api.github.com/graphql \
  -H "Authorization: bearer <PAT>" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"mutation { updateProjectV2ItemFieldValue(input: {projectId: \\\"<project_id>\\\", itemId: \\\"<ITEM_ID>\\\", fieldId: \\\"<due_date_field_id>\\\", value: {date: \\\"<YYYY-MM-DD>\\\"}}) { projectV2Item { id } } }\"}"
```

### 7. Post comment (if `HAS_COMMENT`)

Call `mcp__github__add_issue_comment`:
- `owner`: `gdp-admin`
- `repo`: `SRE-task`
- `issue_number`: from frontmatter
- `body`: the comment text from argument

### 8. Attach PR (if `HAS_PR`)

Normalize the PR value:
- If it is a full URL (`https://github.com/<owner>/<repo>/pull/<N>`) → use as-is; extract `<N>` for display
- If it is a number only (`42` or `#42`) → stop and ask Dizi for the full PR URL, as the repo cannot be inferred

Call `mcp__github__add_issue_comment`:
- `owner`: `gdp-admin`
- `repo`: `SRE-task`
- `issue_number`: from frontmatter
- `body`:
  ```
  Resolved by: [PR #<number>](<pr_url>)
  ```

### 9. Confirm

```
✓ Issue #<number> updated → https://github.com/gdp-admin/SRE-task/issues/<number>
  ↳ Status: <status> | Due: <due date or "not set">
  ↳ Comment posted       ← only if HAS_COMMENT
  ↳ PR attached: <url>   ← only if HAS_PR
```
