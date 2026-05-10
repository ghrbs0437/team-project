import math
import os

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crawled_profiles import repository
from app.crawled_profiles.models import CrawledProfile
from app.crawled_profiles.schemas import (
    CrawledProfileConvertToUsersResult,
    CrawledProfileCreate,
    CrawledProfileImportItem,
    CrawledProfileImportResult,
    CrawledProfileListResponse,
    CrawledProfileRead,
)
from app.users import repository as users_repository
from app.users.schemas import UserCreate


router = APIRouter(prefix="/crawled-profiles", tags=["crawled-profiles"])


@router.post("", response_model=CrawledProfileRead, status_code=status.HTTP_201_CREATED)
def create_crawled_profile(
    profile_create: CrawledProfileCreate,
    db: Session = Depends(get_db),
) -> CrawledProfileRead:
    return repository.create_crawled_profile(db, profile_create)


@router.get("", response_model=CrawledProfileListResponse)
def list_crawled_profiles(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> CrawledProfileListResponse:
    skip = (page - 1) * size
    crawled_profiles = repository.list_crawled_profiles(
        db,
        skip=skip,
        limit=size,
        search_query=q,
    )
    total = repository.count_crawled_profiles(db, search_query=q)

    return CrawledProfileListResponse(
        crawled_profiles=crawled_profiles,
        page=page,
        size=size,
        total=total,
        has_next=page * size < total,
    )


@router.post("/import-json", response_model=CrawledProfileImportResult)
def import_crawled_profiles(
    payload: dict[str, list[str]] | list[CrawledProfileImportItem] = Body(...),
    db: Session = Depends(get_db),
) -> CrawledProfileImportResult:
    imported_count = 0
    skipped_count = 0

    for profile_create in build_crawled_profile_import_items(payload):
        if is_duplicate_crawled_profile(db, profile_create):
            skipped_count += 1
            continue

        repository.create_crawled_profile(db, profile_create)
        imported_count += 1

    return CrawledProfileImportResult(
        imported_count=imported_count,
        skipped_count=skipped_count,
    )


@router.post("/convert-to-users", response_model=CrawledProfileConvertToUsersResult)
def convert_crawled_profiles_to_users(
    db: Session = Depends(get_db),
) -> CrawledProfileConvertToUsersResult:
    converted_count = 0
    skipped_count = 0

    for crawled_profile in repository.list_all_crawled_profiles(db):
        if is_existing_user_for_crawled_profile(db, crawled_profile):
            skipped_count += 1
            continue

        users_repository.create_user(db, build_user_create_from_crawled_profile(crawled_profile))
        converted_count += 1

    return CrawledProfileConvertToUsersResult(
        converted_count=converted_count,
        skipped_count=skipped_count,
    )


def build_crawled_profile_import_items(
    payload: dict[str, list[str]] | list[CrawledProfileImportItem],
) -> list[CrawledProfileCreate]:
    if isinstance(payload, list):
        return [
            build_crawled_profile_create_from_import_item(item)
            for item in payload
        ]

    profile_creates: list[CrawledProfileCreate] = []
    for title, raw_text_items in payload.items():
        for index, raw_text in enumerate(raw_text_items):
            external_key = f"{title}#{index}"
            profile_creates.append(
                CrawledProfileCreate(
                    source="json-import",
                    external_key=external_key,
                    source_url=None,
                    title=title,
                    raw_text=raw_text,
                    parsed_json={"title": title, "index": index},
                )
            )
    return profile_creates


def build_crawled_profile_create_from_import_item(
    item: CrawledProfileImportItem,
) -> CrawledProfileCreate:
    title = item.title or item.name or "이름 없음"
    parsed_json = dict(item.parsed_json or {})

    if item.name is not None:
        parsed_json["name"] = item.name
    if item.tags:
        parsed_json["tags"] = item.tags

    return CrawledProfileCreate(
        source=item.source,
        external_key=item.source_url or item.external_key,
        source_url=item.source_url,
        title=title,
        raw_text=item.raw_text,
        parsed_json=parsed_json or None,
    )


def build_user_create_from_crawled_profile(crawled_profile: CrawledProfile) -> UserCreate:
    parsed_json = crawled_profile.parsed_json or {}
    tags = normalize_tags(parsed_json.get("tags"))
    name = normalize_text(parsed_json.get("name")) or crawled_profile.title
    role = normalize_text(parsed_json.get("role"))
    introduction = normalize_text(parsed_json.get("introduction")) or crawled_profile.raw_text

    return UserCreate(
        name=name,
        title=crawled_profile.title,
        source=crawled_profile.source,
        source_url=crawled_profile.source_url,
        tags=tags,
        role=role,
        introduction=introduction,
        raw_text=crawled_profile.raw_text,
    )


def is_existing_user_for_crawled_profile(
    db: Session,
    crawled_profile: CrawledProfile,
) -> bool:
    if crawled_profile.source_url is not None:
        existing_user_by_url = users_repository.get_user_by_source_url(
            db,
            crawled_profile.source_url,
        )
        if existing_user_by_url is not None:
            return True

    existing_user_by_content = users_repository.get_user_by_source_title_and_raw_text(
        db,
        source=crawled_profile.source,
        title=crawled_profile.title,
        raw_text=crawled_profile.raw_text,
    )
    return existing_user_by_content is not None


def normalize_tags(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [tag for tag in value if isinstance(tag, str)]


def normalize_text(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def is_duplicate_crawled_profile(
    db: Session,
    profile_create: CrawledProfileCreate,
) -> bool:
    if profile_create.source_url is not None:
        existing_profile_by_url = repository.get_crawled_profile_by_source_url(
            db,
            profile_create.source_url,
        )
        if existing_profile_by_url is not None:
            return True

    if profile_create.external_key is None:
        return False

    existing_profile_by_key = repository.get_crawled_profile_by_external_key(
        db,
        source=profile_create.source,
        external_key=profile_create.external_key,
    )
    return existing_profile_by_key is not None


@router.get("/embedded", response_model=CrawledProfileListResponse)
def search_embedded_crawled_profiles(
    context: str = Query(..., description="Context for vector embedding and similarity search"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> CrawledProfileListResponse:
    if genai is None:
        raise HTTPException(status_code=500, detail="google-generativeai package is not installed.")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not set.")

    genai.configure(api_key=api_key)

    try:
        result = genai.embed_content(
            model="gemini-embedding-001",
            content=context,
            task_type="retrieval_query",
        )
        query_embedding = result['embedding']
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate embedding: {str(e)}"
        )

    profiles = repository.list_all_crawled_profiles(db)
    scored_profiles = []

    def cosine_similarity(v1: list[float], v2: list[float]) -> float:
        dot_product = sum(a * b for a, b in zip(v1, v2))
        magnitude_v1 = math.sqrt(sum(a * a for a in v1))
        magnitude_v2 = math.sqrt(sum(b * b for b in v2))
        if magnitude_v1 == 0 or magnitude_v2 == 0:
            return 0.0
        return dot_product / (magnitude_v1 * magnitude_v2)

    for profile in profiles:
        if profile.embedded_data and isinstance(profile.embedded_data, list):
            sim = cosine_similarity(query_embedding, profile.embedded_data)
            scored_profiles.append((sim, profile))

    scored_profiles.sort(key=lambda x: x[0], reverse=True)

    total = len(scored_profiles)
    skip = (page - 1) * size
    paginated_profiles = [p[1] for p in scored_profiles[skip:skip + size]]

    return CrawledProfileListResponse(
        crawled_profiles=paginated_profiles,
        page=page,
        size=size,
        total=total,
        has_next=page * size < total,
    )


@router.get("/{profile_id}", response_model=CrawledProfileRead)
def read_crawled_profile(
    profile_id: int,
    db: Session = Depends(get_db),
) -> CrawledProfileRead:
    profile = repository.get_crawled_profile(db, profile_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawled profile not found",
        )
    return profile


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_crawled_profile(profile_id: int, db: Session = Depends(get_db)) -> None:
    profile = repository.get_crawled_profile(db, profile_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawled profile not found",
        )
    repository.delete_crawled_profile(db, profile)
