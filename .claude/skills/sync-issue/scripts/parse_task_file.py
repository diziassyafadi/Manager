#!/usr/bin/env python3
"""Parse a task markdown file into JSON for GitHub sync.

Usage:
    python3 parse_task_file.py <task_file_path>

Output: JSON to stdout with fields:
    title, status, due, issue, parent, type, state, body, filename
"""
import json
import re
import sys

STATUS_TO_STATE = {
    "backlog": "open", "ready": "open", "in-progress": "open",
    "in-review": "open", "done": "closed", "on-hold": "open",
}

BODY_SECTIONS = [
    ("labels", r"\*\*Labels\*\*\s*:\s*\n((?:-\s*.+\n?)+)"),
    ("description", r"# Description and Contexts\s*\n([\s\S]*?)(?=\n#\s|\Z)"),
    ("action_item", r"# Action Item\s*\n([\s\S]*?)(?=\n#\s|\Z)"),
    ("blocker", r"# Current Issue / Blocker\s*\n([\s\S]*?)(?=\n#\s|\Z)"),
    ("dependencies", r"# Dependencies(?:\s*\(Optional\))?\s*\n([\s\S]*?)(?=\n(?:##?\s)|\Z)"),
]


def parse_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        print("ERROR: no frontmatter found", file=sys.stderr)
        sys.exit(1)
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            v = v.strip().strip("\"'")
            fm[k.strip()] = None if v == "null" else v
    return fm, text[m.end():]


def build_issue_body(sections, due):
    """Build the GitHub issue body from extracted sections."""
    parts = []
    if sections.get("labels"):
        parts.append(f"**Labels** :\n\n{sections['labels']}")
    parts.append(f"# Description and Contexts\n\n{sections.get('description', 'N/A')}")
    if due:
        parts.append(f"> **Due:** {due}")
    parts.append(f"# Action Item\n\n{sections.get('action_item', 'N/A')}")
    parts.append(f"# Current Issue / Blocker\n\n{sections.get('blocker', 'N/A')}")
    parts.append(f"# Dependencies (Optional)\n\n{sections.get('dependencies', 'N/A')}")
    return "\n\n".join(parts)


def to_int_or_none(val):
    if val is None:
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: parse_task_file.py <task_file>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    with open(filepath) as f:
        text = f.read()

    fm, body_text = parse_frontmatter(text)

    sections = {}
    for key, pattern in BODY_SECTIONS:
        m = re.search(pattern, body_text)
        if m:
            sections[key] = m.group(1).strip()

    status = fm.get("status", "backlog")
    due = fm.get("due")

    print(json.dumps({
        "title": fm.get("title", "Untitled"),
        "status": status,
        "due": due,
        "issue": to_int_or_none(fm.get("issue")),
        "parent": to_int_or_none(fm.get("parent")),
        "type": fm.get("type", "Task"),
        "state": STATUS_TO_STATE.get(status, "open"),
        "body": build_issue_body(sections, due),
        "filename": filepath,
    }, indent=2))


if __name__ == "__main__":
    main()
