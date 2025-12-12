@echo off
REM ============================================
REM Kollect-It File Organizer for Windows
REM Run this script from the desktop-app folder
REM ============================================

echo.
echo =============================================
echo    Kollect-It File Organizer
echo =============================================
echo.
echo This script will organize files into the
echo correct directory structure.
echo.
echo Current directory: %CD%
echo.
pause

REM Create directories
echo.
echo Creating directories...

if not exist "config" mkdir config
if not exist "modules" mkdir modules
if not exist "templates" mkdir templates
if not exist "logs" mkdir logs
if not exist "processed" mkdir processed
if not exist "temp" mkdir temp

echo   [OK] Directories created
echo.

REM Move config files
echo Moving configuration files to config/...

if exist "config.json" move "config.json" "config\" >nul 2>&1 && echo   [OK] config.json
if exist "config.example.json" move "config.example.json" "config\" >nul 2>&1 && echo   [OK] config.example.json
if exist "sku_state.json" move "sku_state.json" "config\" >nul 2>&1 && echo   [OK] sku_state.json

echo.

REM Move module files
echo Moving module files to modules/...

if exist "image_processor.py" move "image_processor.py" "modules\" >nul 2>&1 && echo   [OK] image_processor.py
if exist "imagekit_uploader.py" move "imagekit_uploader.py" "modules\" >nul 2>&1 && echo   [OK] imagekit_uploader.py
if exist "sku_generator.py" move "sku_generator.py" "modules\" >nul 2>&1 && echo   [OK] sku_generator.py
if exist "ai_engine.py" move "ai_engine.py" "modules\" >nul 2>&1 && echo   [OK] ai_engine.py
if exist "product_publisher.py" move "product_publisher.py" "modules\" >nul 2>&1 && echo   [OK] product_publisher.py
if exist "background_remover.py" move "background_remover.py" "modules\" >nul 2>&1 && echo   [OK] background_remover.py
if exist "crop_tool.py" move "crop_tool.py" "modules\" >nul 2>&1 && echo   [OK] crop_tool.py
if exist "__init__.py" move "__init__.py" "modules\" >nul 2>&1 && echo   [OK] __init__.py

echo.

REM Move template files
echo Moving template files to templates/...

if exist "militaria_template.json" move "militaria_template.json" "templates\" >nul 2>&1 && echo   [OK] militaria_template.json
if exist "collectibles_template.json" move "collectibles_template.json" "templates\" >nul 2>&1 && echo   [OK] collectibles_template.json
if exist "books_template.json" move "books_template.json" "templates\" >nul 2>&1 && echo   [OK] books_template.json
if exist "fineart_template.json" move "fineart_template.json" "templates\" >nul 2>&1 && echo   [OK] fineart_template.json

echo.

REM Move Next.js API file to its own folder
echo Creating nextjs-api folder...

if not exist "..\nextjs-api" mkdir "..\nextjs-api"
if exist "route.ts" move "route.ts" "..\nextjs-api\" >nul 2>&1 && echo   [OK] route.ts moved to ..\nextjs-api\

echo.

REM Files that should stay in root:
REM - main.py
REM - automation_worker.py
REM - requirements.txt
REM - start_app.bat
REM - start_app.sh
REM - README.md

echo =============================================
echo    Organization Complete!
echo =============================================
echo.
echo Directory structure should now be:
echo.
echo   desktop-app/
echo   +-- main.py
echo   +-- automation_worker.py
echo   +-- requirements.txt
echo   +-- start_app.bat
echo   +-- config/
echo   ^|   +-- config.json
echo   ^|   +-- config.example.json
echo   ^|   +-- sku_state.json
echo   +-- modules/
echo   ^|   +-- __init__.py
echo   ^|   +-- image_processor.py
echo   ^|   +-- imagekit_uploader.py
echo   ^|   +-- sku_generator.py
echo   ^|   +-- ai_engine.py
echo   ^|   +-- product_publisher.py
echo   ^|   +-- background_remover.py
echo   ^|   +-- crop_tool.py
echo   +-- templates/
echo   ^|   +-- militaria_template.json
echo   ^|   +-- collectibles_template.json
echo   ^|   +-- books_template.json
echo   ^|   +-- fineart_template.json
echo   +-- logs/
echo   +-- processed/
echo   +-- temp/
echo.
echo Next steps:
echo   1. Edit config/config.json with your API keys
echo   2. Run: pip install -r requirements.txt
echo   3. Run: python main.py
echo.
pause
