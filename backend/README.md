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
GET /crawled-profiles/embedded
GET /crawled-profiles/{profile_id}
DELETE /crawled-profiles/{profile_id}
POST /crawled-profiles/import-json
POST /crawled-profiles/convert-to-users
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
    "name": "profile A",
    "title": "profile A | Notion",
    "source": "notion",
    "source_url": "https://example.com/profile-a",
    "tags": ["backend", "fastapi"],
    "raw_text": "first profile text"
  }
]
```

`GET /crawled-profiles` returns a paginated response.

Query parameters:

| Query | Required | Default | Description |
| --- | --- | --- | --- |
| `page` | No | `1` | Page number, starting from 1 |
| `size` | No | `20` | Number of profiles per page, maximum 100 |
| `q` | No | None | Text search keyword for `title`, `raw_text`, `source`, or `source_url` |

Example:

```text
GET /crawled-profiles?page=1&size=20&q=react
```

Response:

```json
{
  "crawled_profiles": [
    {
      "id": 1,
      "source": "notion",
      "external_key": "https://example.com/profile-a",
      "source_url": "https://example.com/profile-a",
      "title": "profile A | Notion",
      "raw_text": "first profile text",
      "parsed_json": {
        "name": "profile A",
        "tags": ["backend", "fastapi"]
      },
      "created_at": "2026-05-12T00:00:00"
    }
  ],
  "page": 1,
  "size": 20,
  "total": 1,
  "has_next": false
}
```

`POST /crawled-profiles/convert-to-users` converts saved crawled profiles into
service-facing users. It skips users that were already converted by `source_url`
or by the same `source + title + raw_text`.

```text
POST /crawled-profiles/convert-to-users
```

Response:

```json
{
  "converted_count": 2,
  "skipped_count": 0
}
```

Converted users include the following demo fields:

| Field | Source |
| --- | --- |
| `name` | `parsed_json.name`, or crawled profile `title` |
| `title` | Crawled profile `title` |
| `source` | Crawled profile `source` |
| `source_url` | Crawled profile `source_url` |
| `tags` | `parsed_json.tags`, or an empty list |
| `introduction` | `parsed_json.introduction`, or crawled profile `raw_text` |
| `raw_text` | Crawled profile `raw_text` |

Demo conversion flow:

```text
POST /crawled-profiles/import-json
POST /crawled-profiles/convert-to-users
GET /users
GET /users/{user_id}
```

`GET /crawled-profiles/embedded` searches crawled profiles by vector similarity.
It generates an embedding from the `context` query using Gemini and compares it
with each profile's saved `embedded_data`.

This endpoint requires `GEMINI_API_KEY` in the backend environment.

Query parameters:

| Query | Required | Default | Description |
| --- | --- | --- | --- |
| `context` | Yes | None | Search context used to create the query embedding |
| `page` | No | `1` | Page number, starting from 1 |
| `size` | No | `20` | Number of profiles per page, maximum 100 |

Example:

```text
GET /crawled-profiles/embedded?context=backend%20fastapi&page=1&size=20
```

Response shape is the same as `GET /crawled-profiles`.
