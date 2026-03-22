---
name: push-issue
description: Push a local task file to GitHub Issues in gdp-admin/SRE-task. Trigger when Dizi says "push issue", "push to GitHub", "create issue", or "sync task to GitHub".
---

Push the task file to GitHub Issues in `gdp-admin/SRE-task`.

**Argument:** `$ARGUMENTS`
- If a filename is provided (e.g., `2026-03-22-fix-ingress.md`), use `tasks/$ARGUMENTS`.
- If no argument is provided, read `.claude/.claude-memory.md` to find the active task filename and use that.
- Stop immediately and tell Dizi if no active task is found in memory and no argument was given.

---

## Configuration

- **Project config:** `.claude/config/github-projects.json` — contains project IDs, field IDs, and status option IDs. Look up the entry by repo name (e.g., `SRE-task`).
- **Auth:** `.claude/.env` — contains `GITHUB_PAT`. Read this file at the start and extract the token value. Never log or print the token.

---

## Steps

### 1. Load config and credentials

- Read `.claude/config/github-projects.json` and load the `SRE-task` entry.
- Read `.claude/.env` and extract the value of `GITHUB_PAT`. Store it as `PAT` for use in all curl commands below.

### 2. Validate

Run `.claude/scripts/validate-task.sh tasks/<filename>`.
If it exits non-zero, print the errors and stop — do not push to GitHub.

### 3. Parse the task file

**Frontmatter fields to extract:**
- `title` — required
- `status` — required
- `due` — optional; include in issue body if present
- `issue` — if present, this is an update; if absent, this is a create
- `parent` — optional; GitHub issue number of parent issue
- `type` — optional; defaults to `Task`

**Body sections to extract (preserve content exactly as written):**
- `**Labels** :` block (the list items below it, until the next section)
- `# Description and Contexts` (content until next `#` section)
- `# Action Item` (content until next `#` section)
- `# Current Issue / Blocker` (content until next `#` section)
- `# Dependencies (Optional)` (content until next `#` section, or `N/A` if section absent)

Do NOT extract or push the `## Result` section — it is local only.

### 4. Map status to GitHub state

Status is managed exclusively in GitHub Projects v2 — never via labels.

| Task status   | GitHub state |
|---------------|-------------|
| `backlog`     | open        |
| `ready`       | open        |
| `in-progress` | open        |
| `in-review`   | open        |
| `done`        | closed      |
| `on-hold`     | open        |

### 5. Build the GitHub issue body

Use this exact format:

```
**Labels** :

- <label items from task body>

# Description and Contexts

<content from task>

> **Due:** <due date from frontmatter, or omit this line if not set>

# Action Item

<content from task>

# Current Issue / Blocker

<content from task>

# Dependencies (Optional)

<content from task, or N/A>
```

### 6. Create or update the issue

**If `issue` is absent (new issue):**
- Call `mcp__github__issue_write` with method `create`:
  - `owner`: `gdp-admin`
  - `repo`: `SRE-task`
  - `title`: from frontmatter
  - `body`: built in step 5
  - `type`: from frontmatter (default: `Task`)
  - `assignees`: from config (`["diziassyafadi"]`)
- After creation, write `issue: <number>` back to the task file frontmatter using the Edit tool.

**If `issue` is present (existing issue):**
- Call `mcp__github__issue_write` with method `update`:
  - Same fields as above, plus `issue_number`: the existing issue number
  - `state`: `open` or `closed` per status mapping
  - `assignees`: from config

### 7. Sync to GitHub Project

Using the project config loaded in step 1 (`project_id`, field IDs, status option IDs) and `PAT` from `.claude/.env`:

**7a. Get the issue node ID:**
```bash
curl -s https://api.github.com/repos/GDP-ADMIN/SRE-task/issues/<issue_number> \
  -H "Authorization: bearer <PAT>" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['node_id'])"
```
Store the result as `ISSUE_NODE_ID`.

**7b. Add issue to the project:**
```bash
curl -s -X POST https://api.github.com/graphql \
  -H "Authorization: bearer <PAT>" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"mutation { addProjectV2ItemById(input: {projectId: \\\"<project_id>\\\", contentId: \\\"<ISSUE_NODE_ID>\\\"}) { item { id } } }\"}"
```
Extract `data.addProjectV2ItemById.item.id` from the response — store as `ITEM_ID`.
If the item already exists in the project, the mutation still succeeds and returns the existing item ID.

**7c. Set the Status field:**

Look up the `status_option_id` from `config.fields.status.options[<task_status>]`.

```bash
curl -s -X POST https://api.github.com/graphql \
  -H "Authorization: bearer <PAT>" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"mutation { updateProjectV2ItemFieldValue(input: {projectId: \\\"<project_id>\\\", itemId: \\\"<ITEM_ID>\\\", fieldId: \\\"<status_field_id>\\\", value: {singleSelectOptionId: \\\"<status_option_id>\\\"}}) { projectV2Item { id } } }\"}"
```

**7d. Set the Due Date field (only if `due` is set in frontmatter):**
```bash
curl -s -X POST https://api.github.com/graphql \
  -H "Authorization: bearer <PAT>" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"mutation { updateProjectV2ItemFieldValue(input: {projectId: \\\"<project_id>\\\", itemId: \\\"<ITEM_ID>\\\", fieldId: \\\"<due_date_field_id>\\\", value: {date: \\\"<YYYY-MM-DD>\\\"}}) { projectV2Item { id } } }\"}"
```

### 8. Link as sub-issue (if `parent` is set)

- The `parent` field contains a GitHub issue number.
- Get the node ID of the newly created/updated issue (reuse `ISSUE_NODE_ID` from step 7a).
- Call `mcp__github__sub_issue_write` with method `add`:
  - `owner`: `gdp-admin`
  - `repo`: `SRE-task`
  - `issue_number`: value of `parent` field
  - `sub_issue_id`: `ISSUE_NODE_ID`
  - `replace_parent`: `true` (in case it was previously linked elsewhere)

### 9. Confirm

Print a one-line confirmation:
```
✓ Issue #<number> <created|updated> → https://github.com/gdp-admin/SRE-task/issues/<number>
  ↳ Synced to project #361 (Status: <status>, Due: <due date or "not set">)
```
If sub-issue was linked:
```
  ↳ Linked as sub-issue of #<parent>
```
