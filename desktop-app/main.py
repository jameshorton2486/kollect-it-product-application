#!/usr/bin/env python3
"""
Kollect-It Product Manager
Desktop application for processing, optimizing, and publishing antiques/collectibles listings.

Features:
- Drag-and-drop product folder processing
- AI-powered image renaming and description generation
- WebP conversion with optimization
- Built-in image cropping tool
- AI background removal
- ImageKit cloud upload
- Direct website publishing via API
- SKU generation per category
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# Load environment variables from .env file (if available)
try:
    from dotenv import load_dotenv
    # Load .env from desktop-app directory
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
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
from modules.sku_generator import SKUGenerator  # type: ignore
from modules.ai_engine import AIEngine  # type: ignore
from modules.product_publisher import ProductPublisher  # type: ignore
from modules.background_remover import BackgroundRemover  # type: ignore
from modules.crop_tool import CropDialog  # type: ignore
from modules.import_wizard import ImportWizard  # type: ignore


class DarkPalette:
    """Dark theme color palette for the application - IMPROVED READABILITY."""
    
    # Backgrounds - slightly lighter for better contrast
    BACKGROUND = "#1e1e2e"       # Main background (was #1a1a2e)
    SURFACE = "#1a1a2e"          # Card/panel background (was #16213e)
    SURFACE_LIGHT = "#252542"    # Hover states (was #1f3460)
    
    # Primary colors
    PRIMARY = "#e94560"          # Accent color (unchanged)
    PRIMARY_DARK = "#c73e54"     # Darker accent (unchanged)
    SECONDARY = "#0f3460"        # Secondary accent (unchanged)
    
    # Text colors - IMPROVED CONTRAST
    TEXT = "#ffffff"             # Primary text - pure white (was #eaeaea)
    TEXT_SECONDARY = "#b4b4b4"   # Secondary text - lighter (was #a0a0a0)
    TEXT_MUTED = "#8888a0"       # Muted/placeholder text (new)
    
    # Borders
    BORDER = "#3d3d5c"           # Border color - more visible (was #2d3748)
    BORDER_FOCUS = "#e94560"     # Focus border (new)
    
    # Status colors
    SUCCESS = "#4ade80"          # Brighter green (was #48bb78)
    WARNING = "#fbbf24"          # Brighter yellow (was #ed8936)
    ERROR = "#f87171"            # Error red (was #fc8181)
    INFO = "#60a5fa"             # Info blue (new)
    
    @classmethod
    def get_stylesheet(cls) -> str:
        return f"""
            /* ============================================
               GLOBAL STYLES - Larger base font
               ============================================ */
            QMainWindow, QWidget {{
                background-color: {cls.BACKGROUND};
                color: {cls.TEXT};
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
            }}
            
            /* ============================================
               GROUP BOXES - Section containers
               ============================================ */
            QGroupBox {{
                background-color: {cls.SURFACE};
                border: 1px solid {cls.BORDER};
                border-radius: 8px;
                margin-top: 16px;
                padding: 16px;
                padding-top: 24px;
                font-weight: bold;
                font-size: 15px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                top: 4px;
                padding: 0 10px;
                color: {cls.PRIMARY};
                font-size: 15px;
                font-weight: bold;
            }}
            
            /* ============================================
               BUTTONS - More prominent
               ============================================ */
            QPushButton {{
                background-color: {cls.PRIMARY};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
                min-height: 24px;
            }}
            
            QPushButton:hover {{
                background-color: {cls.PRIMARY_DARK};
            }}
            
            QPushButton:pressed {{
                background-color: #a83246;
            }}
            
            QPushButton:disabled {{
                background-color: #3d3d5c;
                color: #6b6b8a;
            }}
            
            QPushButton.secondary {{
                background-color: {cls.SECONDARY};
            }}
            
            QPushButton.secondary:hover {{
                background-color: {cls.SURFACE_LIGHT};
            }}
            
            /* ============================================
               INPUT FIELDS - Better visibility
               ============================================ */
            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
                background-color: {cls.SURFACE};
                border: 2px solid {cls.BORDER};
                border-radius: 6px;
                padding: 10px 14px;
                color: {cls.TEXT};
                font-size: 14px;
                min-height: 20px;
            }}
            
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
                border-color: {cls.PRIMARY};
                background-color: #1e1e32;
            }}
            
            QLineEdit::placeholder, QTextEdit::placeholder {{
                color: {cls.TEXT_MUTED};
            }}
            
            /* ============================================
               COMBO BOX - Dropdown styling
               ============================================ */
            QComboBox {{
                padding-right: 30px;
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 8px solid {cls.TEXT};
                margin-right: 12px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {cls.SURFACE};
                border: 2px solid {cls.BORDER};
                border-radius: 6px;
                color: {cls.TEXT};
                selection-background-color: {cls.SURFACE_LIGHT};
                padding: 4px;
                font-size: 14px;
            }}
            
            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                min-height: 28px;
            }}
            
            QComboBox QAbstractItemView::item:hover {{
                background-color: {cls.SURFACE_LIGHT};
            }}
            
            /* ============================================
               SPIN BOXES - Number inputs
               ============================================ */
            QSpinBox::up-button, QDoubleSpinBox::up-button,
            QSpinBox::down-button, QDoubleSpinBox::down-button {{
                background-color: {cls.SURFACE_LIGHT};
                border: none;
                width: 24px;
            }}
            
            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
                background-color: {cls.PRIMARY};
            }}
            
            /* ============================================
               PROGRESS BAR - More visible
               ============================================ */
            QProgressBar {{
                background-color: {cls.SURFACE};
                border: none;
                border-radius: 6px;
                height: 12px;
                text-align: center;
                font-size: 11px;
                color: {cls.TEXT};
            }}
            
            QProgressBar::chunk {{
                background-color: {cls.PRIMARY};
                border-radius: 6px;
            }}
            
            /* ============================================
               LIST WIDGET - File lists
               ============================================ */
            QListWidget {{
                background-color: {cls.SURFACE};
                border: 2px solid {cls.BORDER};
                border-radius: 6px;
                padding: 6px;
                font-size: 14px;
            }}
            
            QListWidget::item {{
                padding: 10px;
                border-radius: 4px;
                margin: 2px 0;
            }}
            
            QListWidget::item:selected {{
                background-color: {cls.SURFACE_LIGHT};
                color: {cls.TEXT};
            }}
            
            QListWidget::item:hover {{
                background-color: {cls.SECONDARY};
            }}
            
            /* ============================================
               TABS - Navigation tabs
               ============================================ */
            QTabWidget::pane {{
                background-color: {cls.SURFACE};
                border: 2px solid {cls.BORDER};
                border-radius: 8px;
                top: -2px;
            }}
            
            QTabBar::tab {{
                background-color: {cls.SURFACE};
                color: {cls.TEXT_SECONDARY};
                padding: 12px 24px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid transparent;
                border-bottom: none;
            }}
            
            QTabBar::tab:selected {{
                background-color: {cls.SURFACE};
                color: {cls.PRIMARY};
                border-color: {cls.BORDER};
            }}
            
            QTabBar::tab:hover:!selected {{
                background-color: {cls.SURFACE_LIGHT};
                color: {cls.TEXT};
            }}
            
            /* ============================================
               SCROLL BARS - Wider and more visible
               ============================================ */
            QScrollBar:vertical {{
                background-color: {cls.SURFACE};
                width: 14px;
                border-radius: 7px;
                margin: 2px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {cls.BORDER};
                border-radius: 7px;
                min-height: 40px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {cls.TEXT_MUTED};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                background-color: {cls.SURFACE};
                height: 14px;
                border-radius: 7px;
                margin: 2px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {cls.BORDER};
                border-radius: 7px;
                min-width: 40px;
            }}
            
            /* ============================================
               LABELS - Text styling
               ============================================ */
            QLabel {{
                color: {cls.TEXT};
                font-size: 14px;
            }}
            
            QLabel.title {{
                font-size: 28px;
                font-weight: bold;
                color: {cls.PRIMARY};
            }}
            
            QLabel.subtitle {{
                font-size: 16px;
                color: {cls.TEXT_SECONDARY};
            }}
            
            QLabel.section-header {{
                font-size: 16px;
                font-weight: bold;
                color: {cls.PRIMARY};
            }}
            
            /* ============================================
               CHECKBOXES
               ============================================ */
            QCheckBox {{
                color: {cls.TEXT};
                spacing: 10px;
                font-size: 14px;
            }}
            
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid {cls.BORDER};
                background-color: {cls.SURFACE};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {cls.PRIMARY};
                border-color: {cls.PRIMARY};
            }}
            
            QCheckBox::indicator:hover {{
                border-color: {cls.PRIMARY};
            }}
            
            /* ============================================
               SLIDERS
               ============================================ */
            QSlider::groove:horizontal {{
                height: 8px;
                background-color: {cls.SURFACE};
                border-radius: 4px;
            }}
            
            QSlider::handle:horizontal {{
                width: 20px;
                height: 20px;
                margin: -6px 0;
                background-color: {cls.PRIMARY};
                border-radius: 10px;
            }}
            
            QSlider::handle:horizontal:hover {{
                background-color: {cls.PRIMARY_DARK};
            }}
            
            QSlider::sub-page:horizontal {{
                background-color: {cls.PRIMARY};
                border-radius: 4px;
            }}
            
            /* ============================================
               STATUS BAR
               ============================================ */
            QStatusBar {{
                background-color: {cls.SURFACE};
                color: {cls.TEXT};
                font-size: 13px;
                padding: 6px;
                border-top: 1px solid {cls.BORDER};
            }}
            
            /* ============================================
               MENU BAR
               ============================================ */
            QMenuBar {{
                background-color: {cls.SURFACE};
                color: {cls.TEXT};
                padding: 6px;
                font-size: 14px;
            }}
            
            QMenuBar::item {{
                padding: 8px 14px;
                border-radius: 4px;
            }}
            
            QMenuBar::item:selected {{
                background-color: {cls.SURFACE_LIGHT};
            }}
            
            QMenu {{
                background-color: {cls.SURFACE};
                border: 2px solid {cls.BORDER};
                border-radius: 8px;
                padding: 6px;
                font-size: 14px;
            }}
            
            QMenu::item {{
                padding: 10px 28px;
                border-radius: 4px;
            }}
            
            QMenu::item:selected {{
                background-color: {cls.SURFACE_LIGHT};
            }}
            
            QMenu::separator {{
                height: 1px;
                background-color: {cls.BORDER};
                margin: 6px 10px;
            }}
            
            /* ============================================
               TOOLBAR
               ============================================ */
            QToolBar {{
                background-color: {cls.SURFACE};
                border: none;
                spacing: 10px;
                padding: 10px;
                border-bottom: 1px solid {cls.BORDER};
            }}
            
            QToolBar QToolButton {{
                background-color: transparent;
                color: {cls.TEXT};
                padding: 8px 14px;
                border-radius: 6px;
                font-size: 14px;
            }}
            
            QToolBar QToolButton:hover {{
                background-color: {cls.SURFACE_LIGHT};
            }}
            
            /* ============================================
               TEXT EDIT - Activity log, descriptions
               ============================================ */
            QTextEdit {{
                font-size: 14px;
                line-height: 1.5;
            }}
            
            /* ============================================
               FORM LABELS - Row labels
               ============================================ */
            QFormLayout QLabel {{
                font-size: 14px;
                font-weight: 500;
                color: {cls.TEXT_SECONDARY};
                min-width: 90px;
            }}
            
            /* ============================================
               TOOLTIPS
               ============================================ */
            QToolTip {{
                background-color: {cls.SURFACE_LIGHT};
                color: {cls.TEXT};
                border: 1px solid {cls.BORDER};
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }}
        """


class DropZone(QFrame):
    """Custom drag-and-drop zone for product folders."""
    
    folder_dropped = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.browse_btn = None  # Initialize attribute
        self.setAcceptDrops(True)
        self.setMinimumHeight(200)
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {DarkPalette.SURFACE};
                border: 2px dashed {DarkPalette.BORDER};
                border-radius: 12px;
            }}
            QFrame:hover {{
                border-color: {DarkPalette.PRIMARY};
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
                font-size: 18px;
                font-weight: bold;
            }
        """)
        main_text.setAlignment(Qt.AlignCenter)  # type: ignore
        layout.addWidget(main_text)
        
        # Sub text
        sub_text = QLabel("or click Browse to select a folder")
        sub_text.setStyleSheet("""
            QLabel {
                color: #b4b4b4;
                font-size: 14px;
            }
        """)
        sub_text.setAlignment(Qt.AlignCenter)  # type: ignore
        layout.addWidget(sub_text)
        
        # Browse button
        self.browse_btn = QPushButton("Browse Folder")
        self.browse_btn.setMaximumWidth(200)
        self.browse_btn.clicked.connect(self.browse_folder)
        layout.addWidget(self.browse_btn, alignment=Qt.AlignCenter)  # type: ignore
        
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
    
    def browse_folder(self):
        # Get default path from config, fallback to user's home directory
        default_path = ""
        if hasattr(self, 'config'):
            default_path = self.config.get("paths", {}).get("default_browse", "")
        if not default_path:
            default_path = str(Path.home())
        
        folder = QFileDialog.getExistingDirectory(
            self, "Select Product Folder",
            default_path, QFileDialog.ShowDirsOnly
        )
        if folder:
            self.folder_dropped.emit(folder)


class ImageThumbnail(QLabel):
    """Clickable image thumbnail with edit options."""
    
    clicked = pyqtSignal(str)
    crop_requested = pyqtSignal(str)
    remove_bg_requested = pyqtSignal(str)
    
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.setFixedSize(120, 120)
        self.setCursor(Qt.PointingHandCursor)  # type: ignore
        self.load_image()
        
    def load_image(self):
        pixmap = QPixmap(self.image_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatio,  # type: ignore
                Qt.SmoothTransformation  # type: ignore
            )
            self.setPixmap(scaled)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {DarkPalette.SURFACE};
                border: 2px solid {DarkPalette.BORDER};
                border-radius: 8px;
                padding: 4px;
            }}
            QLabel:hover {{
                border-color: {DarkPalette.PRIMARY};
            }}
        """)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:  # type: ignore
            self.clicked.emit(self.image_path)
        elif event.button() == Qt.RightButton:  # type: ignore
            self.show_context_menu(event.pos())
    
    def show_context_menu(self, pos):
        from PyQt5.QtWidgets import QMenu
        menu = QMenu(self)
        crop_action = menu.addAction("✂️ Crop Image")
        bg_action = menu.addAction("🎨 Remove Background")
        preview_action = menu.addAction("🔍 Preview Full Size")
        
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
        self.current_folder = None
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
        self.publish_btn = None
        self.title_edit = None
        self.sku_edit = None
        self.category_combo = None
        self.subcategory_combo = None
        self.price_spin = None
        self.original_price_spin = None
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
        self.auto_publish_check = None
        self.use_production_check = None
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
        self.ai_key_edit = None
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
                "Add it to .env file or config.json.\n"
                "Publishing to the website will not work until you add your API key."
            )
        
        return config
    
    def save_config(self):
        """Save configuration to config.json."""
        config_path = Path(__file__).parent / "config" / "config.json"
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def setup_ui(self):
        """Initialize the main user interface."""
        self.setWindowTitle("Kollect-It Product Manager")
        self.setMinimumSize(1600, 1000)
        self.setStyleSheet(DarkPalette.get_stylesheet())
        
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
        new_product_btn = QPushButton("📦 Add New Product")
        new_product_btn.setMinimumHeight(40)
        new_product_btn.setStyleSheet("""
            QPushButton {
                background-color: #48bb78;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #38a169;
            }
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
        
        self.crop_all_btn = QPushButton("✂️ Crop Selected")
        self.crop_all_btn.setEnabled(False)
        self.crop_all_btn.clicked.connect(self.crop_selected_image)
        img_actions.addWidget(self.crop_all_btn)
        
        self.remove_bg_btn = QPushButton("🎨 Remove Background")
        self.remove_bg_btn.setEnabled(False)
        self.remove_bg_btn.clicked.connect(self.remove_background)
        img_actions.addWidget(self.remove_bg_btn)
        
        self.optimize_btn = QPushButton("⚡ Optimize All")
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
        form.setSpacing(12)
        
        # Title
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter product title...")
        form.addRow("Title:", self.title_edit)
        
        # SKU (auto-generated)
        sku_layout = QHBoxLayout()
        self.sku_edit = QLineEdit()
        self.sku_edit.setReadOnly(True)
        self.sku_edit.setPlaceholderText("Auto-generated")
        sku_layout.addWidget(self.sku_edit)
        self.regenerate_sku_btn = QPushButton("🔄")
        self.regenerate_sku_btn.setMaximumWidth(40)
        self.regenerate_sku_btn.clicked.connect(self.regenerate_sku)
        sku_layout.addWidget(self.regenerate_sku_btn)
        form.addRow("SKU:", sku_layout)
        
        # Category
        self.category_combo = QComboBox()
        # Clear existing items
        self.category_combo.clear()
        
        # Add categories from config with proper data
        for cat_id, cat_info in self.config.get("categories", {}).items():
            display_name = cat_info.get("name", cat_id.title())
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
        self.price_spin.setPrefix("$ "),
        self.price_spin.setDecimals(2)
        price_layout.addWidget(self.price_spin)
        
        self.original_price_spin = QDoubleSpinBox()
        self.original_price_spin.setRange(0, 999999.99)
        self.original_price_spin.setPrefix("$ ")
        self.original_price_spin.setDecimals(2)
        self.original_price_spin.setSpecialValueText("Optional")
        price_layout.addWidget(self.original_price_spin)
        form.addRow("Price:", price_layout)
        
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
        self.generate_desc_btn = QPushButton("✨ Generate with AI")
        self.generate_desc_btn.clicked.connect(self.generate_description)
        ai_btn_layout.addWidget(self.generate_desc_btn)
        
        self.generate_valuation_btn = QPushButton("💰 AI Valuation")
        self.generate_valuation_btn.clicked.connect(self.generate_valuation)
        ai_btn_layout.addWidget(self.generate_valuation_btn)
        desc_layout.addLayout(ai_btn_layout)
        
        details_layout.addWidget(desc_group)
        tabs.addTab(details_tab, "📦 Product Details")
        
        # SEO Tab
        seo_tab = QWidget()
        seo_layout = QFormLayout(seo_tab)
        seo_layout.setSpacing(12)
        
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
        
        tabs.addTab(seo_tab, "🔍 SEO")
        
        # Settings Tab
        settings_tab = QWidget()
        settings_layout = QFormLayout(settings_tab)
        settings_layout.setSpacing(12)
        
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
        
        self.auto_publish_check = QCheckBox("Auto-publish after processing")
        settings_layout.addRow(self.auto_publish_check)
        
        self.use_production_check = QCheckBox("Use Production API")
        self.use_production_check.setChecked(
            self.config.get("api", {}).get("use_production", True)
        )
        settings_layout.addRow(self.use_production_check)
        
        tabs.addTab(settings_tab, "⚙️ Settings")
        
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
        
        self.upload_btn = QPushButton("☁️ Upload to ImageKit")
        self.upload_btn.setEnabled(False)
        self.upload_btn.clicked.connect(self.upload_to_imagekit)
        actions_layout.addWidget(self.upload_btn)
        
        self.publish_btn = QPushButton("🚀 Publish Product")
        self.publish_btn.setEnabled(False)
        self.publish_btn.clicked.connect(self.publish_product)
        self.publish_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DarkPalette.SUCCESS};
                font-size: 15px;
                padding: 14px 28px;
            }}
            QPushButton:hover {{
                background-color: #38a169;
            }}
        """)
        actions_layout.addWidget(self.publish_btn)
        
        right_layout.addLayout(actions_layout)
        
        # Log output
        log_group = QGroupBox("Activity Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(150)
        self.log_output.setStyleSheet(f"""
            QTextEdit {{
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                background-color: {DarkPalette.BACKGROUND};
            }}
        """)
        log_layout.addWidget(self.log_output)
        
        right_layout.addWidget(log_group)
        
        main_layout.addWidget(right_panel, stretch=1)
        
    def setup_menu(self):
        """Set up the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        # New Product action (at the top of File menu)
        new_product_action = QAction("📦 &New Product...", self)
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
        new_product_action = QAction("📦 New Product", self)
        new_product_action.setStatusTip("Import photos and create a new product")
        new_product_action.triggered.connect(self.open_import_wizard)
        toolbar.addAction(new_product_action)
        
        toolbar.addSeparator()
        
        toolbar.addAction("📂 Open", self.open_folder)
        toolbar.addAction("⚡ Process", self.optimize_images)
        toolbar.addAction("☁️ Upload", self.upload_to_imagekit)
        toolbar.addAction("🚀 Publish", self.publish_product)
        
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
        max_cols = 4
        
        for img_path in images:
            self.current_images.append(str(img_path))
            
            thumb = ImageThumbnail(str(img_path))
            thumb.clicked.connect(self.preview_image)
            thumb.crop_requested.connect(self.crop_image)
            thumb.remove_bg_requested.connect(self.remove_image_background)
            
            self.image_grid_layout.addWidget(thumb, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        self.log(f"Found {len(images)} images", "info")
        
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
            state_file_path = Path(__file__).parent / "config" / "sku_state.json"
            generator = SKUGenerator(str(state_file_path))
            prefix = self.config["categories"][cat_id]["prefix"]
            sku = generator.generate(prefix)
            self.sku_edit.setText(sku)
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
        dialog = CropDialog(image_path, self)
        if dialog.exec_() == QDialog.Accepted:
            _cropped_path = dialog.get_cropped_path()  # Path is used implicitly by reload
            self.log(f"Cropped: {os.path.basename(image_path)}", "success")
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
        from modules.background_remover import REMBG_AVAILABLE, check_rembg_installation  # type: ignore
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
        
        from modules.background_remover import BackgroundRemover  # type: ignore
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
                "images": self.current_images[:5]  # Send up to 5 images
            }
            
            result = engine.generate_description(product_data)
            
            if result:
                self.description_edit.setPlainText(result.get("description", ""))
                self.seo_title_edit.setText(result.get("seo_title", ""))
                self.seo_desc_edit.setPlainText(result.get("seo_description", ""))
                self.seo_keywords_edit.setText(", ".join(result.get("keywords", [])))
                
                if result.get("suggested_title"):
                    self.title_edit.setText(result["suggested_title"])
                    
                self.log("AI description generated", "success")
            else:
                self.log("AI generation returned no results", "warning")
                
        except Exception as e:
            self.log(f"AI error: {e}", "error")
            
        self.status_label.setText("Ready")
        
    def generate_valuation(self):
        """Generate AI-powered valuation estimate."""
        self.log("Generating AI valuation...", "info")
        
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
                "images": self.current_images[:3]
            }
            
            valuation = engine.generate_valuation(product_data)
            
            if valuation:
                low = valuation.get("low", 0)
                high = valuation.get("high", 0)
                recommended = valuation.get("recommended", 0)
                
                self.price_spin.setValue(recommended)
                self.log(
                    f"Valuation: ${low:,.2f} - ${high:,.2f} (Recommended: ${recommended:,.2f})",
                    "success"
                )
                
                if valuation.get("notes"):
                    self.log(f"Valuation notes: {valuation['notes']}", "info")
                    
        except Exception as e:
            self.log(f"Valuation error: {e}", "error")
            
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
                        self.log(f"Uploaded: {Path(img_path).name} → {url}", "info")
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
            self.publish_btn.setEnabled(True)
            
            # Store URLs for publishing
            self.uploaded_image_urls = uploaded_urls
            
        except Exception as e:
            self.log(f"Upload error: {e}", "error")
            
        self.status_label.setText("Ready")
        
    def publish_product(self):
        """Publish the product to the website."""
        # Validate required fields
        if not self.title_edit.text():
            QMessageBox.warning(self, "Missing Title", "Please enter a product title.")
            return
            
        if not self.description_edit.toPlainText():
            QMessageBox.warning(self, "Missing Description", "Please generate or enter a description.")
            return
            
        if self.price_spin.value() <= 0:
            QMessageBox.warning(self, "Missing Price", "Please set a price.")
            return
            
        self.log("Publishing product...", "info")
        self.status_label.setText("Publishing to website...")
        
        try:
            publisher = ProductPublisher(self.config)
            
            # Validate required fields
            category = self.category_combo.currentData()
            if not category:
                QMessageBox.warning(self, "Missing Category", "Please select a category.")
                return
            
            sku = self.sku_edit.text()
            if not sku:
                QMessageBox.warning(self, "Missing SKU", "Please generate a SKU.")
                return
            
            # Build product payload
            product_data = {
                "title": self.title_edit.text(),
                "sku": sku,
                "category": category,
                "subcategory": self.subcategory_combo.currentText(),
                "description": self.description_edit.toPlainText(),
                "descriptionHtml": f"<p>{self.description_edit.toPlainText()}</p>",
                "price": self.price_spin.value(),
                "originalPrice": self.original_price_spin.value() or None,
                "condition": self.condition_combo.currentText(),
                "era": self.era_edit.text() or None,
                "origin": self.origin_edit.text() or None,
                "images": [
                    {"url": url, "alt": f"{self.title_edit.text()} - Image {i+1}", "order": i}
                    for i, url in enumerate(getattr(self, 'uploaded_image_urls', []))
                ],
                "seoTitle": self.seo_title_edit.text() or self.title_edit.text(),
                "seoDescription": self.seo_desc_edit.toPlainText() or self.description_edit.toPlainText()[:160],
                "seoKeywords": [k.strip() for k in self.seo_keywords_edit.text().split(",") if k.strip()],
                "status": "draft"
            }
            
            result = publisher.publish(product_data)
            
            if result.get("success"):
                product_url = result.get("product", {}).get("url", "")
                self.log(f"✅ Product published! URL: {product_url}", "success")
                
                QMessageBox.information(
                    self, "Success!",
                    f"Product published successfully!\n\nSKU: {self.sku_edit.text()}\nURL: {product_url}"
                )
                
                # Reset form for next product
                self.reset_form()
                
            else:
                error = result.get("error", "Unknown error")
                self.log(f"Publish failed: {error}", "error")
                QMessageBox.warning(self, "Publish Failed", f"Error: {error}")
                
        except Exception as e:
            self.log(f"Publish error: {e}", "error")
            QMessageBox.critical(self, "Error", f"Failed to publish: {e}")
            
        self.status_label.setText("Ready")
        
    def reset_form(self):
        """Reset the form for a new product."""
        self.title_edit.clear()
        self.description_edit.clear()
        self.seo_title_edit.clear()
        self.seo_desc_edit.clear()
        self.seo_keywords_edit.clear()
        self.era_edit.clear()
        self.origin_edit.clear()
        self.price_spin.setValue(0)
        self.original_price_spin.setValue(0)
        self.current_folder = None
        self.current_images = []
        self.uploaded_image_urls = []
        
        # Clear image grid
        while self.image_grid_layout.count():
            item = self.image_grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Disable buttons
        self.optimize_btn.setEnabled(False)
        self.upload_btn.setEnabled(False)
        self.publish_btn.setEnabled(False)
        
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
        self.use_prod_check.setChecked(not self.config.get("api", {}).get("use_local", False))
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
        
        self.ai_key_edit = QLineEdit()
        self.ai_key_edit.setText(self.config.get("ai", {}).get("api_key", ""))
        self.ai_key_edit.setEchoMode(QLineEdit.Password)
        ai_layout.addRow("Anthropic API Key:", self.ai_key_edit)
        
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
        self.config["api"]["use_local"] = not self.use_prod_check.isChecked()
        
        self.config["imagekit"]["public_key"] = self.ik_public_edit.text()
        self.config["imagekit"]["private_key"] = self.ik_private_edit.text()
        self.config["imagekit"]["url_endpoint"] = self.ik_url_edit.text()
        
        self.config["ai"]["api_key"] = self.ai_key_edit.text()
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
            "Kollect-It Product Manager v1.0.0\n\n"
            "Desktop application for processing and publishing "
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
