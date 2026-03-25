# Claude Code Skills for SRE Apps

## Overview

A set of Claude Code skills and configuration for managing SRE BAU tasks through:
- **Local task files** (`tasks/YYYY-MM-DD-<slug>.md`) as the source of truth
- **GitHub Issues sync** (`GDP-ADMIN/SRE-task`) via GitHub Projects v2
- **Weekly reports** generated from task history + Google Calendar events

---

## 🗂 Task Management

### File Structure

```
Manager/
├── tasks/                        # BAU task markdown files
│   └── YYYY-MM-DD-<slug>.md
└── .claude/
    ├── .env                      # GITHUB_PAT, GITHUB_ISSUE_ASSIGNEES
    ├── .env.example
    ├── .claude-memory.md         # Active session context (gitignored)
    ├── config/
    │   └── github-projects.json  # GitHub Projects v2 field IDs
    ├── skills/                   # Claude Code skill definitions
    │   ├── new-task/SKILL.md
    │   ├── push-issue/SKILL.md
    │   ├── update-issue/SKILL.md
    │   ├── import-github-issue/SKILL.md
    │   └── weekly-report/SKILL.md
    ├── docs/                     # Skill usage guides
    ├── rules/                    # Operational rules for Claude
    ├── scripts/
    │   └── validate-task.sh      # Pre-push task file validator
    └── report/                   # Generated weekly reports
```

### Task File Template

```markdown
---
title: <task title>
status: backlog | ready | in-progress | in-review | done | on-hold
created: YYYY-MM-DD
completed: YYYY-MM-DD | null
due: YYYY-MM-DD | null
issue: null            # written back by /push-issue
parent: null           # parent GitHub issue number
type: Task             # Task | Bug | Feature
---

**Labels** :
- some_label

# Description and Contexts
# Action Item
- [ ] some_action

# Current Issue / Blocker
# Dependencies (Optional)

## Result
<!-- Local only — not pushed to GitHub -->
```

---

## 🤖 Skills

| Skill | Trigger | What it does |
|-------|---------|--------------|
| `/new-task` | `new-task [name]` | Interactive task creation + optional GitHub push |
| `/push-issue` | `push-issue [file]` | Creates/updates GitHub Issue + syncs to Projects v2 |
| `/update-issue` | `update-issue [file] [comment: ...] [pr: ...]` | Syncs task changes back to GitHub, posts comments |
| `/import-github-issue` | `import-github-issue <issue-number-or-url>` | Pulls GitHub Issue into local task file |
| `/weekly-report` | `weekly-report [date]` | Generates weekly report from tasks + calendar events |

See `.claude/docs/` for detailed usage guides for each skill.

---

## 🔧 Environment Setup

### 1. Configure credentials

```bash
cp .claude/.env.example .claude/.env
```

```ini
GITHUB_PAT=your_github_personal_access_token
GITHUB_ISSUE_ASSIGNEES=your_github_username
```

Required GitHub PAT scopes: `repo`, `project`

### 2. GitHub MCP (for push-issue / update-issue / import-github-issue)

```bash
claude mcp add --scope project github-mcp https://api.githubcopilot.com/mcp/
```

## 🚀 Workspace MCP — Quick Start (Claude Code)

This guide sets up **Google Workspace MCP** with:
- `uvx` runtime
- auto-start via systemd
- Claude Code integration

---

## 🧱 1. Prepare OAuth Credentials

From Google Cloud Console:

- Create OAuth Client (**Desktop App**)
- Copy:
  - `GOOGLE_OAUTH_CLIENT_ID`
  - `GOOGLE_OAUTH_CLIENT_SECRET`

---

## 📁 2. Create environment file

```bash
mkdir -p ~/.config/workspace-mcp
nano ~/.config/workspace-mcp/.env
```

Paste this
```.env
GOOGLE_OAUTH_CLIENT_ID=your_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret
OAUTHLIB_INSECURE_TRANSPORT=1
```

## ⚙️ 3. Install uv (includes uvx)
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Verify:
```
which uvx
```

## 🧩 4. Create startup script and systemd
```bash
nano ~/.local/bin/workspace-mcp-start
```

```sh
#!/usr/bin/env bash

set -a
source ~/.config/workspace-mcp/.env
set +a

exec /home/YOUR_USERNAME/.local/bin/uvx workspace-mcp \
  --tool-tier core \
  --transport streamable-http
```

Make executable:
```bash
chmod +x ~/.local/bin/workspace-mcp-start
```

Create systemd
```bash
sudo nano /etc/systemd/system/workspace-mcp.service
```

```ini
[Unit]
Description=Google Workspace MCP Server
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
ExecStart=/home/YOUR_USERNAME/.local/bin/workspace-mcp-start
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

## 5. Run the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable workspace-mcp
sudo systemctl start workspace-mcp
```

## 6. Connect to Claude Code

```bash
claude mcp add --transport http workspace-mcp http://127.0.0.1:8000/mcp

# on the project `.claude/`
claude mcp add --scope project --transport http workspace-mcp http://127.0.0.1:8000/mcp
```