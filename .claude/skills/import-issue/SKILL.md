---
name: import-issue
description: Import a GitHub Issue from gdp-admin/SRE-task into a local task file. Trigger when Dizi says "import issue", "pull issue from GitHub", "create local task from issue", or provides a GitHub issue number or URL.
---

Import a GitHub Issue into a local `tasks/` file.

**Argument:** `$ARGUMENTS` — issue number (e.g., `3435`) or full GitHub URL (e.g., `https://github.com/GDP-ADMIN/SRE-task/issues/3435`).

---

## Steps

### 1. Parse issue number from argument

- If argument is a full GitHub URL, extract the number from the path.
- If argument is a plain number, use it directly.
- If no argument, ask: "Which issue number do you want to import?"

### 2. Check for existing local task

Search `tasks/` for any file containing `issue: <number>` in frontmatter.
- If found, tell Dizi: "Issue #<number> is already tracked locally as `<filename>`. Overwrite? (yes/no)"
- If no, stop.

### 3. Fetch the issue

Call `mcp__github__issue_read` with method `get` — `owner`: `gdp-admin`, `repo`: `SRE-task`, `issue_number`: parsed number.

### 4. Map issue fields to task format

**Title:** use the issue title directly.

**Status:** status is always read from GitHub Projects v2 — never from labels.

1. If issue state is `closed` → `done`
2. Otherwise query GitHub Projects v2:
   - Load config from `.claude/config/github-projects.json` and `.claude/.env` (`GITHUB_PAT` as `PAT`)
   - **Get issue node ID:**
     ```bash
     curl -s https://api.github.com/repos/GDP-ADMIN/SRE-task/issues/<issue_number> \
       -H "Authorization: bearer <PAT>" \
       | python3 -c "import sys,json; print(json.load(sys.stdin)['node_id'])"
     ```
   - **Query project status:**
     ```bash
     curl -s -X POST https://api.github.com/graphql \
       -H "Authorization: bearer <PAT>" \
       -H "Content-Type: application/json" \
       -d '{"query":"{ node(id: \"<ISSUE_NODE_ID>\") { ... on Issue { projectItems(first: 10) { nodes { project { number } fieldValues(first: 20) { nodes { ... on ProjectV2ItemFieldSingleSelectValue { name field { ... on ProjectV2SingleSelectField { name } } } } } } } } } }"}'
     ```
   - Filter for the project with `project_number: 361`, find the `Status` field value, and reverse-map the option name to task status (case-insensitive match against option keys in `config.fields.status.options`)
   - If no match → default to `backlog`

**Due date:** scan issue body for the line `> **Due:** YYYY-MM-DD`. If found, extract it; otherwise `null`.

**Labels block:** extract from `**Labels** :` section in body if present; otherwise default to `- Operational`.

**Body sections:** attempt to parse known sections from the body:
- `# Description and Contexts` → use content if found
- `# Action Item` → use content if found
- `# Current Issue / Blocker` → use content if found
- `# Dependencies (Optional)` → use content if found

If the issue body does not follow the expected format, put the full body under `# Description and Contexts` and leave other sections as `N/A`.

**Type:** use issue type from the GitHub issue if present; otherwise `Task`.

**Completed date:** if issue state is `closed`, set `completed` to the creation date of the task file (today). Otherwise `null`.

### 5. Generate filename

- Slug: lowercase title, spaces → hyphens, strip special characters, truncate to 60 chars.
- Filename: `<today's date>-<slug>.md`
- Path: `tasks/<filename>`

### 6. Write the task file

```markdown
---
title: <title>
status: <mapped status>
created: <today's date>
completed: <completed date or null>
due: <due date or null>
issue: <issue number>
parent: null
type: <type>
---

<**Labels** : block>

# Description and Contexts
<content>

# Action Item
<content>

# Current Issue / Blocker
<content>

# Dependencies (Optional)
<content>

## Result
N/A
```

### 7. Update session memory

Add to `.claude/.claude-memory.md` under **Active Tasks**:
```
- [<filename>](tasks/<filename>) — <title> (`<status>`, #<issue>)
```

### 8. Confirm

```
✓ Issue #<number> imported → tasks/<filename>
  Title:  <title>
  Status: <status>
  Due:    <due date or "not set">
```
