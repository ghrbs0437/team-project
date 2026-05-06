from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_database_url


class Base(DeclarativeBase):
    pass


engine = create_engine(get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_database_tables() -> None:
    import app.crawled_profiles.models  # noqa: F401
    import app.users.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    ensure_crawled_profiles_source_url_column()


def ensure_crawled_profiles_source_url_column() -> None:
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    if "crawled_profiles" not in table_names:
        return

    column_names = {
        column["name"]
        for column in inspector.get_columns("crawled_profiles")
    }
    if "source_url" in column_names:
        ensure_crawled_profiles_source_url_index()
        return

    with engine.begin() as connection:
        connection.execute(
            text("ALTER TABLE crawled_profiles ADD COLUMN source_url VARCHAR(500)")
        )
    ensure_crawled_profiles_source_url_index()


def ensure_crawled_profiles_source_url_index() -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS "
                "ix_crawled_profiles_source_url "
                "ON crawled_profiles (source_url)"
            )
        )
