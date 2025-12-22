#!/usr/bin/env python3
"""
PATCH: safe_file_operations.py
Fixes uncaught file operation errors in images_drop and images_drag_enter.

INSTALLATION:
Replace the images_drop() method in main.py with this version.
"""

import os
import shutil
from pathlib import Path
from typing import Set

from PyQt5.QtWidgets import QMessageBox


def images_drop(self, event):
    """Handle drop on images area - add images to current set.
    
    PATCHED: Added proper error handling for file operations.
    """
    urls = event.mimeData().urls()
    image_extensions: Set[str] = {'.jpg', '.jpeg', '.png', '.webp', '.tiff', '.tif', '.bmp'}
    added = 0
    errors = []

    for url in urls:
        path = url.toLocalFile()

        try:
            # If a folder is dropped, process all images in it
            if os.path.isdir(path):
                folder_images = [
                    str(f) for f in Path(path).iterdir()
                    if f.suffix.lower() in image_extensions
                ]
                for img_path in folder_images:
                    try:
                        result = self._add_image_to_set(img_path, image_extensions)
                        if result:
                            added += 1
                    except Exception as e:
                        errors.append(f"{Path(img_path).name}: {e}")
                        
            elif Path(path).suffix.lower() in image_extensions:
                try:
                    result = self._add_image_to_set(path, image_extensions)
                    if result:
                        added += 1
                except Exception as e:
                    errors.append(f"{Path(path).name}: {e}")
                    
        except Exception as e:
            errors.append(f"Error processing {path}: {e}")

    # Refresh grid if any images were added
    if added > 0:
        self.refresh_image_grid()
        self.log(f"Added {added} image(s) to set", "success")
        
    if errors:
        self.log(f"Failed to add {len(errors)} image(s)", "warning")
        # Show first few errors in log
        for error in errors[:3]:
            self.log(f"  - {error}", "warning")


def _add_image_to_set(self, img_path: str, image_extensions: Set[str]) -> bool:
    """Helper method to add a single image to the current set.
    
    Returns True if image was added, False if skipped (duplicate).
    Raises exception on file operation error.
    """
    if img_path in self.current_images:
        return False  # Already in set
        
    # Check if file exists and is readable
    if not os.path.isfile(img_path):
        raise FileNotFoundError(f"File not found: {img_path}")
    
    if not os.access(img_path, os.R_OK):
        raise PermissionError(f"Cannot read file: {img_path}")
    
    # Copy to current folder if from different location
    if self.current_folder and Path(img_path).parent != Path(self.current_folder):
        dest = self._get_unique_dest_path(img_path)
        
        # Check if destination is writable
        if not os.access(self.current_folder, os.W_OK):
            raise PermissionError(f"Cannot write to: {self.current_folder}")
        
        # Check available disk space (rough check)
        src_size = os.path.getsize(img_path)
        try:
            stat = os.statvfs(self.current_folder) if hasattr(os, 'statvfs') else None
            if stat:
                free_space = stat.f_frsize * stat.f_bavail
                if free_space < src_size * 2:  # Want at least 2x the file size free
                    raise OSError("Insufficient disk space")
        except (AttributeError, OSError):
            pass  # statvfs not available on Windows, skip check
        
        shutil.copy2(img_path, dest)
        self.current_images.append(str(dest))
    else:
        self.current_images.append(img_path)
    
    return True


def _get_unique_dest_path(self, img_path: str) -> Path:
    """Get a unique destination path, avoiding overwrites."""
    dest = Path(self.current_folder) / Path(img_path).name
    
    if dest.exists():
        base = dest.stem
        ext = dest.suffix
        counter = 1
        while dest.exists():
            dest = Path(self.current_folder) / f"{base}_{counter}{ext}"
            counter += 1
            if counter > 1000:  # Safety limit
                raise ValueError("Too many files with same name")
    
    return dest


# =============================================================================
# MANUAL PATCH INSTRUCTIONS:
# =============================================================================
#
# 1. Wrap all shutil.copy2() calls in try/except:
#
#    try:
#        shutil.copy2(path, dest)
#    except PermissionError as e:
#        self.log(f"Cannot copy {Path(path).name}: Permission denied", "error")
#        continue
#    except OSError as e:
#        self.log(f"Cannot copy {Path(path).name}: {e}", "error")
#        continue
#
# 2. Add file existence check before processing:
#
#    if not os.path.isfile(path):
#        continue
#
# 3. Add the helper method _add_image_to_set() to consolidate logic
#
# 4. Add the helper method _get_unique_dest_path() to handle filename conflicts
#
# =============================================================================
