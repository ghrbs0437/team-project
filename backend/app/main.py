from fastapi import FastAPI

from app.users.router import router as users_router


app = FastAPI(
    title="Team Project Backend",
    description="Backend API for user CRUD, embeddings, and recommendations.",
    version="0.1.0",
)

app.include_router(users_router)


@app.get("/health", tags=["health"])
def read_health() -> dict[str, str]:
    return {"status": "ok"}
