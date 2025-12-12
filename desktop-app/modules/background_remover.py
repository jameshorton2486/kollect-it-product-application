#!/usr/bin/env python3
"""
Background Remover Module
AI-powered background removal for product photography.
Uses rembg (U2-Net based) for accurate background removal.
"""

import os
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageFilter, ImageOps
import numpy as np

# Try to import rembg - will be installed separately
try:
    from rembg import remove as rembg_remove
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    print("Warning: rembg not installed. Background removal will use fallback method.")
    print("Install with: pip install rembg --break-system-packages")


class BackgroundRemover:
    """
    Remove backgrounds from product images.
    
    Features:
    - AI-powered background detection
    - Clean edge feathering
    - Shadow preservation option
    - Multiple background color options
    - Fallback method when AI not available
    """
    
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        bg_config = self.config.get("image_processing", {}).get("background_removal", {})
        
        self.default_strength = bg_config.get("default_strength", 0.8)
        self.default_bg_color = bg_config.get("background_color", "#FFFFFF")
        self.preserve_shadows = bg_config.get("preserve_shadows", True)
        
    def remove_background(
        self,
        image_path: str,
        output_path: Optional[str] = None,
        strength: float = 0.8,
        bg_color: str = "#FFFFFF",
        preserve_shadows: bool = True,
        feather_amount: int = 2
    ) -> str:
        """
        Remove background from an image.
        
        Args:
            image_path: Path to input image
            output_path: Path for output (auto-generated if not provided)
            strength: Removal strength 0.0-1.0 (higher = more aggressive)
            bg_color: Background color hex code or "transparent"
            preserve_shadows: Attempt to preserve natural shadows
            feather_amount: Edge feathering pixels
            
        Returns:
            Path to the output image
        """
        input_path = Path(image_path)
        
        # Generate output path if not provided
        if not output_path:
            output_dir = input_path.parent / "processed"
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"{input_path.stem}-bgremoved.webp"
        else:
            output_path = Path(output_path)
        
        # Open the image
        with Image.open(input_path) as img:
            # Convert to RGBA if needed
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            
            # Use rembg if available
            if REMBG_AVAILABLE:
                result = self._remove_with_rembg(img, strength)
            else:
                result = self._remove_fallback(img, strength)
            
            # Apply feathering to edges
            if feather_amount > 0:
                result = self._feather_edges(result, feather_amount)
            
            # Apply background color
            if bg_color.lower() != "transparent":
                result = self._apply_background(result, bg_color, preserve_shadows)
            
            # Save result
            if output_path.suffix.lower() == ".webp":
                result.save(output_path, format="WEBP", quality=90)
            elif output_path.suffix.lower() == ".png":
                result.save(output_path, format="PNG")
            else:
                # Convert to RGB for JPEG
                if result.mode == "RGBA":
                    background = Image.new("RGB", result.size, self._hex_to_rgb(bg_color))
                    background.paste(result, mask=result.split()[-1])
                    result = background
                result.save(output_path, quality=90)
        
        return str(output_path)
    
    def _remove_with_rembg(self, img: Image.Image, strength: float) -> Image.Image:
        """Use rembg for AI-powered background removal."""
        # rembg works on the raw image
        result = rembg_remove(
            img,
            alpha_matting=True,
            alpha_matting_foreground_threshold=int(240 * strength),
            alpha_matting_background_threshold=int(20 * (1 - strength)),
            alpha_matting_erode_size=int(10 * strength)
        )
        return result
    
    def _remove_fallback(self, img: Image.Image, strength: float) -> Image.Image:
        """
        Fallback background removal using edge detection.
        Not as good as AI, but works without additional dependencies.
        """
        # Convert to numpy for processing
        img_array = np.array(img)
        
        # Simple edge-based detection
        # This is a basic fallback - actual edge detection would be more complex
        
        # For now, just return the original with a note
        print("Using fallback background removal - results may vary")
        print("For best results, install rembg: pip install rembg --break-system-packages")
        
        # Create a simple mask based on color similarity to edges
        # This is a very basic approach
        gray = img.convert("L")
        edges = gray.filter(ImageFilter.FIND_EDGES)
        
        # Threshold the edges
        threshold = int(128 * strength)
        mask = edges.point(lambda x: 255 if x > threshold else 0)
        
        # Dilate the mask
        mask = mask.filter(ImageFilter.MaxFilter(5))
        
        # Apply mask
        img.putalpha(mask)
        
        return img
    
    def _feather_edges(self, img: Image.Image, amount: int) -> Image.Image:
        """Apply feathering to image edges for smoother cutout."""
        if img.mode != "RGBA":
            return img
        
        # Get alpha channel
        r, g, b, a = img.split()
        
        # Blur the alpha slightly for feathering
        a = a.filter(ImageFilter.GaussianBlur(radius=amount))
        
        # Recombine
        return Image.merge("RGBA", (r, g, b, a))
    
    def _apply_background(
        self,
        img: Image.Image,
        bg_color: str,
        preserve_shadows: bool
    ) -> Image.Image:
        """Apply a solid background color."""
        if img.mode != "RGBA":
            return img
        
        # Create background
        rgb_color = self._hex_to_rgb(bg_color)
        background = Image.new("RGBA", img.size, (*rgb_color, 255))
        
        if preserve_shadows:
            # Blend with slight shadow preservation
            # Create a shadow layer from the alpha
            r, g, b, a = img.split()
            
            # Invert and darken for shadow
            shadow = ImageOps.invert(a)
            shadow = shadow.point(lambda x: int(x * 0.1))  # Subtle shadow
            
            # Apply shadow to background
            shadow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
            shadow_layer.putalpha(shadow)
            
            # Composite: background -> shadow -> foreground
            result = Image.alpha_composite(background, shadow_layer)
            result = Image.alpha_composite(result, img)
        else:
            result = Image.alpha_composite(background, img)
        
        return result
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def batch_remove(
        self,
        folder_path: str,
        output_folder: Optional[str] = None,
        **kwargs
    ) -> dict:
        """
        Remove backgrounds from all images in a folder.
        
        Args:
            folder_path: Input folder path
            output_folder: Output folder (creates 'processed' subfolder if not provided)
            **kwargs: Options passed to remove_background
            
        Returns:
            Dictionary with results
        """
        folder = Path(folder_path)
        
        if output_folder:
            output_dir = Path(output_folder)
        else:
            output_dir = folder / "processed"
        
        output_dir.mkdir(exist_ok=True)
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
        images = [f for f in folder.iterdir() if f.suffix.lower() in image_extensions]
        
        results = {
            "total": len(images),
            "processed": 0,
            "failed": 0,
            "files": [],
            "errors": []
        }
        
        for img_path in images:
            try:
                output_path = output_dir / f"{img_path.stem}-bgremoved.webp"
                self.remove_background(str(img_path), str(output_path), **kwargs)
                
                results["processed"] += 1
                results["files"].append(str(output_path))
                
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "file": img_path.name,
                    "error": str(e)
                })
        
        return results
    
    def preview_removal(
        self,
        image_path: str,
        strength: float = 0.8
    ) -> Image.Image:
        """
        Preview background removal without saving.
        
        Args:
            image_path: Path to input image
            strength: Removal strength
            
        Returns:
            PIL Image with removed background (RGBA)
        """
        with Image.open(image_path) as img:
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            
            if REMBG_AVAILABLE:
                return self._remove_with_rembg(img, strength)
            else:
                return self._remove_fallback(img, strength)


def install_rembg():
    """Helper function to install rembg."""
    import subprocess
    import sys
    
    print("Installing rembg for AI background removal...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "rembg", "--break-system-packages"
    ])
    print("rembg installed successfully!")
    print("Please restart the application to use AI background removal.")
