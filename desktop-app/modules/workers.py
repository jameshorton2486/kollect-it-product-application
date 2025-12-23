#!/usr/bin/env python3
"""
Workers Module
Background processing threads for the Kollect-It Product Manager.
"""

import logging
import traceback
from pathlib import Path
from typing import Dict, Any

from PyQt5.QtCore import QThread, pyqtSignal

from .image_processor import ImageProcessor

# Phase 5: Centralized logger for thread errors
logger = logging.getLogger("KollectIt.workers")


# Supported image extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.tiff', '.bmp'}


class ProcessingThread(QThread):
    """Background thread for image processing tasks."""

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, folder_path: str, config: Dict[str, Any], options: Dict[str, Any]):
        super().__init__()
        self.folder_path = folder_path
        self.config = config
        self.options = options

    def run(self) -> None:
        """Execute the image processing task."""
        try:
            processor = ImageProcessor(self.config)
            results: Dict[str, Any] = {"images": [], "errors": []}

            # Get all images in folder
            images = [
                f for f in Path(self.folder_path).iterdir()
                if f.suffix.lower() in IMAGE_EXTENSIONS
            ]

            total = len(images)
            # FIX: Check for empty folder before processing
            if total == 0:
                self.progress.emit(100, "No images found in folder")
                self.finished.emit(results)
                return

            for i, img_path in enumerate(images):
                # Use i+1 to properly show progress (e.g., 1/3, 2/3, 3/3 = 100%)
                progress_pct = int(((i + 1) / total) * 100)
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
            # Phase 5: Enhanced thread error logging
            error_msg = f"ProcessingThread error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error.emit(str(e))


class BackgroundRemovalThread(QThread):
    """Background thread for AI background removal tasks."""

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(
        self, 
        folder_path: str, 
        config: Dict[str, Any], 
        strength: float = 0.8,
        bg_color: str = "#FFFFFF"
    ):
        super().__init__()
        self.folder_path = folder_path
        self.config = config
        self.strength = strength
        self.bg_color = bg_color

    def run(self) -> None:
        """Execute the background removal task."""
        try:
            from .background_remover import BackgroundRemover
            
            remover = BackgroundRemover(self.config)
            
            def progress_callback(current: int, total: int, filename: str) -> None:
                progress = int((current / total) * 100)
                self.progress.emit(progress, f"Processing {current}/{total}: {filename}")

            results = remover.batch_remove(
                self.folder_path,
                progress_callback=progress_callback,
                strength=self.strength,
                bg_color=self.bg_color
            )

            self.progress.emit(100, "Background removal complete!")
            self.finished.emit(results)

        except Exception as e:
            # Phase 5: Enhanced thread error logging
            error_msg = f"BackgroundRemovalThread error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error.emit(str(e))


class UploadThread(QThread):
    """Background thread for ImageKit upload tasks."""

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(
        self, 
        images: list, 
        config: Dict[str, Any], 
        folder: str
    ):
        super().__init__()
        self.images = images
        self.config = config
        self.folder = folder

    def run(self) -> None:
        """Execute the upload task."""
        try:
            from .imagekit_uploader import ImageKitUploader
            
            uploader = ImageKitUploader(self.config)
            uploaded_urls = []
            total = len(self.images)
            
            # Guard against division by zero
            if total == 0:
                self.progress.emit(0, "No images to upload")
                self.finished.emit(uploaded_urls)
                return

            for i, img_path in enumerate(self.images):
                self.progress.emit(
                    int(((i + 1) / total) * 100),
                    f"Uploading {i + 1}/{total}..."
                )

                result = uploader.upload(img_path, self.folder)
                if result and result.get("success"):
                    url = result.get("url")
                    if url:
                        uploaded_urls.append(url)

            self.finished.emit(uploaded_urls)

        except Exception as e:
            # Phase 5: Enhanced thread error logging
            error_msg = f"UploadThread error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error.emit(str(e))
