#!/usr/bin/env python3
"""
PATCH: validate_images_before_upload.py
Adds validation before uploading to ImageKit.

INSTALLATION:
Replace upload_to_imagekit() in main.py with this version.
"""

import os
from pathlib import Path
from typing import List, Tuple

from PyQt5.QtWidgets import QApplication, QMessageBox


# Maximum file size for upload (10 MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

# Supported formats for ImageKit
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.tiff', '.bmp'}


def validate_image_for_upload(image_path: str) -> Tuple[bool, str]:
    """
    Validate a single image before upload.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    path = Path(image_path)
    
    # Check file exists
    if not path.exists():
        return False, f"File not found: {path.name}"
    
    # Check file is readable
    if not os.access(image_path, os.R_OK):
        return False, f"Cannot read file: {path.name}"
    
    # Check file extension
    if path.suffix.lower() not in SUPPORTED_FORMATS:
        return False, f"Unsupported format: {path.suffix}"
    
    # Check file size
    size = path.stat().st_size
    if size == 0:
        return False, f"Empty file: {path.name}"
    if size > MAX_FILE_SIZE:
        size_mb = size / (1024 * 1024)
        return False, f"File too large ({size_mb:.1f} MB): {path.name}"
    
    # Try to verify it's actually an image
    try:
        from PIL import Image
        with Image.open(image_path) as img:
            img.verify()
    except Exception as e:
        return False, f"Invalid image file: {path.name} ({e})"
    
    return True, ""


def validate_images_for_upload(image_paths: List[str]) -> Tuple[List[str], List[Tuple[str, str]]]:
    """
    Validate multiple images before upload.
    
    Returns:
        Tuple of (valid_paths, invalid_items)
        where invalid_items is list of (path, error_message)
    """
    valid = []
    invalid = []
    
    for path in image_paths:
        is_valid, error = validate_image_for_upload(path)
        if is_valid:
            valid.append(path)
        else:
            invalid.append((path, error))
    
    return valid, invalid


def upload_to_imagekit(self):
    """Upload processed images to ImageKit - WITH VALIDATION."""
    if not self.current_images:
        QMessageBox.warning(self, "No Images", "No images to upload.")
        return

    # Validate all images before starting upload
    self.log("Validating images before upload...", "info")
    valid_images, invalid_images = validate_images_for_upload(self.current_images)
    
    if invalid_images:
        # Show validation errors
        error_count = len(invalid_images)
        self.log(f"Found {error_count} invalid image(s)", "warning")
        
        for path, error in invalid_images[:5]:  # Show first 5 errors
            self.log(f"  - {error}", "warning")
        
        if not valid_images:
            QMessageBox.critical(
                self, "Upload Failed",
                f"No valid images to upload.\n\n"
                f"{error_count} image(s) failed validation."
            )
            return
        
        # Ask user if they want to continue with valid images
        reply = QMessageBox.question(
            self, "Validation Warnings",
            f"{error_count} image(s) have issues and will be skipped.\n"
            f"{len(valid_images)} image(s) are valid.\n\n"
            "Continue with valid images only?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply != QMessageBox.Yes:
            return

    # Use valid_images instead of self.current_images
    images_to_upload = valid_images
    
    self.log(f"Uploading {len(images_to_upload)} images to ImageKit...", "info")
    self.status_label.setText("Uploading to ImageKit...")
    self.progress_bar.setValue(0)

    try:
        from modules.imagekit_uploader import ImageKitUploader
        uploader = ImageKitUploader(self.config)

        category = self.category_combo.currentData()
        if not category:
            QMessageBox.warning(self, "No Category", "Please select a category first.")
            return

        sku = self.sku_edit.text()
        if not sku:
            QMessageBox.warning(self, "No SKU", "Please generate a SKU first.")
            return

        folder = f"products/{category}/{sku}"

        uploaded_urls = []
        total = len(images_to_upload)

        for i, img_path in enumerate(images_to_upload):
            result = uploader.upload(img_path, folder)
            if result and result.get("success"):
                url = result.get("url")
                if url:
                    uploaded_urls.append(url)
                    self.log(f"Uploaded: {Path(img_path).name} → {url}", "info")
                else:
                    self.log(f"Upload returned no URL for {Path(img_path).name}", "warning")
            else:
                error_msg = result.get("error", "Unknown error") if result else "No response"
                self.log(f"Failed to upload {Path(img_path).name}: {error_msg}", "error")

            progress = int(((i + 1) / total) * 100)
            self.progress_bar.setValue(progress)
            self.status_label.setText(f"Uploading {i + 1}/{total}...")
            QApplication.processEvents()

        self.log(f"Uploaded {len(uploaded_urls)}/{total} images to ImageKit", "success")

        # Store URLs
        self.uploaded_image_urls = uploaded_urls

        # Enable export button if we have required data
        self.update_export_button_state()

    except Exception as e:
        self.log(f"Upload error: {e}", "error")

    self.status_label.setText("Ready")


# =============================================================================
# MANUAL PATCH INSTRUCTIONS:
# =============================================================================
#
# 1. Add the validate_image_for_upload() function to main.py or a new module
#
# 2. Add the validate_images_for_upload() function
#
# 3. In upload_to_imagekit(), add validation at the start:
#
#    valid_images, invalid_images = validate_images_for_upload(self.current_images)
#    
#    if invalid_images:
#        # Show warnings
#        # Ask user to continue or abort
#    
#    images_to_upload = valid_images
#
# 4. Use images_to_upload instead of self.current_images in the upload loop
#
# =============================================================================
