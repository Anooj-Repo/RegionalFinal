@echo off
TITLE Frontend Web App (Angular 17 - Port 4200)
echo ============================================================
echo Starting Angular 17 Standalone Web Application on Port 4200...
echo ============================================================
echo.

if exist "frontend" (
    cd frontend
    call npm start
) else (
    echo [ERROR] frontend folder not found. Please ensure frontend project exists.
    pause
)
