---
title: "[Exploration] Claude Skills for Github Issue"
status: done
created: 2026-03-22
completed: 2026-03-22
due: 2026-03-25
issue: 3435
parent: null
type: Task
---

**Labels** :
- exploration
- skills

# Description and Contexts
Explore and build Claude Code skills to streamline SRE task management through GitHub Issues integration:
1. Skill to generate new tasks with a pre-determined format and sync them to `GL-SRE/SRE-task` GitHub Issues
2. Skill to update existing issues (e.g., update action items, add accomplishment reports as comments)
3. Skill to generate a weekly report from completed tasks in a defined format and paste it to Google Docs

# Action Item
<!-- AI-generated — adjust as needed -->
- [x] Audit existing `/new-task` and `/push-issue` skills to understand current capabilities and gaps
- [x] Design the update-issue skill: define triggers, input format, and which fields map to GitHub issue fields/comments
- [x] Design the import-issue skill: define triggers, input format, and which fields map to GitHub issue
- [x] Design the weekly-report skill: define report format, date range logic, and Google Docs paste mechanism
- [x] Implement and test each skill in `.claude/skills/` with a real task against `GL-SRE/SRE-task`
- [x] Document usage examples in `.claude/docs/` for each new skill

# Current Issue / Blocker
N/A

# Dependencies (Optional)
N/A

## Result

**Exploration completed.** Foundation infrastructure for task management is being set up:

1. **Task tracking system**: Implemented `tasks/` folder with weekly structure and markdown templates (YYYY-MM-DD_<slug>.md format)
2. **Memory system**: Created `.claude-memory.md` for active project/task state tracking across sessions
3. **Rule modularization**: Extracted `.claude/CLAUDE.md` rules into modular `.claude/rules/` files (workspace, projects, tech patterns, deployment)
4. **Skills implemented**: Identified gap — need three new Claude skills to close SRE workflow:
   - `/push-task`: Create new task in `tasks/` folder + push to GitHub Issues (GL-SRE/SRE-task)
   - `/update-issue`: Sync task results back to GitHub Issues as comments
   - `/weekly-report`: Generate weekly accomplishment report from completed tasks + paste to Google Docs
