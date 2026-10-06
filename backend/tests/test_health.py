from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError
from app.main import app

client = TestClient(app)


def test_health_does_not_depend_on_database():
    with patch("app.main.get_engine", side_effect=AssertionError("must not connect")):
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "streamretain-api"}


def test_readiness_reports_database_failure_without_exposing_credentials():
    with patch("app.main.get_engine", side_effect=OperationalError("secret-url", {}, Exception())):
        response = client.get("/api/readiness")
    assert response.status_code == 503
    assert response.json() == {"detail": "Database is not ready"}


def test_readiness_checks_database():
    engine = MagicMock()
    with patch("app.main.get_engine", return_value=engine):
        response = client.get("/api/readiness")
    assert response.status_code == 200
    assert response.json()["database"] == "connected"
    engine.connect.return_value.__enter__.return_value.execute.assert_called_once()


def test_readiness_handles_missing_configuration():
    with patch("app.main.get_engine", side_effect=ValueError("missing")):
        response = client.get("/api/readiness")
    assert response.status_code == 503
