@echo off
TITLE Enterprise PM AI Assistant - Setup Script
echo ============================================================
echo Setting up Enterprise Program Management AI Assistant
echo ============================================================
echo.

:: 1. Backend & MCP Python Virtual Environment Setup
echo [1/4] Setting up Python virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

call venv\Scripts\activate.bat

echo [2/4] Installing Backend & MCP Python dependencies...
if exist "backend\requirements.txt" (
    pip install -r backend\requirements.txt
) else (
    echo Note: backend\requirements.txt dependencies will be installed upon creation.
)

:: 2. Database & Data Seeding Setup
echo [3/4] Initializing Databases and Synthetic Datasets (5 Project Lifecycle Phases)...
if exist "backend\app\db\seed.py" (
    python backend\app\db\seed.py
)

:: 3. Frontend Angular Setup
echo [4/4] Installing Frontend Node dependencies...
if exist "frontend\package.json" (
    cd frontend
    call npm install
    cd ..
) else (
    echo Note: frontend npm dependencies will be installed upon creation.
)

echo.
echo ============================================================
echo Setup Completed Successfully!
echo You can now start individual services using:
echo   - start_backend.bat
echo   - start_mcp.bat
echo   - start_background_services.bat
echo   - start_frontend.bat
echo Or start all services together using:
echo   - start.bat
echo ============================================================
pause
