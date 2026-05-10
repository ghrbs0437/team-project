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

## Docker Compose

From the project root, the backend can also run as a container with PostgreSQL:

```cmd
docker compose up --build backend
```

Container port `8000` is exposed to `http://localhost:8000` by default.

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

`POST /crawled-profiles/import-json` skips duplicated crawled profiles by
`source_url` first, then `source + external_key`, and returns both counts:

```json
{
  "imported_count": 0,
  "skipped_count": 297
}
```

It supports the current crawled JSON shape:

```json
{
  "profile A | Notion": ["first profile text"]
}
```

It also supports object arrays with source URLs:

```json
[
  {
    "title": "profile A | Notion",
    "source": "notion",
    "source_url": "https://example.com/profile-a",
    "raw_text": "first profile text"
  }
]
```
