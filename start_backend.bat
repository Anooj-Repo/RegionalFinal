@echo off
TITLE Backend API Service (Flask - Port 5000)
echo ============================================================
echo Starting Flask REST API Backend Service on Port 5000...
echo ============================================================
echo.

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

if exist "backend\run.py" (
    python backend\run.py
) else (
    echo [ERROR] backend\run.py not found. Please ensure project files exist.
    pause
)
