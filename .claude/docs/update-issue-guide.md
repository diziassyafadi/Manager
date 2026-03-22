# /update-issue — Usage Guide

Sync a local task file back to its GitHub Issue (body + project fields) and optionally post a comment or attach a resolving PR.

---

## Usage

```
/update-issue [filename] [comment: <text>] [pr: <url_or_number>]
```

All parts are optional and combinable.

| Form | Behavior |
|---|---|
| `/update-issue` | Full sync of active task (body + project fields) |
| `/update-issue 2026-03-22-fix-ingress.md` | Full sync of specific task |
| `/update-issue comment: Fixed the timeout issue` | Add comment to active task's issue (no body sync) |
| `/update-issue 2026-03-22-fix-ingress.md comment: Done` | Sync + add comment |
| `/update-issue pr: 42` | Attach resolving PR to active task (no body sync) |
| `/update-issue pr: https://github.com/.../pull/42` | Same, using full URL |
| `/update-issue 2026-03-22-fix-ingress.md pr: 42` | Sync + attach PR |
| `/update-issue 2026-03-22-fix-ingress.md comment: Done pr: 42` | Sync + comment + attach PR |

---

## What it does

1. Reads the current task file content
2. Updates the GitHub Issue body to match the file (title, description, action items, etc.)
3. Updates GitHub state (`open`/`closed`) and labels to match the task status
4. Syncs project #361 fields: **Status** and **Due Date**
5. Optionally posts a comment
6. Optionally posts a "Resolved by: PR #N" comment when `pr:` is provided

---

## When to use

- After checking off action items in the task file
- After changing the status (e.g., `backlog` → `in-progress`)
- After adding a blocker or dependency
- To post a progress update or completion note as a comment
- To link the PR that closes the issue (use `pr:`)

---

## PR attachment

When `pr:` is provided, a comment is posted on the issue:

```
Resolved by: [PR #42](https://github.com/gdp-admin/SRE-task/pull/42)
```

Accepted PR value formats:
- Full URL: `https://github.com/gdp-admin/gl-sre-fluffy-barnacle/pull/42`
- Number only: `42` or `#42` (resolved against `gdp-admin/SRE-task`)

---

## Status sync behavior

| Task file status | GitHub Issue | Project Status |
|-----------------|-------------|----------------|
| `backlog` | open + label `backlog` | Backlog |
| `in-progress` | open + label `in-progress` | In Progress |
| `in-review` | open + label `in-review` | In Review |
| `done` | **closed** | Done |
| `on-hold` | open + label `on-hold` | On Hold |

Setting `done` also writes `completed: <today>` back to the task file.

---

## Difference from /push-issue

| | `/push-issue` | `/update-issue` |
|---|---|---|
| Creates new issue | ✓ | ✗ |
| Updates existing issue | ✓ | ✓ |
| Adds comment | ✗ | ✓ |
| Attaches PR | ✗ | ✓ |
| Links sub-issue | ✓ | ✗ |

Use `/push-issue` for the first push. Use `/update-issue` for all subsequent syncs.

---

## Examples

```
# Sync after marking action items done
/update-issue

# Sync a specific task file
/update-issue 2026-03-22-exploration-claude-skills.md

# Post completion note
/update-issue comment: All three skills implemented and tested. Closing.

# Close issue and link the resolving PR
/update-issue 2026-03-22-exploration-claude-skills.md pr: 88

# Sync + post blocker note
/update-issue 2026-03-20-cert-rotation.md comment: Blocked by prod access — raised with security team.

# Full combo: sync + close note + PR
/update-issue 2026-03-22-exploration-claude-skills.md comment: Rolled out to prod. pr: 88
```
