# ============================================================================
# Apply Crop Tool Improvements Script
# ============================================================================
# Run this AFTER downloading the crop_tool.py artifact from Claude
# This script will:
# 1. Backup your current crop_tool.py
# 2. Apply the new crop_tool.py
# 3. Update ai_engine.py with the new model name
# ============================================================================

$ProjectDir = "C:\Users\james\Kollect-It Product Application"
$ModulesDir = "$ProjectDir\desktop-app\modules"
$DownloadsDir = "$ProjectDir\work_files"

function Write-Header { param($text) Write-Host "`n$("="*60)" -ForegroundColor Cyan; Write-Host $text -ForegroundColor Cyan; Write-Host "$("="*60)" -ForegroundColor Cyan }
function Write-Success { param($text) Write-Host "✓ $text" -ForegroundColor Green }
function Write-Warning { param($text) Write-Host "⚠ $text" -ForegroundColor Yellow }
function Write-Error { param($text) Write-Host "✗ $text" -ForegroundColor Red }
function Write-Info { param($text) Write-Host "→ $text" -ForegroundColor White }

Write-Header "APPLY CROP TOOL IMPROVEMENTS"

# Check directories exist
if (-not (Test-Path $ModulesDir)) {
    Write-Error "Modules directory not found: $ModulesDir"
    exit 1
}

Set-Location $ModulesDir
Write-Success "Working in: $ModulesDir"

# Step 1: Check if downloaded crop_tool.py exists
Write-Header "STEP 1: Locate Downloaded File"

$downloadedFile = $null
$possibleLocations = @(
    "$DownloadsDir\crop_tool.py",
    "$DownloadsDir\crop tool.py",
    "$DownloadsDir\Crop tool.py"
)

foreach ($loc in $possibleLocations) {
    if (Test-Path $loc) {
        $downloadedFile = $loc
        break
    }
}

if ($downloadedFile) {
    Write-Success "Found downloaded file: $downloadedFile"
}
else {
    Write-Warning "Downloaded crop_tool.py not found in Downloads folder"
    Write-Host ""
    Write-Host "Please download the 'Crop tool' artifact from Claude first!" -ForegroundColor Yellow
    Write-Host "Then run this script again." -ForegroundColor Yellow
    Write-Host ""

    $manual = Read-Host "Or enter the full path to the downloaded file (or press Enter to exit)"
    if ([string]::IsNullOrWhiteSpace($manual)) {
        exit 0
    }
    if (Test-Path $manual) {
        $downloadedFile = $manual
    }
    else {
        Write-Error "File not found: $manual"
        exit 1
    }
}

# Step 2: Backup current crop_tool.py
Write-Header "STEP 2: Backup Current crop_tool.py"

if (Test-Path "crop_tool.py") {
    if (Test-Path "crop_tool_original.py") {
        Write-Info "Backup already exists: crop_tool_original.py"
    }
    else {
        Copy-Item "crop_tool.py" "crop_tool_original.py"
        Write-Success "Created backup: crop_tool_original.py"
    }
}
else {
    Write-Warning "No existing crop_tool.py found (this is unusual)"
}

# Step 3: Copy new crop_tool.py
Write-Header "STEP 3: Install New crop_tool.py"

Copy-Item $downloadedFile "crop_tool.py" -Force
Write-Success "Installed new crop_tool.py"

# Verify the file
$lineCount = (Get-Content "crop_tool.py" | Measure-Object -Line).Lines
Write-Info "New file has $lineCount lines"

if ($lineCount -lt 500) {
    Write-Warning "File seems smaller than expected. Please verify it's the correct file."
}

# Step 4: Update ai_engine.py
Write-Header "STEP 4: Update ai_engine.py Model Name"

$aiEnginePath = "ai_engine.py"
if (Test-Path $aiEnginePath) {
    $content = Get-Content $aiEnginePath -Raw

    $oldModel = 'claude-3-5-sonnet-20240620'
    $newModel = 'claude-sonnet-4-20250514'

    if ($content -match [regex]::Escape($oldModel)) {
        $content = $content -replace [regex]::Escape($oldModel), $newModel
        Set-Content $aiEnginePath $content -NoNewline
        Write-Success "Updated model from '$oldModel' to '$newModel'"
    }
    elseif ($content -match [regex]::Escape($newModel)) {
        Write-Info "Model already updated to '$newModel'"
    }
    else {
        Write-Warning "Could not find model string to update"
        Write-Info "Please manually update line 50 in ai_engine.py"
    }
}
else {
    Write-Error "ai_engine.py not found!"
}

# Step 5: Summary
Write-Header "SUMMARY OF CHANGES"

Write-Host ""
Write-Host "Files modified:" -ForegroundColor White
Write-Host "  1. crop_tool.py - Replaced with improved version" -ForegroundColor Green
Write-Host "  2. crop_tool_original.py - Backup created" -ForegroundColor Green
Write-Host "  3. ai_engine.py - Model name updated" -ForegroundColor Green
Write-Host ""

# Show git status
Write-Header "GIT STATUS"
Set-Location $ProjectDir
git status --short

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Review the changes in VS Code" -ForegroundColor White
Write-Host "  2. Test the application: python desktop-app/main.py" -ForegroundColor White
Write-Host "  3. Commit changes: Run the git-sync-kollect-it.ps1 script" -ForegroundColor White
Write-Host ""

$commit = Read-Host "Would you like to commit these changes now? (y/n)"
if ($commit -eq "y") {
    Write-Header "COMMITTING CHANGES"

    git add .
    git status --short

    $msg = "Improved crop tool with visible handles and restore functionality"
    Write-Info "Commit message: $msg"

    $confirm = Read-Host "Proceed with commit? (y/n)"
    if ($confirm -eq "y") {
        git commit -m $msg

        $push = Read-Host "Push to GitHub? (y/n)"
        if ($push -eq "y") {
            $branch = git branch --show-current
            git push origin $branch
            Write-Success "Pushed to GitHub!"
        }
    }
}

Write-Header "COMPLETE"
