@echo off
title OSCAR Backend (FastAPI :8000)
cd /d "%~dp0.."
set TEMP=%~dp0..\.runtime\tmp
set TMP=%~dp0..\.runtime\tmp
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
