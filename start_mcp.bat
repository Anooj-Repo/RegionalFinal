@echo off
TITLE MCP Server Service (FastMCP - Port 5001)
echo ============================================================
echo Starting FastMCP Server Service on Port 5001...
echo ============================================================
echo.

set PYTHONPATH=.

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

if exist "mcp\mcp_server.py" (
    python mcp\mcp_server.py
) else (
    echo [ERROR] mcp\mcp_server.py not found. Please ensure project files exist.
    pause
)
