@echo off
REM Logging Service Startup Script (Command Prompt)
REM Usage: run.bat

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo Starting logging-service on port 8006...
flask run --port 8006
