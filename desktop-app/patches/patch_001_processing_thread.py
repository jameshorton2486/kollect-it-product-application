# First, uninstall and reinstall PyQt5
pip uninstall PyQt5 PyQt5-Qt5 PyQt5-sip -y
pip install PyQt5#!/usr/bin/env python3
"""
PATCH: safe_processing_thread.py
Fixes division by zero bug in ProcessingThread.run()

INSTALLATION:
Replace the ProcessingThread class in main.py with this version,
OR apply the fix manually by adding the zero-check.
"""

from pathlib import Path
from PyQt5.QtCore import QThread, pyqtSignal


class ProcessingThread(QThread):
    """Background thread for image processing tasks.

    PATCHED: Fixed division by zero when folder is empty.
    """

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, folder_path: str, config: dict, options: dict):
        super().__init__()
        self.folder_path = folder_path
        self.config = config
        self.options = options

    def run(self):
        try:
            # Import here to avoid circular imports
            from modules.image_processor import ImageProcessor

            processor = ImageProcessor(self.config)
            results = {"images": [], "errors": []}

            # Get all images in folder
            image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.tiff', '.bmp'}
            images = [
                f for f in Path(self.folder_path).iterdir()
                if f.suffix.lower() in image_extensions
            ]

            total = len(images)

            # FIX: Check for empty folder before processing
            if total == 0:
                self.progress.emit(100, "No images found in folder")
                self.finished.emit(results)
                return

            for i, img_path in enumerate(images):
                # FIXED: Safe division - total is guaranteed > 0 here
                progress_pct = int(((i + 1) / total) * 100)  # Also fixed off-by-one
                self.progress.emit(
                    progress_pct,
                    f"Processing: {img_path.name} ({i + 1}/{total})"
                )

                try:
                    result = processor.process_image(
                        str(img_path),
                        self.options
                    )
                    results["images"].append(result)
                except Exception as e:
                    results["errors"].append({
                        "file": img_path.name,
                        "error": str(e)
                    })

            self.progress.emit(100, f"Processing complete! ({total} images)")
            self.finished.emit(results)

        except Exception as e:
            self.error.emit(str(e))


# =============================================================================
# MANUAL PATCH INSTRUCTIONS (if you prefer to edit main.py directly):
# =============================================================================
#
# In main.py, find the ProcessingThread.run() method and make these changes:
#
# 1. After getting the images list, add:
#
#    total = len(images)
#
#    # ADD THIS CHECK:
#    if total == 0:
#        self.progress.emit(100, "No images found in folder")
#        self.finished.emit(results)
#        return
#
# 2. In the loop, change:
#    int((i / total) * 100)
#
#    TO:
#    int(((i + 1) / total) * 100)  # Use i+1 for proper progress
#
# =============================================================================
