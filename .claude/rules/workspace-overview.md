---
description: Workspace structure, project families, and per-project descriptions with SRE-relevant folders
globs: *
---

## Workspace Overview

This directory is a multi-project workspace. Each subdirectory is an independent project with its own dependencies and tooling. Always `cd` into the specific project before running commands.

---

## GL-SRE/ — SRE/DevOps Related Repository

Infrastructure-as-Code, platform tooling, Docker images, Helm charts, and Terraform for managing cloud resources.

### gl-common-infra
Shared infrastructure tools and GCP management utilities.
- `infra-management/` — Packer, Teleport, Helm templates for various services
- `infra-script/` — Utility scripts for infra tasks
- `benchmark/` — Performance testing scripts

### gl-sre-backstage
Backstage.io Developer Portal (Node.js 20+, Yarn 4.4.1).
- `deployment/kubernetes/` — K8s manifests
- `packages/` — Core backend/frontend packages
- `plugins/` — Custom Backstage plugins
- `gl-sre-catalog/` — Service catalog definitions
- Config: `app-config.yaml` (local), `app-config.production.yaml` (prod)

### gl-sre-docker
Custom Docker base image library (30+ images).
- `docker/` — Dockerfiles organized by use case (backend-node, frontend-nginx, terraform, python, uv, poetry, rust, etc.)
- `cloudbuild-terraform/` — Terraform IaC for Cloud Build triggers
- Vulnerability scanning with Trivy; versioning via `version.yaml`

### gl-sre-fluffy-barnacle
Production and staging Kubernetes cluster configs (EKS-based).
- `eks-gl-staging/` — Staging EKS: `kube-manifest/`, `helm-values/`, `PolicyFiles/`
- `gl-chat-saas-prod/` — Production GL-Chat SaaS: `kube-manifest/`, `helm-values/`, `charts/`
- `policy/` — Cluster-level policies and RBAC
- IaC: Terragrunt (`terragrunt.hcl`, `terragrunt-staging.hcl`)

### gl-sre-helm-charts
Shared Helm chart templates for EKS/Kubernetes deployments.
- `charts/` — Pre-packaged charts (cluster-autoscaler, kube-prometheus-stack, etc.)

### gl-sre-internal-tools
SRE automation tools and utilities (16 tools).
- Monitoring: `cicd-exporter`, `gh-activities-exporter`, `github-project-exporter`
- Resource mgmt: `cloud-custodian`, `scheduled-start-stop`, `cloudstart`
- Task automation: `ticket-exporter`, `duedate-reminder`, `sre-bot`, `github-pr-reminder`
- Infra: `kubernetes-secret-editor`, `autogt`, `ghtoken2gcp`
- CI/CD: `cloudbuild.yml`, `cloudbuild-pr.yml`

### gl-sre-terraform
Infrastructure-as-Code for multi-cloud (Atlantis-driven GitOps).
- `aws/` — AWS infrastructure
- `gcp/` — GCP infrastructure
- `azure/` — Azure infrastructure
- `kibana/` — Logging infrastructure
- Tools: Terraform 1.9.6+, Terragrunt 0.54.14+, tflint, tfsec

### gl-sre-terraform-modules
Reusable Terraform module library.
- `aws/` — 20+ modules (ECS, EKS, VPC, Lambda, RDS, OpenSearch, IAM, etc.)
- `azure/` — 15+ modules (VMs, app services, containers, functions, key vaults, etc.)
- `gcp/` — 15+ modules (GKE, Cloud Build, Cloud Functions, IAM, storage, etc.)
- `github/` — Admin, app integration, project management modules
- Published to S3, consumed via `source = "s3::https://..."`

### SRE-task
Task tracking repository for SRE team (GitHub Issues integration target).

---

## GLChat/ — GLChat Services Platform

Applications, SDKs, and services powering the GLChat AI platform. Most projects follow a common CI/CD pattern: `cloudbuild.yml` + `cloudeploy-kubernetes.yml`.

### glchat
Core chat application platform.
- `deployment/kubernetes/` — K8s deployment configs
- `deployment/server/` — Server Dockerfiles and configs
- Applications: `glchat-be` (backend), `glchat-ui` (Next.js UI), `glchat-dpo` (document processing), `glchat-slm` (small language model)
- Multiple `catalog-info-*.yaml` for Backstage integration

### gl-glchat-infra
GLChat infrastructure and deployment configurations.
- `catalog-info-*.yaml` — Backstage service catalog entries
- `deploy-kubernetes.sh`, `docker-bake.gcb.hcl`, `docker-compose.test.yml`
- CI/CD: `cloudbuild.yml`, `cloudeploy-kubernetes.yml`, `cloudlint-kubernetes-pr.yml`

### ai-agent-platform
SDK and backend for AI-powered agent systems (Python 3.11+, Poetry, FastAPI).
- Applications: `ai-agent-platform-backend` (REST API), `ai-agent-platform-runner` (agent execution)
- CI/CD: `cloudbuild.yml`, `cloudeploy-kubernetes.yml`, `cloudeploy-server.yml`

### bosa-acidev
Modified ACI.dev platform with 600+ tool integrations (Python backend, Next.js frontend, FastAPI, PostgreSQL + pgvector).
- Applications: backend (FastAPI), frontend (Next.js), mcp (Model Context Protocol server)
- CI/CD: `cloudbuild.yml`, `cloudeploy-kubernetes.yml`, `dev-compose.yml`

### gl-connectors
API platform and interactive playground for third-party integrations (Python).
- `deployment/kubernetes/` — K8s configs
- CI/CD: `cloudbuild.yml`, `cloudeploy-kubernetes.yml`

### gl-connectors-sdk
SDK for building server-side plugins and client applications (Python 3.11+, Poetry/uv). No deployment files — library only.
- Components: `gl-connectors-sdk`, `gl-connectors-plugins`, `gl-connectors-cli`, `gl-connectors-tools`

### gl-open-deepresearch
Deep research orchestration framework (Python 3.12+, FastAPI, PostgreSQL, Redis, Celery).
- Features: SSE streaming, async task processing, profile-based configs
- CI/CD: `cloudbuild.yml`, `cloudeploy-kubernetes.yml`

### gl-smart-crawl
Web crawling service.
- CI/CD: `cloudbuild.yml`, `cloudeploy-kubernetes.yml`

### smart-search
Backend service for enhanced web search (Python).
- Applications: `smart-search-backend`
- CI/CD: `cloudbuild.yml`, `cloudeploy-kubernetes.yml`

### glchat-messaging
WhatsApp messaging webhook server (Python 3.11+, Poetry, FastAPI).
- Providers: Twilio, WhatsApp Cloud API, Qiscus
- CI/CD: `cloudbuild.yml`, `cloudeploy-kubernetes.yml`

### gl-chat-datasaur
Datasaur integration for data annotation.
- CI/CD: `cloudbuild.yml`, `cloudeploy-kubernetes.yml`

### gdplabs-ner-api
Named Entity Recognition API for PII anonymization (Python, uv).

### model-accuracy-benchmarking
Model accuracy benchmarking tool (Python, Celery, Flower, Gemini Batch API).
- Production control via Slack commands in SRE Glair workspace
- CI/CD: `cloudbuild.yml`, `cloudeploy-kubernetes.yml`, `Dockerfile`, `docker-compose.yml`

### gl-sdk
Python SDK for GDP Labs GenAI (Poetry and UV). Library only.
- Sub-libraries: `gllm-core`, `gllm-datastore`

### glaip-sdk
GL AIP SDK for building AI agents (Python 3.10+). Library only.

### stack-auth
Open-source managed user authentication (Node v20, pnpm, Turbo monorepo, React/Next.js).
- Features: OAuth, magic links, RBAC, multi-tenancy, passkeys, webhooks, M2M auth
- Docker required for local setup
