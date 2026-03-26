#!/usr/bin/env python3
"""Sync a GitHub issue to a Projects v2 board (status, due date, parent).

Usage:
    python3 sync_project.py <issue_number> <status> [--due YYYY-MM-DD] [--parent ISSUE_NUMBER] [--config PATH] [--env PATH] [--repo KEY]

Performs:
    1. Gets the issue node ID via REST
    2. Adds the issue to the project (idempotent)
    3. Sets the Status field
    4. Sets the Due Date field (if --due provided)
    5. Sets the Parent field (if --parent provided)

Output: JSON with node_id, item_id, project_id, status, due, parent
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def load_env(env_path):
    env = {}
    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    env[k.strip()] = v.strip().strip("\"'")
    except FileNotFoundError:
        pass
    return env


def load_config(config_path):
    with open(config_path) as f:
        return json.load(f)


def gh_rest(url, pat):
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"bearer {pat}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"ERROR: GitHub REST {e.code} — {body}", file=sys.stderr)
        sys.exit(1)


def gh_graphql(pat, query):
    req = urllib.request.Request("https://api.github.com/graphql", method="POST")
    req.add_header("Authorization", f"bearer {pat}")
    req.add_header("Content-Type", "application/json")
    req.data = json.dumps({"query": query}).encode()
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"ERROR: GitHub GraphQL {e.code} — {body}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Sync issue to GitHub Projects v2")
    parser.add_argument("issue_number", type=int)
    parser.add_argument("status", help="Task status (e.g. backlog, in-progress)")
    parser.add_argument("--due", default=None, help="Due date YYYY-MM-DD")
    parser.add_argument("--parent", default=None, help="Parent issue number")
    parser.add_argument("--config", default=".claude/config/github-projects.json")
    parser.add_argument("--env", default=".claude/.env")
    parser.add_argument("--repo", default=None)
    args = parser.parse_args()

    env = load_env(args.env)
    pat = env.get("GITHUB_PAT") or os.environ.get("GITHUB_PAT")
    if not pat:
        print("ERROR: GITHUB_PAT not found", file=sys.stderr)
        sys.exit(1)

    repo_key = args.repo or env.get("GITHUB_ISSUE_REPO") or os.environ.get("GITHUB_ISSUE_REPO")
    if not repo_key:
        print("ERROR: GITHUB_ISSUE_REPO not found", file=sys.stderr)
        sys.exit(1)

    config = load_config(args.config)
    if repo_key not in config:
        print(f"ERROR: repo key '{repo_key}' not in config", file=sys.stderr)
        sys.exit(1)

    cfg = config[repo_key]
    owner = cfg["owner"]
    repo = cfg["repo"]
    project_id = env.get("GITHUB_PROJECT_ID") or cfg.get("project_id", "")
    status_field_id = cfg["fields"]["status"]["id"]
    status_options = cfg["fields"]["status"]["options"]
    due_field_id = cfg["fields"]["due_date"]["id"]
    parent_field_id = cfg.get("fields", {}).get("parent", {}).get("id")

    # 1. Get issue node ID
    issue = gh_rest(
        f"https://api.github.com/repos/{owner}/{repo}/issues/{args.issue_number}", pat
    )
    node_id = issue["node_id"]

    # 2. Add to project (idempotent)
    result = gh_graphql(pat, f'''mutation {{
      addProjectV2ItemById(input: {{projectId: "{project_id}", contentId: "{node_id}"}}) {{
        item {{ id }}
      }}
    }}''')
    item_id = result["data"]["addProjectV2ItemById"]["item"]["id"]

    # 3. Set status
    status_option = status_options.get(args.status)
    if status_option:
        gh_graphql(pat, f'''mutation {{
          updateProjectV2ItemFieldValue(input: {{
            projectId: "{project_id}", itemId: "{item_id}",
            fieldId: "{status_field_id}",
            value: {{singleSelectOptionId: "{status_option}"}}
          }}) {{ projectV2Item {{ id }} }}
        }}''')

    # 4. Set due date (optional)
    if args.due:
        gh_graphql(pat, f'''mutation {{
          updateProjectV2ItemFieldValue(input: {{
            projectId: "{project_id}", itemId: "{item_id}",
            fieldId: "{due_field_id}",
            value: {{date: "{args.due}"}}
          }}) {{ projectV2Item {{ id }} }}
        }}''')

    # 5. Set parent field (optional, if field is configured)
    if args.parent and parent_field_id:
        gh_graphql(pat, f'''mutation {{
          updateProjectV2ItemFieldValue(input: {{
            projectId: "{project_id}", itemId: "{item_id}",
            fieldId: "{parent_field_id}",
            value: {{text: "{args.parent}"}}
          }}) {{ projectV2Item {{ id }} }}
        }}''')

    print(json.dumps({
        "node_id": node_id,
        "item_id": item_id,
        "project_id": project_id,
        "status": args.status,
        "due": args.due,
        "parent": args.parent,
    }))


if __name__ == "__main__":
    main()
