import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Header, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import engine, get_db
from app.logging_config import configure_logging
from app.metrics import HTTP_DURATION, HTTP_REQUESTS
from app.schemas import (
    AccountResponse,
    HealthResponse,
    ReadinessFailureResponse,
    TransferCreate,
    TransferResponse,
)
from app.services import create_transfer, list_accounts, list_transfers

configure_logging()
logger = logging.getLogger("northstar.api")


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("service_started")
    yield
    engine.dispose()
    logger.info("service_stopped")


app = FastAPI(
    title="Northstar Core Banking API",
    version="0.1.0",
    description="Accounts, transfers, ledger entries, health, and metrics for Northstar Bank.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Idempotency-Key", "X-Request-ID"],
)


@app.middleware("http")
async def request_observability(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    started = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - started
    route = request.scope.get("route")
    path = getattr(route, "path", request.url.path)
    response.headers["X-Request-ID"] = request_id
    HTTP_REQUESTS.labels(request.method, path, str(response.status_code)).inc()
    HTTP_DURATION.labels(request.method, path).observe(duration)
    logger.info(
        "request_completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": path,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
        },
    )
    return response


@app.get("/health/live", response_model=HealthResponse, tags=["Operations"])
def liveness() -> HealthResponse:
    return HealthResponse(status="ok", service=settings.app_name, environment=settings.app_env)


@app.get(
    "/health/ready",
    response_model=HealthResponse,
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ReadinessFailureResponse}},
    tags=["Operations"],
)
def readiness(db: Annotated[Session, Depends(get_db)]) -> HealthResponse | Response:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.warning("readiness_dependency_unavailable", extra={"dependency": "postgresql"})
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "service": settings.app_name,
                "environment": settings.app_env,
                "dependency": "postgresql",
            },
        )
    return HealthResponse(status="ready", service=settings.app_name, environment=settings.app_env)


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/api/v1/accounts", response_model=list[AccountResponse], tags=["Accounts"])
def accounts(db: Annotated[Session, Depends(get_db)]) -> list[AccountResponse]:
    return list_accounts(db)


@app.get("/api/v1/transfers", response_model=list[TransferResponse], tags=["Transfers"])
def transfers(
    db: Annotated[Session, Depends(get_db)],
    account_id: Annotated[uuid.UUID | None, Query()] = None,
) -> list[TransferResponse]:
    return list_transfers(db, account_id)


@app.post(
    "/api/v1/transfers",
    response_model=TransferResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Transfers"],
)
def transfer(
    payload: TransferCreate,
    idempotency_key: Annotated[str, Header(min_length=8, max_length=128)],
    db: Annotated[Session, Depends(get_db)],
) -> TransferResponse:
    return create_transfer(db, payload, idempotency_key)
