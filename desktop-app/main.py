#!/usr/bin/env python3
"""
Kollect-It Product Manager
Desktop application for processing and optimizing antiques/collectibles listings.

Features:
- Drag-and-drop product folder processing
- AI-powered image renaming and description generation
- WebP conversion with optimization
- Built-in image cropping tool
- AI background removal
- ImageKit cloud upload
- SKU generation per category
"""

import sys
import os
import json
import requests
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

VERSION = "1.0.0"

# Early print for startup debugging
print(f"\n{'='*60}")
print(f"  KOLLECT-IT PRODUCT MANAGER v{VERSION}")
print(f"  Starting application...")
print(f"{'='*60}\n")
IMAGE_GRID_COLUMNS = 4
MAX_IMAGES = 20
MAX_AI_IMAGES_DESCRIPTION = 10  # Increased from 5 for richer context
MAX_AI_IMAGES_VALUATION = 5     # Increased from 3 for valuation context
MAX_AI_IMAGES_ANALYZE = 12  # Explicit cap for Analyze Images

# Load environment variables from .env file (if available)
try:
    from dotenv import load_dotenv
    # Load .env from desktop-app directory
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)
except ImportError:
    # python-dotenv not installed, continue without .env support
    pass

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QTextEdit, QComboBox,
    QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QTabWidget,
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox,
    QGroupBox, QFormLayout, QSplitter, QFrame, QScrollArea,
    QSlider, QDialog, QDialogButtonBox, QToolBar, QAction,
    QStatusBar, QMenuBar, QMenu, QGridLayout, QSizePolicy,
    QShortcut
)
from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QUrl, QMimeData, QSize, QTimer
)
from PyQt5.QtGui import (
    QPixmap, QImage, QIcon, QFont, QPalette, QColor,
    QDragEnterEvent, QDropEvent, QPainter, QPen, QKeySequence
)

# Import custom modules
# pyright: reportMissingImports=false
from modules.image_processor import ImageProcessor  # type: ignore
from modules.imagekit_uploader import ImageKitUploader  # type: ignore
from modules.sku_scanner import SKUScanner  # type: ignore
from modules.ai_engine import AIEngine  # type: ignore
from modules.background_remover import BackgroundRemover, check_rembg_installation, REMBG_AVAILABLE  # type: ignore
from modules.crop_tool import CropDialog  # type: ignore
from modules.import_wizard import ImportWizard  # type: ignore
from modules.output_generator import OutputGenerator
from modules.website_publisher import WebsitePublisher  # type: ignore
from modules.config_validator import ConfigValidator  # type: ignore
from modules.theme_modern import ModernPalette  # type: ignore
from modules.widgets import DropZone, ImageThumbnail
from modules.workers import ProcessingThread  # type: ignore
from modules.utils import validate_image_for_upload, validate_images_for_upload  # type: ignore
from modules.help_dialog import show_quick_start # type: ignore
from modules.app_logger import (  # type: ignore
    logger, log_startup_info, log_config_status, log_function_call,
    log_exception, log_ui_action, log_processing, log_api_call,
    log_image_operation, log_operation, debug_print, info_print,
    error_print, success_print, warning_print, safe_execute,
    setup_exception_handling
)

# Log startup
log_startup_info(VERSION)
print("[STARTUP] Modules imported successfully")

# Set up global exception handling
setup_exception_handling()


class KollectItApp(QMainWindow):
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


def validate_images_for_upload(image_paths: List[str]) -> tuple[List[str], List[tuple[str, str]]]:
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


# =============================================================================
# PATCH 6: Global Exception Handler
# =============================================================================

def setup_exception_handling():
    """
    Set up global exception handling for the application.
    Catches unhandled exceptions and shows user-friendly error dialog.
    """
    import logging
    
    # Create logs directory
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Set up file logging for crashes
    crash_log_file = log_dir / f"crash_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        handlers=[
            logging.FileHandler(crash_log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Global exception handler."""
        # Don't handle KeyboardInterrupt
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # Log the exception
        logger.critical(
            "Unhandled exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
        
        # Format error message
        error_text = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        # Write to crash log
        with open(crash_log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"CRASH: {datetime.now().isoformat()}\n")
            f.write(f"{'='*60}\n")
            f.write(error_text)
            f.write("\n")
        
        # Show error dialog if application is running
        try:
            from PyQt5.QtWidgets import QMessageBox, QApplication
            app = QApplication.instance()
            if app:
                # Create a simplified error message for users
                user_message = (
                    f"An unexpected error occurred:\n\n"
                    f"{exc_type.__name__}: {exc_value}\n\n"
                    f"Error details have been saved to:\n"
                    f"{crash_log_file}\n\n"
                    f"Please report this issue with the log file."
                )
                
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Kollect-It - Error")
                msg.setText("An unexpected error occurred.")
                msg.setInformativeText(str(exc_value))
                msg.setDetailedText(error_text)
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Close)
                
                # Close button exits app, Ok continues (risky but user's choice)
                result = msg.exec_()
                
                if result == QMessageBox.Close:
                    sys.exit(1)
        except Exception:
            # If we can't show dialog, just exit
            sys.exit(1)
    
    # Install the exception hook
    sys.excepthook = handle_exception
    
    logger.info("Global exception handling installed")
    return logger


# Set up global exception handling
setup_exception_handling()


class KollectItApp(QMainWindow):
    """Main application window for Kollect-It Product Manager."""

    def __init__(self):
        super().__init__()
        print("[INIT] Initializing KollectItApp...")
        logger.info("Initializing KollectItApp")

        try:
            self.config = self.load_config()
            log_config_status(self.config)
        except Exception as e:
            error_print(f"Failed to load config: {e}")
            logger.error(f"Config load failed: {e}")
            raise

        # Initialize SKU Scanner and Output Generator
        products_root = self.config.get("paths", {}).get("products_root", r"G:\My Drive\Kollect-It\Products")
        self.sku_scanner = SKUScanner(products_root, self.config.get("categories", {}))
        self.output_generator = OutputGenerator(self.config)
        self.website_publisher = WebsitePublisher(self.config)
        self.last_valuation = None
        self.current_folder = None
        self._temp_dirs = []  # Track temporary directories for cleanup
        self.current_images = []
        self.selected_images = []  # Track multi-selected images for batch operations
        self.uploaded_image_urls = []  # Store URLs after ImageKit upload
        self.processing_thread = None

        # Initialize UI component attributes
        self.drop_zone = None
        self.image_grid = None
        self.image_grid_layout = None
        self.crop_all_btn = None
        self.remove_bg_btn = None
        self.optimize_btn = None
        self.clear_all_btn = None
        self.upload_btn = None
        self.export_btn = None
        self.publish_btn = None
        self.title_edit = None
        self.sku_edit = None
        self.category_combo = None
        self.subcategory_combo = None
        self.price_spin = None
        self.condition_combo = None
        self.era_edit = None
        self.origin_edit = None
        self.description_edit = None
        self.generate_desc_btn = None
        self.generate_valuation_btn = None
        self.seo_title_edit = None
        self.seo_desc_edit = None
        self.seo_keywords_edit = None
        self.bg_removal_check = None
        self.bg_strength_slider = None
        self.progress_bar = None
        self.status_label = None
        self.log_output = None
        self.regenerate_sku_btn = None

        # Settings dialog attributes
        self.api_key_edit = None
        self.prod_url_edit = None
        self.use_prod_check = None
        self.ik_public_edit = None
        self.ik_private_edit = None
        self.ik_url_edit = None
        # API key is read from environment variable only
        self.ai_model_edit = None
        self.max_dim_spin = None
        self.quality_spin = None
        self.strip_exif_check = None

        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()

    def load_config(self) -> dict:
        """Load configuration from config.json with validation and .env override."""
        print("[CONFIG] Loading configuration...")
        logger.info("Loading configuration from config.json")
        config_path = Path(__file__).parent / "config" / "config.json"

        # Check if config exists
        if not config_path.exists():
            error_msg = (
                "Configuration file not found!\n\n"
                f"Expected: {config_path}\n\n"
                "Please copy config.example.json to config.json and configure your API keys:\n"
                "1. Copy config/config.example.json to config/config.json\n"
                "2. Add your SERVICE_API_KEY\n"
                "3. Add your ImageKit credentials\n"
                "4. Add your Anthropic API key"
            )
            QMessageBox.critical(None, "Configuration Error", error_msg)
            sys.exit(1)

        # Try to parse config
        try:
            # Try to load with .env support
            try:
                from modules.env_loader import load_config_with_env
                config = load_config_with_env(config_path)
            except ImportError:
                # Fallback to standard JSON loading if env_loader not available
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)

            # Validate configuration. ConfigValidator may require the config
            # in its constructor or in the validate() call depending on version.
            validation_result = {"valid": True}
            try:
                # Prefer passing config into the constructor if supported
                try:
                    validator = ConfigValidator(config)
                    # Newer validators validate without args
                    try:
                        validation_result = validator.validate()
                    except TypeError:
                        validation_result = validator.validate(config)
                except TypeError:
                    # Fallback to old-style: construct without args
                    validator = ConfigValidator()
                    try:
                        validation_result = validator.validate(config)
                    except TypeError:
                        # As a last resort, try validate() without args
                        validation_result = validator.validate()
            except Exception:
                # If anything goes wrong during validation, skip but don't crash
                validation_result = {"valid": True}

            # Normalize older tuple-based validator returns to a dict
            if isinstance(validation_result, tuple):
                try:
                    is_valid, errors, warnings = validation_result
                    validation_result = {"valid": bool(is_valid), "errors": errors or [], "warnings": warnings or []}
                except Exception:
                    validation_result = {"valid": True, "errors": [], "warnings": []}

            if not validation_result.get("valid", True):
                QMessageBox.warning(
                    None, "Configuration Warning",
                    f"Configuration issues found: {validation_result.get('errors', [])}"
                )
        except json.JSONDecodeError as e:
            QMessageBox.critical(
                None, "Configuration Error",
                f"Invalid JSON in config.json:\n\n{e}\n\nPlease fix the syntax error."
            )
            sys.exit(1)
        except Exception as e:
            QMessageBox.critical(
                None, "Configuration Error",
                f"Error reading config.json:\n\n{e}"
            )
            sys.exit(1)

        # Validate required sections
        required_sections = ["api", "imagekit", "categories", "image_processing"]
        missing = [s for s in required_sections if s not in config]

        if missing:
            QMessageBox.warning(
                None, "Configuration Warning",
                f"Missing configuration sections: {', '.join(missing)}\n\n"
                "Some features may not work correctly."
            )

        # Validate API keys are not placeholder values (check .env first, then config)
        api_key = os.getenv("SERVICE_API_KEY") or config.get("api", {}).get("SERVICE_API_KEY", "")
        if not api_key or api_key in ("YOUR_SERVICE_API_KEY_HERE", ""):
            QMessageBox.warning(
                None, "Configuration Warning",
                "SERVICE_API_KEY is not configured.\n\n"
                "Add it to .env file or config.json if needed for future features."
            )

        return config

    def save_config(self):
        """Save configuration to config.json."""
        config_path = Path(__file__).parent / "config" / "config.json"
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def setup_ui(self):
        """Initialize the main user interface."""
        self.setWindowTitle(f"Kollect-It Product Manager v{VERSION}")
        self.setMinimumSize(1600, 1000)
        try:
            try:
                import logging as _logging
                _logging.getLogger(__name__).info(f"Using ModernPalette from module: {ModernPalette.__module__}")
            except Exception:
                pass
            self.setStyleSheet(ModernPalette.get_stylesheet())
        except Exception as e:
            import traceback
            print("Failed to apply stylesheet:", e)
            traceback.print_exc()

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(24)
        main_layout.setContentsMargins(24, 24, 24, 24)

        # Left panel - Input & Images
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(16)

        # Drop zone
        self.drop_zone = DropZone(config=self.config)
        self.drop_zone.folder_dropped.connect(self.on_folder_dropped)
        # self.drop_zone.files_added.connect(lambda path: self.on_folder_dropped(path, append=True))  # TODO: Enable when widgets.py updated
        left_layout.addWidget(self.drop_zone)

        # New Product button below drop zone
        new_product_btn = QPushButton("+ Add New Product")
        new_product_btn.setObjectName("newProductBtn")
        new_product_btn.setProperty("variant", "secondary")
        new_product_btn.setMinimumHeight(48)
        new_product_btn.clicked.connect(self.open_import_wizard)
        left_layout.addWidget(new_product_btn)

        # Image preview section
        images_group = QGroupBox("Product Images")
        images_layout = QVBoxLayout(images_group)

        # ============================================================
        # Feature 2: Enable drag-drop to add images to existing set
        # ============================================================
        images_group.setAcceptDrops(True)
        images_group.dragEnterEvent = self.images_drag_enter
        images_group.dropEvent = self.images_drop

        # Image grid scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(300)
        scroll.setAcceptDrops(True)  # Also accept drops on scroll area
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        self.image_grid = QWidget()
        self.image_grid.setStyleSheet("background-color: transparent;")
        self.image_grid_layout = QGridLayout(self.image_grid)
        self.image_grid_layout.setSpacing(12)
        scroll.setWidget(self.image_grid)
        images_layout.addWidget(scroll)

        # Image action buttons
        img_actions = QHBoxLayout()

        self.crop_all_btn = QPushButton("✂ Crop Selected")
        self.crop_all_btn.setObjectName("cropBtn")
        self.crop_all_btn.setProperty("variant", "utility")
        self.crop_all_btn.setEnabled(False)
        self.crop_all_btn.clicked.connect(self.crop_selected_image)
        img_actions.addWidget(self.crop_all_btn)

        self.remove_bg_btn = QPushButton("🎨 Remove BG")
        self.remove_bg_btn.setObjectName("removeBgBtn")
        self.remove_bg_btn.setProperty("variant", "utility")
        self.remove_bg_btn.setEnabled(False)
        self.remove_bg_btn.clicked.connect(self.remove_background)
        img_actions.addWidget(self.remove_bg_btn)

        self.optimize_btn = QPushButton("⚡ Optimize All")
        self.optimize_btn.setObjectName("optimizeBtn")
        self.optimize_btn.setProperty("variant", "secondary")
        self.optimize_btn.setEnabled(False)
        self.optimize_btn.clicked.connect(self.optimize_images)
        img_actions.addWidget(self.optimize_btn)

        # Clear All button
        self.clear_all_btn = QPushButton("🗑 Clear All")
        self.clear_all_btn.setObjectName("clearAllBtn")
        self.clear_all_btn.setProperty("variant", "utility")
        self.clear_all_btn.setEnabled(False)
        self.clear_all_btn.clicked.connect(self.clear_all_images)
        img_actions.addWidget(self.clear_all_btn)

        images_layout.addLayout(img_actions)
        left_layout.addWidget(images_group)

        main_layout.addWidget(left_panel, stretch=1)

        # Right panel - Product Details & Actions
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(16)

        # Tabs for different sections
        tabs = QTabWidget()

        # Product Details Tab
        details_tab = QWidget()
        details_layout = QVBoxLayout(details_tab)

        form = QFormLayout()
        form.setSpacing(16)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form.setRowWrapPolicy(QFormLayout.DontWrapRows)

        # Title
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter product title...")
        self.title_edit.textChanged.connect(self.update_export_button_state)
        form.addRow("Title:", self.title_edit)

        # SKU (auto-generated)
        sku_layout = QHBoxLayout()
        self.sku_edit = QLineEdit()
        self.sku_edit.setReadOnly(True)
        self.sku_edit.setPlaceholderText("Auto-generated")
        sku_layout.addWidget(self.sku_edit)
        self.regenerate_sku_btn = QPushButton("Regen")
        self.regenerate_sku_btn.setFixedWidth(80)
        self.regenerate_sku_btn.clicked.connect(self.regenerate_sku)
        sku_layout.addWidget(self.regenerate_sku_btn)
        form.addRow("SKU:", sku_layout)

        # Category
        self.category_combo = QComboBox()
        # Clear existing items
        self.category_combo.clear()

        # Add categories from config with proper data
        for cat_id, cat_info in self.config.get("categories", {}).items():
            display_name = cat_info.get("display_name", cat_info.get("name", cat_id.title()))
            # addItem(display_text, user_data) - the second param is returned by currentData()
            self.category_combo.addItem(display_name, cat_id)

        # Set default selection
        default_cat = self.config.get("defaults", {}).get("default_category", "collectibles")
        index = self.category_combo.findData(default_cat)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
        self.category_combo.currentIndexChanged.connect(self.on_category_changed)
        form.addRow("Category:", self.category_combo)

        # Subcategory
        self.subcategory_combo = QComboBox()
        self.update_subcategories()
        form.addRow("Subcategory:", self.subcategory_combo)

        # Price
        price_layout = QHBoxLayout()
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 999999.99)
        self.price_spin.setPrefix("$ ")
        self.price_spin.setDecimals(2)
        price_layout.addWidget(self.price_spin)
        form.addRow("Suggested Price:", price_layout)

        # Condition
        self.condition_combo = QComboBox()
        for condition in self.config.get("defaults", {}).get("condition_grades", []):
            self.condition_combo.addItem(condition)
        form.addRow("Condition:", self.condition_combo)

        # Era/Period
        self.era_edit = QLineEdit()
        self.era_edit.setPlaceholderText("e.g., WWII, Victorian, 1960s")
        form.addRow("Era/Period:", self.era_edit)

        # Origin
        self.origin_edit = QLineEdit()
        self.origin_edit.setPlaceholderText("e.g., United States, Germany")
        form.addRow("Origin:", self.origin_edit)

        details_layout.addLayout(form)

        # Description
        desc_group = QGroupBox("Description")
        desc_layout = QVBoxLayout(desc_group)

        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Product description will be generated by AI...")
        self.description_edit.setMinimumHeight(150)
        desc_layout.addWidget(self.description_edit)

        ai_btn_layout = QHBoxLayout()
        self.analyze_images_btn = QPushButton("🔎 Analyze Images")
        self.analyze_images_btn.setObjectName("analyzeImagesBtn")
        self.analyze_images_btn.setProperty("variant", "utility")
        self.analyze_images_btn.clicked.connect(self.analyze_and_autofill)
        ai_btn_layout.addWidget(self.analyze_images_btn)
        self.generate_desc_btn = QPushButton("✨ Generate with AI")
        self.generate_desc_btn.setObjectName("generateDescBtn")
        self.generate_desc_btn.setProperty("variant", "secondary")
        self.generate_desc_btn.clicked.connect(self.generate_description)
        ai_btn_layout.addWidget(self.generate_desc_btn)

        self.generate_valuation_btn = QPushButton("💰 Price Research")
        self.generate_valuation_btn.setObjectName("generateValuationBtn")
        self.generate_valuation_btn.setProperty("variant", "secondary")
        self.generate_valuation_btn.clicked.connect(self.generate_valuation)
        ai_btn_layout.addWidget(self.generate_valuation_btn)
        ai_btn_layout.setSpacing(12)
        desc_layout.addLayout(ai_btn_layout)
        desc_layout.addSpacing(6)

        details_layout.addWidget(desc_group)
        tabs.addTab(details_tab, "Product Details")

        # SEO Tab
        seo_tab = QWidget()
        seo_layout = QFormLayout(seo_tab)
        seo_layout.setSpacing(16)
        seo_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        seo_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        seo_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)

        self.seo_title_edit = QLineEdit()
        self.seo_title_edit.setPlaceholderText("SEO-optimized title")
        seo_layout.addRow("SEO Title:", self.seo_title_edit)

        self.seo_desc_edit = QTextEdit()
        self.seo_desc_edit.setMaximumHeight(100)
        self.seo_desc_edit.setPlaceholderText("Meta description (160 chars)")
        seo_layout.addRow("Meta Description:", self.seo_desc_edit)

        self.seo_keywords_edit = QLineEdit()
        self.seo_keywords_edit.setPlaceholderText("keyword1, keyword2, keyword3")
        seo_layout.addRow("Keywords:", self.seo_keywords_edit)

        tabs.addTab(seo_tab, "SEO")

        # Settings Tab
        settings_tab = QWidget()
        settings_layout = QFormLayout(settings_tab)
        settings_layout.setSpacing(16)
        settings_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        settings_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        settings_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)

        self.bg_removal_check = QCheckBox("Enable AI Background Removal")
        self.bg_removal_check.setChecked(
            self.config.get("image_processing", {})
            .get("background_removal", {})
            .get("enabled", True)
        )
        settings_layout.addRow(self.bg_removal_check)

        self.bg_strength_slider = QSlider(Qt.Horizontal)
        self.bg_strength_slider.setRange(1, 100)
        self.bg_strength_slider.setValue(80)
        settings_layout.addRow("BG Removal Strength:", self.bg_strength_slider)

        tabs.addTab(settings_tab, "Settings")

        right_layout.addWidget(tabs)

        # Progress section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"color: {ModernPalette.TEXT_SECONDARY};")
        progress_layout.addWidget(self.status_label)

        right_layout.addWidget(progress_group)

        # Action buttons
        actions_layout = QHBoxLayout()

        self.upload_btn = QPushButton("☁ Upload to ImageKit")
        self.upload_btn.setObjectName("uploadBtn")
        self.upload_btn.setProperty("variant", "secondary")
        self.upload_btn.setEnabled(False)
        self.upload_btn.clicked.connect(self.upload_to_imagekit)
        actions_layout.addWidget(self.upload_btn)

        self.export_btn = QPushButton("📦 Export Package")
        self.export_btn.setObjectName("exportBtn")
        self.export_btn.setProperty("variant", "primary")
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self.export_package)
        actions_layout.addWidget(self.export_btn)

        self.publish_btn = QPushButton("🌐 Publish to Website")
        self.publish_btn.setObjectName("publishBtn")
        self.publish_btn.setProperty("variant", "success")
        self.publish_btn.setEnabled(False)
        self.publish_btn.setToolTip("Publish product to kollect-it.com as draft")
        self.publish_btn.clicked.connect(self.publish_to_website)
        actions_layout.addWidget(self.publish_btn)

        right_layout.addLayout(actions_layout)

        # Log output
        log_group = QGroupBox("Activity Log")
        log_layout = QVBoxLayout(log_group)

        self.log_output = QTextEdit()
        self.log_output.setObjectName("activityLog")
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(150)
        log_layout.addWidget(self.log_output)

        right_layout.addWidget(log_group)

        main_layout.addWidget(right_panel, stretch=1)

        # ============================================================
        # Keyboard Shortcuts for Multi-Select
        # ============================================================
        # Delete key - delete selected images
        delete_shortcut = QShortcut(QKeySequence(Qt.Key_Delete), self)
        delete_shortcut.activated.connect(self.delete_selected_images)

        # Ctrl+A - select all images
        select_all_shortcut = QShortcut(QKeySequence("Ctrl+A"), self)
        select_all_shortcut.activated.connect(self.select_all_images)

        # Escape - clear selection
        escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        escape_shortcut.activated.connect(self.clear_image_selection)

    def setup_menu(self):
        """Set up the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        # New Product action (at the top of File menu)
        new_product_action = QAction("&New Product...", self)
        new_product_action.setShortcut("Ctrl+N")
        new_product_action.setStatusTip("Import photos and create a new product")
        new_product_action.triggered.connect(self.open_import_wizard)
        file_menu.addAction(new_product_action)

        file_menu.addSeparator()

        open_action = QAction("Open Folder...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        export_menu = file_menu.addMenu("Export")
        export_json = QAction("Export as JSON", self)
        export_json.triggered.connect(lambda: self.export_product("json"))
        export_menu.addAction(export_json)

        export_docx = QAction("Export as DOCX", self)
        export_docx.triggered.connect(lambda: self.export_product("docx"))
        export_menu.addAction(export_docx)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")

        batch_action = QAction("Batch Process Folder...", self)
        batch_action.triggered.connect(self.batch_process)
        tools_menu.addAction(batch_action)

        tools_menu.addSeparator()

        settings_action = QAction("Settings...", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        quick_start = QAction("📚 Quick Start Guide", self)
        quick_start.setShortcut("F1")
        quick_start.triggered.connect(lambda: show_quick_start(self))
        help_menu.addAction(quick_start)

        help_menu.addSeparator()

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_toolbar(self):
        """Set up the main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # New Product button (at the start)
        new_product_action = QAction("New Product", self)
        new_product_action.setStatusTip("Import photos and create a new product")
        new_product_action.triggered.connect(self.open_import_wizard)
        toolbar.addAction(new_product_action)

        toolbar.addSeparator()

        toolbar.addAction("Open", self.open_folder)
        toolbar.addAction("Process", self.optimize_images)
        toolbar.addAction("Upload", self.upload_to_imagekit)

    def setup_statusbar(self):
        """Set up the status bar."""
        self.statusBar().showMessage("Ready - Drop a product folder to begin")

    def log(self, message: str, level: str = "info"):
        """Add a message to the activity log with timestamp and color coding."""
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Color coding for different levels
        colors = {
            "info": ModernPalette.INFO,
            "success": ModernPalette.SUCCESS,
            "warning": ModernPalette.WARNING,
            "error": ModernPalette.ERROR,
        }
        color = colors.get(level, "#ffffff")

        # Format with HTML for colored output
        formatted = f'<span style="color: {ModernPalette.TEXT_MUTED};">[{timestamp}]</span> <span style="color: {color};">{message}</span>'

        self.log_output.append(formatted)

        # Auto-scroll to bottom
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_folder_dropped(self, folder_path: str, append: bool = False):
        """Handle when a folder is dropped or selected.

        Args:
            folder_path: Path to the folder containing images
            append: If True, add images to existing set instead of replacing
        """
        if append and self.current_images:
            # Append mode: add images from this folder to existing set
            print(f"[LOAD] Appending images from: {folder_path}")
            logger.info(f"Appending images from folder: {folder_path}")

            image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.tiff', '.bmp'}
            new_images = sorted([
                str(f) for f in Path(folder_path).iterdir()
                if f.suffix.lower() in image_extensions
            ])

            added_count = 0
            for img_path in new_images:
                if img_path not in self.current_images:
                    self.current_images.append(img_path)
                    added_count += 1

            if added_count > 0:
                self.log(f"Added {added_count} images from {os.path.basename(folder_path)}", "success")
                self.refresh_image_grid()
                logger.info(f"Added {added_count} images, total now: {len(self.current_images)}")
            else:
                self.log("No new images to add (duplicates skipped)", "info")
            return

        # Normal mode: replace current images with new folder
        self.current_folder = folder_path
        self.log(f"Loaded folder: {os.path.basename(folder_path)}", "success")
        self.statusBar().showMessage(f"Folder: {folder_path}")

        # Load images
        self.load_images_from_folder(folder_path)

        # Auto-detect category from folder name
        self.detect_category(folder_path)

        # Generate SKU
        self.generate_sku()

        # Enable buttons
        self.optimize_btn.setEnabled(True)
        self.crop_all_btn.setEnabled(True)
        self.remove_bg_btn.setEnabled(True)

    def load_images_from_folder(self, folder_path: str):
        """Load and display images from the selected folder."""
        print(f"[LOAD] Loading images from: {folder_path}")
        logger.info(f"Loading images from folder: {folder_path}")

        try:
            # Clear existing thumbnails
            while self.image_grid_layout.count():
                item = self.image_grid_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            self.current_images = []

            image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.tiff', '.bmp'}
            images = sorted([
                f for f in Path(folder_path).iterdir()
                if f.suffix.lower() in image_extensions
            ])

            logger.info(f"Found {len(images)} images")
            print(f"[LOAD] Found {len(images)} images")

            row, col = 0, 0
            max_cols = IMAGE_GRID_COLUMNS

            for img_path in images:
                self.current_images.append(str(img_path))

                thumb = ImageThumbnail(str(img_path))
                thumb.clicked.connect(self.preview_image)
                thumb.selected.connect(self.on_thumbnail_selected)
                thumb.ctrl_clicked.connect(self.on_thumbnail_ctrl_clicked)  # Multi-select
                thumb.crop_requested.connect(self.crop_image)
                thumb.remove_bg_requested.connect(self.remove_image_background)
                thumb.delete_requested.connect(self.delete_image_from_set)

                self.image_grid_layout.addWidget(thumb, row, col)

                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

            # Clear multi-selection when loading new folder
            self.selected_images = []
            self.log(f"Loaded {len(images)} images", "info")
            logger.info(f"Successfully loaded {len(images)} images from {folder_path}")
            print(f"[LOAD] ✓ Loaded {len(images)} images")

            # Enable/disable clear all button based on loaded images
            if self.clear_all_btn:
                self.clear_all_btn.setEnabled(len(self.current_images) > 0)

        except Exception as e:
            error_msg = f"Error loading images: {e}"
            self.log(error_msg, "error")
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            print(f"[LOAD] ✗ Error: {e}")

    def on_thumbnail_clicked(self, image_path: str):
        """Handle thumbnail click to update selection state."""
        # kept for backwards compatibility; not used when double-click flow is active
        self.on_thumbnail_selected(image_path)

    def on_thumbnail_selected(self, image_path: str):
        """Handle single-click selection (clears multi-select, selects only this one)."""
        # Clear multi-select, select only this one
        self.selected_images = [image_path]

        # Update selection state for all thumbnails
        for i in range(self.image_grid_layout.count()):
            item = self.image_grid_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, ImageThumbnail):
                    is_selected = (widget.image_path == image_path)
                    widget.set_selected(is_selected)

        self.statusBar().showMessage(f"Selected: {Path(image_path).name}")

    def on_thumbnail_ctrl_clicked(self, image_path: str):
        """Toggle selection for multi-select (Ctrl+click)."""
        if image_path in self.selected_images:
            self.selected_images.remove(image_path)
        else:
            self.selected_images.append(image_path)

        # Update visual state for all thumbnails
        for i in range(self.image_grid_layout.count()):
            item = self.image_grid_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), ImageThumbnail):
                widget = item.widget()
                widget.set_selected(widget.image_path in self.selected_images)

        count = len(self.selected_images)
        if count > 0:
            self.statusBar().showMessage(f"{count} image(s) selected")
        else:
            self.statusBar().showMessage("Ready")

    def delete_selected_images(self):
        """Delete key handler - remove all selected images with confirmation."""
        if not self.selected_images:
            return

        count = len(self.selected_images)
        if count > 1:
            reply = QMessageBox.question(
                self, "Delete Images",
                f"Remove {count} selected images from set?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

        # Remove all selected images
        for img in self.selected_images[:]:
            if img in self.current_images:
                self.current_images.remove(img)

        removed = count
        self.selected_images = []
        self.log(f"Removed {removed} image(s) from set", "info")
        self.refresh_image_grid()
        self.statusBar().showMessage(f"{len(self.current_images)} images remaining")

    def select_all_images(self):
        """Ctrl+A handler - select all images in the grid."""
        if not self.current_images:
            return

        self.selected_images = self.current_images[:]

        # Update visual state for all thumbnails
        for i in range(self.image_grid_layout.count()):
            item = self.image_grid_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), ImageThumbnail):
                item.widget().set_selected(True)

        self.statusBar().showMessage(f"Selected all {len(self.selected_images)} images")

    def clear_image_selection(self):
        """Escape handler - clear all image selections."""
        self.selected_images = []

        # Update visual state for all thumbnails
        for i in range(self.image_grid_layout.count()):
            item = self.image_grid_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), ImageThumbnail):
                item.widget().set_selected(False)

        self.statusBar().showMessage("Selection cleared")

    def clear_all_images(self):
        """Clear all images from the current view."""
        if not self.current_images:
            return

        confirm = QMessageBox.question(
            self, "Clear All Images",
            f"Remove all {len(self.current_images)} images from view?\n\n"
            "This does NOT delete files from disk.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            self.current_images = []
            self.selected_images = []
            self.refresh_image_grid()
            self.log("Cleared all images from view", "info")
            if self.clear_all_btn:
                self.clear_all_btn.setEnabled(False)

    # ============================================================
    # Feature 1: Delete Individual Images from Set
    # ============================================================
    def delete_image_from_set(self, image_path: str):
        """Remove an image (or all selected images) from the current product set."""
        # If multiple images are selected, delete all of them
        if len(self.selected_images) > 1:
            count = 0
            for img in self.selected_images[:]:  # Copy list to avoid modification during iteration
                if img in self.current_images:
                    self.current_images.remove(img)
                    count += 1
            self.selected_images = []
            self.log(f"Removed {count} images from set", "info")
        else:
            # Single delete
            if image_path in self.current_images:
                self.current_images.remove(image_path)
            if image_path in self.selected_images:
                self.selected_images.remove(image_path)
            self.log(f"Removed: {Path(image_path).name}", "info")

        # Refresh the grid
        self.refresh_image_grid()
        self.statusBar().showMessage(f"{len(self.current_images)} images remaining")

    def refresh_image_grid(self):
        """Refresh the image grid with current images."""
        # Clear existing thumbnails
        while self.image_grid_layout.count():
            item = self.image_grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Re-add remaining images
        row, col = 0, 0
        max_cols = IMAGE_GRID_COLUMNS

        for img_path in self.current_images:
            thumb = ImageThumbnail(img_path)
            thumb.clicked.connect(self.preview_image)
            thumb.selected.connect(self.on_thumbnail_selected)
            thumb.ctrl_clicked.connect(self.on_thumbnail_ctrl_clicked)  # Multi-select
            thumb.crop_requested.connect(self.crop_image)
            thumb.remove_bg_requested.connect(self.remove_image_background)
            thumb.delete_requested.connect(self.delete_image_from_set)

            # Restore selection state if this image was previously selected
            if img_path in self.selected_images:
                thumb.set_selected(True)

            self.image_grid_layout.addWidget(thumb, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        self.log(f"Image grid refreshed: {len(self.current_images)} images", "info")

    # ============================================================
    # Feature 2: Drag Additional Images into Existing Set
    # ============================================================
    def images_drag_enter(self, event):
        """Handle drag enter on images area."""
        if event.mimeData().hasUrls():
            # Check if files are images
            image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.tiff', '.tif', '.bmp'}
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if Path(path).suffix.lower() in image_extensions:
                    event.acceptProposedAction()
                    return
            # Also accept folders containing images
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if os.path.isdir(path):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def images_drop(self, event):
        """Handle drop on images area - add images to current set.
        
        PATCHED: Added proper error handling for file operations.
        """
        urls = event.mimeData().urls()
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.tiff', '.tif', '.bmp'}
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
                            if img_path not in self.current_images:
                                # Copy to current folder if different location
                                if self.current_folder and Path(img_path).parent != Path(self.current_folder):
                                    import shutil
                                    dest = Path(self.current_folder) / Path(img_path).name
                                    # Avoid overwriting existing files
                                    if dest.exists():
                                        base = dest.stem
                                        ext = dest.suffix
                                        counter = 1
                                        while dest.exists():
                                            dest = Path(self.current_folder) / f"{base}_{counter}{ext}"
                                            counter += 1
                                    # FIX: Wrap file copy in try/except for error handling
                                    try:
                                        shutil.copy2(img_path, dest)
                                        self.current_images.append(str(dest))
                                        added += 1
                                    except PermissionError as e:
                                        errors.append(f"{Path(img_path).name}: Permission denied")
                                        logger.error(f"Cannot copy {Path(img_path).name}: {e}")
                                    except OSError as e:
                                        errors.append(f"{Path(img_path).name}: {e}")
                                        logger.error(f"Cannot copy {Path(img_path).name}: {e}")
                                else:
                                    self.current_images.append(img_path)
                                    added += 1
                        except Exception as e:
                            errors.append(f"{Path(img_path).name}: {e}")
                            
                elif Path(path).suffix.lower() in image_extensions:
                    try:
                        if path not in self.current_images:
                            # Copy to current folder if different location
                            if self.current_folder and Path(path).parent != Path(self.current_folder):
                                import shutil
                                dest = Path(self.current_folder) / Path(path).name
                                # Avoid overwriting existing files
                                if dest.exists():
                                    base = dest.stem
                                    ext = dest.suffix
                                    counter = 1
                                    while dest.exists():
                                        dest = Path(self.current_folder) / f"{base}_{counter}{ext}"
                                        counter += 1
                                # FIX: Wrap file copy in try/except for error handling
                                try:
                                    shutil.copy2(path, dest)
                                    self.current_images.append(str(dest))
                                    added += 1
                                except PermissionError as e:
                                    errors.append(f"{Path(path).name}: Permission denied")
                                    logger.error(f"Cannot copy {Path(path).name}: {e}")
                                except OSError as e:
                                    errors.append(f"{Path(path).name}: {e}")
                                    logger.error(f"Cannot copy {Path(path).name}: {e}")
                            else:
                                self.current_images.append(path)
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

    def detect_category(self, folder_path: str):
        """Auto-detect category from folder name or contents."""
        folder_name = os.path.basename(folder_path).lower()

        category_keywords = {
            "militaria": ["military", "wwii", "ww2", "uniform", "medal", "weapon", "army", "navy", "usaf", "luftwaffe"],
            "books": ["book", "manuscript", "document", "map", "atlas", "signed", "first edition"],
            "fineart": ["art", "painting", "sculpture", "print", "drawing", "lithograph"],
            "collectibles": ["antique", "vintage", "coin", "pottery", "ceramic", "glass", "jewelry"]
        }

        for cat_id, keywords in category_keywords.items():
            if any(kw in folder_name for kw in keywords):
                # Find and select the category
                for i in range(self.category_combo.count()):
                    if self.category_combo.itemData(i) == cat_id:
                        self.category_combo.setCurrentIndex(i)
                        self.log(f"Auto-detected category: {cat_id}", "info")
                        return

    def on_category_changed(self, _index: Optional[int] = None):
        """Handle category selection change.
        _index may be None when invoked programmatically by AI flows.
        """
        if _index is None and self.category_combo is not None:
            try:
                _index = self.category_combo.currentIndex()
            except Exception:
                _index = None

        self.update_subcategories()
        if self.current_folder:
            self.generate_sku()

    def update_subcategories(self):
        """Update subcategory dropdown based on selected category."""
        self.subcategory_combo.clear()

        cat_id = self.category_combo.currentData()
        if cat_id:
            subcategories = (
                self.config.get("categories", {})
                .get(cat_id, {})
                .get("subcategories", [])
            )
            for subcat in subcategories:
                self.subcategory_combo.addItem(subcat)

    def generate_sku(self):
        """Generate a new SKU for the current category."""
        logger.debug("Generating SKU...")

        cat_id = self.category_combo.currentData()
        if not cat_id:
            logger.warning("No category selected for SKU generation")
            self.log("No category selected - cannot generate SKU", "warning")
            return

        try:
            prefix = self.config["categories"][cat_id]["prefix"]
            logger.debug(f"Generating SKU with prefix: {prefix}")

            sku = self.sku_scanner.get_next_sku(prefix)
            self.sku_edit.setText(sku)
            self.update_export_button_state()

            logger.info(f"Generated SKU: {sku}")
            print(f"[SKU] Generated: {sku}")
            self.log(f"Generated SKU: {sku}", "info")
        except KeyError as e:
            logger.error(f"Category '{cat_id}' not found in config: {e}")
            self.log(f"Category '{cat_id}' not found in config: {e}", "error")
        except Exception as e:
            logger.error(f"SKU generation error: {e}")
            logger.debug(traceback.format_exc())
            self.log(f"SKU generation error: {e}", "error")

    def regenerate_sku(self):
        """Regenerate SKU (get next available)."""
        self.generate_sku()

    def preview_image(self, image_path: str):
        """Show full-size image preview."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Image Preview")
        # Remove the context help (?) button on Windows titlebar
        try:
            dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        except Exception:
            pass
        dialog.setMinimumSize(800, 600)
        dialog.setStyleSheet(ModernPalette.get_stylesheet())

        layout = QVBoxLayout(dialog)

        label = QLabel()
        pixmap = QPixmap(image_path)
        scaled = pixmap.scaled(
            780, 560,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        label.setPixmap(scaled)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        dialog.exec_()

    def crop_image(self, image_path: str):
        """Open crop dialog for an image - overwrites the original file."""
        print(f"[CROP] Opening crop dialog for: {os.path.basename(image_path)}")
        logger.info(f"Opening crop dialog for: {image_path}")

        try:
            dialog = CropDialog(image_path, self, config=self.config)
            # Apply modern theme to crop dialog if it supports it
            if hasattr(dialog, 'setStyleSheet'):
                dialog.setStyleSheet(ModernPalette.get_stylesheet())

            if dialog.exec_() == QDialog.Accepted:
                self.log(f"✓ Saved: {os.path.basename(image_path)} (original overwritten)", "success")
                logger.info(f"Image cropped and saved: {image_path}")
                print(f"[CROP] ✓ Image saved: {os.path.basename(image_path)}")

                # Refresh the image grid to show updated thumbnail
                if self.current_folder:
                    self.refresh_image_grid()
            else:
                logger.info("Crop dialog cancelled")
                print("[CROP] Cancelled")
        except Exception as e:
            error_print(f"Crop error: {e}")
            logger.error(f"Crop error for {image_path}: {e}")
            logger.debug(traceback.format_exc())
            self.log(f"Crop error: {e}", "error")

    def crop_selected_image(self):
        """Crop the first selected image."""
        if self.current_images:
            self.crop_image(self.current_images[0])

    def remove_image_background(self, image_path: str):
        """Remove background from a single image."""
        print(f"[BG-REMOVE] Starting background removal: {os.path.basename(image_path)}")
        logger.info(f"Starting background removal: {image_path}")

        try:
            self.log(f"Removing background: {os.path.basename(image_path)}", "info")
            self.progress_bar.setValue(0)
            self.status_label.setText("Removing background...")

            remover = BackgroundRemover()
            strength = self.bg_strength_slider.value() / 100
            bg_color = self.config.get("image_processing", {}).get(
                "background_removal", {}
            ).get("background_color", "#FFFFFF")

            logger.debug(f"BG removal settings: strength={strength}, bg_color={bg_color}")

            output_path = remover.remove_background(
                image_path,
                strength=strength,
                bg_color=bg_color
            )

            self.progress_bar.setValue(100)
            self.status_label.setText("Background removed!")
            self.log(f"Background removed: {os.path.basename(output_path)}", "success")
            logger.info(f"Background removed successfully: {output_path}")
            print(f"[BG-REMOVE] ✓ Complete: {os.path.basename(output_path)}")

            # Reload images
            self.load_images_from_folder(self.current_folder)

        except Exception as e:
            error_msg = f"Background removal error: {e}"
            self.log(error_msg, "error")
            self.status_label.setText("Error removing background")
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            print(f"[BG-REMOVE] ✗ Error: {e}")

    def remove_background(self):
        """Remove background from all images."""
        if not self.current_images:
            return

        if not self.bg_removal_check.isChecked():
            QMessageBox.information(
                self, "Background Removal Disabled",
                "Enable 'AI Background Removal' in Settings tab first."
            )
            return

        # Check rembg installation
        status = check_rembg_installation()

        if not REMBG_AVAILABLE:
            reply = QMessageBox.question(
                self, "rembg Not Installed",
                f"{status['recommendation']}\n\n"
                "Would you like to continue with fallback method?\n"
                "(Results may be lower quality)",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        # Process all images with progress
        self.log(f"Removing backgrounds from {len(self.current_images)} images...", "info")
        self.progress_bar.setValue(0)
        self.status_label.setText("Removing backgrounds...")

        remover = BackgroundRemover(self.config)

        strength = self.bg_strength_slider.value() / 100
        bg_color = self.config.get("image_processing", {}).get(
            "background_removal", {}
        ).get("background_color", "#FFFFFF")

        def progress_callback(current, total, filename):
            # Guard against division by zero
            if total == 0:
                progress = 0
            else:
                progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)
            self.status_label.setText(f"Processing {current}/{total}: {filename}")
            QApplication.processEvents()

        try:
            results = remover.batch_remove(
                self.current_folder,
                progress_callback=progress_callback,
                strength=strength,
                bg_color=bg_color
            )

            self.progress_bar.setValue(100)
            self.status_label.setText("Background removal complete!")

            success_count = results["processed"]
            failed_count = results["failed"]

            self.log(f"Background removal: {success_count} succeeded, {failed_count} failed", "success")

            if failed_count > 0:
                self.log(f"Errors: {len(results['errors'])} images failed", "warning")

            # Reload images to show processed versions
            self.load_images_from_folder(self.current_folder)

        except Exception as e:
            self.log(f"Background removal error: {e}", "error")
            self.status_label.setText("Error removing backgrounds")

    def optimize_images(self):
        """Process and optimize all images."""
        if not self.current_folder:
            logger.warning("No folder loaded for optimization")
            return

        print(f"[OPTIMIZE] Starting image optimization for: {self.current_folder}")
        logger.info(f"Starting image optimization: {self.current_folder}")
        logger.info(f"Images to optimize: {len(self.current_images)}")

        self.log("Starting image optimization...", "info")
        self.status_label.setText("Optimizing images...")
        self.progress_bar.setValue(0)

        options = {
            "max_dimension": self.config.get("image_processing", {}).get("max_dimension", 2400),
            "quality": self.config.get("image_processing", {}).get("webp_quality", 88),
            "strip_exif": self.config.get("image_processing", {}).get("strip_exif", True),
            "output_format": "webp",
            "delete_originals": True
        }

        logger.debug(f"Optimization options: {options}")

        self.processing_thread = ProcessingThread(
            self.current_folder,
            self.config,
            options
        )
        self.processing_thread.progress.connect(self.on_processing_progress)
        self.processing_thread.finished.connect(self.on_processing_finished)
        self.processing_thread.error.connect(self.on_processing_error)
        self.processing_thread.start()

        # Disable buttons during processing
        self.optimize_btn.setEnabled(False)

    def on_processing_progress(self, percent: int, message: str):
        """Handle processing progress updates."""
        self.progress_bar.setValue(percent)
        self.status_label.setText(message)
        if percent % 25 == 0:  # Log every 25%
            logger.debug(f"Processing progress: {percent}% - {message}")

    def on_processing_finished(self, results: dict):
        """Handle processing completion - WITH CLEANUP."""
        self.optimize_btn.setEnabled(True)
        self.upload_btn.setEnabled(True)

        success_count = len(results.get("images", []))
        error_count = len(results.get("errors", []))

        logger.info(f"Image optimization complete: {success_count} succeeded, {error_count} failed")
        print(f"[OPTIMIZE] ✓ Complete: {success_count} images processed")

        self.log(f"Optimization complete: {success_count} images processed", "success")

        if error_count > 0:
            self.log(f"Errors: {error_count} images failed", "warning")
            logger.warning(f"Optimization errors: {results.get('errors', [])}")
            for err in results.get("errors", []):
                print(f"[OPTIMIZE] ✗ Error: {err.get('file', 'unknown')}: {err.get('error', 'unknown')}")

        # Reload to show processed images
        processed_folder = Path(self.current_folder) / "processed"
        if processed_folder.exists():
            logger.info(f"Loading processed images from: {processed_folder}")
            self.load_images_from_folder(str(processed_folder))
            if self.clear_all_btn:
                self.clear_all_btn.setEnabled(len(self.current_images) > 0)

        # Log deletion summary if provided by processor
        try:
            deleted_count = sum(1 for r in results.get("images", []) if r.get("original_deleted"))
            if deleted_count:
                logger.info(f"Deleted {deleted_count} original file(s) after optimization")
                self.log(f"Deleted {deleted_count} original file(s)", "info")
        except Exception:
            pass

        # FIX: Clean up thread reference to prevent memory leak
        if self.processing_thread is not None:
            self.processing_thread.deleteLater()
            self.processing_thread = None

    def on_processing_error(self, error: str):
        """Handle processing errors - WITH CLEANUP."""
        self.optimize_btn.setEnabled(True)
        logger.error(f"Processing error: {error}")
        print(f"[OPTIMIZE] ✗ Processing error: {error}")
        self.log(f"Processing error: {error}", "error")
        self.status_label.setText("Error during processing")

        # FIX: Clean up thread reference to prevent memory leak
        if self.processing_thread is not None:
            self.processing_thread.deleteLater()
            self.processing_thread = None

    def analyze_and_autofill(self):
        """
        Use AI to analyze images and autofill ALL product fields.
        This is the primary "upload photos → AI fills everything" workflow.
        """
        print("[AI-ANALYZE] Starting image analysis and autofill...")
        logger.info("Starting AI analyze and autofill")

        if not self.current_images:
            logger.warning("No images loaded for analysis")
            QMessageBox.warning(self, "No Images", "Load a product folder first.")
            return

        try:
            self.log("🔍 Analyzing images with AI...", "info")
            self.status_label.setText("AI analyzing images...")
            self.progress_bar.setValue(10)
            QApplication.processEvents()

            logger.debug("Initializing AIEngine for analysis")
            engine = AIEngine(self.config)
            images = self.current_images[:MAX_AI_IMAGES_ANALYZE]

            logger.info(f"Analyzing {len(images)} images (max {MAX_AI_IMAGES_ANALYZE})")
            print(f"[AI-ANALYZE] Sending {len(images)} images to AI...")

            product_data = {
                "title": self.title_edit.text(),
                "condition": self.condition_combo.currentText(),
                "era": self.era_edit.text(),
                "origin": self.origin_edit.text(),
                "images": images,
            }

            categories = self.config.get("categories", {})
            logger.debug(f"Available categories: {list(categories.keys())}")

            self.progress_bar.setValue(30)
            QApplication.processEvents()

            result = engine.suggest_fields(product_data, categories)

            if not result:
                self.log("❌ AI analysis returned no data - check API key", "warning")
                self.status_label.setText("Analysis failed - check API key")
                self.progress_bar.setValue(0)
                QMessageBox.warning(
                    self, "AI Error",
                    "AI analysis returned no results.\n\n"
                    "Please check:\n"
                    "1. ANTHROPIC_API_KEY is set in .env file\n"
                    "2. API key is valid (starts with sk-ant-)\n"
                    "3. Network connection is working"
                )
                return

            self.progress_bar.setValue(50)
            QApplication.processEvents()

            fields_filled = []

            # Title
            if result.get("title"):
                self.title_edit.setText(result["title"])
                fields_filled.append("Title")
                self.log(f"📝 Title: {result['title']}", "info")

            # Category mapping
            cat_id = result.get("category_id")
            if cat_id:
                idx = self.category_combo.findData(cat_id)
                if idx >= 0:
                    self.category_combo.setCurrentIndex(idx)
                    self.on_category_changed()  # Refresh subcategories
                    fields_filled.append("Category")
                    self.log(f"📂 Category: {cat_id}", "info")
                else:
                    self.log(f"⚠️ Category '{cat_id}' not found in config", "warning")

            QApplication.processEvents()

            # Subcategory
            subc = result.get("subcategory")
            if subc:
                # Try exact match first, then contains match
                idx = self.subcategory_combo.findText(subc, Qt.MatchExactly)
                if idx < 0:
                    idx = self.subcategory_combo.findText(subc, Qt.MatchContains)
                if idx >= 0:
                    self.subcategory_combo.setCurrentIndex(idx)
                else:
                    # Add it temporarily
                    self.subcategory_combo.insertItem(0, subc)
                    self.subcategory_combo.setCurrentIndex(0)
                fields_filled.append("Subcategory")
                self.log(f"📁 Subcategory: {subc}", "info")

            # Condition
            cond = result.get("condition")
            if cond:
                idx = self.condition_combo.findText(cond, Qt.MatchContains)
                if idx >= 0:
                    self.condition_combo.setCurrentIndex(idx)
                else:
                    self.condition_combo.insertItem(0, cond)
                    self.condition_combo.setCurrentIndex(0)
                fields_filled.append("Condition")
                self.log(f"⭐ Condition: {cond}", "info")

            self.progress_bar.setValue(70)
            QApplication.processEvents()

            # Era & Origin
            if result.get("era"):
                self.era_edit.setText(result["era"])
                fields_filled.append("Era")
                self.log(f"📅 Era: {result['era']}", "info")
            if result.get("origin"):
                self.origin_edit.setText(result["origin"])
                fields_filled.append("Origin")
                self.log(f"🌍 Origin: {result['origin']}", "info")

            # Description
            if result.get("description"):
                self.description_edit.setPlainText(result["description"])
                fields_filled.append("Description")
                self.log(f"📄 Description: {len(result['description'])} chars", "info")

            self.progress_bar.setValue(85)
            QApplication.processEvents()

            # SEO fields
            if result.get("seo_title"):
                self.seo_title_edit.setText(result["seo_title"][:70])
                fields_filled.append("SEO Title")

            if result.get("seo_description"):
                self.seo_desc_edit.setPlainText(result["seo_description"][:160])
                fields_filled.append("SEO Description")

            keywords = result.get("keywords", [])
            if keywords:
                if isinstance(keywords, list):
                    self.seo_keywords_edit.setText(", ".join(keywords))
                else:
                    self.seo_keywords_edit.setText(str(keywords))
                fields_filled.append("Keywords")
                self.log(f"🏷️ Keywords: {len(keywords) if isinstance(keywords, list) else 1} generated", "info")

            self.progress_bar.setValue(95)
            QApplication.processEvents()

            # Valuation -> show in log but don't auto-set price
            val = result.get("valuation") or {}
            rec_price = val.get("recommended")
            low_price = val.get("low", 0)
            high_price = val.get("high", 0)
            confidence = val.get("confidence", "Unknown")

            if isinstance(rec_price, (int, float)) and rec_price > 0:
                self.last_valuation = {
                    "low": low_price,
                    "high": high_price,
                    "recommended": rec_price,
                    "confidence": confidence,
                    "notes": val.get("notes", "")
                }
                self.log(
                    f"💰 Estimated Value: ${low_price:,.0f} - ${high_price:,.0f} "
                    f"(Recommended: ${rec_price:,.0f}, {confidence} confidence)",
                    "info"
                )
                # Optionally set the price
                if self.price_spin.value() == 0:
                    self.price_spin.setValue(float(rec_price))
                    fields_filled.append("Price")

            self.progress_bar.setValue(100)
            self.update_export_button_state()
            self.status_label.setText("Analysis complete!")

            # Success summary
            self.log(f"✅ AI filled {len(fields_filled)} fields: {', '.join(fields_filled)}", "success")
            self.log("Review and adjust as needed, then Generate Description for final polish", "info")

        except ValueError as ve:
            # Likely missing API key
            self.progress_bar.setValue(0)
            QMessageBox.critical(
                self,
                "AI Configuration Error",
                f"{ve}\n\n"
                "To fix this:\n"
                "1. Open desktop-app/.env file\n"
                "2. Add: ANTHROPIC_API_KEY=sk-ant-api03-your-key\n"
                "3. Restart the application"
            )
            self.status_label.setText("API key not configured")
        except Exception as e:
            self.progress_bar.setValue(0)
            self.log(f"❌ AI analyze error: {e}", "error")
            self.status_label.setText("Analysis error")
            QMessageBox.warning(
                self, "AI Error",
                f"An error occurred during analysis:\n\n{str(e)}"
            )

    def generate_description(self):
        """Generate product description using AI."""
        print("[AI] Starting description generation...")
        logger.info("Starting AI description generation")

        if not self.current_images:
            logger.warning("No images loaded for description generation")
            QMessageBox.warning(self, "No Images", "Load a product folder first.")
            return

        self.log("Generating AI description...", "info")
        self.status_label.setText("AI generating description...")

        try:
            print("[AI] Initializing AI Engine...")
            logger.debug("Initializing AIEngine")
            engine = AIEngine(self.config)

            category = self.category_combo.currentData()
            if not category:
                logger.warning("No category selected")
                QMessageBox.warning(self, "No Category", "Please select a category first.")
                return

            product_data = {
                "title": self.title_edit.text(),
                "category": category,
                "subcategory": self.subcategory_combo.currentText(),
                "condition": self.condition_combo.currentText(),
                "era": self.era_edit.text(),
                "origin": self.origin_edit.text(),
                "images": self.current_images[:MAX_AI_IMAGES_DESCRIPTION]
            }

            logger.info(f"Sending {len(product_data['images'])} images to AI")
            print(f"[AI] Sending request with {len(product_data['images'])} images...")

            result = engine.generate_description(product_data)

            # Log the result
            logger.debug(f"AI Response: {result}")
            print(f"[AI] Response received: {type(result)}")

            if result:
                # CHECK FOR ERRORS FIRST
                if result.get("error"):
                    self.log(f"AI Error: {result['error']}", "error")
                    QMessageBox.warning(self, "AI Error", f"Failed to generate description:\n\n{result['error']}")
                    self.status_label.setText("AI error - check log")
                    return

                # ============================================================
                # Issue 3: SEO Fields Population - Robust field mapping
                # ============================================================

                # Populate description
                description = result.get("description", "")
                if description:
                    self.description_edit.setPlainText(description)
                    self.log(f"Description generated ({len(description)} chars)", "info")
                else:
                    self.log("Warning: No description in AI response", "warning")

                # Populate SEO Title - try multiple keys
                seo_title = (
                    result.get("seo_title") or
                    result.get("seoTitle") or
                    result.get("suggested_title") or
                    ""
                )
                if seo_title:
                    # Truncate to 70 chars as per SEO best practices
                    self.seo_title_edit.setText(seo_title[:70])
                    self.log(f"SEO Title: {seo_title[:50]}...", "info")

                # Populate SEO Meta Description - try multiple keys
                seo_desc = (
                    result.get("seo_description") or
                    result.get("seoDescription") or
                    result.get("meta_description") or
                    ""
                )
                if seo_desc:
                    # Truncate to 160 chars as per SEO best practices
                    self.seo_desc_edit.setPlainText(seo_desc[:160])
                    self.log(f"SEO Description: {seo_desc[:50]}...", "info")
                elif description:
                    # Fallback: use first 160 chars of description
                    fallback_desc = description[:160].rsplit(' ', 1)[0] + "..."
                    self.seo_desc_edit.setPlainText(fallback_desc)
                    self.log("SEO Description: Auto-generated from description", "info")

                # Populate Keywords - handle both list and string formats
                keywords = result.get("keywords") or result.get("seoKeywords") or []
                if keywords:
                    if isinstance(keywords, list):
                        keywords_str = ", ".join(str(k) for k in keywords)
                    else:
                        keywords_str = str(keywords)
                    self.seo_keywords_edit.setText(keywords_str)
                    keyword_count = len(keywords) if isinstance(keywords, list) else keywords_str.count(",") + 1
                    self.log(f"Keywords: {keyword_count} generated", "info")

                # Populate suggested title if current title is empty
                suggested_title = result.get("suggested_title") or result.get("title") or ""
                if suggested_title and not self.title_edit.text().strip():
                    self.title_edit.setText(suggested_title)
                    self.log(f"Suggested title: {suggested_title}", "info")

                # Handle valuation if present (from description generation)
                valuation = result.get("valuation")
                if valuation and isinstance(valuation, dict):
                    recommended = valuation.get("recommended") or 0
                    low = valuation.get("low") or 0
                    high = valuation.get("high") or 0
                    if recommended:
                        self.log(
                            f"Price Research: ${low:,.2f} - ${high:,.2f} (Recommended: ${recommended:,.2f})",
                            "info"
                        )
                        self.last_valuation = {
                            "low": low,
                            "high": high,
                            "recommended": recommended,
                            "confidence": valuation.get("confidence", "Medium"),
                            "notes": valuation.get("notes", "")
                        }
                        # Optionally suggest the price
                        if self.price_spin.value() == 0 and recommended > 0:
                            self.price_spin.setValue(float(recommended))
                            self.log(f"Price auto-set to ${recommended:,.2f}", "info")

                # Handle condition notes
                condition_notes = result.get("condition_notes", "")
                if condition_notes:
                    self.log(f"Condition: {condition_notes[:100]}...", "info")

                self.log("AI description generated successfully", "success")
                self.update_export_button_state()
            else:
                self.log("AI generation returned no results", "warning")
                QMessageBox.warning(self, "AI Error", "No response from AI. Check your API key configuration.")

        except Exception as e:
            self.log(f"AI error: {e}", "error")
            QMessageBox.critical(self, "AI Error", f"Exception occurred:\n\n{str(e)}")

        self.status_label.setText("Ready")

    def generate_valuation(self):
        """Generate AI-powered price research and display guidance."""
        print("[AI] Starting price valuation research...")
        logger.info("Starting AI price valuation")

        self.log("Generating price research...", "info")
        self.status_label.setText("Researching prices...")

        try:
            logger.debug("Initializing AIEngine for valuation")
            engine = AIEngine(self.config)

            category = self.category_combo.currentData()
            if not category:
                QMessageBox.warning(self, "No Category", "Please select a category first.")
                return

            product_data = {
                "title": self.title_edit.text(),
                "category": category,
                "condition": self.condition_combo.currentText(),
                "era": self.era_edit.text(),
                "description": self.description_edit.toPlainText(),
                "images": self.current_images[:MAX_AI_IMAGES_VALUATION]
            }

            logger.info(f"Sending valuation request with {len(product_data.get('images', []))} images")
            print(f"[AI] Requesting valuation for: {product_data.get('title', 'Unknown')}")

            valuation = engine.generate_valuation(product_data)
            logger.debug(f"Valuation response: {valuation}")

            if valuation:
                low = valuation.get("low") or 0
                high = valuation.get("high") or 0
                recommended = valuation.get("recommended") or 0
                confidence = valuation.get("confidence", "Medium")
                notes = valuation.get("notes", "")

                # Display pricing research in log (don't auto-set)
                self.log(
                    f"Price Research Results:\n"
                    f"   Suggested Range: ${low:,.2f} - ${high:,.2f}\n"
                    f"   Recommended: ${recommended:,.2f}\n"
                    f"   Confidence: {confidence}\n"
                    f"   Notes: {notes}",
                    "info"
                )

                # Store for later export (but don't auto-fill the price field)
                self.last_valuation = {
                    "low": low,
                    "high": high,
                    "recommended": recommended,
                    "confidence": confidence,
                    "notes": notes
                }

                logger.info(f"Valuation complete: ${low}-${high}, recommended=${recommended}")
                print(f"[AI] ✓ Valuation: ${low:,.0f}-${high:,.0f}")
            else:
                logger.warning("Valuation returned no data")
                print("[AI] ✗ No valuation data returned")
                self.log("No valuation data received", "warning")

        except ValueError as ve:
            logger.error(f"Valuation configuration error: {ve}")
            print(f"[AI] ✗ Config error: {ve}")
            self.log(f"Price research config error: {ve}", "error")
            QMessageBox.warning(self, "Configuration Error", str(ve))
        except Exception as e:
            logger.error(f"Price research error: {e}")
            logger.debug(traceback.format_exc())
            print(f"[AI] ✗ Error: {e}")
            self.log(f"Price research error: {e}", "error")
        finally:
            self.status_label.setText("Ready")

    def upload_to_imagekit(self):
        """Upload processed images to ImageKit - WITH VALIDATION."""
        print("[UPLOAD] Starting ImageKit upload...")
        logger.info("Starting ImageKit upload")

        if not self.current_images:
            logger.warning("No images to upload")
            QMessageBox.warning(self, "No Images", "Load a product folder first.")
            return

        # Pre-flight check for ImageKit configuration
        private_key = os.getenv("IMAGEKIT_PRIVATE_KEY") or self.config.get("imagekit", {}).get("private_key", "")
        if not private_key:
            logger.error("ImageKit private key not configured")
            print("[UPLOAD] ✗ ImageKit not configured")
            QMessageBox.warning(
                self, "ImageKit Not Configured",
                "ImageKit private key is not configured.\n\n"
                "Please add IMAGEKIT_PRIVATE_KEY to your .env file:\n"
                "  IMAGEKIT_PRIVATE_KEY=private_xxxxx\n\n"
                "Get your keys from:\n"
                "https://imagekit.io/dashboard/developer/api-keys"
            )
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
            logger.debug("Initializing ImageKitUploader")
            uploader = ImageKitUploader(self.config)

            category = self.category_combo.currentData()
            if not category:
                logger.warning("No category selected for upload")
                QMessageBox.warning(self, "No Category", "Please select a category first.")
                return

            sku = self.sku_edit.text()
            if not sku:
                logger.warning("No SKU for upload")
                QMessageBox.warning(self, "No SKU", "Please generate a SKU first.")
                return

            folder = f"products/{category}/{sku}"
            logger.info(f"Upload folder: {folder}")
            print(f"[UPLOAD] Target folder: {folder}")

            uploaded_urls = []
            total = len(images_to_upload)
            logger.info(f"Uploading {total} images")

            for i, img_path in enumerate(images_to_upload):
                print(f"[UPLOAD] {i+1}/{total}: {Path(img_path).name}")
                logger.debug(f"Uploading: {img_path}")

                result = uploader.upload(img_path, folder)
                if result and result.get("success"):
                    url = result.get("url")
                    if url:
                        uploaded_urls.append(url)
                        self.log(f"Uploaded: {Path(img_path).name} -> {url}", "info")
                        logger.info(f"✓ Uploaded: {Path(img_path).name}")
                    else:
                        self.log(f"Upload returned no URL for {Path(img_path).name}", "warning")
                        logger.warning(f"No URL returned for {img_path}")
                else:
                    error_msg = result.get("error", "Unknown error") if result else "No response"
                    self.log(f"Failed to upload {Path(img_path).name}: {error_msg}", "error")
                    logger.error(f"Upload failed: {Path(img_path).name} - {error_msg}")

                # Guard against division by zero
                if total == 0:
                    progress = 0
                else:
                    progress = int(((i + 1) / total) * 100)
                self.progress_bar.setValue(progress)
                self.status_label.setText(f"Uploading {i + 1}/{total}...")
                QApplication.processEvents()

            success_msg = f"Uploaded {len(uploaded_urls)}/{total} images to ImageKit"
            self.log(success_msg, "success")
            logger.info(success_msg)
            print(f"[UPLOAD] ✓ {success_msg}")

            # Store URLs
            self.uploaded_image_urls = uploaded_urls

            # Enable export button if we have required data
            if uploaded_urls and self.title_edit.text() and self.description_edit.toPlainText():
                self.export_btn.setEnabled(True)

        except Exception as e:
            error_msg = f"Upload error: {e}"
            self.log(error_msg, "error")
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            print(f"[UPLOAD] ✗ Error: {e}")

        self.status_label.setText("Ready")

    def update_export_button_state(self):
        """Update export button enabled state based on required fields."""
        if hasattr(self, 'export_btn'):
            can_export = (
                bool(self.sku_edit.text().strip()) and
                bool(self.title_edit.text().strip()) and
                bool(self.description_edit.toPlainText().strip()) and
                len(self.uploaded_image_urls) > 0
            )
            self.export_btn.setEnabled(can_export)


    def publish_to_website(self):
        """Publish product to kollect-it.com as draft."""
        print("[PUBLISH] Starting website publish...")
        logger.info("Starting website publish")
        
        # Validate required fields
        validation_errors = []
        if not self.title_edit.text():
            validation_errors.append("Missing title")
        if not self.description_edit.toPlainText():
            validation_errors.append("Missing description")
        if not self.uploaded_image_urls:
            validation_errors.append("No uploaded images - upload to ImageKit first")
        if not self.category_combo.currentData():
            validation_errors.append("No category selected")
        if not self.sku_edit.text():
            validation_errors.append("No SKU generated")
        
        if validation_errors:
            QMessageBox.warning(
                self, "Cannot Publish",
                "Please fix the following:\n\n• " + "\n• ".join(validation_errors)
            )
            return
        
        # Check publisher configuration
        if not self.website_publisher.is_configured():
            QMessageBox.warning(
                self, "Publisher Not Configured",
                "PRODUCT_INGEST_API_KEY not set.\n\n"
                "Add to your .env file:\n"
                "PRODUCT_INGEST_API_KEY=your-api-key\n\n"
                "Get this key from your website admin."
            )
            return
        
        # Confirm publish
        reply = QMessageBox.question(
            self, "Publish to Website",
            f"Publish \"{self.title_edit.text()}\" to kollect-it.com?\n\n"
            f"SKU: {self.sku_edit.text()}\n"
            f"Price: ${self.price_spin.value():,.2f}\n"
            f"Images: {len(self.uploaded_image_urls)}\n\n"
            "Product will be created as DRAFT for admin review.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply != QMessageBox.Yes:
            return
        
        self.log("Publishing to website...", "info")
        self.status_label.setText("Publishing to website...")
        QApplication.processEvents()
        
        # Build product data
        product_data = {
            "title": self.title_edit.text(),
            "sku": self.sku_edit.text(),
            "category": self.category_combo.currentData(),
            "subcategory": self.subcategory_combo.currentText() or None,
            "description": self.description_edit.toPlainText(),
            "price": self.price_spin.value(),
            "condition": self.condition_combo.currentText(),
            "era": self.era_edit.text() or None,
            "origin": self.origin_edit.text() or None,
            "images": [
                {"url": url, "alt": f"{self.title_edit.text()} - Image {i+1}", "order": i}
                for i, url in enumerate(self.uploaded_image_urls)
            ],
            "seoTitle": self.seo_title_edit.text() or self.title_edit.text(),
            "seoDescription": self.seo_desc_edit.toPlainText() or self.description_edit.toPlainText()[:160],
            "seoKeywords": [k.strip() for k in self.seo_keywords_edit.text().split(",") if k.strip()],
            "last_valuation": self.last_valuation
        }
        
        # Publish
        try:
            result = self.website_publisher.publish(product_data)
            
            if result.get("success"):
                admin_url = result.get("admin_url", "")
                
                self.log(f"✓ Published to website: {result.get('sku')}", "success")
                logger.info(f"Published to website: {result}")
                
                # Show success dialog
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Published Successfully")
                msg.setText(
                    f"Product published as DRAFT!\n\n"
                    f"SKU: {result.get('sku')}\n"
                    f"Status: Draft (awaiting review)\n\n"
                    f"Next: Review and publish in admin panel"
                )
                
                if admin_url:
                    open_admin_btn = msg.addButton("Open Admin", QMessageBox.ActionRole)
                
                new_product_btn = msg.addButton("New Product", QMessageBox.ActionRole)
                msg.addButton("OK", QMessageBox.AcceptRole)
                
                msg.exec_()
                
                if admin_url and msg.clickedButton() == open_admin_btn:
                    import webbrowser
                    webbrowser.open(admin_url)
                elif msg.clickedButton() == new_product_btn:
                    self.reset_form()
            
            else:
                error_msg = result.get("message") or result.get("error", "Unknown error")
                self.log(f"✗ Publish failed: {error_msg}", "error")
                logger.error(f"Publish failed: {result}")
                
                QMessageBox.warning(
                    self, "Publish Failed",
                    f"Could not publish to website:\n\n{error_msg}"
                )
        
        except Exception as e:
            self.log(f"✗ Publish error: {e}", "error")
            logger.error(f"Publish exception: {e}")
            QMessageBox.critical(self, "Error", f"Publish error: {e}")
        
        self.status_label.setText("Ready")

    def export_package(self):
        """Export product package to files."""
        print("[EXPORT] Starting product export...")
        logger.info("Starting product export")

        # Validate required fields with detailed logging
        validation_errors = []

        if not self.title_edit.text():
            validation_errors.append("Missing title")
        if not self.description_edit.toPlainText():
            validation_errors.append("Missing description")
        if not self.uploaded_image_urls:
            validation_errors.append("No uploaded images")
        if not self.category_combo.currentData():
            validation_errors.append("No category selected")
        if not self.sku_edit.text():
            validation_errors.append("No SKU generated")

        if validation_errors:
            error_msg = f"Export validation failed: {', '.join(validation_errors)}"
            logger.warning(error_msg)
            print(f"[EXPORT] ✗ Validation failed: {validation_errors}")
            QMessageBox.warning(self, "Cannot Export", f"Please fix the following:\n\n• " + "\n• ".join(validation_errors))
            return

        category = self.category_combo.currentData()
        sku = self.sku_edit.text()

        logger.info(f"Exporting product: SKU={sku}, Category={category}")
        print(f"[EXPORT] Exporting: {sku} ({category})")

        self.log("Exporting product package...", "info")
        self.status_label.setText("Exporting package...")

        try:
            # Ensure category folder exists
            category_prefix = self.config["categories"][category]["prefix"]
            self.sku_scanner.ensure_category_folder(category_prefix)
            self.log(f"Verified category folder: {category_prefix}", "info")

            # Build product data dictionary
            product_data = {
                "title": self.title_edit.text(),
                "sku": sku,
                "category": category,
                "subcategory": self.subcategory_combo.currentText() or None,
                "description": self.description_edit.toPlainText(),
                "descriptionHtml": f"<p>{self.description_edit.toPlainText()}</p>",
                "price": self.price_spin.value(),
                "condition": self.condition_combo.currentText(),
                "era": self.era_edit.text() or None,
                "origin": self.origin_edit.text() or None,
                "images": [
                    {"url": url, "alt": f"{self.title_edit.text()} - Image {i+1}", "order": i}
                    for i, url in enumerate(self.uploaded_image_urls)
                ],
                # Canonical ImageKit folder path (used by website ingestion)
                "imagekit_folder": f"products/{category_prefix}/{sku}",
                "seoTitle": self.seo_title_edit.text() or self.title_edit.text(),
                "seoDescription": self.seo_desc_edit.toPlainText() or self.description_edit.toPlainText()[:160],
                "seoKeywords": [k.strip() for k in self.seo_keywords_edit.text().split(",") if k.strip()],
                "last_valuation": self.last_valuation
            }

            # Export the package
            logger.debug(f"Product data prepared: {len(product_data.get('images', []))} images")
            print(f"[EXPORT] Calling output_generator.export_package()...")

            result = self.output_generator.export_package(product_data)
            logger.debug(f"Export result: {result}")

            if result.get("success"):
                output_path = result.get("output_path")
                logger.info(f"Export successful: {output_path}")
                print(f"[EXPORT] ✓ Success: {output_path}")
                self.log(f"Package exported to: {output_path}", "success")

                # Show success dialog with options
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Export Successful")
                msg.setText(f"Product package exported successfully!\n\nSKU: {sku}\nLocation: {output_path}")

                open_folder_btn = msg.addButton("Open Folder", QMessageBox.ActionRole)
                new_product_btn = msg.addButton("New Product", QMessageBox.ActionRole)
                msg.addButton("OK", QMessageBox.AcceptRole)

                msg.exec_()

                if msg.clickedButton() == open_folder_btn:
                    # Open folder in file explorer
                    import subprocess
                    import platform
                    if platform.system() == "Windows":
                        subprocess.Popen(f'explorer "{output_path}"')
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.Popen(["open", str(output_path)])
                    else:  # Linux
                        subprocess.Popen(["xdg-open", str(output_path)])

                elif msg.clickedButton() == new_product_btn:
                    # Reset form for new product
                    self.reset_form()
            else:
                error = result.get("error", "Unknown error")
                logger.error(f"Export failed: {error}")
                print(f"[EXPORT] ✗ Failed: {error}")
                self.log(f"Export failed: {error}", "error")
                QMessageBox.warning(self, "Export Failed", f"Error: {error}")

        except Exception as e:
            error_msg = f"Export exception: {type(e).__name__}: {e}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            print(f"[EXPORT] ✗ Exception: {e}")
            self.log(f"Export error: {e}", "error")
            QMessageBox.critical(self, "Error", f"Failed to export: {e}")

        self.status_label.setText("Ready")
        logger.info("Export operation completed")

    def reset_form(self):
        """Reset the form for a new product."""
        print("[RESET] Resetting form for new product...")
        logger.info("Resetting form for new product")

        self.title_edit.clear()
        self.sku_edit.clear()
        self.description_edit.clear()
        self.seo_title_edit.clear()
        self.seo_desc_edit.clear()
        self.seo_keywords_edit.clear()
        self.era_edit.clear()
        self.origin_edit.clear()
        self.price_spin.setValue(0)
        self.subcategory_combo.setCurrentIndex(0)
        self.current_folder = None
        self.current_images = []
        self.selected_images = []  # Clear multi-selection
        self.uploaded_image_urls = []
        self.last_valuation = None

        # Clear image grid
        while self.image_grid_layout.count():
            item = self.image_grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Disable buttons
        self.optimize_btn.setEnabled(False)
        self.upload_btn.setEnabled(False)
        self.export_btn.setEnabled(False)

        self.progress_bar.setValue(0)
        self.log("Form reset - ready for next product", "info")

    def open_folder(self):
        """Open folder selection dialog."""
        self.drop_zone.browse_folder()

    def export_product(self, format_type: str):
        """Export product data to file."""
        if format_type == "json":
            data = {
                "title": self.title_edit.text(),
                "sku": self.sku_edit.text(),
                "category": self.category_combo.currentData(),
                "description": self.description_edit.toPlainText(),
                "price": self.price_spin.value(),
                "condition": self.condition_combo.currentText()
            }

            filename, _ = QFileDialog.getSaveFileName(
                self, "Export JSON", f"{self.sku_edit.text()}.json", "JSON Files (*.json)"
            )

            if filename:
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                self.log(f"Exported to {filename}", "success")

    def batch_process(self):
        """Open batch processing dialog."""
        QMessageBox.information(
            self, "Batch Processing",
            "Batch processing will be available in the next update."
        )

    def show_settings(self):
        """Show settings dialog."""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTabWidget, QWidget, QFormLayout, QTextEdit, QCheckBox, QSpinBox, QDoubleSpinBox

        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.setMinimumSize(600, 500)
        dialog.setStyleSheet(ModernPalette.get_stylesheet())

        layout = QVBoxLayout(dialog)

        tabs = QTabWidget()

        # API Settings Tab
        api_tab = QWidget()
        api_layout = QFormLayout(api_tab)
        api_layout.setSpacing(12)

        self.api_key_edit = QLineEdit()
        self.api_key_edit.setText(self.config.get("api", {}).get("SERVICE_API_KEY", ""))
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        api_layout.addRow("Service API Key:", self.api_key_edit)

        self.prod_url_edit = QLineEdit()
        self.prod_url_edit.setText(self.config.get("api", {}).get("production_url", "https://kollect-it.com"))
        api_layout.addRow("Production URL:", self.prod_url_edit)

        self.use_prod_check = QCheckBox("Use Production API")
        self.use_prod_check.setChecked(self.config.get("api", {}).get("use_production", True))
        api_layout.addRow(self.use_prod_check)

        tabs.addTab(api_tab, "API")

        # ImageKit Settings Tab
        ik_tab = QWidget()
        ik_layout = QFormLayout(ik_tab)
        ik_layout.setSpacing(12)

        self.ik_public_edit = QLineEdit()
        self.ik_public_edit.setText(self.config.get("imagekit", {}).get("public_key", ""))
        ik_layout.addRow("Public Key:", self.ik_public_edit)

        self.ik_private_edit = QLineEdit()
        self.ik_private_edit.setText(self.config.get("imagekit", {}).get("private_key", ""))
        self.ik_private_edit.setEchoMode(QLineEdit.Password)
        ik_layout.addRow("Private Key:", self.ik_private_edit)

        self.ik_url_edit = QLineEdit()
        self.ik_url_edit.setText(self.config.get("imagekit", {}).get("url_endpoint", ""))
        ik_layout.addRow("URL Endpoint:", self.ik_url_edit)

        tabs.addTab(ik_tab, "ImageKit")

        # AI Settings Tab
        ai_tab = QWidget()
        ai_layout = QFormLayout(ai_tab)
        ai_layout.setSpacing(12)

        # API key is read from ANTHROPIC_API_KEY environment variable only
        # Show status with a Test button to verify connectivity
        api_key_status = "Configured" if os.getenv("ANTHROPIC_API_KEY") else "Not set (set ANTHROPIC_API_KEY in .env)"
        api_key_label = QLabel(api_key_status)
        api_key_label.setStyleSheet("color: #22c55e;" if os.getenv("ANTHROPIC_API_KEY") else "color: #f56565;")
        key_row = QWidget()
        key_row_layout = QHBoxLayout(key_row)
        key_row_layout.setContentsMargins(0, 0, 0, 0)
        key_row_layout.setSpacing(8)
        key_row_layout.addWidget(api_key_label, 1)
        test_key_btn = QPushButton("Test Anthropic Key")
        test_key_btn.clicked.connect(self.test_anthropic_key)
        key_row_layout.addWidget(test_key_btn, 0)
        ai_layout.addRow("Anthropic API Key:", key_row)

        self.ai_model_edit = QLineEdit()
        self.ai_model_edit.setText(self.config.get("ai", {}).get("model", "claude-sonnet-4-20250514"))
        ai_layout.addRow("Model:", self.ai_model_edit)

        tabs.addTab(ai_tab, "AI")

        # Image Processing Tab
        img_tab = QWidget()
        img_layout = QFormLayout(img_tab)
        img_layout.setSpacing(12)

        self.max_dim_spin = QSpinBox()
        self.max_dim_spin.setRange(800, 5000)
        self.max_dim_spin.setValue(self.config.get("image_processing", {}).get("max_dimension", 2400))
        img_layout.addRow("Max Dimension (px):", self.max_dim_spin)

        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(50, 100)
        self.quality_spin.setValue(self.config.get("image_processing", {}).get("webp_quality", 88))
        img_layout.addRow("WebP Quality:", self.quality_spin)

        self.strip_exif_check = QCheckBox("Strip EXIF Data")
        self.strip_exif_check.setChecked(self.config.get("image_processing", {}).get("strip_exif", True))
        img_layout.addRow(self.strip_exif_check)

        tabs.addTab(img_tab, "Image Processing")

        layout.addWidget(tabs)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("variant", "utility")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.setProperty("variant", "primary")
        save_btn.clicked.connect(lambda: self.save_settings_from_dialog(dialog))
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

        dialog.exec_()

    def save_settings_from_dialog(self, dialog):
        """Save settings from the settings dialog - WITH SAFETY CHECKS."""
        
        # FIX: Guard against None widgets
        # This can happen if dialog setup failed partway through
        
        # Ensure config sections exist
        if "api" not in self.config:
            self.config["api"] = {}
        if "imagekit" not in self.config:
            self.config["imagekit"] = {}
        if "ai" not in self.config:
            self.config["ai"] = {}
        if "image_processing" not in self.config:
            self.config["image_processing"] = {}

        # API settings - WITH SAFETY CHECKS
        if self.api_key_edit is not None:
            self.config["api"]["SERVICE_API_KEY"] = self.api_key_edit.text()
        
        if self.prod_url_edit is not None:
            self.config["api"]["production_url"] = self.prod_url_edit.text()
        
        if self.use_prod_check is not None:
            self.config["api"]["use_production"] = self.use_prod_check.isChecked()

        # ImageKit settings - WITH SAFETY CHECKS
        if self.ik_public_edit is not None:
            self.config["imagekit"]["public_key"] = self.ik_public_edit.text()
        
        if self.ik_private_edit is not None:
            self.config["imagekit"]["private_key"] = self.ik_private_edit.text()
        
        if self.ik_url_edit is not None:
            self.config["imagekit"]["url_endpoint"] = self.ik_url_edit.text()

        # AI settings - WITH SAFETY CHECKS
        # Note: API key is read from ANTHROPIC_API_KEY env var only, not saved to config
        if self.ai_model_edit is not None:
            self.config["ai"]["model"] = self.ai_model_edit.text()

        # Image processing settings - WITH SAFETY CHECKS
        if self.max_dim_spin is not None:
            self.config["image_processing"]["max_dimension"] = self.max_dim_spin.value()
        
        if self.quality_spin is not None:
            self.config["image_processing"]["webp_quality"] = self.quality_spin.value()
        
        if self.strip_exif_check is not None:
            self.config["image_processing"]["strip_exif"] = self.strip_exif_check.isChecked()

        # Save to file
        try:
            self.save_config()
            QMessageBox.information(dialog, "Settings Saved", "Settings have been saved successfully.")
            dialog.accept()
        except Exception as e:
            QMessageBox.warning(dialog, "Save Error", f"Failed to save settings:\n{e}")

    def test_anthropic_key(self):
        """Health check Anthropic API key via a minimal Messages API call."""
        key = os.getenv("ANTHROPIC_API_KEY", "")
        if not key:
            QMessageBox.warning(self, "Anthropic Key Test", "No Anthropic API key set. Add ANTHROPIC_API_KEY in .env and try again.")
            return

        model = self.ai_model_edit.text().strip() if self.ai_model_edit else self.config.get("ai", {}).get("model", "claude-sonnet-4-20250514")

        headers = {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        payload = {
            "model": model,
            "max_tokens": 1,
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": "ping"}]}
            ],
        }

        try:
            resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=20)
            if resp.status_code == 200:
                QMessageBox.information(self, "Anthropic Key Test", "Success: Anthropic API responded OK.")
            else:
                msg = None
                try:
                    data = resp.json()
                    msg = data.get("error", {}).get("message") or resp.text
                except Exception:
                    msg = resp.text
                QMessageBox.warning(self, "Anthropic Key Test", f"Failed ({resp.status_code}): {msg}")
        except Exception as e:
            QMessageBox.critical(self, "Anthropic Key Test", f"Error testing key: {e}")

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self, "About Kollect-It Product Manager",
            f"Kollect-It Product Manager v{VERSION}\n\n"
            "Desktop application for processing and optimizing "
            "antiques and collectibles listings.\n\n"
            "© 2025 Kollect-It"
        )

    def open_import_wizard(self):
        """Open the import wizard dialog."""
        wizard = ImportWizard(self.config, self)
        wizard.import_complete.connect(self.on_import_complete)
        wizard.exec_()

    def on_import_complete(self, folder_path: str):
        """Handle completed import - load the new product."""
        self.log(f"Product imported to: {folder_path}", "success")

        # Load the imported folder into the editor
        if folder_path:
            # Read the product_info.json to get title and SKU
            info_file = Path(folder_path) / "product_info.json"
            if info_file.exists():
                try:
                    with open(info_file) as f:
                        info = json.load(f)

                    # Set the SKU
                    self.sku_edit.setText(info.get("sku", ""))

                    # Set the title
                    self.title_edit.setText(info.get("title", ""))

                    # Set the category
                    category = info.get("category", "")
                    if category:
                        index = self.category_combo.findData(category)
                        if index >= 0:
                            self.category_combo.setCurrentIndex(index)

                except Exception as e:
                    self.log(f"Error reading product info: {e}", "warning")

            # Load the folder using existing method
            self.on_folder_dropped(folder_path)

            self.log("Product loaded - ready for processing", "info")

    def closeEvent(self, event):
        """Handle application close event - cleanup temporary directories AND threads."""
        import shutil
        
        # FIX: Stop any running processing thread
        if self.processing_thread is not None:
            if self.processing_thread.isRunning():
                self.processing_thread.terminate()
                self.processing_thread.wait(2000)  # Wait up to 2 seconds
            self.processing_thread.deleteLater()
            self.processing_thread = None
        
        # Clean up temporary directories
        for temp_dir in getattr(self, '_temp_dirs', []):
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except Exception:
                pass
        
        super().closeEvent(event)


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Set application info
    app.setApplicationName("Kollect-It Product Manager")
    app.setOrganizationName("Kollect-It")
    app.setOrganizationDomain("kollect-it.com")

    # Create and show main window
    window = KollectItApp()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
