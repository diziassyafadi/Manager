#!/usr/bin/env python3
"""Parse structured sections from a GitHub issue body.

Reads JSON from stdin (output of fetch_issue.py), adds parsed fields, writes JSON to stdout.

Added fields:
    description  — content of '# Description and Contexts' section, or full body if unstructured
    action_item  — content of '# Action Item' section
    blocker      — content of '# Current Issue / Blocker' section
    dependencies — content of '# Dependencies (Optional)' section
    labels       — list of label strings from '**Labels** :' block
    due          — YYYY-MM-DD string from '> **Due:** ...' line, or null
"""
import json
import re
import sys


SECTION_PATTERNS = {
    "description": r"# Description and Contexts\s*\n([\s\S]*?)(?=\n#\s|\Z)",
    "action_item": r"# Action Item\s*\n([\s\S]*?)(?=\n#\s|\Z)",
    "blocker": r"# Current Issue / Blocker\s*\n([\s\S]*?)(?=\n#\s|\Z)",
    "dependencies": r"# Dependencies(?:\s*\(Optional\))?\s*\n([\s\S]*?)(?=\n#\s|\Z)",
}


def parse_body(body):
    result = {
        "description": "N/A",
        "action_item": "N/A",
        "blocker": "N/A",
        "dependencies": "N/A",
        "labels": ["Operational"],
        "due": None,
    }

    # Due date: "> **Due:** YYYY-MM-DD"
    m = re.search(r">\s*\*\*Due:\*\*\s*(\d{4}-\d{2}-\d{2})", body)
    if m:
        result["due"] = m.group(1)

    # Labels block: "**Labels** :\n- label1\n- label2"
    m = re.search(r"\*\*Labels\*\*\s*:\s*\n((?:-\s*.+\n?)+)", body)
    if m:
        labels = [
            line.strip().lstrip("-").strip()
            for line in m.group(1).strip().splitlines()
            if line.strip().lstrip("-").strip()
        ]
        if labels:
            result["labels"] = labels

    # Section extraction
    found_any = False
    for key, pattern in SECTION_PATTERNS.items():
        m = re.search(pattern, body)
        if m:
            content = m.group(1).strip()
            if content:
                result[key] = content
                found_any = True

    # Unstructured body: place full content under description
    if not found_any and body.strip():
        result["description"] = body.strip()

    return result


def main():
    data = json.load(sys.stdin)
    parsed = parse_body(data.get("body", ""))
    data.update(parsed)
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
