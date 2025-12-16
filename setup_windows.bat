@echo off
REM Kollect-It Product Manager - Windows Setup Script
REM Run this from the project root directory

echo ============================================
echo Kollect-It Product Manager Setup
echo ============================================
echo.

REM Check if Python 3.12 or 3.11 is available
py -3.12 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_VERSION=3.12
    echo Found Python 3.12
) else (
    py -3.11 --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_VERSION=3.11
        echo Found Python 3.11
    ) else (
        echo ERROR: Python 3.11 or 3.12 not found!
        echo Please install from https://python.org
        echo Avoid Python 3.14 - it has compatibility issues.
        pause
        exit /b 1
    )
)

REM Check if .venv exists
if exist .venv (
    echo.
    echo WARNING: .venv folder already exists.
    set /p RECREATE="Delete and recreate? (y/n): "
    if /i "%RECREATE%"=="y" (
        echo Removing old .venv...
        rmdir /s /q .venv
    ) else (
        echo Keeping existing .venv
        goto :activate
    )
)

REM Create virtual environment
echo.
echo Creating virtual environment with Python %PYTHON_VERSION%...
py -%PYTHON_VERSION% -m venv .venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

:activate
REM Activate virtual environment
echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install core dependencies (skip rembg to avoid build issues)
echo.
echo Installing core dependencies...
pip install PyQt5 Pillow python-dotenv requests anthropic python-docx numpy

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo To run the application:
echo   1. Open PowerShell in this directory
echo   2. Run: .\.venv\Scripts\Activate.ps1
echo   3. Run: cd desktop-app
echo   4. Run: python main.py
echo.
echo Optional: To install AI background removal (requires Visual Studio Build Tools):
echo   pip install rembg
echo.
pause
