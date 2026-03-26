#!/usr/bin/env python3
"""Render a task markdown file from parsed issue JSON.

Reads JSON from stdin (output of parse_issue_body.py), writes task file to disk.

Usage:
    python3 generate_task_file.py [--output-dir DIR] [--dry-run]

Output: path of the created file printed to stdout (e.g. tasks/2026-03-24-some-slug.md)
"""
import argparse
import json
import re
import sys
from datetime import date


def slugify(title, max_len=60):
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s-]+", "-", slug).strip("-")
    return slug[:max_len].rstrip("-")


def render(data, today):
    labels_block = "\n".join(f"- {lb}" for lb in data.get("labels", ["Operational"]))
    completed = today if data.get("state") == "closed" else "null"
    due = data.get("due") or "null"

    return (
        f"---\n"
        f"title: {json.dumps(data['title'])}\n"
        f"status: {data['status']}\n"
        f"created: {today}\n"
        f"completed: {completed}\n"
        f"due: {json.dumps(due) if due != 'null' else 'null'}\n"
        f"issue: {data['number']}\n"
        f"parent: null\n"
        f"type: {data.get('type', 'Task')}\n"
        f"---\n"
        f"\n"
        f"**Labels** :\n"
        f"{labels_block}\n"
        f"\n"
        f"# Description and Contexts\n"
        f"{data.get('description', 'N/A')}\n"
        f"\n"
        f"# Action Item\n"
        f"{data.get('action_item', 'N/A')}\n"
        f"\n"
        f"# Current Issue / Blocker\n"
        f"{data.get('blocker', 'N/A')}\n"
        f"\n"
        f"# Dependencies (Optional)\n"
        f"{data.get('dependencies', 'N/A')}\n"
        f"\n"
        f"## Result\n"
        f"N/A\n"
    )


def main():
    parser = argparse.ArgumentParser(description="Write a task markdown file from issue JSON")
    parser.add_argument("--output-dir", default="tasks", help="Directory to write task file")
    parser.add_argument("--dry-run", action="store_true", help="Print file path and content without writing")
    args = parser.parse_args()

    data = json.load(sys.stdin)

    required = {"number", "title", "state", "status"}
    missing = required - data.keys()
    if missing:
        print(f"ERROR: missing required fields: {missing}", file=sys.stderr)
        sys.exit(1)

    today = str(date.today())
    slug = slugify(data["title"])
    filename = f"{today}-{slug}.md"
    filepath = f"{args.output_dir}/{filename}"
    content = render(data, today)

    if args.dry_run:
        print(f"DRY RUN — would write: {filepath}")
        print(content)
    else:
        with open(filepath, "w") as f:
            f.write(content)
        # Print path so SKILL.md workflow can read it
        print(filepath)


if __name__ == "__main__":
    main()
