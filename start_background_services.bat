@echo off
TITLE Background Email & Streaming Services
echo ============================================================
echo Starting Background Email Poller (5-10s loop) & Streaming Agent...
echo ============================================================
echo.

set PYTHONPATH=.

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

if exist "mcp\background_email.py" (
    python mcp\background_email.py
) else (
    echo [ERROR] mcp\background_email.py not found. Please ensure project files exist.
    pause
)
