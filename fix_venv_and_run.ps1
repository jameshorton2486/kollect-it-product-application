# Fix and Rebuild venv, then run the app
# Run from repo root: C:\Users\james\Kollect-It Product Application

param(
  [switch]$NoRun
)

$ErrorActionPreference = 'Stop'

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Kollect-It: Rebuild venv and Run" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot
$desktopApp = Join-Path $projectRoot 'desktop-app'
$venvPath = Join-Path $projectRoot '.venv'
$pythonExe = $null

function Stop-PythonProcesses {
  Write-Host "Stopping python/pythonw processes (if any)" -ForegroundColor Yellow
  Get-Process -Name python, pythonw -ErrorAction SilentlyContinue | ForEach-Object {
    try { $_ | Stop-Process -Force -ErrorAction Stop } catch {}
  }
}

function Remove-Venv {
  if (Test-Path $venvPath) {
    Write-Host "Removing existing .venv (if unlocked)" -ForegroundColor Yellow
    try {
      # Try PowerShell remove first
      Remove-Item -LiteralPath $venvPath -Recurse -Force -ErrorAction Stop
      Write-Host "Removed .venv via PowerShell" -ForegroundColor Green
    }
    catch {
      Write-Host "PowerShell removal failed, trying cmd rmdir..." -ForegroundColor DarkYellow
      try {
        cmd /c rmdir /s /q "$venvPath"
        if (Test-Path $venvPath) { throw "cmd rmdir did not remove .venv" }
        Write-Host "Removed .venv via cmd rmdir" -ForegroundColor Green
      }
      catch {
        Write-Host "Still locked. Attempting rename to .venv_old..." -ForegroundColor DarkYellow
        $old = Join-Path $projectRoot (".venv_old_" + (Get-Date -Format 'yyyyMMdd_HHmmss'))
        try { Move-Item -LiteralPath $venvPath -Destination $old -Force; Write-Host "Renamed to $old" -ForegroundColor Green }
        catch {
          Write-Host "Could not rename .venv. Please close VS Code or reboot and re-run." -ForegroundColor Red
          throw
        }
      }
    }
  }
  else {
    Write-Host ".venv not present (nothing to remove)" -ForegroundColor Gray
  }
}

function Resolve-Python312 {
  # Prefer 'py -3.12' if available
  try {
    $ver = (& py -3.12 -c "import sys; print(sys.version)" 2>$null)
    if ($LASTEXITCODE -eq 0 -and $ver) {
      return 'py -3.12'
    }
  }
  catch {}
  # Fallback to current python
  $ver2 = (& python -c "import sys; print(sys.version)" 2>$null)
  if ($LASTEXITCODE -eq 0 -and $ver2) { return 'python' }
  throw "No suitable Python found (3.12+ recommended)."
}

function New-Venv {
  param([string]$py)
  Write-Host "Creating venv with: $py" -ForegroundColor Yellow
  & $py -m venv .venv
  if ($LASTEXITCODE -ne 0) { throw "venv creation failed" }
}

function Activate-Venv {
  $activate = Join-Path $venvPath 'Scripts/Activate.ps1'
  if (-not (Test-Path $activate)) { throw "Activate.ps1 not found at $activate" }
  & $activate
}

function Install-Requirements {
  Write-Host "Upgrading pip/setuptools/wheel" -ForegroundColor Yellow
  python -m pip install --upgrade pip setuptools wheel
  Write-Host "Installing requirements from desktop-app/requirements.txt" -ForegroundColor Yellow
  pip install -r "$desktopApp/requirements.txt"
}

function Verify-PyQt {
  Write-Host "Verifying PyQt5 import" -ForegroundColor Yellow
  python - <<'PY'
  import sys
  try:
  import PyQt5
  from PIL import Image
  print('OK: PyQt5+Pillow present on', sys.executable)
  except Exception as e:
  print('ERROR:', e)
  sys.exit(1)
  PY
}

try {
  Stop-PythonProcesses
  Remove-Venv
  $pythonExe = Resolve-Python312
  New-Venv -py $pythonExe
  Activate-Venv
  Install-Requirements
  Verify-PyQt

  if (-not $NoRun) {
    Write-Host "Launching app..." -ForegroundColor Cyan
    Set-Location $desktopApp
    python main.py
  }
  else {
    Write-Host "NoRun specified: skipping app launch." -ForegroundColor Yellow
  }
}
catch {
  Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
  exit 1
}
