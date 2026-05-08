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
            "source_url": "https://example.com/profile-1",
            "title": "backend profile",
            "raw_text": "Interested in backend, PostgreSQL, and recommendation.",
            "parsed_json": {"role": "Backend"},
        },
    )

    assert create_response.status_code == 201
    created_profile = create_response.json()
    assert created_profile["id"] == 1
    assert created_profile["source"] == "notion"
    assert created_profile["source_url"] == "https://example.com/profile-1"
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
    list_body = list_response.json()
    assert len(list_body["crawled_profiles"]) == 3
    assert list_body["page"] == 1
    assert list_body["size"] == 20
    assert list_body["total"] == 3
    assert list_body["has_next"] is False


def test_import_json_object_array_payload(client: TestClient) -> None:
    import_response = client.post(
        "/crawled-profiles/import-json",
        json=[
            {
                "title": "profile A | Notion",
                "source": "notion",
                "source_url": "https://example.com/profile-a",
                "raw_text": "first profile text",
            },
            {
                "title": "profile B | Github",
                "source": "github",
                "source_url": "https://github.com/profile-b",
                "raw_text": "second profile text",
                "parsed_json": {"name": "profile B"},
            },
        ],
    )

    assert import_response.status_code == 200
    assert import_response.json() == {"imported_count": 2, "skipped_count": 0}

    list_response = client.get("/crawled-profiles")

    assert list_response.status_code == 200
    profiles = list_response.json()["crawled_profiles"]
    assert len(profiles) == 2
    assert profiles[0]["external_key"] == "https://example.com/profile-a"
    assert profiles[0]["source_url"] == "https://example.com/profile-a"
    assert profiles[1]["parsed_json"] == {"name": "profile B"}


def test_import_json_object_array_payload_skips_existing_source_urls(
    client: TestClient,
) -> None:
    payload = [
        {
            "title": "profile A | Notion",
            "source": "notion",
            "source_url": "https://example.com/profile-a",
            "raw_text": "first profile text",
        },
        {
            "title": "profile A edited | Notion",
            "source": "notion",
            "source_url": "https://example.com/profile-a",
            "raw_text": "edited profile text",
        },
    ]

    import_response = client.post("/crawled-profiles/import-json", json=payload)

    assert import_response.status_code == 200
    assert import_response.json() == {"imported_count": 1, "skipped_count": 1}

    list_response = client.get("/crawled-profiles")

    assert list_response.status_code == 200
    list_body = list_response.json()
    assert len(list_body["crawled_profiles"]) == 1
    assert list_body["total"] == 1


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
    assert len(list_response.json()["crawled_profiles"]) == 3


def test_list_crawled_profiles_supports_pagination_and_search(client: TestClient) -> None:
    import_response = client.post(
        "/crawled-profiles/import-json",
        json=[
            {
                "title": "backend profile",
                "source": "notion",
                "source_url": "https://example.com/backend",
                "raw_text": "FastAPI and PostgreSQL",
            },
            {
                "title": "frontend profile",
                "source": "notion",
                "source_url": "https://example.com/frontend",
                "raw_text": "React and TypeScript",
            },
            {
                "title": "ai profile",
                "source": "notion",
                "source_url": "https://example.com/ai",
                "raw_text": "LLM and recommendation",
            },
        ],
    )
    assert import_response.status_code == 200

    first_page_response = client.get("/crawled-profiles?page=1&size=2")

    assert first_page_response.status_code == 200
    first_page_body = first_page_response.json()
    assert len(first_page_body["crawled_profiles"]) == 2
    assert first_page_body["page"] == 1
    assert first_page_body["size"] == 2
    assert first_page_body["total"] == 3
    assert first_page_body["has_next"] is True

    search_response = client.get("/crawled-profiles?q=react")

    assert search_response.status_code == 200
    search_body = search_response.json()
    assert search_body["total"] == 1
    assert search_body["crawled_profiles"][0]["title"] == "frontend profile"


def test_allows_vite_dev_server_cors_preflight(client: TestClient) -> None:
    response = client.options(
        "/crawled-profiles",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_import_convert_and_read_users_demo_flow(client: TestClient) -> None:
    import_response = client.post(
        "/crawled-profiles/import-json",
        json=[
            {
                "name": "김민준",
                "title": "김민준 | Notion",
                "source": "notion",
                "source_url": "https://example.com/minjun",
                "tags": ["backend", "fastapi"],
                "raw_text": "FastAPI 기반 추천 API 개발에 관심이 있습니다.",
            },
            {
                "name": "이서윤",
                "source": "github",
                "source_url": "https://github.com/seoyun",
                "tags": ["frontend", "react"],
                "raw_text": "React 기반 데모 UI를 빠르게 구현합니다.",
                "parsed_json": {"role": "Frontend"},
            },
        ],
    )
    assert import_response.status_code == 200
    assert import_response.json() == {"imported_count": 2, "skipped_count": 0}

    convert_response = client.post("/crawled-profiles/convert-to-users")

    assert convert_response.status_code == 200
    assert convert_response.json() == {"converted_count": 2, "skipped_count": 0}

    duplicate_convert_response = client.post("/crawled-profiles/convert-to-users")

    assert duplicate_convert_response.status_code == 200
    assert duplicate_convert_response.json() == {"converted_count": 0, "skipped_count": 2}

    users_response = client.get("/users")

    assert users_response.status_code == 200
    users = users_response.json()
    assert len(users) == 2
    assert users[0]["name"] == "김민준"
    assert users[0]["title"] == "김민준 | Notion"
    assert users[0]["source"] == "notion"
    assert users[0]["source_url"] == "https://example.com/minjun"
    assert users[0]["tags"] == ["backend", "fastapi"]
    assert users[0]["introduction"] == "FastAPI 기반 추천 API 개발에 관심이 있습니다."
    assert users[1]["name"] == "이서윤"
    assert users[1]["title"] == "이서윤"
    assert users[1]["role"] == "Frontend"

    read_response = client.get("/users/1")

    assert read_response.status_code == 200
    assert read_response.json()["source_url"] == "https://example.com/minjun"


def test_convert_to_users_is_exposed_in_openapi(client: TestClient) -> None:
    openapi_response = client.get("/openapi.json")

    assert openapi_response.status_code == 200
    assert "/crawled-profiles/convert-to-users" in openapi_response.json()["paths"]
