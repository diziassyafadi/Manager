# /import-github-issue — Usage Guide

Import an existing GitHub Issue from `gdp-admin/SRE-task` into a local task file.

---

## Usage

```
/import-github-issue <issue-number-or-url>
```

| Form | Behavior |
|---|---|
| `/import-github-issue 3435` | Import issue #3435 |
| `/import-github-issue https://github.com/GDP-ADMIN/SRE-task/issues/3435` | Same, from URL |

---

## What it does

1. Fetches the issue from GitHub
2. Maps the issue content to the standard task file format
3. Creates `tasks/YYYY-MM-DD-<slug>.md`
4. Updates `.claude/.claude-memory.md` with the new task

The `issue:` frontmatter field is set automatically — the task is already linked to GitHub from the start.

---

## Field mapping

| GitHub Issue | Task File |
|---|---|
| Title | `title` |
| Labels (`backlog`, `in-progress`, etc.) | `status` |
| Body `> **Due:** YYYY-MM-DD` | `due` |
| Body `# Description and Contexts` section | Same section |
| Body `# Action Item` section | Same section |
| Body `# Current Issue / Blocker` section | Same section |
| Body `# Dependencies (Optional)` section | Same section |
| Issue number | `issue` |
| Issue state `closed` | `status: done` + `completed: <today>` |

If the issue body doesn't use the standard format, the full body is placed under `# Description and Contexts`.

---

## When to use

- You were assigned a GitHub Issue that doesn't have a local task file yet
- You want to track an existing issue locally for session context
- You're picking up work that was created outside the `/new-task` flow

---

## After importing

Run `/update-issue` to sync any local changes back to GitHub.
Run `/push-issue` is **not needed** — the issue number is already set.

---

## Duplicate protection

If a local task file already has `issue: <number>`, Claude will ask before overwriting.

---

## Examples

```
# Import by number
/import-github-issue 3400

# Import by URL (useful when copying from browser)
/import-github-issue https://github.com/GDP-ADMIN/SRE-task/issues/3400

# Then start working and sync changes
/update-issue 2026-03-22-<slug>.md
```
