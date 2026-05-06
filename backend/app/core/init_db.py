from app.core.database import create_database_tables


def main() -> None:
    create_database_tables()
    print("Database tables are ready.")


if __name__ == "__main__":
    main()
