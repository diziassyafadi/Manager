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
| `/import-github-issue diziassyafadi` | List open issues assigned to user, pick one |

---

## What it does

1. Fetches the issue from GitHub (including Projects v2 status)
2. Maps the issue content to the standard task file format
3. Creates `tasks/YYYY-MM-DD-<slug>.md`
4. Updates `.claude/.claude-memory.md` with the new task

The `issue:` frontmatter field is set automatically — the task is already linked to GitHub.

---

## Field mapping

| GitHub Issue | Task File |
|---|---|
| Title | `title` |
| Projects v2 Status | `status` |
| Body `> **Due:** YYYY-MM-DD` | `due` |
| Body sections | Mapped 1:1 (Description, Action Item, Blocker, Dependencies) |
| Issue number | `issue` |
| Issue state `closed` | `status: done` + `completed: <today>` |

If the issue body doesn't use the standard format, the full body is placed under `# Description and Contexts`.

---

## After importing

Run `/sync-issue` to sync any local changes back to GitHub. No need for a separate push — the issue number is already set.

---

## Duplicate protection

If a local task file already has `issue: <number>`, Claude will ask before overwriting.
