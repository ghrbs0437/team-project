from sqlalchemy import select
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


def list_crawled_profiles(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[CrawledProfile]:
    statement = select(CrawledProfile).offset(skip).limit(limit).order_by(CrawledProfile.id)
    return list(db.scalars(statement).all())


def delete_crawled_profile(db: Session, profile: CrawledProfile) -> None:
    db.delete(profile)
    db.commit()
