from sqlalchemy import select
from sqlalchemy.orm import Session

from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate


def create_user(db: Session, user_create: UserCreate) -> User:
    user = User(**user_create.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_source_url(db: Session, source_url: str) -> User | None:
    statement = select(User).where(User.source_url == source_url)
    return db.scalars(statement).first()


def get_user_by_source_title_and_raw_text(
    db: Session,
    source: str | None,
    title: str | None,
    raw_text: str | None,
) -> User | None:
    statement = select(User).where(
        User.source == source,
        User.title == title,
        User.raw_text == raw_text,
    )
    return db.scalars(statement).first()


def list_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    statement = select(User).offset(skip).limit(limit).order_by(User.id)
    return list(db.scalars(statement).all())


def update_user(db: Session, user: User, user_update: UserUpdate) -> User:
    update_data = user_update.model_dump(exclude_unset=True)
    for field_name, field_value in update_data.items():
        setattr(user, field_name, field_value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()
