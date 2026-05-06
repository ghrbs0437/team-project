@echo off
setlocal

set "BACKEND_ROOT=%~dp0"
set "PYTHON_PATH=%BACKEND_ROOT%.venv\Scripts\python.exe"

if not exist "%PYTHON_PATH%" (
    echo Virtual environment not found. Run: python -m venv .venv
    exit /b 1
)

"%PYTHON_PATH%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000
