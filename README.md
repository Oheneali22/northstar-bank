# Northstar Bank

Northstar Bank is a production-minded learning application for practicing the full DevOps lifecycle: application delivery, containers, Kubernetes, AWS, infrastructure as code, observability, security, and incident response.

> This project uses synthetic customers and fake money only. It is not financial software.

## Current milestone: Sprint 1A

The first vertical slice is a responsive customer dashboard with:

- Checking-account balances and financial summary
- Searchable transaction activity
- Savings-goal and platform-health panels
- An interactive money-transfer workflow
- Server-rendered smoke tests and a production build

The current transfer flow is intentionally a UI prototype. Persistent transactions, authentication, idempotency, and ledger rules arrive in Sprint 1B.

## Run locally

Requirements: Node.js 22+ and pnpm 11+.

```bash
pnpm install
pnpm dev
```

Build and test:

```bash
pnpm build
node --test tests/rendered-html.test.mjs
```

## Delivery roadmap

1. **Application:** account, transaction, notification, and identity services with PostgreSQL and Redis.
2. **Containers:** secure multi-stage images and Docker Compose development environment.
3. **Kubernetes:** kind cluster, Helm, Kustomize, workloads, configuration, storage, RBAC, policies, autoscaling, and GitOps.
4. **AWS:** Terraform-managed VPC, EKS, ECR, RDS, ElastiCache, S3, SQS, SNS, IAM, KMS, Secrets Manager, ALB, Route 53, and observability.
5. **Operations:** CI/CD, SLOs, dashboards, alerts, backups, disaster recovery, security scanning, and incident exercises.

## Repository direction

```text
app/             customer web application
tests/           rendered application checks
services/        backend services (Sprint 1B)
deploy/docker/   local container environment (Sprint 2)
deploy/helm/     Kubernetes packages (Sprint 3)
infra/terraform/ AWS infrastructure (Sprint 4)
docs/runbooks/   operational procedures and incidents
```

## Definition of done for Sprint 1B

- Double-entry ledger stored in PostgreSQL
- Atomic and idempotent transfers
- REST API with validation and health endpoints
- Redis-backed request throttling
- Database migrations and automated API tests
- Docker Compose starts the complete local platform
