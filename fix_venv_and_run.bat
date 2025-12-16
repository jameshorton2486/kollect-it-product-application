@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File ".\fix_venv_and_run.ps1" %*
endlocal
