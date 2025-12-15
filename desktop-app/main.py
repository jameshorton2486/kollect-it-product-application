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

# Application constants
VERSION = "1.0.0"
IMAGE_GRID_COLUMNS = 4
THUMBNAIL_SIZE = 150
MAX_IMAGES = 20
MAX_AI_IMAGES_DESCRIPTION = 5
MAX_AI_IMAGES_VALUATION = 3

# Load environment variables from .env file (if available)
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)
except ImportError:
    pass

# PyQt5 imports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QTextEdit, QComboBox,
    QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QTabWidget,
    QFileDialog, QMessageBox, QGroupBox, QFormLayout, QScrollArea,
    QSlider, QDialog, QToolBar, QAction, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

# Import custom modules
from modules.theme import DarkPalette
from modules.widgets import DropZone, ImageThumbnail
from modules.workers import ProcessingThread
from modules.image_processor import ImageProcessor  # type: ignore
from modules.imagekit_uploader import ImageKitUploader  # type: ignore
from modules.sku_scanner import SKUScanner  # type: ignore
from modules.ai_engine import AIEngine  # type: ignore
from modules.background_remover import BackgroundRemover, check_rembg_installation, REMBG_AVAILABLE  # type: ignore
from modules.crop_tool import CropDialog  # type: ignore
from modules.import_wizard import ImportWizard  # type: ignore
from modules.output_generator import OutputGenerator  # type: ignore
from modules.config_validator import ConfigValidator  # type: ignore


class KollectItApp(QMainWindow):
    """Main application window for Kollect-It Product Manager."""

    def __init__(self):
        super().__init__()
        self.config = self._load_config()

        # Initialize core services
        products_root = self.config.get("paths", {}).get("products_root", r"G:\My Drive\Kollect-It\Products")
        self.sku_scanner = SKUScanner(products_root, self.config.get("categories", {}))
        self.output_generator = OutputGenerator(self.config)

        # State management
        self.last_valuation: Optional[Dict[str, Any]] = None
        self.current_folder: Optional[str] = None
        self._temp_dirs: List[str] = []
        self.current_images: List[str] = []
        self.uploaded_image_urls: List[str] = []
        self.processing_thread: Optional[ProcessingThread] = None

        # UI component references (initialized in setup_ui)
        self._init_ui_attributes()

        # Build the UI
        self._setup_ui()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_statusbar()

    def _init_ui_attributes(self) -> None:
        """Initialize UI component attribute placeholders."""
        # Main components
        self.drop_zone: Optional[DropZone] = None
        self.image_grid: Optional[QWidget] = None
        self.image_grid_layout: Optional[QGridLayout] = None

        # Action buttons
        self.crop_all_btn: Optional[QPushButton] = None
        self.remove_bg_btn: Optional[QPushButton] = None
        self.optimize_btn: Optional[QPushButton] = None
        self.upload_btn: Optional[QPushButton] = None
        self.export_btn: Optional[QPushButton] = None
        self.regenerate_sku_btn: Optional[QPushButton] = None

        # Form fields
        self.title_edit: Optional[QLineEdit] = None
        self.sku_edit: Optional[QLineEdit] = None
        self.category_combo: Optional[QComboBox] = None
        self.subcategory_combo: Optional[QComboBox] = None
        self.price_spin: Optional[QDoubleSpinBox] = None
        self.condition_combo: Optional[QComboBox] = None
        self.era_edit: Optional[QLineEdit] = None
        self.origin_edit: Optional[QLineEdit] = None
        self.description_edit: Optional[QTextEdit] = None

        # AI buttons
        self.generate_desc_btn: Optional[QPushButton] = None
        self.generate_valuation_btn: Optional[QPushButton] = None

        # SEO fields
        self.seo_title_edit: Optional[QLineEdit] = None
        self.seo_desc_edit: Optional[QTextEdit] = None
        self.seo_keywords_edit: Optional[QLineEdit] = None

        # Settings
        self.bg_removal_check: Optional[QCheckBox] = None
        self.bg_strength_slider: Optional[QSlider] = None

        # Progress & logging
        self.progress_bar: Optional[QProgressBar] = None
        self.status_label: Optional[QLabel] = None
        self.log_output: Optional[QTextEdit] = None

        # Settings dialog fields
        self.api_key_edit: Optional[QLineEdit] = None
        self.prod_url_edit: Optional[QLineEdit] = None
        self.use_prod_check: Optional[QCheckBox] = None
        self.ik_public_edit: Optional[QLineEdit] = None
        self.ik_private_edit: Optional[QLineEdit] = None
        self.ik_url_edit: Optional[QLineEdit] = None
        self.anthropic_key_edit: Optional[QLineEdit] = None
        self.ai_model_edit: Optional[QLineEdit] = None
        self.max_dim_spin: Optional[QSpinBox] = None
        self.quality_spin: Optional[QSpinBox] = None
        self.strip_exif_check: Optional[QCheckBox] = None

    # -------------------------------------------------------------------------
    # Configuration Management
    # -------------------------------------------------------------------------

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from config.json with validation and .env override."""
        config_path = Path(__file__).parent / "config" / "config.json"

        if not config_path.exists():
            self._show_config_error(
                "Configuration file not found!\n\n"
                f"Expected: {config_path}\n\n"
                "Please copy config.example.json to config.json and configure your API keys."
            )
            sys.exit(1)

        try:
            config = self._load_config_file(config_path)
            self._validate_config(config)
            return config
        except json.JSONDecodeError as e:
            self._show_config_error(f"Invalid JSON in config.json:\n\n{e}")
            sys.exit(1)
        except Exception as e:
            self._show_config_error(f"Error reading config.json:\n\n{e}")
            sys.exit(1)

    def _load_config_file(self, config_path: Path) -> Dict[str, Any]:
        """Load config file with optional .env support."""
        try:
            from modules.env_loader import load_config_with_env
            return load_config_with_env(config_path)
        except ImportError:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration and show warnings."""
        validator = ConfigValidator(config)
        is_valid, errors, warnings = validator.validate()

        if not is_valid:
            QMessageBox.warning(
                None, "Configuration Warning",
                f"Configuration issues found:\n\n" + "\n".join(errors)
            )

        if warnings:
            for warning in warnings:
                print(f"Config warning: {warning}")

        # Check required sections
        required_sections = ["api", "imagekit", "categories", "image_processing"]
        missing = [s for s in required_sections if s not in config]
        if missing:
            QMessageBox.warning(
                None, "Configuration Warning",
                f"Missing configuration sections: {', '.join(missing)}\n\n"
                "Some features may not work correctly."
            )

    def _show_config_error(self, message: str) -> None:
        """Show a configuration error dialog."""
        QMessageBox.critical(None, "Configuration Error", message)

    def _save_config(self) -> None:
        """Save configuration to config.json."""
        config_path = Path(__file__).parent / "config" / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)

    # -------------------------------------------------------------------------
    # UI Setup
    # -------------------------------------------------------------------------

    def _setup_ui(self) -> None:
        """Initialize the main user interface."""
        self.setWindowTitle(f"Kollect-It Product Manager v{VERSION}")
        self.setMinimumSize(1600, 1000)
        self.setStyleSheet(DarkPalette.get_stylesheet())

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # Build panels
        left_panel = self._build_left_panel()
        right_panel = self._build_right_panel()

        main_layout.addWidget(left_panel, stretch=1)
        main_layout.addWidget(right_panel, stretch=1)

    def _build_left_panel(self) -> QWidget:
        """Build the left panel with drop zone and image grid."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)

        # Drop zone
        self.drop_zone = DropZone(config=self.config)
        self.drop_zone.folder_dropped.connect(self._on_folder_dropped)
        layout.addWidget(self.drop_zone)

        # New Product button
        new_product_btn = QPushButton("📦 Add New Product")
        new_product_btn.setMinimumHeight(40)
        new_product_btn.setStyleSheet("""
            QPushButton {
                background-color: #48bb78;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #38a169;
            }
        """)
        new_product_btn.clicked.connect(self._open_import_wizard)
        layout.addWidget(new_product_btn)

        # Image preview section
        images_group = QGroupBox("Product Images")
        images_layout = QVBoxLayout(images_group)

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

        self.crop_all_btn = QPushButton("✂️ Crop Selected")
        self.crop_all_btn.setEnabled(False)
        self.crop_all_btn.clicked.connect(self._crop_selected_image)
        img_actions.addWidget(self.crop_all_btn)

        self.remove_bg_btn = QPushButton("🎨 Remove Background")
        self.remove_bg_btn.setEnabled(False)
        self.remove_bg_btn.clicked.connect(self._remove_background)
        img_actions.addWidget(self.remove_bg_btn)

        self.optimize_btn = QPushButton("⚡ Optimize All")
        self.optimize_btn.setEnabled(False)
        self.optimize_btn.clicked.connect(self._optimize_images)
        img_actions.addWidget(self.optimize_btn)

        images_layout.addLayout(img_actions)
        layout.addWidget(images_group)

        return panel

    def _build_right_panel(self) -> QWidget:
        """Build the right panel with product details and actions."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)

        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self._build_details_tab(), "📦 Product Details")
        tabs.addTab(self._build_seo_tab(), "🔍 SEO")
        tabs.addTab(self._build_settings_tab(), "⚙️ Settings")
        layout.addWidget(tabs)

        # Progress section
        layout.addWidget(self._build_progress_section())

        # Action buttons
        layout.addLayout(self._build_action_buttons())

        # Log output
        layout.addWidget(self._build_log_section())

        return panel

    def _build_details_tab(self) -> QWidget:
        """Build the Product Details tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        form = QFormLayout()
        form.setSpacing(12)

        # Title
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter product title...")
        self.title_edit.textChanged.connect(self._update_export_button_state)
        form.addRow("Title:", self.title_edit)

        # SKU
        sku_layout = QHBoxLayout()
        self.sku_edit = QLineEdit()
        self.sku_edit.setReadOnly(True)
        self.sku_edit.setPlaceholderText("Auto-generated")
        sku_layout.addWidget(self.sku_edit)
        self.regenerate_sku_btn = QPushButton("🔄")
        self.regenerate_sku_btn.setMaximumWidth(40)
        self.regenerate_sku_btn.clicked.connect(self._generate_sku)
        sku_layout.addWidget(self.regenerate_sku_btn)
        form.addRow("SKU:", sku_layout)

        # Category
        self.category_combo = QComboBox()
        self._populate_categories()
        self.category_combo.currentIndexChanged.connect(self._on_category_changed)
        form.addRow("Category:", self.category_combo)

        # Subcategory
        self.subcategory_combo = QComboBox()
        self._update_subcategories()
        form.addRow("Subcategory:", self.subcategory_combo)

        # Price
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 999999.99)
        self.price_spin.setPrefix("$ ")
        self.price_spin.setDecimals(2)
        form.addRow("Suggested Price:", self.price_spin)

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

        layout.addLayout(form)

        # Description section
        desc_group = QGroupBox("Description")
        desc_layout = QVBoxLayout(desc_group)

        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Product description will be generated by AI...")
        self.description_edit.setMinimumHeight(150)
        desc_layout.addWidget(self.description_edit)

        ai_btn_layout = QHBoxLayout()
        self.generate_desc_btn = QPushButton("✨ Generate with AI")
        self.generate_desc_btn.clicked.connect(self._generate_description)
        ai_btn_layout.addWidget(self.generate_desc_btn)

        self.generate_valuation_btn = QPushButton("💰 Price Research")
        self.generate_valuation_btn.clicked.connect(self._generate_valuation)
        ai_btn_layout.addWidget(self.generate_valuation_btn)
        desc_layout.addLayout(ai_btn_layout)

        layout.addWidget(desc_group)
        return tab

    def _build_seo_tab(self) -> QWidget:
        """Build the SEO tab."""
        tab = QWidget()
        layout = QFormLayout(tab)
        layout.setSpacing(12)

        self.seo_title_edit = QLineEdit()
        self.seo_title_edit.setPlaceholderText("SEO-optimized title")
        layout.addRow("SEO Title:", self.seo_title_edit)

        self.seo_desc_edit = QTextEdit()
        self.seo_desc_edit.setMaximumHeight(100)
        self.seo_desc_edit.setPlaceholderText("Meta description (160 chars)")
        layout.addRow("Meta Description:", self.seo_desc_edit)

        self.seo_keywords_edit = QLineEdit()
        self.seo_keywords_edit.setPlaceholderText("keyword1, keyword2, keyword3")
        layout.addRow("Keywords:", self.seo_keywords_edit)

        return tab

    def _build_settings_tab(self) -> QWidget:
        """Build the Settings tab."""
        tab = QWidget()
        layout = QFormLayout(tab)
        layout.setSpacing(12)

        self.bg_removal_check = QCheckBox("Enable AI Background Removal")
        self.bg_removal_check.setChecked(
            self.config.get("image_processing", {})
            .get("background_removal", {})
            .get("enabled", True)
        )
        layout.addRow(self.bg_removal_check)

        self.bg_strength_slider = QSlider(Qt.Horizontal)
        self.bg_strength_slider.setRange(1, 100)
        self.bg_strength_slider.setValue(80)
        layout.addRow("BG Removal Strength:", self.bg_strength_slider)

        return tab

    def _build_progress_section(self) -> QGroupBox:
        """Build the progress section."""
        group = QGroupBox("Progress")
        layout = QVBoxLayout(group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"color: {DarkPalette.TEXT_SECONDARY};")
        layout.addWidget(self.status_label)

        return group

    def _build_action_buttons(self) -> QHBoxLayout:
        """Build the main action buttons."""
        layout = QHBoxLayout()

        self.upload_btn = QPushButton("☁️ Upload to ImageKit")
        self.upload_btn.setEnabled(False)
        self.upload_btn.clicked.connect(self._upload_to_imagekit)
        layout.addWidget(self.upload_btn)

        self.export_btn = QPushButton("📦 Export Package")
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self._export_package)
        self.export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DarkPalette.PRIMARY};
                font-size: 15px;
                padding: 14px 28px;
            }}
            QPushButton:hover {{
                background-color: {DarkPalette.PRIMARY_DARK};
            }}
        """)
        layout.addWidget(self.export_btn)

        return layout

    def _build_log_section(self) -> QGroupBox:
        """Build the activity log section."""
        group = QGroupBox("Activity Log")
        layout = QVBoxLayout(group)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(150)
        self.log_output.setStyleSheet(f"""
            QTextEdit {{
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                background-color: {DarkPalette.BACKGROUND};
            }}
        """)
        layout.addWidget(self.log_output)

        return group

    def _setup_menu(self) -> None:
        """Set up the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_product_action = QAction("📦 &New Product...", self)
        new_product_action.setShortcut("Ctrl+N")
        new_product_action.setStatusTip("Import photos and create a new product")
        new_product_action.triggered.connect(self._open_import_wizard)
        file_menu.addAction(new_product_action)

        file_menu.addSeparator()

        open_action = QAction("Open Folder...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_folder)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        export_menu = file_menu.addMenu("Export")
        export_json = QAction("Export as JSON", self)
        export_json.triggered.connect(lambda: self._export_product("json"))
        export_menu.addAction(export_json)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")

        batch_action = QAction("Batch Process Folder...", self)
        batch_action.triggered.connect(self._batch_process)
        tools_menu.addAction(batch_action)

        tools_menu.addSeparator()

        settings_action = QAction("Settings...", self)
        settings_action.triggered.connect(self._show_settings)
        tools_menu.addAction(settings_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_toolbar(self) -> None:
        """Set up the main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        new_product_action = QAction("📦 New Product", self)
        new_product_action.setStatusTip("Import photos and create a new product")
        new_product_action.triggered.connect(self._open_import_wizard)
        toolbar.addAction(new_product_action)

        toolbar.addSeparator()

        toolbar.addAction("📂 Open", self._open_folder)
        toolbar.addAction("⚡ Process", self._optimize_images)
        toolbar.addAction("☁️ Upload", self._upload_to_imagekit)

    def _setup_statusbar(self) -> None:
        """Set up the status bar."""
        self.statusBar().showMessage("Ready - Drop a product folder to begin")

    # -------------------------------------------------------------------------
    # Category Management
    # -------------------------------------------------------------------------

    def _populate_categories(self) -> None:
        """Populate the category dropdown from config."""
        self.category_combo.clear()
        for cat_id, cat_info in self.config.get("categories", {}).items():
            display_name = cat_info.get("display_name", cat_info.get("name", cat_id.title()))
            self.category_combo.addItem(display_name, cat_id)

        default_cat = self.config.get("defaults", {}).get("default_category", "collectibles")
        index = self.category_combo.findData(default_cat)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)

    def _on_category_changed(self, _index: int) -> None:
        """Handle category selection change."""
        self._update_subcategories()
        if self.current_folder:
            self._generate_sku()

    def _update_subcategories(self) -> None:
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

    # -------------------------------------------------------------------------
    # Logging
    # -------------------------------------------------------------------------

    def _log(self, message: str, level: str = "info") -> None:
        """Add a message to the activity log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "info": "#60a5fa",
            "success": "#4ade80",
            "warning": "#fbbf24",
            "error": "#f87171",
        }
        color = colors.get(level, "#ffffff")
        formatted = f'<span style="color: #6b7280;">[{timestamp}]</span> <span style="color: {color};">{message}</span>'
        self.log_output.append(formatted)
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    # -------------------------------------------------------------------------
    # Folder & Image Handling
    # -------------------------------------------------------------------------

    def _on_folder_dropped(self, folder_path: str) -> None:
        """Handle when a folder is dropped or selected."""
        self.current_folder = folder_path
        self._log(f"Loaded folder: {os.path.basename(folder_path)}", "success")
        self.statusBar().showMessage(f"Folder: {folder_path}")

        self._load_images_from_folder(folder_path)
        self._detect_category(folder_path)
        self._generate_sku()

        self.optimize_btn.setEnabled(True)
        self.crop_all_btn.setEnabled(True)
        self.remove_bg_btn.setEnabled(True)

    def _load_images_from_folder(self, folder_path: str) -> None:
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
            thumb.clicked.connect(self._on_thumbnail_clicked)
            thumb.crop_requested.connect(self._crop_image)
            thumb.remove_bg_requested.connect(self._remove_image_background)

            self.image_grid_layout.addWidget(thumb, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        self._log(f"Found {len(images)} images", "info")

    def _on_thumbnail_clicked(self, image_path: str) -> None:
        """Handle thumbnail click."""
        for i in range(self.image_grid_layout.count()):
            item = self.image_grid_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, ImageThumbnail):
                    widget.set_selected(widget.image_path == image_path)
        self._preview_image(image_path)

    def _preview_image(self, image_path: str) -> None:
        """Show full-size image preview."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Image Preview")
        dialog.setMinimumSize(800, 600)

        layout = QVBoxLayout(dialog)
        label = QLabel()
        pixmap = QPixmap(image_path)
        scaled = pixmap.scaled(780, 560, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(scaled)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        dialog.exec_()

    def _detect_category(self, folder_path: str) -> None:
        """Auto-detect category from folder name."""
        folder_name = os.path.basename(folder_path).lower()
        category_keywords = {
            "militaria": ["military", "wwii", "ww2", "uniform", "medal", "weapon", "army", "navy", "usaf", "luftwaffe"],
            "books": ["book", "manuscript", "document", "map", "atlas", "signed", "first edition"],
            "fineart": ["art", "painting", "sculpture", "print", "drawing", "lithograph"],
            "collectibles": ["antique", "vintage", "coin", "pottery", "ceramic", "glass", "jewelry"]
        }

        for cat_id, keywords in category_keywords.items():
            if any(kw in folder_name for kw in keywords):
                for i in range(self.category_combo.count()):
                    if self.category_combo.itemData(i) == cat_id:
                        self.category_combo.setCurrentIndex(i)
                        self._log(f"Auto-detected category: {cat_id}", "info")
                        return

    # -------------------------------------------------------------------------
    # SKU Generation
    # -------------------------------------------------------------------------

    def _generate_sku(self) -> None:
        """Generate a new SKU for the current category."""
        cat_id = self.category_combo.currentData()
        if not cat_id:
            self._log("No category selected - cannot generate SKU", "warning")
            return

        try:
            prefix = self.config["categories"][cat_id]["prefix"]
            sku = self.sku_scanner.get_next_sku(prefix)
            self.sku_edit.setText(sku)
            self._update_export_button_state()
            self._log(f"Generated SKU: {sku}", "info")
        except KeyError as e:
            self._log(f"Category '{cat_id}' not found in config: {e}", "error")
        except Exception as e:
            self._log(f"SKU generation error: {e}", "error")

    # -------------------------------------------------------------------------
    # Image Operations
    # -------------------------------------------------------------------------

    def _crop_image(self, image_path: str) -> None:
        """Open crop dialog for an image."""
        dialog = CropDialog(image_path, self)
        if dialog.exec_() == QDialog.Accepted:
            self._log(f"Cropped: {os.path.basename(image_path)}", "success")
            self._load_images_from_folder(self.current_folder)

    def _crop_selected_image(self) -> None:
        """Crop the first selected image."""
        if self.current_images:
            self._crop_image(self.current_images[0])

    def _remove_image_background(self, image_path: str) -> None:
        """Remove background from a single image."""
        try:
            self._log(f"Removing background: {os.path.basename(image_path)}", "info")
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
            self._log(f"Background removed: {os.path.basename(output_path)}", "success")
            self._load_images_from_folder(self.current_folder)

        except Exception as e:
            self._log(f"Background removal error: {e}", "error")
            self.status_label.setText("Error removing background")

    def _remove_background(self) -> None:
        """Remove background from all images."""
        if not self.current_images:
            return

        if not self.bg_removal_check.isChecked():
            QMessageBox.information(
                self, "Background Removal Disabled",
                "Enable 'AI Background Removal' in Settings tab first."
            )
            return

        status = check_rembg_installation()
        if not REMBG_AVAILABLE:
            reply = QMessageBox.question(
                self, "rembg Not Installed",
                f"{status['recommendation']}\n\nContinue with fallback method?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        self._log(f"Removing backgrounds from {len(self.current_images)} images...", "info")
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
            self._log(f"Background removal: {results['processed']} succeeded, {results['failed']} failed", "success")
            self._load_images_from_folder(self.current_folder)

        except Exception as e:
            self._log(f"Background removal error: {e}", "error")
            self.status_label.setText("Error removing backgrounds")

    def _optimize_images(self) -> None:
        """Process and optimize all images."""
        if not self.current_folder:
            return

        self._log("Starting image optimization...", "info")
        self.status_label.setText("Optimizing images...")
        self.progress_bar.setValue(0)

        options = {
            "max_dimension": self.config.get("image_processing", {}).get("max_dimension", 2400),
            "quality": self.config.get("image_processing", {}).get("webp_quality", 88),
            "strip_exif": self.config.get("image_processing", {}).get("strip_exif", True),
            "output_format": "webp"
        }

        self.processing_thread = ProcessingThread(self.current_folder, self.config, options)
        self.processing_thread.progress.connect(self._on_processing_progress)
        self.processing_thread.finished.connect(self._on_processing_finished)
        self.processing_thread.error.connect(self._on_processing_error)
        self.processing_thread.start()

        self.optimize_btn.setEnabled(False)

    def _on_processing_progress(self, percent: int, message: str) -> None:
        """Handle processing progress updates."""
        self.progress_bar.setValue(percent)
        self.status_label.setText(message)

    def _on_processing_finished(self, results: Dict[str, Any]) -> None:
        """Handle processing completion."""
        self.optimize_btn.setEnabled(True)
        self.upload_btn.setEnabled(True)

        success_count = len(results.get("images", []))
        error_count = len(results.get("errors", []))

        self._log(f"Optimization complete: {success_count} images processed", "success")
        if error_count > 0:
            self._log(f"Errors: {error_count} images failed", "warning")

        processed_folder = Path(self.current_folder) / "processed"
        if processed_folder.exists():
            self._load_images_from_folder(str(processed_folder))

    def _on_processing_error(self, error: str) -> None:
        """Handle processing errors."""
        self.optimize_btn.setEnabled(True)
        self._log(f"Processing error: {error}", "error")
        self.status_label.setText("Error during processing")

    # -------------------------------------------------------------------------
    # AI Generation
    # -------------------------------------------------------------------------

    def _generate_description(self) -> None:
        """Generate product description using AI."""
        if not self.current_images:
            QMessageBox.warning(self, "No Images", "Load a product folder first.")
            return

        self._log("Generating AI description...", "info")
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

                valuation = result.get("valuation")
                if valuation and isinstance(valuation, dict):
                    recommended = valuation.get("recommended") or 0
                    low = valuation.get("low") or 0
                    high = valuation.get("high") or 0
                    if recommended:
                        self._log(
                            f"💰 Price Research: ${low:,.2f} - ${high:,.2f} (Rec: ${recommended:,.2f})",
                            "info"
                        )
                        self.last_valuation = {
                            "low": low,
                            "high": high,
                            "recommended": recommended,
                            "confidence": valuation.get("confidence", "Medium"),
                            "notes": valuation.get("notes", "")
                        }

                self._log("AI description generated", "success")
                self._update_export_button_state()
            else:
                self._log("AI generation returned no results", "warning")

        except Exception as e:
            self._log(f"AI error: {e}", "error")

        self.status_label.setText("Ready")

    def _generate_valuation(self) -> None:
        """Generate AI-powered price research."""
        self._log("Generating price research...", "info")

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

                self._log(
                    f"💰 Price Research Results:\n"
                    f"   Suggested Range: ${low:,.2f} - ${high:,.2f}\n"
                    f"   Recommended: ${recommended:,.2f}\n"
                    f"   Confidence: {confidence}\n"
                    f"   Notes: {notes}",
                    "info"
                )

                self.last_valuation = {
                    "low": low,
                    "high": high,
                    "recommended": recommended,
                    "confidence": confidence,
                    "notes": notes
                }

        except Exception as e:
            self._log(f"Price research error: {e}", "error")

    # -------------------------------------------------------------------------
    # Upload & Export
    # -------------------------------------------------------------------------

    def _upload_to_imagekit(self) -> None:
        """Upload processed images to ImageKit."""
        if not self.current_images:
            return

        self._log("Uploading to ImageKit...", "info")
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
                        self._log(f"Uploaded: {Path(img_path).name} → {url}", "info")
                    else:
                        self._log(f"Upload returned no URL for {Path(img_path).name}", "warning")
                else:
                    error_msg = result.get("error", "Unknown error") if result else "No response"
                    self._log(f"Failed to upload {Path(img_path).name}: {error_msg}", "error")

                progress = int(((i + 1) / total) * 100)
                self.progress_bar.setValue(progress)
                self.status_label.setText(f"Uploading {i + 1}/{total}...")
                QApplication.processEvents()

            self._log(f"Uploaded {len(uploaded_urls)} images to ImageKit", "success")
            self.uploaded_image_urls = uploaded_urls

            if uploaded_urls and self.title_edit.text() and self.description_edit.toPlainText():
                self.export_btn.setEnabled(True)

        except Exception as e:
            self._log(f"Upload error: {e}", "error")

        self.status_label.setText("Ready")

    def _update_export_button_state(self) -> None:
        """Update export button enabled state."""
        if self.export_btn:
            can_export = (
                bool(self.sku_edit.text().strip()) and
                bool(self.title_edit.text().strip()) and
                bool(self.description_edit.toPlainText().strip()) and
                len(self.uploaded_image_urls) > 0
            )
            self.export_btn.setEnabled(can_export)

    def _export_package(self) -> None:
        """Export product package to files."""
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

        self._log("Exporting product package...", "info")
        self.status_label.setText("Exporting package...")

        try:
            category_prefix = self.config["categories"][category]["prefix"]
            self.sku_scanner.ensure_category_folder(category_prefix)
            self._log(f"Verified category folder: {category_prefix}", "info")

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
                "imagekit_folder": f"products/{category_prefix}/{sku}",
                "seoTitle": self.seo_title_edit.text() or self.title_edit.text(),
                "seoDescription": self.seo_desc_edit.toPlainText() or self.description_edit.toPlainText()[:160],
                "seoKeywords": [k.strip() for k in self.seo_keywords_edit.text().split(",") if k.strip()],
                "last_valuation": self.last_valuation
            }

            result = self.output_generator.export_package(product_data)

            if result.get("success"):
                output_path = result.get("output_path")
                self._log(f"✅ Package exported to: {output_path}", "success")
                self._show_export_success_dialog(sku, output_path)
            else:
                error = result.get("error", "Unknown error")
                self._log(f"Export failed: {error}", "error")
                QMessageBox.warning(self, "Export Failed", f"Error: {error}")

        except Exception as e:
            self._log(f"Export error: {e}", "error")
            QMessageBox.critical(self, "Error", f"Failed to export: {e}")

        self.status_label.setText("Ready")

    def _show_export_success_dialog(self, sku: str, output_path: str) -> None:
        """Show export success dialog with options."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Export Successful")
        msg.setText(f"Product package exported successfully!\n\nSKU: {sku}\nLocation: {output_path}")

        open_folder_btn = msg.addButton("Open Folder", QMessageBox.ActionRole)
        new_product_btn = msg.addButton("New Product", QMessageBox.ActionRole)
        msg.addButton("OK", QMessageBox.AcceptRole)

        msg.exec_()

        if msg.clickedButton() == open_folder_btn:
            import subprocess
            import platform
            if platform.system() == "Windows":
                subprocess.Popen(f'explorer "{output_path}"')
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", str(output_path)])
            else:
                subprocess.Popen(["xdg-open", str(output_path)])
        elif msg.clickedButton() == new_product_btn:
            self._reset_form()

    def _reset_form(self) -> None:
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

        while self.image_grid_layout.count():
            item = self.image_grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.optimize_btn.setEnabled(False)
        self.upload_btn.setEnabled(False)
        self.export_btn.setEnabled(False)

        self.progress_bar.setValue(0)
        self._log("Form reset - ready for next product", "info")

    def _export_product(self, format_type: str) -> None:
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
                self._log(f"Exported to {filename}", "success")

    # -------------------------------------------------------------------------
    # Dialogs
    # -------------------------------------------------------------------------

    def _open_folder(self) -> None:
        """Open folder selection dialog."""
        self.drop_zone.browse_folder()

    def _batch_process(self) -> None:
        """Open batch processing dialog."""
        QMessageBox.information(
            self, "Batch Processing",
            "Batch processing will be available in the next update."
        )

    def _show_settings(self) -> None:
        """Show settings dialog."""
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

        self.anthropic_key_edit = QLineEdit()
        current_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.anthropic_key_edit.setText(current_key)
        self.anthropic_key_edit.setEchoMode(QLineEdit.Password)
        self.anthropic_key_edit.setPlaceholderText("sk-ant-...")
        ai_layout.addRow("Anthropic API Key:", self.anthropic_key_edit)

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
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: self._save_settings_from_dialog(dialog))
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)
        dialog.exec_()

    def _save_settings_from_dialog(self, dialog: QDialog) -> None:
        """Save settings from the settings dialog."""
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

        # Save Anthropic Key to .env
        new_key = self.anthropic_key_edit.text().strip()
        if new_key != os.getenv("ANTHROPIC_API_KEY", ""):
            try:
                from modules.env_loader import update_env_key
                if update_env_key("ANTHROPIC_API_KEY", new_key):
                    os.environ["ANTHROPIC_API_KEY"] = new_key
                    # Update config in memory if needed, though AIEngine reads from env
            except ImportError:
                print("Could not update .env file (module not found)")

        self.config["ai"]["model"] = self.ai_model_edit.text()

        self.config["image_processing"]["max_dimension"] = self.max_dim_spin.value()
        self.config["image_processing"]["webp_quality"] = self.quality_spin.value()
        self.config["image_processing"]["strip_exif"] = self.strip_exif_check.isChecked()

        self._save_config()

        QMessageBox.information(dialog, "Settings Saved", "Settings have been saved successfully.")
        dialog.accept()

    def _show_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self, "About Kollect-It Product Manager",
            f"Kollect-It Product Manager v{VERSION}\n\n"
            "Desktop application for processing and optimizing "
            "antiques and collectibles listings.\n\n"
            "© 2025 Kollect-It"
        )

    def _open_import_wizard(self) -> None:
        """Open the import wizard dialog."""
        wizard = ImportWizard(self.config, self)
        wizard.import_complete.connect(self._on_import_complete)
        wizard.exec_()

    def _on_import_complete(self, folder_path: str) -> None:
        """Handle completed import - load the new product."""
        self._log(f"Product imported to: {folder_path}", "success")

        if folder_path:
            info_file = Path(folder_path) / "product_info.json"
            if info_file.exists():
                try:
                    with open(info_file) as f:
                        info = json.load(f)

                    self.sku_edit.setText(info.get("sku", ""))
                    self.title_edit.setText(info.get("title", ""))

                    category = info.get("category", "")
                    if category:
                        index = self.category_combo.findData(category)
                        if index >= 0:
                            self.category_combo.setCurrentIndex(index)

                except Exception as e:
                    self._log(f"Error reading product info: {e}", "warning")

            self._on_folder_dropped(folder_path)
            self._log("Product loaded - ready for processing", "info")

    # -------------------------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------------------------

    def closeEvent(self, event) -> None:
        """Handle application close event - cleanup temporary directories."""
        import shutil
        for temp_dir in self._temp_dirs:
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

    # Increase global font size by 2 points
    font = app.font()
    font.setPointSize(font.pointSize() + 2)
    app.setFont(font)

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
