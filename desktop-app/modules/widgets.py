#!/usr/bin/env python3
"""
Custom Widgets Module
Reusable UI widgets for the Kollect-It Product Manager.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QMenu, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QDragEnterEvent, QDropEvent

from .theme_clean import DarkPalette


# Constants
THUMBNAIL_SIZE = 150


class DropZone(QFrame):
    """Custom drag-and-drop zone for product folders."""

    folder_dropped = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.config = config or {}
        self.browse_btn: Optional[QPushButton] = None
        self.browse_files_btn: Optional[QPushButton] = None
        self.setAcceptDrops(True)
        self.setMinimumHeight(200)
        self._setup_ui()

    def set_config(self, config: Dict[str, Any]) -> None:
        """Update the configuration."""
        self.config = config

    def _setup_ui(self) -> None:
        """Initialize the drop zone UI."""
        self._apply_default_style()

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
        self.browse_btn.setMaximumWidth(150)
        self.browse_btn.clicked.connect(self.browse_folder)
        browse_layout.addWidget(self.browse_btn)

        # Browse files button
        self.browse_files_btn = QPushButton("Browse Files")
        self.browse_files_btn.setMaximumWidth(150)
        self.browse_files_btn.clicked.connect(self.browse_files)
        browse_layout.addWidget(self.browse_files_btn)

        # Add browse buttons layout to main layout
        browse_container = QWidget()
        browse_container.setLayout(browse_layout)
        layout.addWidget(browse_container, alignment=Qt.AlignCenter)  # type: ignore

    def _apply_default_style(self) -> None:
        """Apply the default style to the drop zone."""
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

    def _apply_drag_style(self) -> None:
        """Apply the drag-over style to the drop zone."""
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {DarkPalette.SURFACE_LIGHT};
                border: 2px dashed {DarkPalette.PRIMARY};
                border-radius: 12px;
            }}
        """)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Handle drag enter events."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._apply_drag_style()

    def dragLeaveEvent(self, event) -> None:
        """Handle drag leave events."""
        self._apply_default_style()

    def dropEvent(self, event: QDropEvent) -> None:
        """Handle drop events."""
        self._apply_default_style()

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
        if self.config:
            config_path = self.config.get("paths", {}).get("default_browse", "")
            if config_path and Path(config_path).exists():
                return config_path
            camera_path = self.config.get("paths", {}).get("camera_import", "")
            if camera_path and Path(camera_path).exists():
                return camera_path
        return str(Path.home())

    def browse_folder(self) -> None:
        """Open folder selection dialog."""
        default_path = self._get_default_browse_path()

        # Use a custom file dialog to allow seeing files while selecting a folder
        dialog = QFileDialog(self, "Select Product Folder", default_path)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, False)  # Allow seeing files
        dialog.setViewMode(QFileDialog.Detail)
        dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.webp *.tiff *.bmp);;All Files (*)")

        if dialog.exec_() == QFileDialog.Accepted:
            folder = dialog.selectedFiles()[0]
            if folder:
                self.folder_dropped.emit(folder)

    def browse_files(self) -> None:
        """Open file selection dialog for individual images."""
        default_path = ""

        # Get path from config
        if self.config:
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
        file_filter = (
            "Image Files (*.png *.jpg *.jpeg *.webp *.tiff *.bmp);;"
            "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;"
            "WebP Files (*.webp);;All Files (*.*)"
        )

        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Image Files",
            default_path, file_filter
        )
        if files:
            # Create a temporary folder structure for individual files
            temp_dir = tempfile.mkdtemp(prefix="kollect_files_")

            # Track temp dir in the main window application
            main_window = self.window()
            if hasattr(main_window, '_temp_dirs'):
                main_window._temp_dirs.append(temp_dir)

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
    crop_requested = pyqtSignal(str)
    remove_bg_requested = pyqtSignal(str)

    def __init__(self, image_path: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.image_path = image_path
        self.is_selected = False
        self.setFixedSize(THUMBNAIL_SIZE, THUMBNAIL_SIZE)
        self.setCursor(Qt.PointingHandCursor)  # type: ignore
        self._load_image()

    def set_selected(self, selected: bool) -> None:
        """Set the selected state and update style."""
        self.is_selected = selected
        self._update_style()

    def _update_style(self) -> None:
        """Update the stylesheet based on selection state."""
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

    def _load_image(self) -> None:
        """Load and display the image thumbnail."""
        pixmap = QPixmap(self.image_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatio,  # type: ignore
                Qt.SmoothTransformation  # type: ignore
            )
            self.setPixmap(scaled)
        self._update_style()

    def reload_image(self) -> None:
        """Reload the image (e.g., after editing)."""
        self._load_image()

    def mousePressEvent(self, event) -> None:
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:  # type: ignore
            self.clicked.emit(self.image_path)
        elif event.button() == Qt.RightButton:  # type: ignore
            self._show_context_menu(event.pos())

    def _show_context_menu(self, pos) -> None:
        """Show the right-click context menu."""
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
