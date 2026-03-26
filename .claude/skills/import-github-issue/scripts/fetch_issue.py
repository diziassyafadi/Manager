#!/usr/bin/env python3
"""Fetch a GitHub issue and its Projects v2 status, type, and parent.

Usage:
    python3 fetch_issue.py <issue_number> [--config PATH] [--env PATH] [--repo KEY]

Output: JSON to stdout with fields: number, title, body, state, status, type, node_id, owner, repo, parent
"""
import argparse
import json
import os
import re
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


def get_project_fields(pat, node_id, project_number, status_options):
    """Query GitHub Projects v2 for status and parent fields."""
    query = f"""{{
      node(id: "{node_id}") {{
        ... on Issue {{
          projectItems(first: 10) {{
            nodes {{
              project {{ number }}
              fieldValues(first: 20) {{
                nodes {{
                  ... on ProjectV2ItemFieldSingleSelectValue {{
                    name
                    field {{ ... on ProjectV2SingleSelectField {{ name }} }}
                  }}
                  ... on ProjectV2ItemFieldTextValue {{
                    text
                    field {{ ... on ProjectV2TextField {{ name }} }}
                  }}
                  ... on ProjectV2ItemFieldNumberValue {{
                    number
                    field {{ ... on ProjectV2NumberField {{ name }} }}
                  }}
                }}
              }}
            }}
          }}
        }}
      }}
    }}"""
    result = gh_graphql(pat, query)
    items = (
        result.get("data", {})
        .get("node", {})
        .get("projectItems", {})
        .get("nodes", [])
    )
    status = "backlog"
    parent = None

    for item in items:
        if item.get("project", {}).get("number") == project_number:
            for fv in item.get("fieldValues", {}).get("nodes", []):
                field_name = fv.get("field", {}).get("name", "").lower()

                # Extract status
                if field_name == "status":
                    raw_name = fv.get("name", "").lower().replace(" ", "-")
                    for status_key in status_options:
                        if status_key.lower() == raw_name:
                            status = status_key
                            break

                # Extract parent (as text or number field)
                if field_name == "parent":
                    parent_val = fv.get("text") or fv.get("number")
                    if parent_val:
                        # Extract issue number (e.g., "#3019" or "3019")
                        m = re.search(r"#?(\d+)", str(parent_val))
                        if m:
                            parent = int(m.group(1))

    return status, parent


def main():
    parser = argparse.ArgumentParser(description="Fetch a GitHub issue as JSON")
    parser.add_argument("issue_number", type=int)
    parser.add_argument("--config", default=".claude/config/github-projects.json")
    parser.add_argument("--env", default=".claude/.env")
    parser.add_argument(
        "--repo",
        default=None,
        help="Key in config JSON (default: value of GITHUB_ISSUE_REPO in .env)",
    )
    args = parser.parse_args()

    env = load_env(args.env)
    pat = env.get("GITHUB_PAT") or os.environ.get("GITHUB_PAT")
    if not pat:
        print("ERROR: GITHUB_PAT not found in .claude/.env or environment", file=sys.stderr)
        sys.exit(1)

    repo_key = args.repo or env.get("GITHUB_ISSUE_REPO") or os.environ.get("GITHUB_ISSUE_REPO")
    if not repo_key:
        print("ERROR: --repo not set and GITHUB_ISSUE_REPO not found in .claude/.env", file=sys.stderr)
        sys.exit(1)

    config = load_config(args.config)
    if repo_key not in config:
        available = [k for k in config if not k.startswith("_")]
        print(f"ERROR: repo key '{repo_key}' not in config. Available: {available}", file=sys.stderr)
        sys.exit(1)

    repo_cfg = config[repo_key]
    owner = repo_cfg["owner"]
    repo = repo_cfg["repo"]
    project_number = repo_cfg["project_number"]
    status_options = repo_cfg["fields"]["status"]["options"]

    issue = gh_rest(
        f"https://api.github.com/repos/{owner}/{repo}/issues/{args.issue_number}",
        pat,
    )

    if issue.get("pull_request"):
        print(f"ERROR: #{args.issue_number} is a pull request, not an issue", file=sys.stderr)
        sys.exit(1)

    # Determine status and parent
    if issue["state"] == "closed":
        status = "done"
        parent = None
    else:
        status, parent = get_project_fields(pat, issue["node_id"], project_number, status_options)

    # Infer type from labels (Bug > Feature > Task)
    issue_type = "Task"
    for label in issue.get("labels", []):
        name = label["name"].lower()
        if name == "bug":
            issue_type = "Bug"
            break
        if name == "feature":
            issue_type = "Feature"

    print(json.dumps({
        "number": issue["number"],
        "title": issue["title"],
        "body": issue.get("body") or "",
        "state": issue["state"],
        "status": status,
        "type": issue_type,
        "node_id": issue["node_id"],
        "owner": owner,
        "repo": repo,
        "parent": parent,
    }, indent=2))


if __name__ == "__main__":
    main()
