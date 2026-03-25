---
name: weekly-report
description: Generate a weekly work report from local task files in a standard format. Trigger when Dizi says "weekly report", "generate weekly report", "weekly recap", or "what did I do this week".
---

Generate a weekly report markdown file in `report/` from task files and Google Calendar, then publish it as a formatted Google Doc.

**Argument:** `$ARGUMENTS`
- No argument → use the most recent "[Fill Weekly Report: ...]" email to determine the week range
- `YYYY-MM-DD` → use the email whose week range contains that date
- `YYYY-MM-DD YYYY-MM-DD` → explicit start and end date range (skip Gmail lookup)

---

## Steps

### 1. Determine the week range

**If no explicit date range was given**, find the week range via Gmail:

Call `mcp__workspace-mcp__search_gmail_messages`:
- `user_google_email`: `raden.d.a.putra@gdplabs.id`
- `query`: `subject:"Fill Weekly Report:" in:inbox`
- `page_size`: 5

Select the most recent result (or the one whose subject date range contains the argument date).

Call `mcp__workspace-mcp__get_gmail_message_content` with that message ID to read the email body.
Extract the date range from the subject line (e.g., `"22 March 2026 - 28 March 2026"`).
Parse → `WEEK_START` (YYYY-MM-DD) and `WEEK_END` (YYYY-MM-DD).

> If no email is found and no argument date range was given, stop and ask Dizi for the date range.

Print: `Generating report for: WEEK_START → WEEK_END`

### 2. Scan task files

Read all `*.md` files in `tasks/` (skip `README.md`). For each file parse:
- Frontmatter: `title`, `status`, `created`, `completed`, `due`, `issue`
- Section: `# Current Issue / Blocker`

Categorize into buckets:

| Bucket | Criteria |
|--------|----------|
| **Accomplishments (Done)** | `status: done` AND `completed` is within `WEEK_START`–`WEEK_END` |
| **Accomplishments (In Progress)** | `status: in-progress` or `in-review` |
| **Next Actions** | `status: ready`, `in-progress`, or `in-review` |
| **Issues** | `# Current Issue / Blocker` is NOT `N/A`, AND task is in Accomplishments or has `created` within the week range |

### 3. Get Google Calendar events

Call `mcp__workspace-mcp__get_events`:
- `user_google_email`: `raden.d.a.putra@gdplabs.id`
- `time_min`: `<WEEK_START>T00:00:00+07:00`
- `time_max`: `<WEEK_END>T23:59:59+07:00`
- `max_results`: 50

Filter: keep only events that represent meetings, standups, training, conferences, or notable external events. Exclude personal block-time or recurring placeholder events (e.g., "Busy", "Focus Time", "Lunch Time").

Format each kept event as: `<Event Name> (<Day, DD MMM YYYY>)`

### 4. Prompt user for optional data

Ask Dizi the following in a single message before proceeding:

```
Before I generate the report, I need a few optional inputs:

1. Key Metrics — provide a value for each or leave as "-":
   • Individual average response time (e.g., 0.3)
   • Team average response time (e.g., 0.7)

2. Out of Office — any OOO during WEEK_START – WEEK_END?
   If yes, provide the date range (e.g., "March 25–26").
   If no, say "none".

3. Articles for "Technology, Business, Communication, Leadership, Management & Marketing" section?
   If yes, provide one per line as: Headline | https://article-url
   If no, say "none".
```

Wait for Dizi's reply before proceeding to step 5.

### 5. Build and write the markdown report

Write the report to `report/<WEEK_START>_<WEEK_END>.md` using the template below.

For each section:
- If there is data, fill it in with the appropriate format.
- If there is no data, put `(please insert here)` as the content so Dizi can fill it manually.

```markdown
# [Weekly Report: Raden Dizi Assyafadi Putra] <DD Month YYYY> - <DD Month YYYY>

## Issues

<issues_content OR (please insert here)>

## Accomplishments

<accomplishments_content OR (please insert here)>

## Meetings/Events/Training/Conferences

<meetings_content OR (please insert here)>

## Key Metrics / OMTM

<metrics_content OR (please insert here)>

## Next Actions

<next_actions_content OR (please insert here)>

## Technology, Business, Communication, Leadership, Management & Marketing

<articles_content OR (please insert here)>

## Out of Office

<ooo_content OR (please insert here)>
```

**Section content formats:**

**Issues** (if blockers exist):
```
- <Task Title> — <first non-empty line of blocker section>
```

**Accomplishments**:
```
Done:
- <Task Title> — https://github.com/gdp-admin/SRE-task/issues/<issue>

In Progress / In Review:
- <Task Title> — https://github.com/gdp-admin/SRE-task/issues/<issue>
```
Omit the GitHub link if `issue` is null. Omit a sub-section header if it has no entries.

**Meetings/Events/Training/Conferences**:
```
- <Event Name> (<Day, DD MMM YYYY>)
```

**Key Metrics / OMTM**:
```
Ticket response time in a week within 0.5 hour.
- Average individual response time: <individual_time> / 0.5 hour
- Average team response time: <team_time> / 0.8 hour.
```
Use `-` for any value Dizi did not provide.

**Next Actions**:
```
- <Task Title> (Status: <status>, Due: <due or "not set">)
```

**Technology, Business, Communication, Leadership, Management & Marketing**:
```
- <Headline> — <URL>
```

**Out of Office**: date range string (e.g., `March 25–26, 2026`).

### 6. Publish to Google Docs

Call `mcp__workspace-mcp__import_to_google_doc`:
- `user_google_email`: `raden.d.a.putra@gdplabs.id`
- `file_name`: `Weekly Report Dizi — <WEEK_START> to <WEEK_END>`
- `content`: the full markdown string written in step 5
- `source_format`: `md`

This converts the markdown to a formatted Google Doc (headings, bullets, bold preserved).

### 7. Confirm

```
Report generated → report/<WEEK_START>_<WEEK_END>.md
Google Doc → <link returned by import_to_google_doc>
Week: WEEK_START → WEEK_END
Sections filled: <list sections that were written>
Sections skipped (no data): <list sections left as placeholder>
```
