#!/usr/bin/env python3
"""
Kollect-It Product Manager - Utility Functions
General-purpose helper functions for validation and file operations.
"""

import os
from pathlib import Path
from typing import List, Tuple


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

