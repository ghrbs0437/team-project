from fastapi import FastAPI


app = FastAPI(
    title="Team Project Backend",
    description="Backend API for user CRUD, embeddings, and recommendations.",
    version="0.1.0",
)


@app.get("/health", tags=["health"])
def read_health() -> dict[str, str]:
    return {"status": "ok"}
