from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.database import get_db
from app.main import app


class UnavailableDatabase:
    def execute(self, _statement):
        raise OperationalError("SELECT 1", {}, ConnectionError("connection refused"))


def unavailable_database():
    yield UnavailableDatabase()


def test_readiness_returns_503_with_request_id_when_database_is_unavailable() -> None:
    app.dependency_overrides[get_db] = unavailable_database
    try:
        with TestClient(app) as client:
            response = client.get("/health/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "service": "northstar-core-api",
        "environment": "development",
        "dependency": "postgresql",
    }
    assert response.headers["x-request-id"]
