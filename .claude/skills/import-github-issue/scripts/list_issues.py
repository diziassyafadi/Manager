#!/usr/bin/env python3
"""List open GitHub issues assigned to a user.

Usage:
    python3 list_issues.py <assignee> [--config PATH] [--env PATH] [--repo KEY] [--limit N]

Output: JSON array to stdout with fields: number, title, state, labels
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
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


def main():
    parser = argparse.ArgumentParser(description="List open GitHub issues by assignee")
    parser.add_argument("assignee", help="GitHub username to filter by")
    parser.add_argument("--config", default=".claude/config/github-projects.json")
    parser.add_argument("--env", default=".claude/.env")
    parser.add_argument(
        "--repo",
        default=None,
        help="Key in config JSON (default: value of GITHUB_ISSUE_REPO in .env)",
    )
    parser.add_argument("--limit", type=int, default=30, help="Max issues to return")
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

    params = urllib.parse.urlencode({
        "assignee": args.assignee,
        "state": "open",
        "per_page": min(args.limit, 100),
        "sort": "updated",
        "direction": "desc",
    })
    issues = gh_rest(
        f"https://api.github.com/repos/{owner}/{repo}/issues?{params}",
        pat,
    )

    # Exclude pull requests (GitHub REST returns PRs in issues endpoint)
    output = [
        {
            "number": i["number"],
            "title": i["title"],
            "state": i["state"],
            "labels": [lb["name"] for lb in i.get("labels", [])],
        }
        for i in issues
        if "pull_request" not in i
    ]

    if not output:
        print(f"No open issues assigned to '{args.assignee}' in {owner}/{repo}", file=sys.stderr)
        sys.exit(0)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
