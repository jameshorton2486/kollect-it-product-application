@echo off
REM ============================================
REM Kollect-It Project Setup Script
REM Run from: Kollect-It Product Application\desktop-app\
REM ============================================

echo.
echo =============================================
echo    Kollect-It Project Setup
echo =============================================
echo.
echo Current directory: %CD%
echo.

REM Check if we're in the right place
if not exist "desktop-app" (
    echo ERROR: Cannot find 'desktop-app' folder.
    echo Make sure you run this from the root project folder.
    pause
    exit /b 1
)

echo Found desktop-app folder. Starting setup...
echo.

REM Remove the malformed {desktop-app folder if it exists
if exist "{desktop-app" (
    echo Removing malformed {desktop-app folder...
    rmdir /s /q "{desktop-app"
    echo   [OK] Removed {desktop-app
)

REM Create subdirectories inside desktop-app
echo.
echo Creating directories in desktop-app...

if not exist "desktop-app\config" mkdir "desktop-app\config"
if not exist "desktop-app\modules" mkdir "desktop-app\modules"
if not exist "desktop-app\templates" mkdir "desktop-app\templates"
if not exist "desktop-app\logs" mkdir "desktop-app\logs"
if not exist "desktop-app\processed" mkdir "desktop-app\processed"
if not exist "desktop-app\temp" mkdir "desktop-app\temp"

echo   [OK] All directories created
echo.

REM Check what's inside desktop-app and organize if needed
echo Checking desktop-app contents...

REM Move config files if they're in root of desktop-app
if exist "desktop-app\config.json" (
    move "desktop-app\config.json" "desktop-app\config\" >nul 2>&1
    echo   [OK] Moved config.json to config/
)
if exist "desktop-app\config.example.json" (
    move "desktop-app\config.example.json" "desktop-app\config\" >nul 2>&1
    echo   [OK] Moved config.example.json to config/
)
if exist "desktop-app\sku_state.json" (
    move "desktop-app\sku_state.json" "desktop-app\config\" >nul 2>&1
    echo   [OK] Moved sku_state.json to config/
)

REM Move module files if they're in root of desktop-app
if exist "desktop-app\image_processor.py" (
    move "desktop-app\image_processor.py" "desktop-app\modules\" >nul 2>&1
    echo   [OK] Moved image_processor.py to modules/
)
if exist "desktop-app\imagekit_uploader.py" (
    move "desktop-app\imagekit_uploader.py" "desktop-app\modules\" >nul 2>&1
    echo   [OK] Moved imagekit_uploader.py to modules/
)
if exist "desktop-app\sku_generator.py" (
    move "desktop-app\sku_generator.py" "desktop-app\modules\" >nul 2>&1
    echo   [OK] Moved sku_generator.py to modules/
)
if exist "desktop-app\ai_engine.py" (
    move "desktop-app\ai_engine.py" "desktop-app\modules\" >nul 2>&1
    echo   [OK] Moved ai_engine.py to modules/
)
if exist "desktop-app\product_publisher.py" (
    move "desktop-app\product_publisher.py" "desktop-app\modules\" >nul 2>&1
    echo   [OK] Moved product_publisher.py to modules/
)
if exist "desktop-app\background_remover.py" (
    move "desktop-app\background_remover.py" "desktop-app\modules\" >nul 2>&1
    echo   [OK] Moved background_remover.py to modules/
)
if exist "desktop-app\crop_tool.py" (
    move "desktop-app\crop_tool.py" "desktop-app\modules\" >nul 2>&1
    echo   [OK] Moved crop_tool.py to modules/
)
if exist "desktop-app\__init__.py" (
    move "desktop-app\__init__.py" "desktop-app\modules\" >nul 2>&1
    echo   [OK] Moved __init__.py to modules/
)

REM Move template files if they're in root of desktop-app
if exist "desktop-app\militaria_template.json" (
    move "desktop-app\militaria_template.json" "desktop-app\templates\" >nul 2>&1
    echo   [OK] Moved militaria_template.json to templates/
)
if exist "desktop-app\collectibles_template.json" (
    move "desktop-app\collectibles_template.json" "desktop-app\templates\" >nul 2>&1
    echo   [OK] Moved collectibles_template.json to templates/
)
if exist "desktop-app\books_template.json" (
    move "desktop-app\books_template.json" "desktop-app\templates\" >nul 2>&1
    echo   [OK] Moved books_template.json to templates/
)
if exist "desktop-app\fineart_template.json" (
    move "desktop-app\fineart_template.json" "desktop-app\templates\" >nul 2>&1
    echo   [OK] Moved fineart_template.json to templates/
)

REM Move route.ts to nextjs-api if it's in desktop-app
if exist "desktop-app\route.ts" (
    if not exist "nextjs-api" mkdir "nextjs-api"
    move "desktop-app\route.ts" "nextjs-api\" >nul 2>&1
    echo   [OK] Moved route.ts to nextjs-api/
)

echo.
echo =============================================
echo    Verifying Structure
echo =============================================
echo.

REM Verify structure
echo Checking desktop-app\config\...
if exist "desktop-app\config\config.json" (echo   [OK] config.json) else (echo   [MISSING] config.json)
if exist "desktop-app\config\config.example.json" (echo   [OK] config.example.json) else (echo   [MISSING] config.example.json)

echo.
echo Checking desktop-app\modules\...
if exist "desktop-app\modules\image_processor.py" (echo   [OK] image_processor.py) else (echo   [MISSING] image_processor.py)
if exist "desktop-app\modules\imagekit_uploader.py" (echo   [OK] imagekit_uploader.py) else (echo   [MISSING] imagekit_uploader.py)
if exist "desktop-app\modules\sku_generator.py" (echo   [OK] sku_generator.py) else (echo   [MISSING] sku_generator.py)
if exist "desktop-app\modules\ai_engine.py" (echo   [OK] ai_engine.py) else (echo   [MISSING] ai_engine.py)
if exist "desktop-app\modules\product_publisher.py" (echo   [OK] product_publisher.py) else (echo   [MISSING] product_publisher.py)
if exist "desktop-app\modules\background_remover.py" (echo   [OK] background_remover.py) else (echo   [MISSING] background_remover.py)
if exist "desktop-app\modules\crop_tool.py" (echo   [OK] crop_tool.py) else (echo   [MISSING] crop_tool.py)

echo.
echo Checking desktop-app\templates\...
if exist "desktop-app\templates\militaria_template.json" (echo   [OK] militaria_template.json) else (echo   [MISSING] militaria_template.json)
if exist "desktop-app\templates\collectibles_template.json" (echo   [OK] collectibles_template.json) else (echo   [MISSING] collectibles_template.json)
if exist "desktop-app\templates\books_template.json" (echo   [OK] books_template.json) else (echo   [MISSING] books_template.json)
if exist "desktop-app\templates\fineart_template.json" (echo   [OK] fineart_template.json) else (echo   [MISSING] fineart_template.json)

echo.
echo Checking desktop-app root files...
if exist "desktop-app\main.py" (echo   [OK] main.py) else (echo   [MISSING] main.py)
if exist "desktop-app\automation_worker.py" (echo   [OK] automation_worker.py) else (echo   [MISSING] automation_worker.py)
if exist "desktop-app\requirements.txt" (echo   [OK] requirements.txt) else (echo   [MISSING] requirements.txt)

echo.
echo Checking nextjs-api\...
if exist "nextjs-api\route.ts" (echo   [OK] route.ts) else (echo   [MISSING] route.ts)

echo.
echo =============================================
echo    Setup Complete!
echo =============================================
echo.
echo Your project structure:
echo.
echo   Kollect-It Product Application\
echo   +-- desktop-app\
echo   ^|   +-- main.py              (main application)
echo   ^|   +-- automation_worker.py (background daemon)
echo   ^|   +-- requirements.txt
echo   ^|   +-- config\
echo   ^|   +-- modules\
echo   ^|   +-- templates\
echo   ^|   +-- logs\
echo   ^|   +-- processed\
echo   ^|   +-- temp\
echo   +-- nextjs-api\
echo   ^|   +-- route.ts
echo   +-- README.md
echo   +-- .gitignore
echo.
echo NEXT STEPS:
echo   1. cd desktop-app
echo   2. pip install -r requirements.txt
echo   3. Edit config\config.json with your API keys
echo   4. python main.py
echo.
pause
