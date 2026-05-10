from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.crawled_profiles.router import router as crawled_profiles_router
from app.users.router import router as users_router
from dotenv import load_dotenv

load_dotenv()

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


@app.get("/health", tags=["health"])
def read_health() -> dict[str, str]:
    return {"status": "ok"}
