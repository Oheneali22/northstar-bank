# Northstar Bank

Northstar Bank is a synthetic banking application designed as a realistic DevOps and
observability portfolio environment. It contains a customer web application and a core banking
API with PostgreSQL persistence, atomic transfers, a double-entry ledger, health probes,
structured logs, metrics, tests, migrations, and OpenAPI documentation.

> Northstar Bank uses fake customers and fake money. It is not financial software and must not
> process real personal or payment data.

## Components

```text
Browser
   |
   v
northstar-web :3000
   |
   v
northstar-core-api :8000
   |
   v
PostgreSQL
```

- `app/`: Next.js customer dashboard and same-origin API gateway routes
- `services/core-api/`: FastAPI accounts, transfers, ledger, health, metrics, and OpenAPI
- `services/core-api/migrations/`: versioned PostgreSQL schema
- `tests/`: web application contract tests
- `docs/developer-handoff.md`: complete runtime and operational contract

## Developer validation

Web:

```bash
pnpm install --frozen-lockfile
pnpm test
pnpm lint
pnpm build
```

Core API:

```bash
cd services/core-api
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
ruff check .
pytest
```

Database migration and synthetic seed:

```bash
alembic upgrade head
python -m scripts.seed
```

See `docs/developer-handoff.md` before packaging or deploying the application. It documents
ports, commands, variables, dependencies, probes, metrics, logging, migration behavior, and
known limitations without performing platform-engineering work for you.
