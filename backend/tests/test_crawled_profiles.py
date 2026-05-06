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


def test_create_and_read_crawled_profile(client: TestClient) -> None:
    create_response = client.post(
        "/crawled-profiles",
        json={
            "source": "notion",
            "external_key": "profile-1",
            "title": "backend profile",
            "raw_text": "Interested in backend, PostgreSQL, and recommendation.",
            "parsed_json": {"role": "Backend"},
        },
    )

    assert create_response.status_code == 201
    created_profile = create_response.json()
    assert created_profile["id"] == 1
    assert created_profile["source"] == "notion"
    assert created_profile["parsed_json"] == {"role": "Backend"}

    read_response = client.get("/crawled-profiles/1")

    assert read_response.status_code == 200
    assert read_response.json()["title"] == "backend profile"


def test_import_json_payload(client: TestClient) -> None:
    import_response = client.post(
        "/crawled-profiles/import-json",
        json={
            "profile A | Notion": ["first profile text", "second profile text"],
            "profile B | Notion": ["third profile text"],
        },
    )

    assert import_response.status_code == 200
    assert import_response.json() == {"imported_count": 3, "skipped_count": 0}

    list_response = client.get("/crawled-profiles")

    assert list_response.status_code == 200
    assert len(list_response.json()) == 3


def test_import_json_payload_skips_existing_external_keys(client: TestClient) -> None:
    payload = {
        "profile A | Notion": ["first profile text", "second profile text"],
        "profile B | Notion": ["third profile text"],
    }

    first_import_response = client.post("/crawled-profiles/import-json", json=payload)
    second_import_response = client.post("/crawled-profiles/import-json", json=payload)

    assert first_import_response.status_code == 200
    assert first_import_response.json() == {"imported_count": 3, "skipped_count": 0}
    assert second_import_response.status_code == 200
    assert second_import_response.json() == {"imported_count": 0, "skipped_count": 3}

    list_response = client.get("/crawled-profiles")

    assert list_response.status_code == 200
    assert len(list_response.json()) == 3
