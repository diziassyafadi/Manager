#!/usr/bin/env python3
"""Create a new task file in tasks/ from CLI arguments.

Usage:
    python3 create_task_file.py --title "Fix something" \
        --description "Why and what" \
        [--due 2026-04-01] \
        [--output-dir tasks]
    # Action items are read from stdin (one per line):
    echo "- [ ] Do this
- [ ] Do that" | python3 create_task_file.py --title ...

Output: path of the created file (e.g. tasks/2026-03-25-fix-something.md)
"""
import argparse
import re
import sys
from datetime import date


def slugify(title, max_len=60):
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s-]+", "-", slug).strip("-")
    return slug[:max_len].rstrip("-")


def render(title, description, action_items, due, today):
    return (
        f"---\n"
        f"title: {title}\n"
        f"status: backlog\n"
        f"created: {today}\n"
        f"completed: null\n"
        f"due: {due or 'null'}\n"
        f"issue: null\n"
        f"parent: null\n"
        f"type: Task\n"
        f"---\n"
        f"\n"
        f"**Labels** :\n"
        f"- \n"
        f"\n"
        f"# Description and Contexts\n"
        f"{description}\n"
        f"\n"
        f"# Action Item\n"
        f"{action_items}\n"
        f"\n"
        f"# Current Issue / Blocker\n"
        f"N/A\n"
        f"\n"
        f"# Dependencies (Optional)\n"
        f"N/A\n"
        f"\n"
        f"## Result\n"
        f"N/A\n"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--due", default=None)
    parser.add_argument("--output-dir", default="tasks")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    action_items = sys.stdin.read().strip() or "- [ ] (add action items)"

    today = str(date.today())
    slug = slugify(args.title)
    filename = f"{today}-{slug}.md"
    filepath = f"{args.output_dir}/{filename}"
    content = render(args.title, args.description, action_items, args.due, today)

    if args.dry_run:
        print(f"DRY RUN — would write: {filepath}")
        print(content)
    else:
        with open(filepath, "w") as f:
            f.write(content)
        print(filepath)


if __name__ == "__main__":
    main()
