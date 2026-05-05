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

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Health check:

```text
GET http://localhost:8000/health
```

## Test

```powershell
pytest
```

