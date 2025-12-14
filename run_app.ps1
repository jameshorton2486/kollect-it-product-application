# Kollect-It Product Application Launcher (PowerShell)
# This script launches the desktop application from the root directory

Write-Host "============================================="
Write-Host "   Kollect-It Product Automation System"
Write-Host "============================================="
Write-Host ""

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $scriptPath ".venv\Scripts\python.exe"
$mainPy = Join-Path $scriptPath "desktop-app\main.py"

# Check for virtual environment
if (Test-Path $venvPython) {
    Write-Host "Using virtual environment..."
    & $venvPython $mainPy
    exit $LASTEXITCODE
}

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python version: $pythonVersion"
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH"
    Write-Host "Please install Python 3.9+ from https://python.org"
    exit 1
}

# Change to desktop-app directory
Set-Location "$scriptPath\desktop-app"

# Launch the application
Write-Host "Starting Kollect-It Desktop App..."
python main.py
