@echo off
cd /d "%~dp0"
start "SetuX Backend" cmd /k "%~dp0start-backend.bat"
timeout /t 2 /nobreak >nul
start "SetuX Frontend" cmd /k "%~dp0start-frontend.bat"
echo Opened backend and frontend windows.
echo Login at http://localhost:5173  (admin_pune / password)
pause
