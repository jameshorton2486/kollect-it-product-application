# Cursor AI Prompt: Add "New Product Import Wizard" Feature

## Feature Overview

Add a complete **"Add New Product"** workflow to the Kollect-It Product Application that:

1. Opens an import wizard dialog
2. Lets user select category (MILI/COLL/BOOK/ART)
3. Enter a brief product description (becomes initial title)
4. Scans existing folders to determine next SKU number
5. Shows photo thumbnails from camera folder for selection
6. Creates product folder in Google Drive with SKU name
7. Copies selected photos to the new folder
8. Archives originals to E:\MISC\{SKU}\
9. Opens the product in the main editor for processing

---

## FILE 1: Update Config

**File:** `desktop-app/config/config.example.json`

**Add these new paths** to the `paths` section:

```json
"paths": {
  "camera_import": "E:/DCIM/100CANON",
  "archive_folder": "E:/MISC",
  "products_root": "G:/My Drive/Kollect-It/Products",
  "default_browse": "G:/My Drive/Kollect-It/Products",
  "category_folders": {
    "militaria": "MILI",
    "collectibles": "COLL",
    "books": "BOOK",
    "fineart": "ART"
  },
  "watch_folder": "G:/My Drive/Kollect-It/New Products",
  "processed": "./processed",
  "completed": "G:/My Drive/Kollect-It/Completed",
  "failed": "G:/My Drive/Kollect-It/Failed",
  "temp": "./temp",
  "logs": "./logs"
}
```

---

## FILE 2: Create Import Wizard Module

**Create new file:** `desktop-app/modules/import_wizard.py`

```python
#!/usr/bin/env python3
"""
Import Wizard Module
Handles importing photos from camera to product folders with SKU generation.
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Tuple

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QGridLayout, QScrollArea, QWidget, QCheckBox,
    QFrame, QMessageBox, QProgressDialog, QApplication,
    QButtonGroup, QSizePolicy, QGroupBox
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QFont, QIcon

from PIL import Image


class CategoryButton(QPushButton):
    """Custom styled button for category selection."""
    
    def __init__(self, category_id: str, display_name: str, prefix: str, parent=None):
        super().__init__(parent)
        self.category_id = category_id
        self.prefix = prefix
        
        self.setText(f"{prefix}\n{display_name}")
        self.setCheckable(True)
        self.setMinimumSize(120, 80)
        self.setFont(QFont("Segoe UI", 11, QFont.Bold))
        
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
        
        self.setFixedSize(130, 150)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        
        # Thumbnail image
        self.image_label = QLabel()
        self.image_label.setFixedSize(120, 100)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #0f0f1a;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.image_label)
        
        # Filename label
        filename = Path(file_path).name
        if len(filename) > 15:
            filename = filename[:12] + "..."
        self.name_label = QLabel(filename)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("color: #a0a0a0; font-size: 10px;")
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
        """Load and display thumbnail."""
        try:
            with Image.open(self.file_path) as img:
                # Convert to RGB if needed
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Create thumbnail
                img.thumbnail((120, 100), Image.Resampling.LANCZOS)
                
                # Convert to QPixmap
                data = img.tobytes("raw", "RGB")
                qimg = QImage(data, img.width, img.height, img.width * 3, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimg)
                
                self.image_label.setPixmap(pixmap)
        except Exception as e:
            self.image_label.setText("Error")
            print(f"Error loading thumbnail: {e}")
    
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
                font-size: 14px;
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
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
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
        self.sku_label.setStyleSheet("color: #48bb78; font-weight: bold; font-size: 16px;")
        preview_layout.addWidget(self.sku_label, 0, 1)
        
        preview_layout.addWidget(QLabel("Folder:"), 1, 0)
        self.folder_label = QLabel("—")
        self.folder_label.setStyleSheet("color: #a0a0a0; font-size: 12px;")
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
        
        camera_path = self.config.get("paths", {}).get("camera_import", "E:/DCIM/100CANON")
        self.source_path_label = QLabel(camera_path)
        self.source_path_label.setStyleSheet("color: #eaeaea;")
        source_layout.addWidget(self.source_path_label)
        source_layout.addStretch()
        
        self.change_source_btn = QPushButton("Change Folder")
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
        
        # Photo grid (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(200)
        scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #2d3748;
                border-radius: 6px;
                background-color: #0f0f1a;
            }
        """)
        
        self.photo_grid_widget = QWidget()
        self.photo_grid = QGridLayout(self.photo_grid_widget)
        self.photo_grid.setSpacing(8)
        self.photo_grid.setContentsMargins(8, 8, 8, 8)
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
        """
        Scan existing folders to determine next SKU number.
        
        Scans: G:/My Drive/Kollect-It/Products/{PREFIX}/
        Finds highest: PREFIX-YYYY-NNNN
        Returns: NNNN + 1
        """
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
    
    def load_photos(self):
        """Load photos from camera folder."""
        # Clear existing thumbnails
        while self.photo_grid.count():
            item = self.photo_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.photo_thumbnails = []
        self.selected_photos = []
        
        camera_path = self.config.get("paths", {}).get("camera_import", "E:/DCIM/100CANON")
        self.source_path_label.setText(camera_path)
        
        folder = Path(camera_path)
        
        if not folder.exists():
            no_folder = QLabel(f"Camera folder not found:\n{camera_path}")
            no_folder.setAlignment(Qt.AlignCenter)
            no_folder.setStyleSheet("color: #fc8181; padding: 40px;")
            self.photo_grid.addWidget(no_folder, 0, 0)
            return
        
        # Find image files
        extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.cr2', '.nef', '.arw'}
        images = []
        
        try:
            for f in folder.iterdir():
                if f.suffix.lower() in extensions:
                    images.append(f)
        except Exception as e:
            print(f"Error reading folder: {e}")
        
        # Sort by modification time (newest first)
        images.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not images:
            no_photos = QLabel("No photos found in camera folder")
            no_photos.setAlignment(Qt.AlignCenter)
            no_photos.setStyleSheet("color: #a0a0a0; padding: 40px;")
            self.photo_grid.addWidget(no_photos, 0, 0)
            return
        
        # Create thumbnails (grid: 5 columns)
        cols = 5
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
        from PyQt5.QtWidgets import QFileDialog
        
        current = self.config.get("paths", {}).get("camera_import", "E:/DCIM/100CANON")
        
        folder = QFileDialog.getExistingDirectory(
            self, "Select Camera/Source Folder",
            current, QFileDialog.ShowDirsOnly
        )
        
        if folder:
            # Update config temporarily
            if "paths" not in self.config:
                self.config["paths"] = {}
            self.config["paths"]["camera_import"] = folder
            
            # Reload photos
            self.load_photos()
    
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
            f"E:/MISC/{self.generated_sku}/",
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
            archive_folder = Path(self.config.get("paths", {}).get("archive_folder", "E:/MISC")) / self.generated_sku
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
            import json
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
```

---

## FILE 3: Integrate Import Wizard into Main Application

**File:** `desktop-app/main.py`

### 3A: Add Import at Top of File

After the existing imports, add:

```python
from modules.import_wizard import ImportWizard
```

### 3B: Add Menu Item

Find the `setup_menu` method and add a new menu item. Look for where the File menu is created and add:

```python
def setup_menu(self):
    """Set up the menu bar."""
    menubar = self.menuBar()
    
    # File Menu
    file_menu = menubar.addMenu("&File")
    
    # ADD THIS: New Product action (at the top of File menu)
    new_product_action = QAction("📦 &New Product...", self)
    new_product_action.setShortcut("Ctrl+N")
    new_product_action.setStatusTip("Import photos and create a new product")
    new_product_action.triggered.connect(self.open_import_wizard)
    file_menu.addAction(new_product_action)
    
    file_menu.addSeparator()
    
    # ... rest of existing menu items ...
```

### 3C: Add Toolbar Button

Find the `setup_toolbar` method and add:

```python
def setup_toolbar(self):
    """Set up the toolbar."""
    toolbar = QToolBar("Main Toolbar")
    toolbar.setMovable(False)
    toolbar.setIconSize(QSize(24, 24))
    self.addToolBar(toolbar)
    
    # ADD THIS: New Product button (at the start)
    new_product_action = QAction("📦 New Product", self)
    new_product_action.setStatusTip("Import photos and create a new product")
    new_product_action.triggered.connect(self.open_import_wizard)
    toolbar.addAction(new_product_action)
    
    toolbar.addSeparator()
    
    # ... rest of existing toolbar items ...
```

### 3D: Add the Import Wizard Method

Add this new method to the `KollectItApp` class:

```python
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
                import json
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
```

### 3E: Add "New Product" Button to Drop Zone (Optional but Recommended)

Find the `DropZone` class and modify its `paintEvent` or add a button. Alternatively, add a prominent button in the main UI. In the `setup_ui` method of `KollectItApp`, after creating the drop zone:

```python
# Drop zone
self.drop_zone = DropZone()
self.drop_zone.folder_dropped.connect(self.on_folder_dropped)
left_layout.addWidget(self.drop_zone)

# ADD THIS: New Product button below drop zone
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
```

---

## FILE 4: Update Existing Paths in Config

**File:** `desktop-app/config/config.example.json`

The complete `paths` section should now be:

```json
"paths": {
  "camera_import": "E:/DCIM/100CANON",
  "archive_folder": "E:/MISC",
  "products_root": "G:/My Drive/Kollect-It/Products",
  "default_browse": "G:/My Drive/Kollect-It/Products",
  "category_folders": {
    "militaria": "MILI",
    "collectibles": "COLL",
    "books": "BOOK",
    "fineart": "ART"
  },
  "watch_folder": "G:/My Drive/Kollect-It/New Products",
  "processed": "./processed",
  "completed": "G:/My Drive/Kollect-It/Completed",
  "failed": "G:/My Drive/Kollect-It/Failed",
  "temp": "./temp",
  "logs": "./logs"
}
```

---

## Summary of Changes

| File | Change |
|------|--------|
| `config/config.example.json` | Added `camera_import`, `archive_folder`, `products_root`, `category_folders` |
| `modules/import_wizard.py` | **NEW FILE** - Complete import wizard dialog |
| `main.py` | Added import, menu item, toolbar button, new product button, handler methods |

---

## Testing Checklist

After implementing:

1. **Menu Access:**
   - [ ] File → New Product... opens wizard
   - [ ] Ctrl+N keyboard shortcut works

2. **Toolbar:**
   - [ ] "New Product" button visible in toolbar
   - [ ] Button opens wizard

3. **Import Wizard:**
   - [ ] Category buttons work (only one selected at a time)
   - [ ] Description field accepts input
   - [ ] SKU preview updates when category selected
   - [ ] Photos load from camera folder
   - [ ] Photo selection works (click and checkbox)
   - [ ] Select All / Select None buttons work
   - [ ] Change Folder button works
   - [ ] Import button disabled until form valid

4. **Import Process:**
   - [ ] Creates folder: `G:/My Drive/Kollect-It/Products/{CAT}/{SKU}/`
   - [ ] Copies photos to new folder
   - [ ] Creates archive folder: `E:/MISC/{SKU}/`
   - [ ] Moves originals to archive folder
   - [ ] Creates `product_info.json` with metadata
   - [ ] Opens product in main editor after import

5. **SKU Generation:**
   - [ ] Scans existing folders correctly
   - [ ] Increments from highest found number
   - [ ] Works when folder is empty (starts at 0001)
   - [ ] Handles year correctly

---

## Folder Structure After Import

```
G:\My Drive\Kollect-It\Products\
├── MILI\
│   └── MILI-2025-0001\
│       ├── IMG_4401.JPG
│       ├── IMG_4402.JPG
│       └── product_info.json
├── COLL\
│   └── COLL-2025-0047\
│       ├── IMG_4521.JPG
│       ├── IMG_4522.JPG
│       ├── IMG_4523.JPG
│       └── product_info.json
├── BOOK\
└── ART\

E:\MISC\
├── MILI-2025-0001\
│   ├── IMG_4401.JPG
│   └── IMG_4402.JPG
└── COLL-2025-0047\
    ├── IMG_4521.JPG
    ├── IMG_4522.JPG
    └── IMG_4523.JPG
```

---

*Prompt created: December 12, 2025*
*Feature: Add New Product Import Wizard*
