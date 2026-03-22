---
description: Per-project commands, package managers, and tooling reference
globs: *
---

## Project Quick Reference

### GL-SRE/gl-sre-backstage (Backstage.io platform)
- Package manager: **Yarn 4.4.1** (Node.js 18+/20)
- `make install` → install deps
- `yarn dev` → local dev server
- `make build` → build backend
- `yarn test` → run tests
- `yarn lint` → lint
- `make containerize` → build Docker image
- Config files: `app-config.yaml` (local), `app-config.production.yaml` (prod)

### GLChat/stack-auth (Auth platform monorepo)
- Package manager: **pnpm** (Turbo monorepo)
- `pnpm pre` → codegen and setup (run first)
- `pnpm dev` → dev with hot reload
- `pnpm build` → full build
- `pnpm test` → unit tests
- `pnpm lint` → lint
- See its own `CLAUDE.md` for deeper architecture notes

### GLChat/gl-connectors (API platform with plugins)
- See `CLAUDE.md` and `AGENTS.md` in that directory for architecture
- Python + TypeScript hybrid

### GLChat/ai-agent-platform (AI agent SDK + backend)
- Package manager: **Poetry** (Python 3.11+)
- `poetry install` → install deps
- Pre-commit hooks: black, isort, flake8, pylint, pydocstyle
- See `.cursorrules` in that directory for code style rules

### GLChat/gl-sdk (Python SDK for GDP Labs GenAI)
- **Poetry** (Python)
- Sub-libraries: `gllm-core`, `gllm-datastore`

## Project-Specific Instruction Files

Several projects have their own instruction files — always check these before diving deep into a specific project:
- `GLChat/stack-auth/CLAUDE.md`
- `GLChat/gl-connectors/CLAUDE.md` + `AGENTS.md`
- `GLChat/ai-agent-platform/.cursorrules`
