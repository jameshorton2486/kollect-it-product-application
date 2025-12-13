@echo off
REM ============================================
REM Fix Nested Folder Structure
REM ============================================
REM Run this from: C:\Users\james\Kollect-It Product Application
REM ============================================

echo.
echo =============================================
echo    Fixing Nested Folder Structure
echo =============================================
echo.

REM Check we're in the right place
if not exist "desktop-app\desktop-app" (
    echo ERROR: Cannot find nested desktop-app\desktop-app folder
    echo Make sure you run this from "Kollect-It Product Application" folder
    pause
    exit /b 1
)

echo Current location: %CD%
echo.
echo This will move files from desktop-app\desktop-app\ up to desktop-app\
echo.
pause

REM Move all contents from nested folder up one level
echo.
echo Moving files...

REM Move folders
if exist "desktop-app\desktop-app\config" (
    xcopy "desktop-app\desktop-app\config" "desktop-app\config\" /E /I /Y >nul
    echo   [OK] config\
)
if exist "desktop-app\desktop-app\modules" (
    xcopy "desktop-app\desktop-app\modules" "desktop-app\modules\" /E /I /Y >nul
    echo   [OK] modules\
)
if exist "desktop-app\desktop-app\templates" (
    xcopy "desktop-app\desktop-app\templates" "desktop-app\templates\" /E /I /Y >nul
    echo   [OK] templates\
)
if exist "desktop-app\desktop-app\logs" (
    xcopy "desktop-app\desktop-app\logs" "desktop-app\logs\" /E /I /Y >nul
    echo   [OK] logs\
)
if exist "desktop-app\desktop-app\processed" (
    xcopy "desktop-app\desktop-app\processed" "desktop-app\processed\" /E /I /Y >nul
    echo   [OK] processed\
)
if exist "desktop-app\desktop-app\temp" (
    xcopy "desktop-app\desktop-app\temp" "desktop-app\temp\" /E /I /Y >nul
    echo   [OK] temp\
)

REM Move files
if exist "desktop-app\desktop-app\main.py" (
    copy "desktop-app\desktop-app\main.py" "desktop-app\" /Y >nul
    echo   [OK] main.py
)
if exist "desktop-app\desktop-app\automation_worker.py" (
    copy "desktop-app\desktop-app\automation_worker.py" "desktop-app\" /Y >nul
    echo   [OK] automation_worker.py
)
if exist "desktop-app\desktop-app\requirements.txt" (
    copy "desktop-app\desktop-app\requirements.txt" "desktop-app\" /Y >nul
    echo   [OK] requirements.txt
)
if exist "desktop-app\desktop-app\start_app.bat" (
    copy "desktop-app\desktop-app\start_app.bat" "desktop-app\" /Y >nul
    echo   [OK] start_app.bat
)
if exist "desktop-app\desktop-app\start_app.sh" (
    copy "desktop-app\desktop-app\start_app.sh" "desktop-app\" /Y >nul
    echo   [OK] start_app.sh
)

REM Move nextjs-api up if it's nested
if exist "desktop-app\nextjs-api" (
    xcopy "desktop-app\nextjs-api" "nextjs-api\" /E /I /Y >nul
    echo   [OK] nextjs-api\
)

REM Move README and gitignore if nested
if exist "desktop-app\README.md" (
    copy "desktop-app\README.md" "README.md" /Y >nul
    echo   [OK] README.md
)
if exist "desktop-app\.gitignore" (
    copy "desktop-app\.gitignore" ".gitignore" /Y >nul
    echo   [OK] .gitignore
)

echo.
echo Cleaning up nested folders...

REM Remove the nested desktop-app folder
if exist "desktop-app\desktop-app" (
    rmdir /s /q "desktop-app\desktop-app"
    echo   [OK] Removed nested desktop-app\desktop-app\
)

REM Remove nested nextjs-api if we moved it
if exist "nextjs-api\route.ts" (
    if exist "desktop-app\nextjs-api" (
        rmdir /s /q "desktop-app\nextjs-api"
        echo   [OK] Removed desktop-app\nextjs-api\
    )
)

REM Remove empty root config folder if it exists and is empty
if exist "config" (
    rmdir "config" 2>nul
    if not exist "config" echo   [OK] Removed empty root config\
)

REM Remove root logs folder if it's a duplicate
if exist "logs" (
    if exist "desktop-app\logs" (
        rmdir "logs" 2>nul
        if not exist "logs" echo   [OK] Removed duplicate root logs\
    )
)

echo.
echo =============================================
echo    Verifying Final Structure
echo =============================================
echo.

echo desktop-app\
if exist "desktop-app\main.py" (echo   [OK] main.py) else (echo   [MISSING] main.py)
if exist "desktop-app\automation_worker.py" (echo   [OK] automation_worker.py) else (echo   [MISSING] automation_worker.py)
if exist "desktop-app\requirements.txt" (echo   [OK] requirements.txt) else (echo   [MISSING] requirements.txt)

echo.
echo desktop-app\config\
if exist "desktop-app\config\config.json" (echo   [OK] config.json) else (echo   [MISSING] config.json)
if exist "desktop-app\config\config.example.json" (echo   [OK] config.example.json) else (echo   [MISSING] config.example.json)
if exist "desktop-app\config\sku_state.json" (echo   [OK] sku_state.json) else (echo   [MISSING] sku_state.json)

echo.
echo desktop-app\modules\
if exist "desktop-app\modules\__init__.py" (echo   [OK] __init__.py) else (echo   [MISSING] __init__.py)
if exist "desktop-app\modules\main.py" (echo   [OK] main.py) else (echo   [MISSING] main.py - check ai_engine.py exists)
if exist "desktop-app\modules\ai_engine.py" (echo   [OK] ai_engine.py) else (echo   [MISSING] ai_engine.py)
if exist "desktop-app\modules\image_processor.py" (echo   [OK] image_processor.py) else (echo   [MISSING] image_processor.py)
if exist "desktop-app\modules\imagekit_uploader.py" (echo   [OK] imagekit_uploader.py) else (echo   [MISSING] imagekit_uploader.py)
if exist "desktop-app\modules\sku_generator.py" (echo   [OK] sku_generator.py) else (echo   [MISSING] sku_generator.py)
if exist "desktop-app\modules\product_publisher.py" (echo   [OK] product_publisher.py) else (echo   [MISSING] product_publisher.py)
if exist "desktop-app\modules\background_remover.py" (echo   [OK] background_remover.py) else (echo   [MISSING] background_remover.py)
if exist "desktop-app\modules\crop_tool.py" (echo   [OK] crop_tool.py) else (echo   [MISSING] crop_tool.py)

echo.
echo desktop-app\templates\
if exist "desktop-app\templates\militaria_template.json" (echo   [OK] militaria_template.json) else (echo   [MISSING] militaria_template.json)
if exist "desktop-app\templates\collectibles_template.json" (echo   [OK] collectibles_template.json) else (echo   [MISSING] collectibles_template.json)
if exist "desktop-app\templates\books_template.json" (echo   [OK] books_template.json) else (echo   [MISSING] books_template.json)
if exist "desktop-app\templates\fineart_template.json" (echo   [OK] fineart_template.json) else (echo   [MISSING] fineart_template.json)

echo.
echo nextjs-api\
if exist "nextjs-api\route.ts" (echo   [OK] route.ts) else (echo   [MISSING] route.ts)

echo.
echo =============================================
echo    DONE!
echo =============================================
echo.
echo Your corrected structure:
echo.
echo   Kollect-It Product Application\
echo   +-- desktop-app\
echo   ^|   +-- main.py
echo   ^|   +-- automation_worker.py
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
echo   1. Open PyCharm terminal
echo   2. cd desktop-app
echo   3. pip install -r requirements.txt
echo   4. python main.py
echo.
pause
