@echo off
:: ═══════════════════════════════════════════════════════════════
:: KOLLECT-IT REFACTOR - STEP 1: BACKUP PROJECT
:: ═══════════════════════════════════════════════════════════════
:: Run this FIRST before making any changes
:: ═══════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion

echo.
echo ═══════════════════════════════════════════════════════════════
echo   KOLLECT-IT REFACTOR - BACKUP SCRIPT
echo ═══════════════════════════════════════════════════════════════
echo.

:: Set paths
set "PROJECT=C:\Users\james\Kollect-It Product Application"
set "BACKUP_ROOT=C:\Users\james\Downloads\kollect-it-backups"

:: Create timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set "TIMESTAMP=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,2%-%datetime:~10,2%"

set "BACKUP_FOLDER=%BACKUP_ROOT%\backup-%TIMESTAMP%"

:: Check if project exists
if not exist "%PROJECT%" (
    echo [ERROR] Project folder not found: %PROJECT%
    echo Please update the PROJECT path in this script.
    pause
    exit /b 1
)

:: Create backup directory
echo [1/3] Creating backup directory...
if not exist "%BACKUP_ROOT%" mkdir "%BACKUP_ROOT%"
mkdir "%BACKUP_FOLDER%"

:: Copy project (excluding node_modules, __pycache__, .git)
echo [2/3] Copying project files (this may take a moment)...
echo       From: %PROJECT%
echo       To:   %BACKUP_FOLDER%
echo.

robocopy "%PROJECT%" "%BACKUP_FOLDER%" /E /XD node_modules __pycache__ .git .venv venv /XF *.pyc /NFL /NDL /NJH /NJS /nc /ns /np

:: Verify backup
echo.
echo [3/3] Verifying backup...
if exist "%BACKUP_FOLDER%\desktop-app\main.py" (
    echo.
    echo ═══════════════════════════════════════════════════════════════
    echo   ✅ BACKUP COMPLETE!
    echo ═══════════════════════════════════════════════════════════════
    echo.
    echo   Location: %BACKUP_FOLDER%
    echo.
    echo   Backup includes:
    dir /b "%BACKUP_FOLDER%"
    echo.
    echo ═══════════════════════════════════════════════════════════════
    echo   NEXT STEP: Run 02-delete-publishing.bat
    echo ═══════════════════════════════════════════════════════════════
) else (
    echo.
    echo [WARNING] Backup may be incomplete. Please verify manually.
)

echo.
pause
