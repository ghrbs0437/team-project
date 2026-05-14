import logging
from collections.abc import Generator
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app


client = TestClient(app)


@contextmanager
def capture_app_logs(caplog) -> Generator[None, None, None]:
    app_logger = logging.getLogger("app")
    app_logger.addHandler(caplog.handler)
    try:
        yield
    finally:
        app_logger.removeHandler(caplog.handler)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def api_client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_successful_request_logs_to_server_only(caplog) -> None:
    with caplog.at_level(logging.INFO, logger="app"), capture_app_logs(caplog):
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "[REQUEST START]" not in response.text
    assert "[HEALTH READ SUCCESS]" not in response.text

    messages = [record.getMessage() for record in caplog.records]
    assert any("[REQUEST START]" in message for message in messages)
    assert any(
        "[REQUEST END]" in message and "status_code=200" in message
        for message in messages
    )
    assert any("[HEALTH READ SUCCESS]" in message for message in messages)


def test_request_id_connects_http_and_route_logs(
    api_client: TestClient,
    caplog,
) -> None:
    request_id = "test-request-123"

    with caplog.at_level(logging.INFO, logger="app"), capture_app_logs(caplog):
        response = api_client.post(
            "/users",
            json={"name": "log-test"},
            headers={
                "X-Request-ID": request_id,
                "Origin": "http://localhost:5173",
                "Referer": "http://localhost:5173/",
                "User-Agent": "pytest-agent",
            },
        )

    assert response.status_code == 201
    assert response.headers["X-Request-ID"] == request_id

    messages = [record.getMessage() for record in caplog.records]
    assert any(
        "[REQUEST START]" in message
        and f"request_id={request_id}" in message
        and "origin=http://localhost:5173" in message
        for message in messages
    )
    assert not any(
        "[REQUEST START]" in message and "user_agent=pytest-agent" in message
        for message in messages
    )
    assert any(
        "[USERS CREATE SUCCESS]" in message
        and f"request_id={request_id}" in message
        for message in messages
    )
    assert any(
        "[REQUEST END]" in message
        and f"request_id={request_id}" in message
        and "status_code=201" in message
        for message in messages
    )


def test_blank_request_id_header_generates_new_request_id(caplog) -> None:
    with caplog.at_level(logging.INFO, logger="app"), capture_app_logs(caplog):
        response = client.get("/health", headers={"X-Request-ID": "   "})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"]
    assert (
        response.headers["X-Request-ID"].strip()
        == response.headers["X-Request-ID"]
    )


def test_empty_search_query_logs_search_not_applied(
    api_client: TestClient,
    caplog,
) -> None:
    with caplog.at_level(logging.INFO, logger="app"), capture_app_logs(caplog):
        response = api_client.get("/crawled-profiles?q=")

    assert response.status_code == 200
    messages = [record.getMessage() for record in caplog.records]
    assert any(
        "[CRAWLED_PROFILES LIST SUCCESS]" in message
        and "q_present=False" in message
        for message in messages
    )


def test_empty_user_patch_logs_no_updated_fields(
    api_client: TestClient,
    caplog,
) -> None:
    create_response = api_client.post("/users", json={"name": "patch-log-test"})
    user_id = create_response.json()["id"]

    with caplog.at_level(logging.INFO, logger="app"), capture_app_logs(caplog):
        response = api_client.patch(f"/users/{user_id}", json={})

    assert response.status_code == 200
    messages = [record.getMessage() for record in caplog.records]
    assert any(
        "[USERS UPDATE SUCCESS]" in message
        and f"user_id={user_id}" in message
        and "updated_fields=none" in message
        for message in messages
    )
