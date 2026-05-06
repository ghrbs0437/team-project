from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crawled_profiles import repository
from app.crawled_profiles.schemas import (
    CrawledProfileCreate,
    CrawledProfileImportResult,
    CrawledProfileRead,
)


router = APIRouter(prefix="/crawled-profiles", tags=["crawled-profiles"])


@router.post("", response_model=CrawledProfileRead, status_code=status.HTTP_201_CREATED)
def create_crawled_profile(
    profile_create: CrawledProfileCreate,
    db: Session = Depends(get_db),
) -> CrawledProfileRead:
    return repository.create_crawled_profile(db, profile_create)


@router.get("", response_model=list[CrawledProfileRead])
def list_crawled_profiles(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[CrawledProfileRead]:
    return repository.list_crawled_profiles(db, skip=skip, limit=limit)


@router.post("/import-json", response_model=CrawledProfileImportResult)
def import_crawled_profiles(
    payload: dict[str, list[str]] = Body(...),
    db: Session = Depends(get_db),
) -> CrawledProfileImportResult:
    imported_count = 0
    skipped_count = 0
    for title, raw_text_items in payload.items():
        for index, raw_text in enumerate(raw_text_items):
            external_key = f"{title}#{index}"
            existing_profile = repository.get_crawled_profile_by_external_key(
                db,
                source="json-import",
                external_key=external_key,
            )
            if existing_profile is not None:
                skipped_count += 1
                continue

            profile_create = CrawledProfileCreate(
                source="json-import",
                external_key=external_key,
                title=title,
                raw_text=raw_text,
                parsed_json={"title": title, "index": index},
            )
            repository.create_crawled_profile(db, profile_create)
            imported_count += 1

    return CrawledProfileImportResult(
        imported_count=imported_count,
        skipped_count=skipped_count,
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
