from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.crawled_profiles.models import CrawledProfile
from app.crawled_profiles.schemas import CrawledProfileCreate


def create_crawled_profile(
    db: Session,
    profile_create: CrawledProfileCreate,
) -> CrawledProfile:
    profile = CrawledProfile(**profile_create.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def get_crawled_profile(db: Session, profile_id: int) -> CrawledProfile | None:
    return db.get(CrawledProfile, profile_id)


def get_crawled_profile_by_external_key(
    db: Session,
    source: str,
    external_key: str,
) -> CrawledProfile | None:
    statement = select(CrawledProfile).where(
        CrawledProfile.source == source,
        CrawledProfile.external_key == external_key,
    )
    return db.scalars(statement).first()


def get_crawled_profile_by_source_url(
    db: Session,
    source_url: str,
) -> CrawledProfile | None:
    statement = select(CrawledProfile).where(CrawledProfile.source_url == source_url)
    return db.scalars(statement).first()


def list_crawled_profiles(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search_query: str | None = None,
) -> list[CrawledProfile]:
    statement = build_crawled_profiles_statement(search_query)
    statement = statement.offset(skip).limit(limit).order_by(CrawledProfile.id)
    return list(db.scalars(statement).all())


def list_all_crawled_profiles(db: Session) -> list[CrawledProfile]:
    statement = select(CrawledProfile).order_by(CrawledProfile.id)
    return list(db.scalars(statement).all())


def count_crawled_profiles(
    db: Session,
    search_query: str | None = None,
) -> int:
    filtered_profiles = build_crawled_profiles_statement(search_query).subquery()
    statement = select(func.count()).select_from(filtered_profiles)
    return db.scalar(statement) or 0


def build_crawled_profiles_statement(search_query: str | None = None):
    statement = select(CrawledProfile)

    if search_query:
        search_pattern = f"%{search_query}%"
        statement = statement.where(
            or_(
                CrawledProfile.title.ilike(search_pattern),
                CrawledProfile.raw_text.ilike(search_pattern),
                CrawledProfile.source.ilike(search_pattern),
                CrawledProfile.source_url.ilike(search_pattern),
            )
        )

    return statement


def delete_crawled_profile(db: Session, profile: CrawledProfile) -> None:
    db.delete(profile)
    db.commit()
