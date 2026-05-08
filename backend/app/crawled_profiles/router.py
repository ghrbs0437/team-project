from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crawled_profiles import repository
from app.crawled_profiles.schemas import (
    CrawledProfileCreate,
    CrawledProfileImportItem,
    CrawledProfileImportResult,
    CrawledProfileListResponse,
    CrawledProfileRead,
)


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


def build_crawled_profile_import_items(
    payload: dict[str, list[str]] | list[CrawledProfileImportItem],
) -> list[CrawledProfileCreate]:
    if isinstance(payload, list):
        return [
            CrawledProfileCreate(
                source=item.source,
                external_key=item.source_url or item.external_key,
                source_url=item.source_url,
                title=item.title,
                raw_text=item.raw_text,
                parsed_json=item.parsed_json,
            )
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
