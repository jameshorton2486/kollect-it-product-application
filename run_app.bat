@echo off
REM Kollect-It Product Application Launcher
REM This script launches the desktop application from the root directory

echo =============================================
echo    Kollect-It Product Automation System
echo =============================================
echo.

REM Check for virtual environment
if exist "%~dp0.venv\Scripts\python.exe" (
    echo Using virtual environment...
    "%~dp0.venv\Scripts\python.exe" "%~dp0desktop-app\main.py"
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

REM Change to desktop-app directory
cd /d "%~dp0desktop-app"

REM Launch the application
echo Starting Kollect-It Desktop App...
python main.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)
