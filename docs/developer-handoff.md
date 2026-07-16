# Developer handoff

This document is the application contract delivered to the platform team. It describes what
the software needs; it intentionally does not prescribe Docker, Kubernetes, cloud, or CI/CD
implementations.

## Deployable components

### `northstar-web`

- Source: repository root
- Runtime: Node.js 22.13+
- Package manager: pnpm 11.7
- Build: `pnpm install --frozen-lockfile && pnpm build`
- Test: `pnpm test`
- Start: `pnpm start -- --hostname 0.0.0.0 --port 3000`
- Port: `3000/TCP`
- Required runtime variable: `CORE_API_URL`
- Liveness: `GET /health/live`
- Readiness: `GET /health/ready`
- Filesystem: no durable writes required
- Shutdown: handles the process termination behavior provided by Next.js/Node.js

The Next.js build uses standalone output so the production runtime can contain only
`.next/standalone`, `.next/static`, and `public` assets.

### `northstar-core-api`

- Source: `services/core-api`
- Runtime: Python 3.12+
- Install: `pip install .`
- Test: `pip install '.[dev]' && pytest`
- Lint: `ruff check .`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Port: `8000/TCP`
- Required runtime variable: `DATABASE_URL`
- Optional variables: `APP_ENV`, `LOG_LEVEL`, `CORS_ORIGINS`
- Liveness: `GET /health/live`
- Readiness: `GET /health/ready`
- Metrics: `GET /metrics`
- OpenAPI: `GET /openapi.json`; interactive documentation at `GET /docs`
- Filesystem: no durable writes required
- Logs: newline-delimited JSON on stdout/stderr

## PostgreSQL contract

- Supported target: PostgreSQL 16+
- Schema migration: run `alembic upgrade head` as a one-time release operation
- Seed data: run `python -m scripts.seed` only for disposable development environments
- Application runtime must not execute migrations automatically
- Accounts are locked in deterministic order during transfers to reduce deadlock risk
- Balances and transfer amounts are stored as integer cents
- Every transfer produces one debit and one equal credit ledger entry

## Failure behavior

- The web readiness endpoint returns `503` when the core API is unavailable.
- The core API readiness endpoint returns a non-success response when PostgreSQL is unavailable.
- Core API liveness remains independent of PostgreSQL to avoid restart loops during a database outage.
- Transfer validation uses `404` for missing accounts and `409` for business conflicts such as
  insufficient funds, inactive accounts, or currency mismatch.
- Upstream requests from the web tier time out after five seconds.

## Observability contract

The core API emits:

- JSON request logs with timestamp, level, service, environment, request ID, route, status, and duration
- `X-Request-ID` response headers
- HTTP request counts by method, route, and status
- HTTP request-duration histograms
- Transfer counters by business outcome
- Transfer-amount histograms

The platform is expected to collect stdout logs and scrape `/metrics`. Dashboard, alert, retention,
sampling, and remote-storage decisions are intentionally owned by the platform team.

## Explicit non-production limitations

- All customer data is synthetic.
- User authentication and authorization are not implemented yet.
- Notification delivery and fraud decisions are not implemented yet.
- The application has no PCI-DSS claim and must never process real financial information.

Those limitations are visible rather than hidden so that future releases can introduce identity,
messaging, and fraud services as separate operational exercises.
