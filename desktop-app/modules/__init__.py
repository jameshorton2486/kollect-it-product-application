"""
Kollect-It Automation Modules
=============================

This package contains all processing modules for the Kollect-It automation system.

Modules:
    - image_processor: Image optimization and WebP conversion
    - imagekit_uploader: ImageKit CDN integration

    - ai_engine: AI-powered description and valuation
    - background_remover: AI background removal
    - crop_tool: Interactive image cropping
    - config_validator: Configuration validation and error checking
    - theme_modern: Modern theme palette and stylesheet
    - widgets: Custom UI widgets (DropZone, ImageThumbnail)
    - workers: Background processing threads
"""

from .image_processor import ImageProcessor
from .imagekit_uploader import ImageKitUploader
from .sku_scanner import SKUScanner
from .ai_engine import AIEngine
from .background_remover import BackgroundRemover, check_rembg_installation, REMBG_AVAILABLE
from .crop_tool import CropDialog
from .config_validator import ConfigValidator
from .output_generator import OutputGenerator
from .import_wizard import ImportWizard
from .theme_modern import ModernPalette
from .widgets import DropZone, ImageThumbnail
from .workers import ProcessingThread, BackgroundRemovalThread, UploadThread

__all__ = [
    # Core processing
    'ImageProcessor',
    'ImageKitUploader',
    'SKUScanner',
    'AIEngine',
    'BackgroundRemover',
    'check_rembg_installation',
    'REMBG_AVAILABLE',
    'CropDialog',
    'ConfigValidator',
    'OutputGenerator',
    'ImportWizard',
    # UI components
    'ModernPalette',
    'DropZone',
    'ImageThumbnail',
    # Workers
    'ProcessingThread',
    'BackgroundRemovalThread',
    'UploadThread',
]

__version__ = '1.0.0'
