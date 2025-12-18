#!/usr/bin/env python3
"""
Image Processor Module
Handles image optimization, resizing, WebP conversion, and EXIF stripping.

Updated: Deletes original files after successful optimization.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List
from PIL import Image, ImageOps, ExifTags
import io
import logging

logger = logging.getLogger(__name__)


class ImageProcessor:
    """
    Process images for web optimization.
    
    Features:
    - Resize to max dimension while preserving aspect ratio
    - Convert to WebP format
    - Strip EXIF metadata
    - Optimize file size with quality settings
    - Apply color profile normalization
    - DELETE ORIGINALS after successful optimization (optional)
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.image_config = config.get("image_processing", {})
        self.max_dimension = self.image_config.get("max_dimension", 2400)
        self.webp_quality = self.image_config.get("webp_quality", 88)
        self.strip_exif = self.image_config.get("strip_exif", True)
        self.thumbnail_size = self.image_config.get("thumbnail_size", 400)
        
    def process_image(
        self,
        input_path: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a single image with optimization.
        
        Args:
            input_path: Path to the source image
            options: Optional processing options to override config
                - max_dimension: Max width/height (default: 2400)
                - quality: WebP quality 1-100 (default: 88)
                - strip_exif: Remove EXIF data (default: True)
                - output_format: Output format (default: "webp")
                - delete_originals: Delete source file after success (default: True)
            
        Returns:
            Dictionary with processed image info
        """
        options = options or {}
        
        # Override config with options
        max_dim = options.get("max_dimension", self.max_dimension)
        quality = options.get("quality", self.webp_quality)
        strip = options.get("strip_exif", self.strip_exif)
        output_format = options.get("output_format", "webp")
        delete_originals = options.get("delete_originals", True)  # NEW: Default True
        
        input_path = Path(input_path)
        
        # Create output directory
        output_dir = input_path.parent / "processed"
        output_dir.mkdir(exist_ok=True)
        
        # Generate output filename
        output_name = input_path.stem + f".{output_format}"
        output_path = output_dir / output_name
        
        # Track if we should delete original
        original_deleted = False
        
        # Open and process image
        with Image.open(input_path) as img:
            original_size = img.size
            original_format = img.format
            
            # Convert to RGB if necessary (handles RGBA, P mode, etc.)
            if img.mode in ("RGBA", "P"):
                # Create white background for transparency
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")
            
            # Auto-orient based on EXIF
            img = ImageOps.exif_transpose(img)
            
            # Resize if needed
            if max(img.size) > max_dim:
                img = self._resize_image(img, max_dim)
            
            new_size = img.size
            
            # Strip EXIF if requested
            if strip:
                # Create clean image without EXIF
                clean_img = Image.new(img.mode, img.size)
                clean_img.putdata(list(img.getdata()))
                img = clean_img
            
            # Save as WebP
            img.save(
                output_path,
                format="WEBP",
                quality=quality,
                method=6,  # Highest compression method
                optimize=True
            )
            
            # Get file sizes
            original_file_size = input_path.stat().st_size
            new_file_size = output_path.stat().st_size
            
            # Generate thumbnail
            thumb_path = self._create_thumbnail(img, output_dir, input_path.stem)
        
        # ============================================
        # DELETE ORIGINAL after successful optimization
        # ============================================
        if delete_originals and output_path.exists():
            try:
                input_path.unlink()
                original_deleted = True
                logger.info(f"Deleted original: {input_path.name}")
                print(f"[OPTIMIZE] 🗑 Deleted original: {input_path.name}")
            except PermissionError as e:
                logger.warning(f"Permission denied deleting {input_path.name}: {e}")
                print(f"[OPTIMIZE] ⚠ Could not delete (in use?): {input_path.name}")
            except Exception as e:
                logger.warning(f"Could not delete original {input_path.name}: {e}")
                print(f"[OPTIMIZE] ⚠ Delete failed: {input_path.name} - {e}")
        
        return {
            "input_path": str(input_path),
            "output_path": str(output_path),
            "thumbnail_path": str(thumb_path) if thumb_path else None,
            "original_size": original_size,
            "new_size": new_size,
            "original_format": original_format,
            "new_format": "WEBP",
            "original_file_size": original_file_size,
            "new_file_size": new_file_size,
            "compression_ratio": round(new_file_size / original_file_size, 3),
            "savings_percent": round((1 - new_file_size / original_file_size) * 100, 1),
            "original_deleted": original_deleted  # NEW: Track deletion status
        }
    
    def _resize_image(self, img: Image.Image, max_dim: int) -> Image.Image:
        """
        Resize image to fit within max dimension while preserving aspect ratio.
        """
        width, height = img.size
        
        if width > height:
            new_width = max_dim
            new_height = int(height * (max_dim / width))
        else:
            new_height = max_dim
            new_width = int(width * (max_dim / height))
        
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def _create_thumbnail(
        self,
        img: Image.Image,
        output_dir: Path,
        base_name: str
    ) -> Optional[Path]:
        """
        Create a thumbnail version of the image.
        """
        try:
            thumb = img.copy()
            thumb.thumbnail((self.thumbnail_size, self.thumbnail_size), Image.Resampling.LANCZOS)
            
            thumb_path = output_dir / f"{base_name}_thumb.webp"
            thumb.save(thumb_path, format="WEBP", quality=80, optimize=True)
            
            return thumb_path
        except Exception as e:
            print(f"Thumbnail creation failed: {e}")
            return None
    
    def batch_process(
        self,
        folder_path: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process all images in a folder.
        
        Args:
            folder_path: Path to folder containing images
            options: Processing options (including delete_originals)
            
        Returns:
            Dictionary with batch processing results
        """
        folder = Path(folder_path)
        options = options or {}
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.tiff', '.bmp', '.gif'}
        images = [
            f for f in folder.iterdir()
            if f.suffix.lower() in image_extensions
        ]
        
        results = {
            "total": len(images),
            "processed": 0,
            "failed": 0,
            "deleted": 0,  # NEW: Track deleted count
            "images": [],
            "errors": [],
            "total_original_size": 0,
            "total_new_size": 0
        }
        
        for img_path in images:
            try:
                result = self.process_image(str(img_path), options)
                results["images"].append(result)
                results["processed"] += 1
                results["total_original_size"] += result["original_file_size"]
                results["total_new_size"] += result["new_file_size"]
                
                # Track deletions
                if result.get("original_deleted", False):
                    results["deleted"] += 1
                    
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "file": img_path.name,
                    "error": str(e)
                })
        
        if results["total_original_size"] > 0:
            results["total_savings_percent"] = round(
                (1 - results["total_new_size"] / results["total_original_size"]) * 100,
                1
            )
        else:
            results["total_savings_percent"] = 0
        
        # Log summary
        logger.info(f"Batch processing complete: {results['processed']} optimized, {results['deleted']} originals deleted")
            
        return results
    
    def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """
        Get detailed information about an image.
        
        Args:
            image_path: Path to the image
            
        Returns:
            Dictionary with image metadata
        """
        path = Path(image_path)
        
        with Image.open(path) as img:
            # Get EXIF data
            exif_data = {}
            if hasattr(img, '_getexif') and img._getexif():
                for tag_id, value in img._getexif().items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    if isinstance(value, bytes):
                        value = value.decode(errors='ignore')
                    exif_data[tag] = str(value)[:100]  # Truncate long values
            
            return {
                "path": str(path),
                "filename": path.name,
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "width": img.size[0],
                "height": img.size[1],
                "file_size": path.stat().st_size,
                "file_size_mb": round(path.stat().st_size / (1024 * 1024), 2),
                "exif": exif_data,
                "has_transparency": img.mode in ("RGBA", "LA", "P")
            }
    
    def auto_rename_images(
        self,
        folder_path: str,
        base_name: str
    ) -> Dict[str, str]:
        """
        Auto-rename images in a folder with sequential numbering.
        
        Args:
            folder_path: Path to folder
            base_name: Base name for renamed files
            
        Returns:
            Dictionary mapping old names to new names
        """
        folder = Path(folder_path)
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.tiff', '.bmp'}
        images = sorted([
            f for f in folder.iterdir()
            if f.suffix.lower() in image_extensions
        ])
        
        renames = {}
        
        for i, img_path in enumerate(images, start=1):
            new_name = f"{i:02d}-{base_name}{img_path.suffix.lower()}"
            new_path = folder / new_name
            
            if img_path != new_path:
                # Avoid overwriting existing files
                if new_path.exists():
                    continue
                    
                img_path.rename(new_path)
                renames[str(img_path)] = str(new_path)
        
        return renames
