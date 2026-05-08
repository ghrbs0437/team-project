from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app


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
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_create_and_read_user(client: TestClient) -> None:
    create_response = client.post(
        "/users",
        json={
            "name": "junhee",
            "title": "Backend profile",
            "source": "manual",
            "source_url": "https://example.com/users/junhee",
            "tags": ["backend", "fastapi"],
            "role": "Backend",
            "introduction": "Responsible for FastAPI and PostgreSQL.",
            "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
            "interests": ["AI", "Recommendation"],
            "raw_text": "Responsible for backend CRUD and vector similarity.",
        },
    )

    assert create_response.status_code == 201
    created_user = create_response.json()
    assert created_user["id"] == 1
    assert created_user["name"] == "junhee"
    assert created_user["title"] == "Backend profile"
    assert created_user["source"] == "manual"
    assert created_user["source_url"] == "https://example.com/users/junhee"
    assert created_user["tags"] == ["backend", "fastapi"]
    assert created_user["tech_stack"] == ["Python", "FastAPI", "PostgreSQL"]

    read_response = client.get("/users/1")

    assert read_response.status_code == 200
    assert read_response.json()["name"] == "junhee"


def test_list_update_and_delete_user(client: TestClient) -> None:
    client.post("/users", json={"name": "kanghoon", "role": "Frontend"})

    list_response = client.get("/users")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    update_response = client.patch(
        "/users/1",
        json={
            "role": "UI Designer",
            "tags": ["frontend", "design"],
            "interests": ["UX", "Design System"],
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["role"] == "UI Designer"
    assert update_response.json()["tags"] == ["frontend", "design"]
    assert update_response.json()["interests"] == ["UX", "Design System"]

    delete_response = client.delete("/users/1")
    assert delete_response.status_code == 204

    read_deleted_response = client.get("/users/1")
    assert read_deleted_response.status_code == 404
