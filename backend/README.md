# Backend

FastAPI, PostgreSQL, user CRUD, embeddings, and recommendation API live here.

## Local Setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

Initialize database tables:

```powershell
.\init-db.bat
```

Run API server:

```powershell
.\dev.bat
```

Health check:

```text
GET http://localhost:8000/health
```

## Test

```powershell
.\test.bat
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

