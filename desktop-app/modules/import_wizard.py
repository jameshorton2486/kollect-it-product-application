#!/usr/bin/env python3
"""
Import Wizard Module
Handles importing photos from camera to product folders with SKU generation.
"""

import os
import re
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Tuple

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QGridLayout, QScrollArea, QWidget, QCheckBox,
    QFrame, QMessageBox, QProgressDialog, QApplication,
    QButtonGroup, QSizePolicy, QGroupBox, QFileDialog
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QFont, QIcon

from PIL import Image, ImageOps
from io import BytesIO


# Supported image extensions (lowercase for comparison)
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.tiff', '.tif', '.bmp', '.cr2', '.nef', '.arw'}


class CategoryButton(QPushButton):
    """Custom styled button for category selection."""

    def __init__(self, category_id: str, display_name: str, prefix: str, parent=None):
        super().__init__(parent)
        self.category_id = category_id
        self.prefix = prefix

        self.setText(f"{prefix}\n{display_name}")
        self.setCheckable(True)
        self.setMinimumSize(120, 80)
        self.setFont(QFont("Segoe UI", 13, QFont.Bold))

        self.update_style(False)

    def update_style(self, selected: bool):
        """Update button style based on selection state."""
        if selected:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #e94560;
                    color: white;
                    border: 2px solid #e94560;
                    border-radius: 8px;
                    padding: 10px;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #16213e;
                    color: #a0a0a0;
                    border: 2px solid #2d3748;
                    border-radius: 8px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #1f3460;
                    border-color: #e94560;
                    color: white;
                }
            """)


class PhotoThumbnail(QFrame):
    """Clickable photo thumbnail with checkbox."""

    clicked = pyqtSignal(str, bool)

    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.selected = False

        # Larger size for better visibility (large icons)
        self.setFixedSize(200, 240)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # Thumbnail image - much larger for visibility
        self.image_label = QLabel()
        self.image_label.setFixedSize(188, 200)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(True)  # Scale image to fit
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #0f0f1a;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.image_label)

        # Filename label - show more characters for larger view
        filename = Path(file_path).name
        if len(filename) > 20:
            filename = filename[:17] + "..."
        self.name_label = QLabel(filename)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("color: #a0a0a0; font-size: 14px;")
        self.name_label.setWordWrap(True)
        layout.addWidget(self.name_label)

        # Checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        self.checkbox.stateChanged.connect(self._on_checkbox_changed)

        # Position checkbox in corner
        self.checkbox.setParent(self)
        self.checkbox.move(4, 4)
        self.checkbox.raise_()

        self.update_style()
        self.load_thumbnail()

    def load_thumbnail(self):
        """Load and display thumbnail with large icon view."""
        try:
            with Image.open(self.file_path) as img:
                # Auto-rotate based on EXIF orientation
                img = ImageOps.exif_transpose(img)

                # Convert to RGB if needed
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background for transparency
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                    else:
                        background.paste(img)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # Create larger thumbnail for better visibility (large icons)
                # Keep aspect ratio, scale to fit 188x200
                img.thumbnail((188, 200), Image.Resampling.LANCZOS)

                # Convert PIL Image to QPixmap via bytes (most reliable)
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                buffer.seek(0)
                pixmap = QPixmap()
                pixmap.loadFromData(buffer.getvalue())

                # If that fails, try direct conversion
                if pixmap.isNull():
                    data = img.tobytes("raw", "RGB")
                    qimg = QImage(data, img.width, img.height, img.width * 3, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(qimg)

                # Set pixmap (scaledContents is already True, so it will auto-scale)
                if not pixmap.isNull():
                    self.image_label.setPixmap(pixmap)
                else:
                    raise Exception("Failed to create pixmap")

        except Exception as e:
            self.image_label.clear()
            self.image_label.setText("Error\nLoading")
            self.image_label.setStyleSheet("color: #fc8181; font-size: 14px; background-color: #0f0f1a;")
            print(f"Error loading thumbnail for {self.file_path}: {e}")

    def mousePressEvent(self, event):
        """Handle click to toggle selection."""
        if event.button() == Qt.LeftButton:
            self.set_selected(not self.selected)

    def set_selected(self, selected: bool):
        """Set selection state."""
        self.selected = selected
        self.checkbox.blockSignals(True)
        self.checkbox.setChecked(selected)
        self.checkbox.blockSignals(False)
        self.update_style()
        self.clicked.emit(self.file_path, selected)

    def _on_checkbox_changed(self, state):
        """Handle checkbox state change."""
        self.selected = state == Qt.Checked
        self.update_style()
        self.clicked.emit(self.file_path, self.selected)

    def update_style(self):
        """Update frame style based on selection."""
        if self.selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #1f3460;
                    border: 2px solid #e94560;
                    border-radius: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #16213e;
                    border: 2px solid #2d3748;
                    border-radius: 8px;
                }
                QFrame:hover {
                    border-color: #4a5568;
                }
            """)


class ImportWizard(QDialog):
    """
    Import Wizard Dialog for adding new products.

    Workflow:
    1. Select category (MILI/COLL/BOOK/ART)
    2. Enter brief description
    3. View generated SKU preview
    4. Select photos from camera folder
    5. Import to Google Drive, archive originals
    """

    # Signal emitted when import is complete with the new folder path
    import_complete = pyqtSignal(str)

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = config
        self.selected_category = None
        self.selected_photos = []
        self.generated_sku = None
        self.target_folder = None
        self.photo_thumbnails = []

        self.setWindowTitle("Add New Product")
        self.setMinimumSize(800, 700)
        self.setModal(True)

        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a2e;
                color: #eaeaea;
            }
            QLabel {
                color: #eaeaea;
            }
            QLineEdit {
                background-color: #16213e;
                border: 1px solid #2d3748;
                border-radius: 6px;
                padding: 10px;
                color: #eaeaea;
                font-size: 16px;
            }
            QLineEdit:focus {
                border-color: #e94560;
            }
            QPushButton {
                background-color: #e94560;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c73e54;
            }
            QPushButton:disabled {
                background-color: #2d3748;
                color: #6b7280;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #2d3748;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 10px;
                color: #e94560;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
        """)

        self.setup_ui()
        self.load_photos()

    def setup_ui(self):
        """Set up the wizard UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("📦 Add New Product")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet("color: #e94560;")
        layout.addWidget(title)

        # Step 1: Category Selection
        cat_group = QGroupBox("Step 1: Select Category")
        cat_layout = QHBoxLayout(cat_group)
        cat_layout.setSpacing(12)

        self.category_buttons = {}
        categories = self.config.get("categories", {})

        for cat_id, cat_info in categories.items():
            prefix = cat_info.get("prefix", cat_id[:4].upper())
            name = cat_info.get("name", cat_id.title())

            btn = CategoryButton(cat_id, name, prefix)
            btn.clicked.connect(lambda checked, cid=cat_id: self.on_category_selected(cid))
            self.category_buttons[cat_id] = btn
            cat_layout.addWidget(btn)

        cat_layout.addStretch()
        layout.addWidget(cat_group)

        # Step 2: Description
        desc_group = QGroupBox("Step 2: Brief Description (becomes product title)")
        desc_layout = QVBoxLayout(desc_group)

        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("e.g., Victorian Silver Tea Set with Floral Engraving")
        self.description_edit.textChanged.connect(self.update_preview)
        desc_layout.addWidget(self.description_edit)

        layout.addWidget(desc_group)

        # Step 3: Preview
        preview_group = QGroupBox("Step 3: Preview")
        preview_layout = QGridLayout(preview_group)
        preview_layout.setColumnStretch(1, 1)

        preview_layout.addWidget(QLabel("SKU:"), 0, 0)
        self.sku_label = QLabel("—")
        self.sku_label.setStyleSheet("color: #48bb78; font-weight: bold; font-size: 18px;")
        preview_layout.addWidget(self.sku_label, 0, 1)

        preview_layout.addWidget(QLabel("Folder:"), 1, 0)
        self.folder_label = QLabel("—")
        self.folder_label.setStyleSheet("color: #a0a0a0; font-size: 14px;")
        self.folder_label.setWordWrap(True)
        preview_layout.addWidget(self.folder_label, 1, 1)

        layout.addWidget(preview_group)

        # Step 4: Photo Selection
        photo_group = QGroupBox("Step 4: Select Photos")
        photo_layout = QVBoxLayout(photo_group)

        # Source folder info
        source_layout = QHBoxLayout()
        source_label = QLabel("Source:")
        source_label.setStyleSheet("color: #a0a0a0;")
        source_layout.addWidget(source_label)

        # Default camera path
        camera_path = self._get_camera_path()
        self.source_path_label = QLabel(camera_path)
        self.source_path_label.setStyleSheet("color: #eaeaea;")
        source_layout.addWidget(self.source_path_label)
        source_layout.addStretch()

        self.change_source_btn = QPushButton("Browse Folder...")
        self.change_source_btn.setStyleSheet("""
            QPushButton {
                background-color: #16213e;
                border: 1px solid #2d3748;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #1f3460;
            }
        """)
        self.change_source_btn.clicked.connect(self.change_source_folder)
        source_layout.addWidget(self.change_source_btn)

        self.select_photos_btn = QPushButton("Select Photos...")
        self.select_photos_btn.setStyleSheet("""
            QPushButton {
                background-color: #16213e;
                border: 1px solid #2d3748;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #1f3460;
            }
        """)
        self.select_photos_btn.clicked.connect(self.select_individual_photos)
        source_layout.addWidget(self.select_photos_btn)

        photo_layout.addLayout(source_layout)

        # Selection buttons
        sel_layout = QHBoxLayout()

        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #16213e;
                border: 1px solid #2d3748;
                padding: 6px 12px;
            }
        """)
        self.select_all_btn.clicked.connect(self.select_all_photos)
        sel_layout.addWidget(self.select_all_btn)

        self.select_none_btn = QPushButton("Select None")
        self.select_none_btn.setStyleSheet("""
            QPushButton {
                background-color: #16213e;
                border: 1px solid #2d3748;
                padding: 6px 12px;
            }
        """)
        self.select_none_btn.clicked.connect(self.select_no_photos)
        sel_layout.addWidget(self.select_none_btn)

        sel_layout.addStretch()

        self.selected_count_label = QLabel("0 photos selected")
        self.selected_count_label.setStyleSheet("color: #a0a0a0;")
        sel_layout.addWidget(self.selected_count_label)

        photo_layout.addLayout(sel_layout)

        # Photo grid (scrollable) - larger for better visibility
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(400)  # Increased height for large icons
        scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #2d3748;
                border-radius: 6px;
                background-color: #0f0f1a;
            }
        """)

        self.photo_grid_widget = QWidget()
        self.photo_grid = QGridLayout(self.photo_grid_widget)
        self.photo_grid.setSpacing(12)  # More spacing for larger icons
        self.photo_grid.setContentsMargins(12, 12, 12, 12)
        scroll.setWidget(self.photo_grid_widget)

        photo_layout.addWidget(scroll)
        layout.addWidget(photo_group)

        # Bottom buttons
        btn_layout = QHBoxLayout()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #16213e;
                border: 1px solid #2d3748;
            }
            QPushButton:hover {
                background-color: #1f3460;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        btn_layout.addStretch()

        self.import_btn = QPushButton("📥 Import && Open")
        self.import_btn.setEnabled(False)
        self.import_btn.setMinimumWidth(150)
        self.import_btn.clicked.connect(self.do_import)
        btn_layout.addWidget(self.import_btn)

        layout.addLayout(btn_layout)

    def _get_camera_path(self) -> str:
        """Get camera import path from config with fallback."""
        path = self.config.get("paths", {}).get("camera_import", "E:\\DCIM\\100CANON")
        # Normalize to Windows format
        return path.replace("/", "\\")

    def on_category_selected(self, category_id: str):
        """Handle category button selection."""
        self.selected_category = category_id

        # Update button styles
        for cid, btn in self.category_buttons.items():
            btn.setChecked(cid == category_id)
            btn.update_style(cid == category_id)

        self.update_preview()

    def update_preview(self):
        """Update SKU and folder preview."""
        if not self.selected_category:
            self.sku_label.setText("—")
            self.folder_label.setText("Select a category first")
            self.validate_form()
            return

        # Get category info
        cat_info = self.config.get("categories", {}).get(self.selected_category, {})
        prefix = cat_info.get("prefix", self.selected_category[:4].upper())

        # Scan folders to find next SKU number
        next_num = self.get_next_sku_number(prefix)
        year = datetime.now().year

        self.generated_sku = f"{prefix}-{year}-{next_num:04d}"
        self.sku_label.setText(self.generated_sku)

        # Build folder path
        products_root = self.config.get("paths", {}).get("products_root", "G:/My Drive/Kollect-It/Products")
        cat_folder = self.config.get("paths", {}).get("category_folders", {}).get(
            self.selected_category, prefix
        )

        self.target_folder = Path(products_root) / cat_folder / self.generated_sku
        self.folder_label.setText(str(self.target_folder))

        self.validate_form()

    def get_next_sku_number(self, prefix: str) -> int:
        """Scan existing folders to determine next SKU number."""
        products_root = self.config.get("paths", {}).get("products_root", "G:/My Drive/Kollect-It/Products")
        cat_folder = self.config.get("paths", {}).get("category_folders", {}).get(
            self.selected_category, prefix
        )

        search_path = Path(products_root) / cat_folder

        if not search_path.exists():
            return 1

        year = datetime.now().year
        pattern = re.compile(rf"^{prefix}-{year}-(\d{{4}})$", re.IGNORECASE)

        max_num = 0

        try:
            for item in search_path.iterdir():
                if item.is_dir():
                    match = pattern.match(item.name)
                    if match:
                        num = int(match.group(1))
                        max_num = max(max_num, num)
        except Exception as e:
            print(f"Error scanning folders: {e}")

        return max_num + 1

    def load_photos(self, folder_path: str = None):
        """Load photos from camera folder."""
        # Clear existing thumbnails
        while self.photo_grid.count():
            item = self.photo_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.photo_thumbnails = []
        self.selected_photos = []

        # Use provided path or get from config
        if folder_path:
            camera_path = folder_path
        else:
            camera_path = self._get_camera_path()

        self.source_path_label.setText(camera_path)

        folder = Path(camera_path)

        # Debug output
        print(f"[ImportWizard] Loading photos from: {folder}")
        print(f"[ImportWizard] Folder exists: {folder.exists()}")

        # If folder doesn't exist, show message
        if not folder.exists():
            no_folder = QLabel(
                f"Camera folder not found:\n{camera_path}\n\n"
                f"Please use 'Browse Folder' or 'Select Photos' to choose a location."
            )
            no_folder.setAlignment(Qt.AlignCenter)
            no_folder.setStyleSheet("color: #fc8181; padding: 40px; font-size: 14px;")
            self.photo_grid.addWidget(no_folder, 0, 0)
            return

        # Find image files
        images = []

        try:
            for f in folder.iterdir():
                # Skip directories (like "processed" folder)
                if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS:
                    images.append(f)
                    
            print(f"[ImportWizard] Found {len(images)} images")
            
        except PermissionError as e:
            error_label = QLabel(
                f"Permission denied accessing folder:\n{camera_path}\n\n"
                f"Please check folder permissions or select a different location."
            )
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: #fc8181; padding: 40px; font-size: 14px;")
            self.photo_grid.addWidget(error_label, 0, 0)
            return
        except Exception as e:
            error_label = QLabel(f"Error reading folder:\n{str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: #fc8181; padding: 40px; font-size: 14px;")
            self.photo_grid.addWidget(error_label, 0, 0)
            return

        # Sort by modification time (newest first)
        images.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        if not images:
            no_photos = QLabel(
                f"No photos found in:\n{camera_path}\n\n"
                f"Supported formats: JPG, JPEG, PNG, WebP, TIFF, BMP, CR2, NEF, ARW\n\n"
                f"Use 'Browse Folder' to select a different folder,\n"
                f"or 'Select Photos' to choose individual files."
            )
            no_photos.setAlignment(Qt.AlignCenter)
            no_photos.setStyleSheet("color: #a0a0a0; padding: 40px; font-size: 14px;")
            self.photo_grid.addWidget(no_photos, 0, 0)
            return

        # Create thumbnails (grid: 4 columns for larger icons)
        cols = 4
        for i, img_path in enumerate(images):
            row = i // cols
            col = i % cols

            thumb = PhotoThumbnail(str(img_path))
            thumb.clicked.connect(self.on_photo_clicked)
            self.photo_thumbnails.append(thumb)
            self.photo_grid.addWidget(thumb, row, col)

        # Add stretch at bottom
        self.photo_grid.setRowStretch(len(images) // cols + 1, 1)

        self.update_selected_count()

    def change_source_folder(self):
        """Open dialog to change source folder."""
        # Get current path
        current = self._get_camera_path()

        # Ensure the path exists, if not use E:\ or home
        current_path = Path(current)
        if not current_path.exists():
            if Path("E:\\").exists():
                current = "E:\\"
            else:
                current = str(Path.home())

        # Use native dialog
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Select Camera/Source Folder",
            current
        )

        if folder:
            # Update config temporarily
            if "paths" not in self.config:
                self.config["paths"] = {}
            self.config["paths"]["camera_import"] = folder.replace("/", "\\")

            # Reload photos
            self.load_photos(folder)

    def select_individual_photos(self):
        """Open file dialog to select individual photos."""
        # Get default directory
        default_dir = self._get_camera_path()

        # Ensure the path exists
        default_path = Path(default_dir)
        if not default_path.exists():
            if Path("E:\\").exists():
                default_dir = "E:\\"
            else:
                default_dir = str(Path.home())

        # Open file dialog for multiple image selection
        file_filter = "Image Files (*.jpg *.jpeg *.png *.webp *.tiff *.tif *.bmp *.cr2 *.nef *.arw);;All Files (*.*)"
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Photos to Import",
            default_dir,
            file_filter
        )

        if files:
            # Clear existing thumbnails
            while self.photo_grid.count():
                item = self.photo_grid.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            self.photo_thumbnails = []
            self.selected_photos = []

            # Update source path label to show "Selected Files"
            if len(files) == 1:
                self.source_path_label.setText(f"Selected: {Path(files[0]).parent}")
            else:
                self.source_path_label.setText(f"Selected: {len(files)} files from {Path(files[0]).parent}")

            # Create thumbnails for selected files
            cols = 4
            for i, file_path in enumerate(files):
                row = i // cols
                col = i % cols

                thumb = PhotoThumbnail(file_path)
                thumb.clicked.connect(self.on_photo_clicked)
                # Auto-select all selected files
                thumb.set_selected(True)
                self.photo_thumbnails.append(thumb)
                self.photo_grid.addWidget(thumb, row, col)

            # Add stretch at bottom
            self.photo_grid.setRowStretch(len(files) // cols + 1, 1)

            self.update_selected_count()
            self.validate_form()

    def on_photo_clicked(self, file_path: str, selected: bool):
        """Handle photo selection change."""
        if selected and file_path not in self.selected_photos:
            self.selected_photos.append(file_path)
        elif not selected and file_path in self.selected_photos:
            self.selected_photos.remove(file_path)

        self.update_selected_count()
        self.validate_form()

    def select_all_photos(self):
        """Select all photos."""
        for thumb in self.photo_thumbnails:
            thumb.set_selected(True)

    def select_no_photos(self):
        """Deselect all photos."""
        for thumb in self.photo_thumbnails:
            thumb.set_selected(False)

    def update_selected_count(self):
        """Update selected count label."""
        count = len(self.selected_photos)
        self.selected_count_label.setText(f"{count} photo{'s' if count != 1 else ''} selected")

    def validate_form(self):
        """Check if form is valid for import."""
        valid = (
            self.selected_category is not None and
            len(self.description_edit.text().strip()) > 0 and
            len(self.selected_photos) > 0
        )
        self.import_btn.setEnabled(valid)

    def do_import(self):
        """Perform the import operation."""
        if not self.validate_import():
            return

        description = self.description_edit.text().strip()

        # Confirm
        confirm = QMessageBox.question(
            self, "Confirm Import",
            f"Import {len(self.selected_photos)} photos?\n\n"
            f"SKU: {self.generated_sku}\n"
            f"Title: {description}\n"
            f"Folder: {self.target_folder}\n\n"
            f"Photos will be archived to:\n"
            f"{self.config.get('paths', {}).get('archive_folder', 'Archived')}/{self.generated_sku}/",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if confirm != QMessageBox.Yes:
            return

        # Show progress
        progress = QProgressDialog("Importing photos...", "Cancel", 0, len(self.selected_photos) + 2, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle("Importing")
        progress.setStyleSheet("""
            QProgressDialog {
                background-color: #1a1a2e;
                color: #eaeaea;
            }
        """)
        progress.show()

        try:
            # Step 1: Create target folder
            progress.setLabelText("Creating product folder...")
            progress.setValue(1)
            QApplication.processEvents()

            self.target_folder.mkdir(parents=True, exist_ok=True)

            # Step 2: Create archive folder
            archive_folder = Path(self.config.get("paths", {}).get("archive_folder", "Archived")) / self.generated_sku
            archive_folder.mkdir(parents=True, exist_ok=True)

            # Step 3: Copy photos and archive originals
            copied_files = []

            for i, photo_path in enumerate(self.selected_photos):
                if progress.wasCanceled():
                    raise Exception("Import cancelled by user")

                progress.setLabelText(f"Copying {Path(photo_path).name}...")
                progress.setValue(i + 2)
                QApplication.processEvents()

                src = Path(photo_path)

                # Copy to target folder
                dst = self.target_folder / src.name
                shutil.copy2(src, dst)
                copied_files.append(dst)

                # Move original to archive
                archive_dst = archive_folder / src.name
                shutil.move(str(src), str(archive_dst))

            progress.setValue(len(self.selected_photos) + 2)

            # Save product metadata
            metadata = {
                "sku": self.generated_sku,
                "title": description,
                "category": self.selected_category,
                "created": datetime.now().isoformat(),
                "images": [f.name for f in copied_files],
                "archived_to": str(archive_folder)
            }

            metadata_file = self.target_folder / "product_info.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            progress.close()

            # Success message
            QMessageBox.information(
                self, "Import Complete",
                f"✅ Successfully imported {len(copied_files)} photos!\n\n"
                f"SKU: {self.generated_sku}\n"
                f"Location: {self.target_folder}\n\n"
                f"Originals archived to:\n{archive_folder}"
            )

            # Emit signal and close
            self.import_complete.emit(str(self.target_folder))
            self.accept()

        except Exception as e:
            progress.close()
            QMessageBox.critical(
                self, "Import Error",
                f"Failed to import photos:\n\n{str(e)}"
            )

    def validate_import(self) -> bool:
        """Validate all required fields before import."""
        if not self.selected_category:
            QMessageBox.warning(self, "Missing Category", "Please select a category.")
            return False

        if not self.description_edit.text().strip():
            QMessageBox.warning(self, "Missing Description", "Please enter a brief description.")
            return False

        if not self.selected_photos:
            QMessageBox.warning(self, "No Photos Selected", "Please select at least one photo.")
            return False

        if not self.generated_sku:
            QMessageBox.warning(self, "SKU Error", "Could not generate SKU. Please try again.")
            return False

        return True

    def get_imported_folder(self) -> Optional[str]:
        """Get the path to the imported product folder."""
        return str(self.target_folder) if self.target_folder else None

    def get_product_title(self) -> str:
        """Get the entered product title/description."""
        return self.description_edit.text().strip()

    def get_generated_sku(self) -> str:
        """Get the generated SKU."""
        return self.generated_sku or ""
