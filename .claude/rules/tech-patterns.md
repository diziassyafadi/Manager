---
description: Common technology patterns across Node.js, Python, and deployment projects
globs: *
---

## Common Technology Patterns

**Node.js projects** typically use:
- TypeScript with strict mode
- Prettier for formatting
- ESLint for linting
- vitest (unit) / Playwright (E2E)

**Python projects** typically use:
- UV for dependency management (but Poetry is still used for SDK that haven't been migrated)
- pytest for testing
- Pre-commit hooks (black, isort, flake8, pylint)

**Deployment** (GL-SRE):
- Google Cloud Build for CI (`cloudbuild.yml`)
- Kubernetes via CloudDeploy for CD (`cloudeploy-kubernetes.yml`)
- Terraform modules, Helm charts, Addons Docker Images, and Backstage in `GL-SRE/`
