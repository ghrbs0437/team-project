# Backend

FastAPI, PostgreSQL, user CRUD, embeddings, and recommendation API live here.

## Local Setup

```cmd
cd C:\Users\USER\Github\team-project\backend
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

## Run

Start local PostgreSQL:

```cmd
cd C:\Users\USER\Github\team-project
docker compose up -d db
```

Initialize database tables:

```cmd
cd C:\Users\USER\Github\team-project\backend
init-db.bat
```

Run API server:

```cmd
cd C:\Users\USER\Github\team-project\backend
dev.bat
```

Swagger UI:

```text
http://localhost:8000/docs
```

Health check:

```text
GET http://localhost:8000/health
```

## Test

```cmd
test.bat
```

## Current API

```text
GET /health
POST /users
GET /users
GET /users/{user_id}
PATCH /users/{user_id}
DELETE /users/{user_id}
POST /crawled-profiles
GET /crawled-profiles
GET /crawled-profiles/{profile_id}
DELETE /crawled-profiles/{profile_id}
POST /crawled-profiles/import-json
```

