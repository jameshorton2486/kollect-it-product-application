@echo off
echo.
echo =============================================
echo    Fixing Nested Folder Structure
echo =============================================
echo.
echo Current directory: %CD%
echo.

cd /d "C:\Users\james\Kollect-It Product Application"

echo Checking for nested structure...

if not exist "desktop-app\desktop-app" (
    echo ERROR: Cannot find desktop-app\desktop-app folder
    echo.
    echo Checking what exists...
    dir desktop-app
    pause
    exit /b 1
)

echo Found nested folders. Moving files up one level...
echo.

xcopy "desktop-app\desktop-app\*" "desktop-app\" /E /I /Y
echo [OK] Copied all files

echo.
echo Removing nested folder...
rmdir /s /q "desktop-app\desktop-app"
echo [OK] Removed desktop-app\desktop-app

echo.
echo Moving nextjs-api to root...
if exist "desktop-app\nextjs-api" (
    xcopy "desktop-app\nextjs-api" "nextjs-api\" /E /I /Y
    rmdir /s /q "desktop-app\nextjs-api"
    echo [OK] Moved nextjs-api
)

echo.
echo =============================================
echo    Checking Results
echo =============================================
echo.
echo Files in desktop-app:
dir /b desktop-app
echo.
echo Files in desktop-app\modules:
dir /b desktop-app\modules
echo.
echo Files in desktop-app\config:
dir /b desktop-app\config
echo.
echo =============================================
echo    DONE - Now run these commands:
echo =============================================
echo.
echo    cd desktop-app
echo    pip install -r requirements.txt
echo    python main.py
echo.
pause
