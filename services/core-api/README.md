# Northstar Core API

The core API owns customer accounts, balances, transfers, and double-entry ledger records.

## Runtime contract

| Setting | Value |
|---|---|
| Runtime | Python 3.12+ |
| HTTP port | `8000` |
| Process | `uvicorn app.main:app --host 0.0.0.0 --port 8000` |
| Database | PostgreSQL |
| Migration | `alembic upgrade head` |
| Seed | `python -m scripts.seed` |
| Test | `pytest` |
| Lint | `ruff check .` |

## Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /health/live` | Process liveness; does not check dependencies |
| `GET /health/ready` | Readiness; verifies a PostgreSQL query |
| `GET /metrics` | Prometheus exposition endpoint |
| `GET /docs` | Interactive OpenAPI documentation |
| `GET /api/v1/accounts` | List synthetic customer accounts |
| `GET /api/v1/transfers` | List recent transfers |
| `POST /api/v1/transfers` | Execute an idempotent account transfer |

`POST /api/v1/transfers` requires an `Idempotency-Key` header. Retrying a request with the
same key returns the existing transfer rather than moving money twice.

## Configuration

Copy `.env.example` to `.env` for developer execution. Runtime configuration is read from
environment variables; secrets are not committed to this repository.

This service uses synthetic data only and is not financial software.
