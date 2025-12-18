# add_clear_all_button.ps1
# Run this from: C:\Users\james\Kollect-It Product Application\desktop-app
# Usage: .\add_clear_all_button.ps1

$mainFile = "main.py"

if (-not (Test-Path $mainFile)) {
    Write-Host "ERROR: main.py not found. Run this from the desktop-app folder." -ForegroundColor Red
    exit 1
}

Write-Host "Adding 'Clear All' button to main.py..." -ForegroundColor Cyan

# Read the file
$content = Get-Content $mainFile -Raw

# ============================================
# CHANGE 1: Add Clear All button after Optimize button
# ============================================
$oldButtonSection = @'
        self.optimize_btn = QPushButton("⚡ Optimize All")
        self.optimize_btn.setObjectName("optimizeBtn")
        self.optimize_btn.setProperty("variant", "secondary")
        self.optimize_btn.setEnabled(False)
        self.optimize_btn.clicked.connect(self.optimize_images)
        img_actions.addWidget(self.optimize_btn)

        images_layout.addLayout(img_actions)
'@

$newButtonSection = @'
        self.optimize_btn = QPushButton("⚡ Optimize All")
        self.optimize_btn.setObjectName("optimizeBtn")
        self.optimize_btn.setProperty("variant", "secondary")
        self.optimize_btn.setEnabled(False)
        self.optimize_btn.clicked.connect(self.optimize_images)
        img_actions.addWidget(self.optimize_btn)

        self.clear_all_btn = QPushButton("🗑 Clear All")
        self.clear_all_btn.setObjectName("clearAllBtn")
        self.clear_all_btn.setProperty("variant", "utility")
        self.clear_all_btn.setEnabled(False)
        self.clear_all_btn.clicked.connect(self.clear_all_images)
        img_actions.addWidget(self.clear_all_btn)

        images_layout.addLayout(img_actions)
'@

if ($content -match [regex]::Escape('self.optimize_btn = QPushButton("⚡ Optimize All")')) {
    $content = $content.Replace($oldButtonSection, $newButtonSection)
    Write-Host "  ✓ Added Clear All button definition" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Could not find optimize button section - may already be modified" -ForegroundColor Yellow
}

# ============================================
# CHANGE 2: Add clear_all_btn to __init__ attributes
# ============================================
$oldInit = 'self.optimize_btn = None'
$newInit = @'
self.optimize_btn = None
        self.clear_all_btn = None
'@

if ($content -match [regex]::Escape($oldInit) -and -not ($content -match 'self.clear_all_btn = None')) {
    $content = $content.Replace($oldInit, $newInit)
    Write-Host "  ✓ Added clear_all_btn to __init__" -ForegroundColor Green
}

# ============================================
# CHANGE 3: Add clear_all_images method (before optimize_images)
# ============================================
$clearAllMethod = @'

    def clear_all_images(self):
        """Clear all images from the current view (does NOT delete files)."""
        if not self.current_images:
            return
        
        confirm = QMessageBox.question(
            self, "Clear All Images",
            f"Remove all {len(self.current_images)} images from view?\n\n"
            "This does NOT delete files from disk.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.current_images = []
            self.selected_images = []
            self._rebuild_image_grid()
            self.log("Cleared all images from view", "info")
            self.clear_all_btn.setEnabled(False)
            self.optimize_btn.setEnabled(False)
            self.crop_all_btn.setEnabled(False)
            self.remove_bg_btn.setEnabled(False)
            logger.info("User cleared all images from view")

'@

# Insert before optimize_images method
$optimizeMethodStart = '    def optimize_images(self):'
if (-not ($content -match 'def clear_all_images')) {
    $content = $content.Replace($optimizeMethodStart, "$clearAllMethod$optimizeMethodStart")
    Write-Host "  ✓ Added clear_all_images method" -ForegroundColor Green
} else {
    Write-Host "  ⚠ clear_all_images method already exists" -ForegroundColor Yellow
}

# ============================================
# CHANGE 4: Enable clear_all_btn in load_images_from_folder
# ============================================
$oldLoadEnd = 'self.optimize_btn.setEnabled(len(self.current_images) > 0)'
$newLoadEnd = @'
self.optimize_btn.setEnabled(len(self.current_images) > 0)
        if self.clear_all_btn:
            self.clear_all_btn.setEnabled(len(self.current_images) > 0)
'@

if ($content -match [regex]::Escape($oldLoadEnd) -and -not ($content -match 'self.clear_all_btn.setEnabled')) {
    $content = $content.Replace($oldLoadEnd, $newLoadEnd)
    Write-Host "  ✓ Added clear_all_btn enable in load_images_from_folder" -ForegroundColor Green
}

# ============================================
# CHANGE 5: Update on_processing_finished to show deleted count
# ============================================
$oldFinishedLog = 'self.log(f"Optimization complete: {success_count} images processed", "success")'
$newFinishedLog = @'
deleted_count = sum(1 for img in results.get("images", []) if img.get("original_deleted", False))
        self.log(f"Optimization complete: {success_count} images processed, {deleted_count} originals deleted", "success")
'@

if ($content -match [regex]::Escape($oldFinishedLog) -and -not ($content -match 'deleted_count = sum')) {
    $content = $content.Replace($oldFinishedLog, $newFinishedLog)
    Write-Host "  ✓ Updated on_processing_finished to show deleted count" -ForegroundColor Green
}

# ============================================
# Save the modified file
# ============================================
Set-Content $mainFile $content -NoNewline -Encoding UTF8
Write-Host "`n✅ main.py updated successfully!" -ForegroundColor Green

Write-Host "`n📋 Changes made:" -ForegroundColor Cyan
Write-Host "   1. Added '🗑 Clear All' button next to 'Optimize All'"
Write-Host "   2. Added clear_all_images() method"
Write-Host "   3. Button enables when images are loaded"
Write-Host "   4. Shows deleted count in optimization log"

Write-Host "`n🔄 Now copy the updated image_processor.py:" -ForegroundColor Yellow
Write-Host "   Copy-Item `"`$env:USERPROFILE\Downloads\image_processor.py`" `"modules\image_processor.py`" -Force"

Write-Host "`n🚀 Then restart the app:" -ForegroundColor Yellow
Write-Host "   python main.py"
