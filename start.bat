@echo off
TITLE Unified Launcher - Enterprise PM AI Assistant
echo ============================================================
echo Starting All Services for Enterprise Program Management AI Assistant
echo ============================================================
echo.
echo Launching 1. Flask Backend API (Port 5000)...
start "Flask Backend (5000)" cmd /k "start_backend.bat"

echo Launching 2. FastMCP Server (Port 5001)...
start "MCP Server (5001)" cmd /k "start_mcp.bat"

echo Launching 3. Background Email & Streaming Services...
start "Background Services" cmd /k "start_background_services.bat"

echo Launching 4. Angular 17 Frontend (Port 4200)...
start "Angular Frontend (4200)" cmd /k "start_frontend.bat"

echo.
echo ============================================================
echo All services launched in separate windows!
echo   - Backend REST API: http://localhost:5000
echo   - MCP Server:       http://localhost:5001
echo   - Angular App:      http://localhost:4200
echo ============================================================
