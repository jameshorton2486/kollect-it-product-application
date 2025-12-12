@echo off
cd /d "C:\Users\james\Kollect-It Product Application"

echo.
echo =============================================
echo    Fixing Kollect-It Folder Structure
echo =============================================
echo.

echo Step 1: Moving files from nested desktop-app up one level...

xcopy "desktop-app\desktop-app\*" "desktop-app\" /E /I /Y
echo [DONE] Files copied

echo.
echo Step 2: Moving nextjs-api to root level...

xcopy "desktop-app\nextjs-api" "nextjs-api\" /E /I /Y
echo [DONE] nextjs-api moved

echo.
echo Step 3: Removing nested folders...

rmdir /s /q "desktop-app\desktop-app"
rmdir /s /q "desktop-app\nextjs-api"
echo [DONE] Nested folders removed

echo.
echo Step 4: Removing empty root folders...

rmdir "config" 2>nul
rmdir "logs" 2>nul
rmdir "modules" 2>nul
rmdir "processed" 2>nul
rmdir "temp" 2>nul
rmdir "templates" 2>nul
echo [DONE] Empty folders removed

echo.
echo =============================================
echo    Verifying Structure
echo =============================================
echo.

echo desktop-app contents:
dir /b "desktop-app"

echo.
echo desktop-app\modules contents:
dir /b "desktop-app\modules"

echo.
echo desktop-app\config contents:
dir /b "desktop-app\config"

echo.
echo desktop-app\templates contents:
dir /b "desktop-app\templates"

echo.
echo nextjs-api contents:
dir /b "nextjs-api"

echo.
echo =============================================
echo    COMPLETE!
echo =============================================
echo.
echo Your structure is now:
echo.
echo   Kollect-It Product Application\
echo   +-- desktop-app\
echo   ^|   +-- main.py
echo   ^|   +-- automation_worker.py
echo   ^|   +-- requirements.txt
echo   ^|   +-- config\
echo   ^|   +-- modules\
echo   ^|   +-- templates\
echo   +-- nextjs-api\
echo   ^|   +-- route.ts
echo.
echo NEXT STEPS:
echo   1. Open PyCharm terminal
echo   2. cd desktop-app
echo   3. pip install -r requirements.txt
echo   4. python main.py
echo.
pause