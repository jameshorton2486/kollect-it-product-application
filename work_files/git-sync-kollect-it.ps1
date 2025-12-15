# ============================================================================
# Kollect-It Git Analysis and Sync Script
# ============================================================================
# This script will:
# 1. Analyze your current Git status
# 2. Show any uncommitted changes
# 3. Help you commit and push to GitHub
# 4. Merge your feature branch to main
# ============================================================================

# Set the project directory
$ProjectDir = "C:\Users\james\Kollect-It Product Application"

# Colors for output
function Write-Header { param($text) Write-Host "`n$("="*70)" -ForegroundColor Cyan; Write-Host $text -ForegroundColor Cyan; Write-Host "$("="*70)" -ForegroundColor Cyan }
function Write-Success { param($text) Write-Host "✓ $text" -ForegroundColor Green }
function Write-Warning { param($text) Write-Host "⚠ $text" -ForegroundColor Yellow }
function Write-Error { param($text) Write-Host "✗ $text" -ForegroundColor Red }
function Write-Info { param($text) Write-Host "→ $text" -ForegroundColor White }

# Navigate to project directory
Write-Header "STEP 1: Checking Project Directory"
if (Test-Path $ProjectDir) {
    Set-Location $ProjectDir
    Write-Success "Found project at: $ProjectDir"
} else {
    Write-Error "Project directory not found: $ProjectDir"
    Write-Info "Please update the `$ProjectDir variable at the top of this script"
    exit 1
}

# Check if it's a Git repository
Write-Header "STEP 2: Verifying Git Repository"
if (Test-Path ".git") {
    Write-Success "Git repository found"
} else {
    Write-Error "This is not a Git repository!"
    Write-Info "Run: git init"
    exit 1
}

# Show current branch
Write-Header "STEP 3: Current Branch Status"
$currentBranch = git branch --show-current
Write-Info "Current branch: $currentBranch"

# List all branches
Write-Host "`nAll branches:" -ForegroundColor White
git branch -a

# Show remote info
Write-Header "STEP 4: Remote Repository Info"
git remote -v
if ($LASTEXITCODE -ne 0) {
    Write-Warning "No remote repository configured"
}

# Fetch latest from remote (without merging)
Write-Header "STEP 5: Fetching Latest from GitHub"
Write-Info "Fetching updates from remote..."
git fetch --all 2>&1

# Show status
Write-Header "STEP 6: Git Status (Uncommitted Changes)"
$status = git status --porcelain
if ($status) {
    Write-Warning "You have uncommitted changes:"
    Write-Host ""
    git status --short
    Write-Host ""
    
    # Categorize changes
    $untracked = git ls-files --others --exclude-standard
    $modified = git diff --name-only
    $staged = git diff --cached --name-only
    
    if ($untracked) {
        Write-Host "Untracked (new) files:" -ForegroundColor Yellow
        $untracked | ForEach-Object { Write-Host "  + $_" -ForegroundColor Green }
    }
    if ($modified) {
        Write-Host "Modified files:" -ForegroundColor Yellow
        $modified | ForEach-Object { Write-Host "  M $_" -ForegroundColor Yellow }
    }
    if ($staged) {
        Write-Host "Staged for commit:" -ForegroundColor Yellow
        $staged | ForEach-Object { Write-Host "  S $_" -ForegroundColor Cyan }
    }
} else {
    Write-Success "Working directory is clean - no uncommitted changes"
}

# Check if branch is ahead/behind remote
Write-Header "STEP 7: Sync Status with GitHub"
$ahead = git rev-list --count "origin/$currentBranch..HEAD" 2>$null
$behind = git rev-list --count "HEAD..origin/$currentBranch" 2>$null

if ($ahead -gt 0) {
    Write-Warning "Your local branch is $ahead commit(s) AHEAD of GitHub"
    Write-Info "You need to PUSH to sync"
}
if ($behind -gt 0) {
    Write-Warning "Your local branch is $behind commit(s) BEHIND GitHub"
    Write-Info "You need to PULL to sync"
}
if ($ahead -eq 0 -and $behind -eq 0) {
    Write-Success "Branch is in sync with GitHub"
}

# Show recent commits
Write-Header "STEP 8: Recent Commits (Last 5)"
git log --oneline -5

# Summary and recommendations
Write-Header "SUMMARY & RECOMMENDATIONS"

$needsAction = $false

if ($status) {
    $needsAction = $true
    Write-Warning "ACTION NEEDED: You have uncommitted changes"
    Write-Host @"

To commit your changes, run:
  git add .
  git commit -m "Your commit message here"

"@ -ForegroundColor White
}

if ($ahead -gt 0) {
    $needsAction = $true
    Write-Warning "ACTION NEEDED: Push your commits to GitHub"
    Write-Host @"

To push to GitHub, run:
  git push origin $currentBranch

"@ -ForegroundColor White
}

if ($behind -gt 0) {
    $needsAction = $true
    Write-Warning "ACTION NEEDED: Pull latest changes from GitHub"
    Write-Host @"

To pull from GitHub, run:
  git pull origin $currentBranch

"@ -ForegroundColor White
}

if ($currentBranch -ne "main" -and $currentBranch -ne "master") {
    Write-Warning "You are on branch '$currentBranch', not 'main'"
    Write-Host @"

To merge this branch into main:
  1. First commit and push all changes on this branch
  2. Then run the merge script (Part 2 below)

"@ -ForegroundColor White
}

if (-not $needsAction -and ($currentBranch -eq "main" -or $currentBranch -eq "master")) {
    Write-Success "Everything is synced and you're on the main branch!"
}

Write-Header "WHAT WOULD YOU LIKE TO DO?"
Write-Host @"

Choose an option:
  [1] Commit all changes and push to current branch ($currentBranch)
  [2] Merge current branch to main and push
  [3] View detailed diff of changes
  [4] Exit (do nothing)

"@ -ForegroundColor White

$choice = Read-Host "Enter your choice (1-4)"

switch ($choice) {
    "1" {
        Write-Header "COMMITTING AND PUSHING CHANGES"
        
        # Stage all changes
        Write-Info "Staging all changes..."
        git add .
        
        # Get commit message
        $commitMsg = Read-Host "Enter commit message"
        if ([string]::IsNullOrWhiteSpace($commitMsg)) {
            $commitMsg = "Update application files - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
        }
        
        # Commit
        Write-Info "Committing..."
        git commit -m $commitMsg
        
        # Push
        Write-Info "Pushing to GitHub..."
        git push origin $currentBranch
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Successfully pushed to GitHub!"
        } else {
            Write-Error "Push failed. You may need to pull first or set upstream."
            Write-Info "Try: git push -u origin $currentBranch"
        }
    }
    "2" {
        Write-Header "MERGING TO MAIN BRANCH"
        
        # First, commit any uncommitted changes
        if ($status) {
            Write-Info "First, committing current changes..."
            git add .
            $commitMsg = Read-Host "Enter commit message for current changes"
            if ([string]::IsNullOrWhiteSpace($commitMsg)) {
                $commitMsg = "Update before merge - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
            }
            git commit -m $commitMsg
            git push origin $currentBranch
        }
        
        # Switch to main
        Write-Info "Switching to main branch..."
        git checkout main
        if ($LASTEXITCODE -ne 0) {
            Write-Info "Trying 'master' branch instead..."
            git checkout master
        }
        
        # Pull latest main
        Write-Info "Pulling latest main branch..."
        git pull origin main 2>$null
        if ($LASTEXITCODE -ne 0) {
            git pull origin master 2>$null
        }
        
        # Merge feature branch
        Write-Info "Merging '$currentBranch' into main..."
        git merge $currentBranch -m "Merge $currentBranch into main"
        
        if ($LASTEXITCODE -eq 0) {
            # Push main
            Write-Info "Pushing main to GitHub..."
            git push origin main 2>$null
            if ($LASTEXITCODE -ne 0) {
                git push origin master
            }
            Write-Success "Successfully merged and pushed to main!"
            
            # Ask about deleting feature branch
            $deleteBranch = Read-Host "Delete the feature branch '$currentBranch'? (y/n)"
            if ($deleteBranch -eq "y") {
                git branch -d $currentBranch
                git push origin --delete $currentBranch 2>$null
                Write-Success "Feature branch deleted"
            }
        } else {
            Write-Error "Merge conflict detected!"
            Write-Info "Please resolve conflicts manually in VS Code, then:"
            Write-Info "  git add ."
            Write-Info "  git commit -m 'Resolve merge conflicts'"
            Write-Info "  git push origin main"
        }
    }
    "3" {
        Write-Header "DETAILED DIFF"
        git diff
        Write-Host "`nStaged changes:" -ForegroundColor Cyan
        git diff --cached
    }
    "4" {
        Write-Info "Exiting without changes"
    }
    default {
        Write-Warning "Invalid choice"
    }
}

Write-Header "SCRIPT COMPLETE"
Write-Host "Run this script again anytime to check your Git status.`n"
