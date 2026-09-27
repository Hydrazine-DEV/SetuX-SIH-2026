@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo  SetuX first-time setup
echo ========================================
echo.

where python >nul 2>&1
if errorlevel 1 (
  echo ERROR: Python is not on PATH.
  echo Install Python 3.10+ from https://www.python.org/downloads/
  echo Tick "Add Python to PATH" during install.
  pause
  exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
  echo ERROR: Node.js / npm is not on PATH.
  echo Install Node.js LTS from https://nodejs.org/
  pause
  exit /b 1
)

echo [1/4] Creating Python virtual environment...
if not exist "backend\venv\Scripts\python.exe" (
  python -m venv backend\venv
)

echo [2/4] Installing Python packages...
backend\venv\Scripts\python.exe -m pip install --upgrade pip
backend\venv\Scripts\python.exe -m pip install -r backend\requirements.txt
if errorlevel 1 (
  echo ERROR: pip install failed.
  pause
  exit /b 1
)

echo [3/4] Seeding demo database...
backend\venv\Scripts\python.exe scripts\seed_database.py
if errorlevel 1 (
  echo ERROR: database seed failed.
  pause
  exit /b 1
)

echo [4/4] Installing frontend packages (this can take a few minutes)...
pushd frontend
call npm install
if errorlevel 1 (
  popd
  echo ERROR: npm install failed.
  pause
  exit /b 1
)
popd

echo.
echo Setup complete.
echo Next:
echo   1. Run start-backend.bat
echo   2. Run start-frontend.bat
echo   3. Open http://localhost:5173
echo   Login: admin_pune  /  password
echo.
pause
