"""
Kollect-It Automation Modules
=============================

This package contains all processing modules for the Kollect-It automation system.

Modules:
    - image_processor: Image optimization and WebP conversion
    - imagekit_uploader: ImageKit CDN integration
    - sku_generator: SKU generation and management
    - ai_engine: AI-powered description and valuation
    - product_publisher: Website API integration
    - background_remover: AI background removal
    - crop_tool: Interactive image cropping
    - config_validator: Configuration validation and error checking
"""

from .image_processor import ImageProcessor
from .imagekit_uploader import ImageKitUploader
from .sku_generator import SKUGenerator
from .ai_engine import AIEngine
from .product_publisher import ProductPublisher
from .background_remover import BackgroundRemover
from .crop_tool import CropDialog
from .config_validator import ConfigValidator

__all__ = [
    'ImageProcessor',
    'ImageKitUploader', 
    'SKUGenerator',
    'AIEngine',
    'ProductPublisher',
    'BackgroundRemover',
    'CropDialog',
    'ConfigValidator'
]

__version__ = '1.0.0'
