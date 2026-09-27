@echo off
cd /d "%~dp0frontend"
if not exist "node_modules\" (
  echo Run setup-first-time.bat first.
  pause
  exit /b 1
)
echo Starting SetuX UI...
echo Open the URL shown below (usually http://localhost:5173)
echo Keep this window open.
echo.
call npm run dev
pause
