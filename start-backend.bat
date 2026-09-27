@echo off
cd /d "%~dp0backend"
if not exist "venv\Scripts\python.exe" (
  echo Run setup-first-time.bat first.
  pause
  exit /b 1
)
echo Starting SetuX API on http://localhost:8000
echo Keep this window open.
echo.
venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
pause
