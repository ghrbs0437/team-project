import logging
import time
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging_config import configure_logging
from app.crawled_profiles.router import router as crawled_profiles_router
from app.users.router import router as users_router

load_dotenv()
configure_logging()

logger = logging.getLogger("app.http")
health_logger = logging.getLogger("app.health")

app = FastAPI(
    title="Team Project Backend",
    description="Backend API for user CRUD, embeddings, and recommendations.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(crawled_profiles_router)
app.include_router(users_router)


def get_safe_header(request: Request, name: str, max_length: int = 200) -> str:
    value = request.headers.get(name)
    if value is None:
        return "-"
    value = value.strip()
    if not value:
        return "-"
    return value.replace("\r", " ").replace("\n", " ")[:max_length]


@app.middleware("http")
async def log_http_request(request: Request, call_next):
    incoming_request_id = get_safe_header(request, "X-Request-ID", max_length=64)
    request_id = incoming_request_id if incoming_request_id != "-" else uuid4().hex[:12]
    request.state.request_id = request_id

    started_at = time.perf_counter()
    client_host = request.client.host if request.client else "unknown"
    origin = get_safe_header(request, "Origin")
    referer = get_safe_header(request, "Referer")
    user_agent = get_safe_header(request, "User-Agent")

    logger.debug(
        "[REQUEST META] request_id=%s | referer=%s | user_agent=%s",
        request_id,
        referer,
        user_agent,
    )
    logger.info(
        "[REQUEST START] request_id=%s | client=%s | origin=%s | method=%s | path=%s",
        request_id,
        client_host,
        origin,
        request.method,
        request.url.path,
    )

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        logger.exception(
            "[REQUEST FAILED] request_id=%s | client=%s | origin=%s | method=%s | path=%s | duration_ms=%s",
            request_id,
            client_host,
            origin,
            request.method,
            request.url.path,
            duration_ms,
        )
        raise

    duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "[REQUEST END] request_id=%s | client=%s | origin=%s | method=%s | path=%s | status_code=%s | duration_ms=%s",
        request_id,
        client_host,
        origin,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.get("/health", tags=["health"])
def read_health(request: Request) -> dict[str, str]:
    health_logger.info(
        "[HEALTH READ SUCCESS] request_id=%s",
        request.state.request_id,
    )
    return {"status": "ok"}
