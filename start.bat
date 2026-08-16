@echo off
:: Change directory to the folder where start.bat is located
cd /d "%~dp0"

echo ===================================================
echo   Starting HealthGuard AI (Backend + Frontend)
echo ===================================================

start "HealthGuard AI - FastAPI Backend" cmd /k "cd /d "%~dp0" && python -m uvicorn backend.main:app --port 8000 --reload"

timeout /t 3 /nobreak >nul

start "HealthGuard AI - React Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo Servers started successfully!
echo   - Backend API: http://localhost:8000/docs
echo   - React UI:    http://localhost:5173/
echo.
