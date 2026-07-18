# syntax=docker/dockerfile:1

FROM python:3.12.3-slim-bookworm AS builder

ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build
RUN python -m venv "$VIRTUAL_ENV"

COPY pyproject.toml ./
COPY app ./app

RUN --mount=type=cache,id=pip,target=/root/.cache/pip \
    pip install .

FROM python:3.12.3-slim-bookworm AS runtime

ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN groupadd --system --gid 10001 northstar \
    && useradd --system --uid 10001 --gid northstar --home-dir /nonexistent northstar

COPY --from=builder /opt/venv /opt/venv
COPY --chown=northstar:northstar alembic.ini ./
COPY --chown=northstar:northstar migrations ./migrations
COPY --chown=northstar:northstar scripts ./scripts

USER northstar
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
