import os


DEFAULT_DATABASE_URL = "postgresql+psycopg://soma:soma@localhost:5432/soma17ai35"


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
