import logging
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app


client = TestClient(app)


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
    with caplog.at_level(logging.INFO):
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

    with caplog.at_level(logging.INFO):
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
