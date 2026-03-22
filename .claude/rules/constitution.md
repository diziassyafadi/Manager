---
description: Guardrails and operational rules Claude must follow in all tasks
globs: *
---

## Constitution

### 1. Destructive Operations Require Approval

Any action that mutates live infrastructure must be documented in the task file and approved by Dizi before execution:
- `terraform apply`, `terraform destroy`
- `kubectl apply`, `kubectl delete`, `kubectl patch`
- `helm install`, `helm upgrade`, `helm uninstall`
- Any `gcloud` command that creates, deletes, or modifies resources

Claude must:
- State the exact command and target (cluster, namespace, project)
- Document it in the active task file under **Action Item**
- Wait for explicit approval before running

### 2. Suggest Automation for Repetitive Patterns

When a task follows a pattern Claude has seen before (or could clearly be templated), flag it:
- Suggest a Claude Code skill, hook, or shell script
- Keep the suggestion to one line with a concrete example
- Do not build the automation unless Dizi asks for it

### 3. Rollback Plan on Every Implementation

Every implementation plan must include a rollback strategy before Dizi approves:
- State what to revert and how (e.g., `git revert`, `helm rollback`, `terraform plan` with previous state)
- Call out risks: data loss, downtime window, dependency ordering
- Ensure Dizi acknowledges the risk before proceeding

### 4. Validate Files Before Presenting

Claude must validate generated or modified files before presenting them:
- YAML: structure and syntax correctness
- Python: linter compliance (black, isort, flake8 where configured)
- Terraform: `terraform fmt` and `terraform validate` conventions
- JSON: valid parse
- Kubernetes manifests: required fields present (apiVersion, kind, metadata)

If a project has pre-commit hooks or linters, run them. If not, apply best-effort validation inline.

### 5. Minimal, Runnable Output

- Deliver only what Dizi asked for — no extra files, no scaffolding, no unsolicited abstractions
- Include a one-liner smoke-check or test command where applicable
- Explicitly note any external dependencies or required environment variables
- No markdown files (migration.md, CHANGELOG.md, etc.) unless Dizi explicitly requests one

### 6. No Token Waste

- Do not generate documentation files, migration guides, or explanatory markdown unless requested
- Do not add comments explaining obvious code
- Do not create README files for new directories unless asked
- Keep responses tight — if the diff speaks for itself, do not narrate it
