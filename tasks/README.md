# Task Tracking

This folder contains markdown files documenting Dizi's BAU (Business As Usual) and project tasks.

## Structure

- Flat structure with date-prefixed filenames: `YYYY-MM-DD-<slug>.md`
- Each file follows the template defined in `.claude/rules/task-workflow.md`
- Files in this folder serve as the base for weekly report generation

## Statuses

| Status        | Meaning                              |
| ------------- | ------------------------------------ |
| `backlog`     | Created but might need more context  |
| `ready`       | Defined but not yet started          |
| `in-progress` | Currently being worked on            |
| `in-progress` | Finished and currently on review     |
| `done`        | Completed and verified               |
| `on hold`     | Waiting on external input or blocker |

## Usage

- Claude creates a task file when Dizi assigns work
- Claude updates the file as work progresses
- Weekly reports are generated from task files grouped by week
