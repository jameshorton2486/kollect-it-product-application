@echo off
:: ═══════════════════════════════════════════════════════════════
:: KOLLECT-IT REFACTOR - STEP 2: DELETE PUBLISHING COMPONENTS
:: ═══════════════════════════════════════════════════════════════
:: This script removes files that are out-of-scope for the 
:: intake-only architecture.
:: ═══════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion

echo.
echo ═══════════════════════════════════════════════════════════════
echo   KOLLECT-IT REFACTOR - DELETE PUBLISHING COMPONENTS
echo ═══════════════════════════════════════════════════════════════
echo.
echo   This will DELETE the following:
echo.
echo   FILES:
echo     - desktop-app\modules\product_publisher.py
echo     - run_app.bat (root)
echo     - run_app.ps1 (root)
echo     - pyrightconfig.json (root)
echo.
echo   FOLDERS:
echo     - nextjs-api\ (entire folder)
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

set "PROJECT=C:\Users\james\Kollect-It Product Application"

:: Confirm before proceeding
set /p CONFIRM="Have you run the backup script first? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo.
    echo [ABORTED] Please run 01-backup-project.bat first.
    pause
    exit /b 0
)

echo.
echo Starting deletion...
echo.

:: Track what was deleted
set "DELETED=0"
set "SKIPPED=0"

:: Delete product_publisher.py
echo [1/5] Checking product_publisher.py...
if exist "%PROJECT%\desktop-app\modules\product_publisher.py" (
    del /Q "%PROJECT%\desktop-app\modules\product_publisher.py"
    echo       ✅ DELETED: product_publisher.py
    set /a DELETED+=1
) else (
    echo       ⚠️  NOT FOUND: product_publisher.py (already deleted?)
    set /a SKIPPED+=1
)

:: Delete nextjs-api folder
echo [2/5] Checking nextjs-api folder...
if exist "%PROJECT%\nextjs-api" (
    rmdir /S /Q "%PROJECT%\nextjs-api"
    echo       ✅ DELETED: nextjs-api\ folder
    set /a DELETED+=1
) else (
    echo       ⚠️  NOT FOUND: nextjs-api\ (already deleted?)
    set /a SKIPPED+=1
)

:: Delete root run_app.bat
echo [3/5] Checking run_app.bat (root)...
if exist "%PROJECT%\run_app.bat" (
    del /Q "%PROJECT%\run_app.bat"
    echo       ✅ DELETED: run_app.bat
    set /a DELETED+=1
) else (
    echo       ⚠️  NOT FOUND: run_app.bat (already deleted?)
    set /a SKIPPED+=1
)

:: Delete root run_app.ps1
echo [4/5] Checking run_app.ps1 (root)...
if exist "%PROJECT%\run_app.ps1" (
    del /Q "%PROJECT%\run_app.ps1"
    echo       ✅ DELETED: run_app.ps1
    set /a DELETED+=1
) else (
    echo       ⚠️  NOT FOUND: run_app.ps1 (already deleted?)
    set /a SKIPPED+=1
)

:: Delete root pyrightconfig.json
echo [5/5] Checking pyrightconfig.json (root)...
if exist "%PROJECT%\pyrightconfig.json" (
    del /Q "%PROJECT%\pyrightconfig.json"
    echo       ✅ DELETED: pyrightconfig.json
    set /a DELETED+=1
) else (
    echo       ⚠️  NOT FOUND: pyrightconfig.json (already deleted?)
    set /a SKIPPED+=1
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo   DELETION COMPLETE
echo ═══════════════════════════════════════════════════════════════
echo.
echo   Files deleted: %DELETED%
echo   Files skipped: %SKIPPED%
echo.
echo ═══════════════════════════════════════════════════════════════
echo   NEXT STEPS (Use CURSOR):
echo ═══════════════════════════════════════════════════════════════
echo.
echo   Open desktop-app\main.py in Cursor and remove:
echo.
echo   1. Line ~60: Delete the ProductPublisher import
echo   2. Lines 1121-1126: Delete Original Price field
echo   3. Lines 1207-1208: Delete auto_publish_check
echo   4. Lines 1210-1214: Delete use_production_check  
echo   5. Lines 1242-1255: Delete publish_btn
echo   6. Lines 1864-1942: Delete publish_product() method
echo.
echo   See the Cursor Instructions document for details.
echo.
echo ═══════════════════════════════════════════════════════════════

echo.
pause
