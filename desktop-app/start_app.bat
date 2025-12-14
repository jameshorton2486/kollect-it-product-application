@echo off
REM Kollect-It Desktop App Launcher for Windows
REM Double-click this file to start the application

echo =============================================
echo    Kollect-It Product Automation System
echo =============================================
echo.

REM Check for virtual environment in parent directory
if exist "%~dp0..\.venv\Scripts\python.exe" (
    echo Using virtual environment...
    "%~dp0..\.venv\Scripts\python.exe" "%~dp0main.py"
    exit /b
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

REM Change to script directory
cd /d "%~dp0"

REM Check if dependencies are installed
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Launch the application
echo Starting Kollect-It Desktop App...
python main.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)
