@echo off
REM Rebuild venv on stable Python, install deps, and run app
setlocal enableextensions enabledelayedexpansion

echo ============================================
echo Rebuilding venv and launching Kollect-It App
echo ============================================

cd /d "%~dp0"

echo.
echo Moving to repository root...
cd "C:\Users\james\Kollect-It Product Application"

echo.
echo Removing existing .venv (if any)...
if exist .venv (
  rmdir /s /q .venv
)

echo.
echo Creating fresh virtual environment...
python -m venv .venv
if %errorlevel% neq 0 (
  echo Python on PATH may be 3.14 or missing. Trying Python launcher 3.12/3.11...
  py -3.12 -m venv .venv 2>nul || py -3.11 -m venv .venv
)

if not exist .venv (
  echo ERROR: Failed to create virtual environment.
  exit /b 1
)

echo.
echo Activating venv...
call .\.venv\Scripts\activate.bat

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing required packages...
pip install PyQt5 Pillow python-dotenv requests anthropic python-docx numpy

echo.
echo Launching application...
cd desktop-app
python main.py

endlocal
exit /b %errorlevel%
