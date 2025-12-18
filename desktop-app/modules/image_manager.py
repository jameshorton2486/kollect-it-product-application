#!/usr/bin/env python3
"""
Image Manager Module
Centralized image handling with EXIF orientation, additive loading, and optimization.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any
from PIL import Image, ImageOps, ExifTags
from datetime import datetime


# Supported image extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.tiff', '.bmp'}


class ImageManager:
    """
    Manages the collection of images for a product.
    
    Features:
    - Additive loading (add images without clearing existing)
    - EXIF orientation correction
    - Duplicate detection
    - Optimization with original deletion
    - Image reordering
    """
    
    def __init__(self, working_dir: Optional[str] = None):
        """
        Initialize the image manager.
        
        Args:
            working_dir: Directory for processed images. If None, uses temp dir.
        """
        self.images: List[str] = []  # List of image paths
        self.working_dir = working_dir
        self._original_to_processed: Dict[str, str] = {}  # Track original -> processed mapping
    
    def set_working_dir(self, path: str) -> None:
        """Set the working directory for processed images."""
        self.working_dir = path
        Path(path).mkdir(parents=True, exist_ok=True)
    
    def clear(self) -> None:
        """Clear all images."""
        self.images = []
        self._original_to_processed = {}
    
    def add_from_folder(self, folder_path: str, clear_existing: bool = False) -> List[str]:
        """
        Add images from a folder.
        
        Args:
            folder_path: Path to folder containing images
            clear_existing: If True, clear existing images first
            
        Returns:
            List of newly added image paths
        """
        if clear_existing:
            self.clear()
        
        folder = Path(folder_path)
        if not folder.exists():
            return []
        
        new_images = []
        for f in sorted(folder.iterdir()):
            if f.suffix.lower() in IMAGE_EXTENSIONS:
                img_path = str(f)
                if img_path not in self.images:  # Duplicate check
                    self.images.append(img_path)
                    new_images.append(img_path)
        
        return new_images
    
    def add_files(self, file_paths: List[str]) -> List[str]:
        """
        Add individual image files (additive - doesn't clear existing).
        
        Args:
            file_paths: List of image file paths to add
            
        Returns:
            List of newly added image paths (excludes duplicates)
        """
        new_images = []
        for path in file_paths:
            p = Path(path)
            if p.suffix.lower() in IMAGE_EXTENSIONS and p.exists():
                img_path = str(p)
                if img_path not in self.images:  # Duplicate check
                    self.images.append(img_path)
                    new_images.append(img_path)
        
        return new_images
    
    def remove_image(self, image_path: str) -> bool:
        """
        Remove an image from the collection.
        
        Args:
            image_path: Path to image to remove
            
        Returns:
            True if removed, False if not found
        """
        if image_path in self.images:
            self.images.remove(image_path)
            return True
        return False
    
    def reorder(self, from_index: int, to_index: int) -> bool:
        """
        Move an image from one position to another.
        
        Args:
            from_index: Current index of image
            to_index: Desired index for image
            
        Returns:
            True if successful, False otherwise
        """
        if 0 <= from_index < len(self.images) and 0 <= to_index < len(self.images):
            image = self.images.pop(from_index)
            self.images.insert(to_index, image)
            return True
        return False
    
    def set_as_primary(self, image_path: str) -> bool:
        """
        Set an image as the primary (first) image.
        
        Args:
            image_path: Path to image to make primary
            
        Returns:
            True if successful, False if image not found
        """
        if image_path in self.images:
            self.images.remove(image_path)
            self.images.insert(0, image_path)
            return True
        return False
    
    @property
    def count(self) -> int:
        """Return the number of images."""
        return len(self.images)
    
    @property
    def is_empty(self) -> bool:
        """Return True if no images loaded."""
        return len(self.images) == 0
    
    def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """
        Get information about an image.
        
        Returns:
            Dict with width, height, format, size_kb, needs_rotation
        """
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                file_size = Path(image_path).stat().st_size / 1024
                
                # Check for EXIF orientation
                needs_rotation = False
                try:
                    exif = img._getexif()
                    if exif:
                        for tag, value in exif.items():
                            if ExifTags.TAGS.get(tag) == 'Orientation':
                                needs_rotation = value != 1
                                break
                except (AttributeError, KeyError):
                    pass
                
                return {
                    'width': width,
                    'height': height,
                    'format': img.format,
                    'size_kb': round(file_size, 1),
                    'needs_rotation': needs_rotation,
                    'is_landscape': width > height,
                    'is_small': width < 800 or height < 800
                }
        except Exception as e:
            return {'error': str(e)}


def apply_exif_orientation(image_path: str) -> Image.Image:
    """
    Load an image and apply EXIF orientation correction.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        PIL Image with correct orientation
    """
    img = Image.open(image_path)
    
    try:
        # Use PIL's built-in EXIF transpose
        img = ImageOps.exif_transpose(img)
    except Exception:
        # If EXIF processing fails, return original
        pass
    
    return img


def load_image_with_exif(image_path: str) -> Image.Image:
    """
    Load an image with EXIF orientation applied.
    Alias for apply_exif_orientation for clarity.
    """
    return apply_exif_orientation(image_path)


def optimize_image(
    input_path: str,
    output_path: str,
    max_dimension: int = 2400,
    quality: int = 88,
    strip_exif: bool = True,
    delete_original: bool = True
) -> Dict[str, Any]:
    """
    Optimize an image: resize, convert to WebP, apply EXIF orientation.
    
    Args:
        input_path: Path to original image
        output_path: Path for optimized output (should end in .webp)
        max_dimension: Maximum width or height
        quality: WebP quality (1-100)
        strip_exif: Whether to strip EXIF data
        delete_original: Whether to delete the original file after optimization
        
    Returns:
        Dict with success status and details
    """
    try:
        # Load with EXIF orientation
        img = apply_exif_orientation(input_path)
        
        # Convert to RGB if necessary (for WebP compatibility)
        if img.mode in ('RGBA', 'P'):
            # Keep alpha for images that have it
            if img.mode == 'P':
                img = img.convert('RGBA')
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if needed
        original_size = img.size
        if max(img.size) > max_dimension:
            img.thumbnail((max_dimension, max_dimension), Image.LANCZOS)
        
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save as WebP
        save_kwargs = {
            'quality': quality,
            'method': 4  # Balanced compression
        }
        
        # Handle transparency
        if img.mode == 'RGBA':
            img.save(output_path, 'WEBP', **save_kwargs)
        else:
            img.save(output_path, 'WEBP', **save_kwargs)
        
        # Get file sizes for comparison
        original_size_kb = Path(input_path).stat().st_size / 1024
        new_size_kb = Path(output_path).stat().st_size / 1024
        
        # Delete original if requested and output is different file
        if delete_original and Path(input_path).resolve() != Path(output_path).resolve():
            try:
                os.remove(input_path)
            except Exception as e:
                return {
                    'success': True,
                    'warning': f'Could not delete original: {e}',
                    'input': input_path,
                    'output': output_path,
                    'original_size_kb': original_size_kb,
                    'new_size_kb': new_size_kb,
                    'reduction_percent': round((1 - new_size_kb / original_size_kb) * 100, 1)
                }
        
        return {
            'success': True,
            'input': input_path,
            'output': output_path,
            'original_size': original_size,
            'new_size': img.size,
            'original_size_kb': original_size_kb,
            'new_size_kb': new_size_kb,
            'reduction_percent': round((1 - new_size_kb / original_size_kb) * 100, 1) if original_size_kb > 0 else 0
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'input': input_path
        }


def batch_optimize(
    image_paths: List[str],
    output_dir: str,
    sku: str,
    max_dimension: int = 2400,
    quality: int = 88,
    delete_originals: bool = True,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> Dict[str, Any]:
    """
    Optimize multiple images with SKU-based naming.
    
    Args:
        image_paths: List of image paths to optimize
        output_dir: Directory for optimized images
        sku: Product SKU for naming (e.g., "MILI-2025-0005")
        max_dimension: Maximum dimension
        quality: WebP quality
        delete_originals: Delete original files after optimization
        progress_callback: Called with (current, total, filename)
        
    Returns:
        Dict with results summary and list of output paths
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    results = {
        'success': True,
        'processed': 0,
        'failed': 0,
        'output_paths': [],
        'errors': [],
        'total_original_kb': 0,
        'total_new_kb': 0
    }
    
    total = len(image_paths)
    
    for i, input_path in enumerate(image_paths):
        # Generate output filename: SKU-001.webp, SKU-002.webp, etc.
        output_filename = f"{sku}-{(i + 1):03d}.webp"
        output_path = str(Path(output_dir) / output_filename)
        
        if progress_callback:
            progress_callback(i + 1, total, Path(input_path).name)
        
        result = optimize_image(
            input_path,
            output_path,
            max_dimension=max_dimension,
            quality=quality,
            delete_original=delete_originals
        )
        
        if result['success']:
            results['processed'] += 1
            results['output_paths'].append(output_path)
            results['total_original_kb'] += result.get('original_size_kb', 0)
            results['total_new_kb'] += result.get('new_size_kb', 0)
        else:
            results['failed'] += 1
            results['errors'].append(result)
            results['success'] = False
    
    # Calculate overall reduction
    if results['total_original_kb'] > 0:
        results['total_reduction_percent'] = round(
            (1 - results['total_new_kb'] / results['total_original_kb']) * 100, 1
        )
    else:
        results['total_reduction_percent'] = 0
    
    return results


def copy_to_google_drive(
    image_paths: List[str],
    drive_folder: str,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> Dict[str, Any]:
    """
    Copy optimized images to Google Drive folder.
    
    Args:
        image_paths: List of image paths to copy
        drive_folder: Destination folder on Google Drive
        progress_callback: Called with (current, total, filename)
        
    Returns:
        Dict with success status and copied paths
    """
    Path(drive_folder).mkdir(parents=True, exist_ok=True)
    
    results = {
        'success': True,
        'copied': 0,
        'failed': 0,
        'destination_paths': [],
        'errors': []
    }
    
    total = len(image_paths)
    
    for i, src_path in enumerate(image_paths):
        filename = Path(src_path).name
        dest_path = str(Path(drive_folder) / filename)
        
        if progress_callback:
            progress_callback(i + 1, total, filename)
        
        try:
            shutil.copy2(src_path, dest_path)
            results['copied'] += 1
            results['destination_paths'].append(dest_path)
        except Exception as e:
            results['failed'] += 1
            results['errors'].append({'file': filename, 'error': str(e)})
            results['success'] = False
    
    return results
