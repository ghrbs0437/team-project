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
    ensure_crawled_profiles_embedded_data_column()
    ensure_users_demo_columns()


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


def ensure_crawled_profiles_embedded_data_column() -> None:
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    if "crawled_profiles" not in table_names:
        return

    column_names = {
        column["name"]
        for column in inspector.get_columns("crawled_profiles")
    }
    if "embedded_data" in column_names:
        return

    with engine.begin() as connection:
        connection.execute(
            text("ALTER TABLE crawled_profiles ADD COLUMN embedded_data JSON")
        )


def ensure_crawled_profiles_source_url_index() -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS "
                "ix_crawled_profiles_source_url "
                "ON crawled_profiles (source_url)"
            )
        )


def ensure_users_demo_columns() -> None:
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    if "users" not in table_names:
        return

    column_names = {
        column["name"]
        for column in inspector.get_columns("users")
    }

    column_definitions = {
        "title": "VARCHAR(255)",
        "source": "VARCHAR(100)",
        "source_url": "VARCHAR(500)",
        "tags": get_json_list_column_definition(),
    }

    with engine.begin() as connection:
        for column_name, column_definition in column_definitions.items():
            if column_name not in column_names:
                connection.execute(
                    text(f"ALTER TABLE users ADD COLUMN {column_name} {column_definition}")
                )

    ensure_users_source_url_index()


def get_json_list_column_definition() -> str:
    if engine.dialect.name == "postgresql":
        return "JSON DEFAULT '[]'::json NOT NULL"
    return "JSON DEFAULT '[]' NOT NULL"


def ensure_users_source_url_index() -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS "
                "ix_users_source_url "
                "ON users (source_url)"
            )
        )
