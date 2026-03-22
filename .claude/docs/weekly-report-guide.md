# /weekly-report — Usage Guide

Generate a weekly work report as a markdown file in `.claude/report/`.

---

## Usage

```
/weekly-report [date]
```

| Form | Behavior |
|---|---|
| `/weekly-report` | Uses the most recent "[Fill Weekly Report: ...]" email to determine the week range |
| `/weekly-report 2026-03-17` | Uses the email whose week range contains March 17, 2026 |
| `/weekly-report 2026-03-16 2026-03-22` | Explicit date range (skips Gmail lookup) |

---

## What it does

1. Determines the week range from Gmail (subject line of the weekly report notification email)
2. Scans `tasks/*.md` files and categorizes tasks by status
3. Fetches Google Calendar events for the week
4. Asks Dizi for optional inputs (key metrics, OOO, articles)
5. Writes a markdown report to `.claude/report/<WEEK_START>_<WEEK_END>.md`

---

## Output location

```
.claude/report/2026-03-22_2026-03-28.md
```

Dizi copies the content into the Google Doc manually.

---

## Report structure

```markdown
# [Weekly Report: Raden Dizi Assyafadi Putra] DD Month YYYY - DD Month YYYY

## Issues
## Accomplishments
## Meetings/Events/Training/Conferences
## Key Metrics / OMTM
## Next Actions
## Technology, Business, Communication, Leadership, Management & Marketing
## Out of Office
```

Sections with no data show `(please insert here)` as a placeholder.

---

## Task categorization rules

| Bucket | Criteria |
|--------|----------|
| Accomplishments (Done) | `status: done` AND `completed` within the week |
| Accomplishments (In Progress) | `status: in-progress` or `in-review` |
| Next Actions | `status: ready`, `in-progress`, or `in-review` |
| Issues | Blocker section is not `N/A`, AND task is in Accomplishments or created within the week |

---

## Calendar event filtering

Included: meetings, standups, training, conferences, notable external events.
Excluded: personal block-time, recurring placeholders (e.g., "Busy", "Focus Time", "Lunch Time").

---

## Examples

```
# Current week report (uses most recent email)
/weekly-report

# Report for week containing a specific date
/weekly-report 2026-03-17

# Explicit date range
/weekly-report 2026-03-16 2026-03-22
```
