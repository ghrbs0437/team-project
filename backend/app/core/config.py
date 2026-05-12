import os

from dotenv import load_dotenv

load_dotenv()

DEFAULT_DATABASE_URL = "postgresql+psycopg://soma:soma@localhost:5432/soma17ai35"


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def get_gemini_api_key() -> str:
    key = os.getenv("GEMINI_API_KEY", "")
    if not key:
        raise RuntimeError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
    return key


def get_openai_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY", "")
    if not key:
        raise RuntimeError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
    return key


def get_upstage_api_key() -> str:
    key = os.getenv("UPSTAGE_API_KEY", "")
    if not key:
        raise RuntimeError("UPSTAGE_API_KEY 환경변수가 설정되지 않았습니다.")
    return key


def get_upstage_base_url() -> str:
    return os.getenv("UPSTAGE_BASE_URL", "https://api.upstage.ai/v1")


def get_upstage_model() -> str:
    return os.getenv("UPSTAGE_MODEL", "solar-pro2")


def get_neo4j_uri() -> str:
    return os.getenv("NEO4J_URI", "bolt://localhost:7687")


def get_neo4j_user() -> str:
    return os.getenv("NEO4J_USER", "neo4j")


def get_neo4j_password() -> str:
    return os.getenv("NEO4J_PASSWORD", "soma_neo4j")
