---
name: import-github-issue
description: Imports a GitHub Issue into a local task file in tasks/. Triggers when Dizi says "import issue", "pull issue from GitHub", "create local task from issue", provides a GitHub issue number, URL, or assignee username.
---

Import a GitHub issue into `tasks/`.

**Argument:** `$ARGUMENTS` — issue number, full URL, or assignee username. No argument → ask.

## Steps

### 1. Parse argument
- URL → extract number from `.../issues/<N>`
- Number → use directly
- Username → list issues: `python3 .claude/skills/import-github-issue/scripts/list_issues.py <username>` → present numbered list, ask which to import

### 2. Check duplicate
`grep -rl "issue: <number>" tasks/` — if found, ask to overwrite; stop if no.

### 3. Fetch, parse, write
```bash
python3 .claude/skills/import-github-issue/scripts/fetch_issue.py <number> \
  | python3 .claude/skills/import-github-issue/scripts/parse_issue_body.py \
  | python3 .claude/skills/import-github-issue/scripts/generate_task_file.py
```
Prints created file path (e.g. `tasks/2026-03-24-some-slug.md`).

### 4. Confirm
```
✓ Issue #<N> imported → tasks/<filename>
  Title: <title> | Status: <status> | Due: <due or "not set">
```

## Config
- `.claude/config/github-projects.json` — owner, repo, project config
- `.claude/.env` — `GITHUB_PAT`, `GITHUB_ISSUE_REPO`, `GITHUB_ORG`
- Scripts default to `GITHUB_ISSUE_REPO`; pass `--repo <key>` to override
