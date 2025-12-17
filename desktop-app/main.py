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
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

VERSION = "1.0.0"
IMAGE_GRID_COLUMNS = 4
THUMBNAIL_SIZE = 150
MAX_IMAGES = 20
MAX_AI_IMAGES_DESCRIPTION = 5
MAX_AI_IMAGES_VALUATION = 3
MAX_AI_IMAGES_ANALYZE = 5

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
    QStatusBar, QMenuBar, QMenu, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QUrl, QMimeData, QSize, QTimer
)
from PyQt5.QtGui import (
    QPixmap, QImage, QIcon, QFont, QPalette, QColor,
    QDragEnterEvent, QDropEvent, QPainter, QPen
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
from modules.output_generator import OutputGenerator  # type: ignore
from modules.config_validator import ConfigValidator  # type: ignore
from modules.theme import DarkPalette  # type: ignore
import logging
from pathlib import Path as _Path

# Ensure logs directory exists and configure logging
_logs_dir = _Path(__file__).parent / "logs"
_logs_dir.mkdir(exist_ok=True)
logging.basicConfig(
    filename=str(_logs_dir / "app.log"),
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger("kollectit")



class DropZone(QFrame):
    """Custom drag-and-drop zone for product folders."""

    folder_dropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.browse_btn = None  # Initialize attribute
        self.browse_files_btn = None  # Initialize attribute for new button
        self.setAcceptDrops(True)
        self.setMinimumHeight(200)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {DarkPalette.SURFACE};
                border: 3px dashed {DarkPalette.BORDER};
                border-radius: 16px;
            }}
            QFrame:hover {{
                border-color: {DarkPalette.PRIMARY};
                background-color: {DarkPalette.SURFACE_LIGHT};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)  # type: ignore

        # Icon placeholder
        icon_label = QLabel("📁")
        icon_label.setStyleSheet("font-size: 48px; border: none;")
        icon_label.setAlignment(Qt.AlignCenter)  # type: ignore
        layout.addWidget(icon_label)

        # Main text
        main_text = QLabel("Drag & Drop Product Folder Here")
        main_text.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        main_text.setAlignment(Qt.AlignCenter)  # type: ignore
        layout.addWidget(main_text)

        # Sub text
        sub_text = QLabel("or click Browse to select folder/files")
        sub_text.setStyleSheet("""
            QLabel {
                color: #b4b4b4;
                font-size: 16px;
            }
        """)
        sub_text.setAlignment(Qt.AlignCenter)  # type: ignore
        layout.addWidget(sub_text)

        # Browse buttons container
        browse_layout = QHBoxLayout()

        # Browse folder button
        self.browse_btn = QPushButton("Browse Folder")
        self.browse_btn.setProperty("variant", "utility")
        self.browse_btn.setMinimumWidth(130)
        self.browse_btn.clicked.connect(self.browse_folder)
        browse_layout.addWidget(self.browse_btn)

        # Browse files button
        self.browse_files_btn = QPushButton("Browse Files")
        self.browse_files_btn.setProperty("variant", "utility")
        self.browse_files_btn.setMinimumWidth(130)
        self.browse_files_btn.clicked.connect(self.browse_files)
        browse_layout.addWidget(self.browse_files_btn)

        # Add browse buttons layout to main layout
        browse_container = QWidget()
        browse_container.setLayout(browse_layout)
        layout.addWidget(browse_container, alignment=Qt.AlignCenter)  # type: ignore

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {DarkPalette.SURFACE_LIGHT};
                    border: 2px dashed {DarkPalette.PRIMARY};
                    border-radius: 12px;
                }}
            """)

    def dragLeaveEvent(self, event):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {DarkPalette.SURFACE};
                border: 2px dashed {DarkPalette.BORDER};
                border-radius: 12px;
            }}
        """)

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {DarkPalette.SURFACE};
                border: 2px dashed {DarkPalette.BORDER};
                border-radius: 12px;
            }}
        """)

        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.isdir(path):
                self.folder_dropped.emit(path)
            else:
                QMessageBox.warning(
                    self, "Invalid Selection",
                    "Please drop a folder containing product images."
                )

    def _get_default_browse_path(self) -> str:
        """Get default browse path from config or fall back to home."""
        if hasattr(self, 'config') and self.config:
            config_path = self.config.get("paths", {}).get("default_browse", "")
            if config_path and Path(config_path).exists():
                return config_path
            camera_path = self.config.get("paths", {}).get("camera_import", "")
            if camera_path and Path(camera_path).exists():
                return camera_path
        return str(Path.home())

    def browse_folder(self):
        # Get default path from config, fallback to user's home directory
        default_path = self._get_default_browse_path()

        # Use a custom file dialog to allow seeing files while selecting a folder
        dialog = QFileDialog(self, "Select Product Folder", default_path)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, False)  # Allow seeing files
        dialog.setViewMode(QFileDialog.Detail)  # Try to show details/icons
        dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.webp *.tiff *.bmp);;All Files (*)")

        if dialog.exec_() == QFileDialog.Accepted:
            folder = dialog.selectedFiles()[0]
            if folder:
                self.folder_dropped.emit(folder)

    def browse_files(self):
        # Get default path from config, fallback to user's home directory
        default_path = ""

        # Get path from config
        if hasattr(self, 'config'):
            default_path = self.config.get("paths", {}).get("camera_import", "")
            if default_path:
                requested_path = Path(default_path)
                if requested_path.exists():
                    default_path = str(requested_path)
                else:
                    default_path = ""

        if not default_path:
            default_path = str(Path.home())

        # Define image file filters
        file_filter = "Image Files (*.png *.jpg *.jpeg *.webp *.tiff *.bmp);;PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;WebP Files (*.webp);;All Files (*.*)"

        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Image Files",
            default_path, file_filter
        )
        if files:
            # Create a temporary folder structure for individual files
            import tempfile
            import shutil

            # Create a temporary directory to hold the selected files
            temp_dir = tempfile.mkdtemp(prefix="kollect_files_")
            # Track temp dir in the main window application
            if hasattr(self.window(), '_temp_dirs'):
                self.window()._temp_dirs.append(temp_dir)

            # Copy selected files to temp directory
            for file_path in files:
                file_name = Path(file_path).name
                temp_file_path = Path(temp_dir) / file_name
                shutil.copy2(file_path, temp_file_path)

            # Emit the temporary folder as if it was dropped/selected
            self.folder_dropped.emit(temp_dir)


class ImageThumbnail(QLabel):
    """Clickable image thumbnail with edit options."""

    clicked = pyqtSignal(str)
    selected = pyqtSignal(str)
    crop_requested = pyqtSignal(str)
    remove_bg_requested = pyqtSignal(str)

    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.is_selected = False  # Track selection state
        # Increased size for "large format" display
        self.setFixedSize(THUMBNAIL_SIZE, THUMBNAIL_SIZE)
        self.setCursor(Qt.PointingHandCursor)  # type: ignore
        self.load_image()

    def set_selected(self, selected: bool):
        """Set the selected state and update style."""
        self.is_selected = selected
        self.update_style()

    def update_style(self):
        """Update the stylesheet based on state."""
        border_color = DarkPalette.PRIMARY if self.is_selected else DarkPalette.BORDER
        border_width = "4px" if self.is_selected else "2px"

        self.setStyleSheet(f"""
            QLabel {{
                background-color: {DarkPalette.SURFACE};
                border: {border_width} solid {border_color};
                border-radius: 8px;
                padding: 4px;
            }}
            QLabel:hover {{
                border-color: {DarkPalette.PRIMARY};
            }}
        """)

    def load_image(self):
        pixmap = QPixmap(self.image_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatio,  # type: ignore
                Qt.SmoothTransformation  # type: ignore
            )
            self.setPixmap(scaled)
        self.update_style()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:  # type: ignore
            # single press: mark as selected (but don't open preview yet)
            self.selected.emit(self.image_path)
        elif event.button() == Qt.RightButton:  # type: ignore
            self.show_context_menu(event.pos())

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            # double-click opens preview / edit
            self.clicked.emit(self.image_path)

    def show_context_menu(self, pos):
        menu = QMenu(self)
        crop_action = menu.addAction("Crop Image")
        bg_action = menu.addAction("Remove Background")
        preview_action = menu.addAction("Preview Full Size")

        action = menu.exec_(self.mapToGlobal(pos))
        if action == crop_action:
            self.crop_requested.emit(self.image_path)
        elif action == bg_action:
            self.remove_bg_requested.emit(self.image_path)
        elif action == preview_action:
            self.clicked.emit(self.image_path)


class ProcessingThread(QThread):
    """Background thread for image processing tasks."""

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, folder_path: str, config: dict, options: dict):
        super().__init__()
        self.folder_path = folder_path
        self.config = config
        self.options = options

    def run(self):
        try:
            processor = ImageProcessor(self.config)
            results = {"images": [], "errors": []}

            # Get all images in folder
            image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.tiff', '.bmp'}
            images = [
                f for f in Path(self.folder_path).iterdir()
                if f.suffix.lower() in image_extensions
            ]

            total = len(images)

            for i, img_path in enumerate(images):
                self.progress.emit(
                    int((i / total) * 100),
                    f"Processing: {img_path.name}"
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

            self.progress.emit(100, "Processing complete!")
            self.finished.emit(results)

        except Exception as e:
            self.error.emit(str(e))


class KollectItApp(QMainWindow):
    """Main application window for Kollect-It Product Manager."""

    def __init__(self):
        super().__init__()
        self.config = self.load_config()

        # Initialize SKU Scanner and Output Generator
        products_root = self.config.get("paths", {}).get("products_root", r"G:\My Drive\Kollect-It\Products")
        self.sku_scanner = SKUScanner(products_root, self.config.get("categories", {}))
        self.output_generator = OutputGenerator(self.config)
        self.last_valuation = None
        self.current_folder = None
        self._temp_dirs = []  # Track temporary directories for cleanup
        self.current_images = []
        self.uploaded_image_urls = []  # Store URLs after ImageKit upload
        self.processing_thread = None

        # Initialize UI component attributes
        self.drop_zone = None
        self.image_grid = None
        self.image_grid_layout = None
        self.crop_all_btn = None
        self.remove_bg_btn = None
        self.optimize_btn = None
        self.upload_btn = None
        self.export_btn = None
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
            self.setStyleSheet(DarkPalette.get_stylesheet())
        except Exception as e:
            import traceback
            print("Failed to apply stylesheet:", e)
            traceback.print_exc()

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # Left panel - Input & Images
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(12)

        # Drop zone
        self.drop_zone = DropZone()
        self.drop_zone.folder_dropped.connect(self.on_folder_dropped)
        left_layout.addWidget(self.drop_zone)

        # New Product button below drop zone
        new_product_btn = QPushButton("+ Add New Product")
        new_product_btn.setObjectName("newProductBtn")
        new_product_btn.setProperty("variant", "secondary")
        new_product_btn.setMinimumHeight(44)
        new_product_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DarkPalette.SUCCESS};
                color: #1a1b26;
                font-size: 15px;
                font-weight: 600;
                border-radius: 10px;
                padding: 12px 24px;
            }}
            QPushButton:hover {{
                background-color: #7dd87d;
            }}
        """)
        new_product_btn.clicked.connect(self.open_import_wizard)
        left_layout.addWidget(new_product_btn)

        # Image preview section
        images_group = QGroupBox("Product Images")
        images_layout = QVBoxLayout(images_group)

        # Image grid scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(200)

        self.image_grid = QWidget()
        self.image_grid_layout = QGridLayout(self.image_grid)
        self.image_grid_layout.setSpacing(8)
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

        images_layout.addLayout(img_actions)
        left_layout.addWidget(images_group)

        main_layout.addWidget(left_panel, stretch=1)

        # Right panel - Product Details & Actions
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(12)

        # Tabs for different sections
        tabs = QTabWidget()

        # Product Details Tab
        details_tab = QWidget()
        details_layout = QVBoxLayout(details_tab)

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form.setRowWrapPolicy(QFormLayout.DontWrapRows)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

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
        self.regenerate_sku_btn = QPushButton("↻")
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
        ai_btn_layout.setSpacing(10)
        desc_layout.addLayout(ai_btn_layout)
        desc_layout.addSpacing(6)

        details_layout.addWidget(desc_group)
        tabs.addTab(details_tab, "Product Details")

        # SEO Tab
        seo_tab = QWidget()
        seo_layout = QFormLayout(seo_tab)
        seo_layout.setSpacing(14)
        seo_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        seo_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        seo_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        seo_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        seo_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

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
        settings_layout.setSpacing(14)
        settings_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        settings_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        settings_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        settings_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        settings_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

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
        self.status_label.setStyleSheet(f"color: {DarkPalette.TEXT_SECONDARY};")
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
        # Inline export_btn stylesheet removed; handled by theme via object name
        actions_layout.addWidget(self.export_btn)

        right_layout.addLayout(actions_layout)

        # Log output
        log_group = QGroupBox("Activity Log")
        log_layout = QVBoxLayout(log_group)

        self.log_output = QTextEdit()
        self.log_output.setObjectName("activityLog")
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(150)
        # Inline log_output stylesheet removed; handled by theme via object name
        log_layout.addWidget(self.log_output)

        right_layout.addWidget(log_group)

        main_layout.addWidget(right_panel, stretch=1)

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
            "info": "#60a5fa",      # Blue
            "success": "#4ade80",   # Green
            "warning": "#fbbf24",   # Yellow
            "error": "#f87171",     # Red
        }
        color = colors.get(level, "#ffffff")

        # Format with HTML for colored output
        formatted = f'<span style="color: #6b7280;">[{timestamp}]</span> <span style="color: {color};">{message}</span>'

        self.log_output.append(formatted)

        # Auto-scroll to bottom
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_folder_dropped(self, folder_path: str):
        """Handle when a folder is dropped or selected."""
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

        row, col = 0, 0
        max_cols = IMAGE_GRID_COLUMNS

        for img_path in images:
            self.current_images.append(str(img_path))

            thumb = ImageThumbnail(str(img_path))
            thumb.clicked.connect(self.preview_image)
            thumb.selected.connect(self.on_thumbnail_selected)
            thumb.crop_requested.connect(self.crop_image)
            thumb.remove_bg_requested.connect(self.remove_image_background)

            self.image_grid_layout.addWidget(thumb, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        self.log(f"Found {len(images)} images", "info")

    def on_thumbnail_clicked(self, image_path: str):
        """Handle thumbnail click to update selection state."""
        # kept for backwards compatibility; not used when double-click flow is active
        self.on_thumbnail_selected(image_path)

    def on_thumbnail_selected(self, image_path: str):
        """Handle single-click selection without opening preview."""
        # Update selection state for all thumbnails
        for i in range(self.image_grid_layout.count()):
            item = self.image_grid_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, ImageThumbnail):
                    is_selected = (widget.image_path == image_path)
                    widget.set_selected(is_selected)

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

    def on_category_changed(self, _index: int):
        """Handle category selection change."""
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
        cat_id = self.category_combo.currentData()
        if not cat_id:
            self.log("No category selected - cannot generate SKU", "warning")
            return

        try:
            prefix = self.config["categories"][cat_id]["prefix"]
            sku = self.sku_scanner.get_next_sku(prefix)
            self.sku_edit.setText(sku)
            self.update_export_button_state()
            self.log(f"Generated SKU: {sku}", "info")
        except KeyError as e:
            self.log(f"Category '{cat_id}' not found in config: {e}", "error")
        except Exception as e:
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
        """Open crop dialog for an image."""
        dialog = CropDialog(image_path, self, config=self.config)
        if dialog.exec_() == QDialog.Accepted:
            _cropped_path = dialog.get_cropped_path()
            self.log(f"Cropped: {os.path.basename(image_path)}", "success")

            # If the crop produced a file in a 'processed' subfolder,
            # switch the view there so the user immediately sees results.
            try:
                if _cropped_path:
                    from pathlib import Path as _P
                    _out = _P(_cropped_path)
                    if _out.exists() and _out.parent.name.lower() == "processed":
                        self.load_images_from_folder(str(_out.parent))
                        return
            except Exception:
                # Fall back to reloading current folder
                pass

            self.load_images_from_folder(self.current_folder)

    def crop_selected_image(self):
        """Crop the first selected image."""
        if self.current_images:
            self.crop_image(self.current_images[0])

    def remove_image_background(self, image_path: str):
        """Remove background from a single image."""
        try:
            self.log(f"Removing background: {os.path.basename(image_path)}", "info")
            self.progress_bar.setValue(0)
            self.status_label.setText("Removing background...")

            remover = BackgroundRemover()
            strength = self.bg_strength_slider.value() / 100
            bg_color = self.config.get("image_processing", {}).get(
                "background_removal", {}
            ).get("background_color", "#FFFFFF")

            output_path = remover.remove_background(
                image_path,
                strength=strength,
                bg_color=bg_color
            )

            self.progress_bar.setValue(100)
            self.status_label.setText("Background removed!")
            self.log(f"Background removed: {os.path.basename(output_path)}", "success")

            # Reload images
            self.load_images_from_folder(self.current_folder)

        except Exception as e:
            self.log(f"Background removal error: {e}", "error")
            self.status_label.setText("Error removing background")

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
            return

        self.log("Starting image optimization...", "info")
        self.status_label.setText("Optimizing images...")
        self.progress_bar.setValue(0)

        options = {
            "max_dimension": self.config.get("image_processing", {}).get("max_dimension", 2400),
            "quality": self.config.get("image_processing", {}).get("webp_quality", 88),
            "strip_exif": self.config.get("image_processing", {}).get("strip_exif", True),
            "output_format": "webp"
        }

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

    def on_processing_finished(self, results: dict):
        """Handle processing completion."""
        self.optimize_btn.setEnabled(True)
        self.upload_btn.setEnabled(True)

        success_count = len(results.get("images", []))
        error_count = len(results.get("errors", []))

        self.log(f"Optimization complete: {success_count} images processed", "success")

        if error_count > 0:
            self.log(f"Errors: {error_count} images failed", "warning")

        # Reload to show processed images
        processed_folder = Path(self.current_folder) / "processed"
        if processed_folder.exists():
            self.load_images_from_folder(str(processed_folder))

    def on_processing_error(self, error: str):
        """Handle processing errors."""
        self.optimize_btn.setEnabled(True)
        self.log(f"Processing error: {error}", "error")
        self.status_label.setText("Error during processing")

    def analyze_and_autofill(self):
        """Use AI to analyze images and autofill product fields."""
        if not self.current_images:
            QMessageBox.warning(self, "No Images", "Load a product folder first.")
            return

        try:
            self.log("Analyzing images to suggest fields...", "info")
            self.status_label.setText("AI analyzing images...")

            engine = AIEngine(self.config)
            images = self.current_images[:MAX_AI_IMAGES_ANALYZE]

            product_data = {
                "title": self.title_edit.text(),
                "condition": self.condition_combo.currentText(),
                "era": self.era_edit.text(),
                "origin": self.origin_edit.text(),
                "images": images,
            }

            categories = self.config.get("categories", {})
            result = engine.suggest_fields(product_data, categories)

            if not result:
                self.log("AI analysis returned no data", "warning")
                self.status_label.setText("Ready")
                return

            # Title
            if result.get("title"):
                self.title_edit.setText(result["title"])

            # Category mapping
            cat_id = result.get("category_id")
            if cat_id:
                idx = self.category_combo.findData(cat_id)
                if idx >= 0:
                    self.category_combo.setCurrentIndex(idx)
                    # ensure subcategories are refreshed
                    self.on_category_changed()
                else:
                    self.log(f"AI suggested category '{cat_id}' not found in config; keeping current.", "warning")

            # Subcategory
            subc = result.get("subcategory")
            if subc:
                idx = self.subcategory_combo.findText(subc)
                if idx >= 0:
                    self.subcategory_combo.setCurrentIndex(idx)
                else:
                    # If not present, add it temporarily for convenience
                    self.subcategory_combo.insertItem(0, subc)
                    self.subcategory_combo.setCurrentIndex(0)

            # Condition
            cond = result.get("condition")
            if cond:
                idx = self.condition_combo.findText(cond)
                if idx >= 0:
                    self.condition_combo.setCurrentIndex(idx)
                else:
                    self.condition_combo.insertItem(0, cond)
                    self.condition_combo.setCurrentIndex(0)

            # Era & Origin
            if result.get("era"):
                self.era_edit.setText(result["era"])
            if result.get("origin"):
                self.origin_edit.setText(result["origin"])

            # Description & SEO
            if result.get("description"):
                self.description_edit.setPlainText(result["description"])
            if result.get("seo_title"):
                self.seo_title_edit.setText(result["seo_title"])
            if result.get("seo_description"):
                self.seo_desc_edit.setPlainText(result["seo_description"])
            if result.get("keywords") and isinstance(result["keywords"], list):
                self.seo_keywords_edit.setText(", ".join(result["keywords"]))

            # Valuation -> suggest price (user can adjust)
            val = result.get("valuation") or {}
            rec_price = val.get("recommended")
            if isinstance(rec_price, (int, float)) and rec_price > 0:
                try:
                    self.price_spin.setValue(float(rec_price))
                except Exception:
                    pass
                self.last_valuation = {
                    "low": val.get("low"),
                    "high": val.get("high"),
                    "recommended": rec_price,
                    "confidence": val.get("confidence", ""),
                    "notes": val.get("notes", "")
                }
                self.log(
                    f"AI suggested price range: ${val.get('low', 0):,.2f} - ${val.get('high', 0):,.2f} (Rec: ${rec_price:,.2f})",
                    "info"
                )

            self.update_export_button_state()
            self.status_label.setText("Ready")
            self.log("Fields autofilled from images", "success")

        except ValueError as ve:
            # Likely missing API key
            QMessageBox.critical(
                self,
                "AI Configuration",
                f"{ve}\n\nSet ANTHROPIC_API_KEY in desktop-app/.env and restart."
            )
            self.status_label.setText("Ready")
        except Exception as e:
            self.log(f"AI analyze error: {e}", "error")
            self.status_label.setText("Ready")

    def generate_description(self):
        """Generate product description using AI."""
        if not self.current_images:
            QMessageBox.warning(self, "No Images", "Load a product folder first.")
            return

        self.log("Generating AI description...", "info")
        self.status_label.setText("AI generating description...")

        try:
            engine = AIEngine(self.config)

            category = self.category_combo.currentData()
            if not category:
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

            result = engine.generate_description(product_data)

            if result:
                self.description_edit.setPlainText(result.get("description", ""))
                self.seo_title_edit.setText(result.get("seo_title", ""))
                self.seo_desc_edit.setPlainText(result.get("seo_description", ""))
                self.seo_keywords_edit.setText(", ".join(result.get("keywords", [])))

                if result.get("suggested_title"):
                    self.title_edit.setText(result["suggested_title"])

                # Handle valuation if present (from description generation)
                valuation = result.get("valuation")
                if valuation and isinstance(valuation, dict):
                    recommended = valuation.get("recommended") or 0
                    low = valuation.get("low") or 0
                    high = valuation.get("high") or 0
                    if recommended:
                        # Display pricing research (don't auto-set price)
                        self.log(
                            f"Price Research (from description): ${low:,.2f} - ${high:,.2f} (Rec: ${recommended:,.2f})",
                            "info"
                        )
                        # Store for later use
                        self.last_valuation = {
                            "low": low,
                            "high": high,
                            "recommended": recommended,
                            "confidence": valuation.get("confidence", "Medium"),
                            "notes": valuation.get("notes", "")
                        }

                self.log("AI description generated", "success")

                # Update export button state
                self.update_export_button_state()
            else:
                self.log("AI generation returned no results", "warning")

        except Exception as e:
            self.log(f"AI error: {e}", "error")

        self.status_label.setText("Ready")

    def generate_valuation(self):
        """Generate AI-powered price research and display guidance."""
        self.log("Generating price research...", "info")

        try:
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

            valuation = engine.generate_valuation(product_data)

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

        except Exception as e:
            self.log(f"Price research error: {e}", "error")

    def upload_to_imagekit(self):
        """Upload processed images to ImageKit."""
        if not self.current_images:
            return

        self.log("Uploading to ImageKit...", "info")
        self.status_label.setText("Uploading to ImageKit...")
        self.progress_bar.setValue(0)

        try:
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
            total = len(self.current_images)

            for i, img_path in enumerate(self.current_images):
                result = uploader.upload(img_path, folder)
                if result and result.get("success"):
                    url = result.get("url")
                    if url:
                        uploaded_urls.append(url)
                        self.log(f"Uploaded: {Path(img_path).name} -> {url}", "info")
                    else:
                        self.log(f"Upload returned no URL for {Path(img_path).name}", "warning")
                else:
                    error_msg = result.get("error", "Unknown error") if result else "No response"
                    self.log(f"Failed to upload {Path(img_path).name}: {error_msg}", "error")

                progress = int(((i + 1) / total) * 100)
                self.progress_bar.setValue(progress)
                self.status_label.setText(f"Uploading {i + 1}/{total}...")
                QApplication.processEvents()  # Keep UI responsive

            self.log(f"Uploaded {len(uploaded_urls)} images to ImageKit", "success")

            # Store URLs
            self.uploaded_image_urls = uploaded_urls

            # Enable export button if we have required data
            if uploaded_urls and self.title_edit.text() and self.description_edit.toPlainText():
                self.export_btn.setEnabled(True)

        except Exception as e:
            self.log(f"Upload error: {e}", "error")

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

    def export_package(self):
        """Export product package to files."""
        # Validate required fields
        if not self.title_edit.text():
            QMessageBox.warning(self, "Missing Title", "Please enter a product title.")
            return

        if not self.description_edit.toPlainText():
            QMessageBox.warning(self, "Missing Description", "Please generate or enter a description.")
            return

        if not self.uploaded_image_urls:
            QMessageBox.warning(self, "No Images", "Please upload images to ImageKit first.")
            return

        category = self.category_combo.currentData()
        if not category:
            QMessageBox.warning(self, "No Category", "Please select a category first.")
            return

        sku = self.sku_edit.text()
        if not sku:
            QMessageBox.warning(self, "No SKU", "Please generate a SKU first.")
            return

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
            result = self.output_generator.export_package(product_data)

            if result.get("success"):
                output_path = result.get("output_path")
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
                self.log(f"Export failed: {error}", "error")
                QMessageBox.warning(self, "Export Failed", f"Error: {error}")

        except Exception as e:
            self.log(f"Export error: {e}", "error")
            QMessageBox.critical(self, "Error", f"Failed to export: {e}")

        self.status_label.setText("Ready")

    def reset_form(self):
        """Reset the form for a new product."""
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
        dialog.setStyleSheet(DarkPalette.get_stylesheet())

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
        # Display status instead of editable field
        api_key_status = "Configured" if os.getenv("ANTHROPIC_API_KEY") else "Not set (set ANTHROPIC_API_KEY in .env)"
        api_key_label = QLabel(api_key_status)
        api_key_label.setStyleSheet("color: #48bb78;" if os.getenv("ANTHROPIC_API_KEY") else "color: #f56565;")
        ai_layout.addRow("Anthropic API Key:", api_key_label)

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
        """Save settings from the settings dialog."""
        # Update config
        if "api" not in self.config:
            self.config["api"] = {}
        if "imagekit" not in self.config:
            self.config["imagekit"] = {}
        if "ai" not in self.config:
            self.config["ai"] = {}
        if "image_processing" not in self.config:
            self.config["image_processing"] = {}

        self.config["api"]["SERVICE_API_KEY"] = self.api_key_edit.text()
        self.config["api"]["production_url"] = self.prod_url_edit.text()
        self.config["api"]["use_production"] = self.use_prod_check.isChecked()

        self.config["imagekit"]["public_key"] = self.ik_public_edit.text()
        self.config["imagekit"]["private_key"] = self.ik_private_edit.text()
        self.config["imagekit"]["url_endpoint"] = self.ik_url_edit.text()

        # API key is read from ANTHROPIC_API_KEY environment variable only, not saved to config
        self.config["ai"]["model"] = self.ai_model_edit.text()

        self.config["image_processing"]["max_dimension"] = self.max_dim_spin.value()
        self.config["image_processing"]["webp_quality"] = self.quality_spin.value()
        self.config["image_processing"]["strip_exif"] = self.strip_exif_check.isChecked()

        # Save to file
        self.save_config()

        QMessageBox.information(dialog, "Settings Saved", "Settings have been saved successfully.")
        dialog.accept()

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
        """Handle application close event - cleanup temporary directories."""
        # Clean up temporary directories
        import shutil
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
