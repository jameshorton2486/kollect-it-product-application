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
    QFileDialog, QMessageBox, QMenu, QWidget, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QDragEnterEvent, QDropEvent

from .theme_modern import ModernPalette


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
        self.setMinimumHeight(180)
        self._setup_ui()

    def set_config(self, config: Dict[str, Any]) -> None:
        self.config = config

    def _setup_ui(self) -> None:
        self._apply_default_style()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel("📁")
        icon_label.setStyleSheet("font-size: 40px; border: none; background: transparent;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        main_text = QLabel("Drag & Drop Product Folder Here")
        main_text.setStyleSheet(f"""
            QLabel {{
                color: {ModernPalette.TEXT};
                font-size: 15px;
                font-weight: 600;
                border: none;
                background: transparent;
            }}
        """)
        main_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(main_text)

        sub_text = QLabel("or click Browse to select folder/files")
        sub_text.setStyleSheet(f"""
            QLabel {{
                color: {ModernPalette.TEXT_MUTED};
                font-size: 13px;
                border: none;
                background: transparent;
            }}
        """)
        sub_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(sub_text)

        layout.addSpacing(10)

        browse_layout = QHBoxLayout()
        browse_layout.setSpacing(12)

        self.browse_btn = QPushButton("Browse Folder")
        self.browse_btn.setFixedWidth(120)
        self.browse_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernPalette.BTN_SECONDARY_BG};
                color: {ModernPalette.TEXT};
                border: 1px solid {ModernPalette.BORDER};
                border-radius: 4px;
                padding: 8px 14px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {ModernPalette.BTN_SECONDARY_HOVER};
                border-color: {ModernPalette.PRIMARY};
            }}
        """)
        self.browse_btn.clicked.connect(self.browse_folder)
        browse_layout.addWidget(self.browse_btn)

        self.browse_files_btn = QPushButton("Browse Files")
        self.browse_files_btn.setFixedWidth(120)
        self.browse_files_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernPalette.BTN_SECONDARY_BG};
                color: {ModernPalette.TEXT};
                border: 1px solid {ModernPalette.BORDER};
                border-radius: 4px;
                padding: 8px 14px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {ModernPalette.BTN_SECONDARY_HOVER};
                border-color: {ModernPalette.PRIMARY};
            }}
        """)
        self.browse_files_btn.clicked.connect(self.browse_files)
        browse_layout.addWidget(self.browse_files_btn)

        browse_container = QWidget()
        browse_container.setStyleSheet("background: transparent; border: none;")
        browse_container.setLayout(browse_layout)
        layout.addWidget(browse_container, alignment=Qt.AlignCenter)

    def _apply_default_style(self) -> None:
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {ModernPalette.SURFACE};
                border: 2px dashed {ModernPalette.BORDER};
                border-radius: 8px;
            }}
            QFrame:hover {{
                border-color: {ModernPalette.PRIMARY};
            }}
        """)

    def _apply_drag_style(self) -> None:
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {ModernPalette.SURFACE_LIGHT};
                border: 2px dashed {ModernPalette.PRIMARY};
                border-radius: 8px;
            }}
        """)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._apply_drag_style()

    def dragLeaveEvent(self, event) -> None:
        self._apply_default_style()

    def dropEvent(self, event: QDropEvent) -> None:
        self._apply_default_style()
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.isdir(path):
                self.folder_dropped.emit(path)
            else:
                QMessageBox.warning(self, "Invalid Selection",
                    "Please drop a folder containing product images.")

    def _get_default_browse_path(self) -> str:
        if self.config:
            config_path = self.config.get("paths", {}).get("default_browse", "")
            if config_path and Path(config_path).exists():
                return config_path
            camera_path = self.config.get("paths", {}).get("camera_import", "")
            if camera_path and Path(camera_path).exists():
                return camera_path
        return str(Path.home())

    def browse_folder(self) -> None:
        default_path = self._get_default_browse_path()
        dialog = QFileDialog(self, "Select Product Folder", default_path)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, False)
        dialog.setViewMode(QFileDialog.Detail)
        dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.webp *.tiff *.bmp);;All Files (*)")
        if dialog.exec_() == QFileDialog.Accepted:
            folder = dialog.selectedFiles()[0]
            if folder:
                self.folder_dropped.emit(folder)

    def browse_files(self) -> None:
        default_path = ""
        if self.config:
            default_path = self.config.get("paths", {}).get("camera_import", "")
            if default_path:
                if not Path(default_path).exists():
                    default_path = ""
        if not default_path:
            default_path = str(Path.home())

        file_filter = (
            "Image Files (*.png *.jpg *.jpeg *.webp *.tiff *.bmp);;"
            "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;"
            "WebP Files (*.webp);;All Files (*.*)"
        )
        files, _ = QFileDialog.getOpenFileNames(self, "Select Image Files", default_path, file_filter)
        if files:
            temp_dir = tempfile.mkdtemp(prefix="kollect_files_")
            main_window = self.window()
            if hasattr(main_window, '_temp_dirs'):
                main_window._temp_dirs.append(temp_dir)
            for file_path in files:
                try:
                    file_name = Path(file_path).name
                    temp_file_path = Path(temp_dir) / file_name
                    # FIX: Wrap file copy in try/except for error handling
                    shutil.copy2(file_path, temp_file_path)
                except PermissionError as e:
                    print(f"[ERROR] Cannot copy {Path(file_path).name}: Permission denied - {e}")
                    continue
                except OSError as e:
                    print(f"[ERROR] Cannot copy {Path(file_path).name}: {e}")
                    continue
            self.folder_dropped.emit(temp_dir)


class ImageThumbnail(QLabel):
    """Clickable image thumbnail with multi-select support."""

    clicked = pyqtSignal(str)
    selected = pyqtSignal(str)
    ctrl_clicked = pyqtSignal(str)
    crop_requested = pyqtSignal(str)
    remove_bg_requested = pyqtSignal(str)
    delete_requested = pyqtSignal(str)

    def __init__(self, image_path: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.image_path = image_path
        self.is_selected = False
        self.setFixedSize(THUMBNAIL_SIZE, THUMBNAIL_SIZE)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)
        self._load_image()

    def set_selected(self, selected: bool) -> None:
        self.is_selected = selected
        self._update_style()

    def _update_style(self) -> None:
        border_color = ModernPalette.PRIMARY if self.is_selected else ModernPalette.BORDER
        border_width = "3px" if self.is_selected else "1px"
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {ModernPalette.SURFACE};
                border: {border_width} solid {border_color};
                border-radius: 6px;
                padding: 4px;
            }}
            QLabel:hover {{
                border-color: {ModernPalette.PRIMARY};
            }}
        """)

    def _load_image(self) -> None:
        pixmap = QPixmap(self.image_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled)
        self._update_style()

    def reload_image(self) -> None:
        self._load_image()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ControlModifier:
                self.ctrl_clicked.emit(self.image_path)
            else:
                self.clicked.emit(self.image_path)
                self.selected.emit(self.image_path)
        elif event.button() == Qt.RightButton:
            self._show_context_menu(event.pos())

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Delete:
            self.delete_requested.emit(self.image_path)
        else:
            super().keyPressEvent(event)

    def _show_context_menu(self, pos) -> None:
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {ModernPalette.SURFACE};
                border: 1px solid {ModernPalette.BORDER};
                border-radius: 4px;
                padding: 6px;
                font-size: 14px;
            }}
            QMenu::item {{
                padding: 8px 18px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {ModernPalette.PRIMARY};
                color: {ModernPalette.TEXT_DARK};
            }}
        """)
        crop_action = menu.addAction("✂️ Crop Image")
        bg_action = menu.addAction("🎨 Remove Background")
        menu.addSeparator()
        delete_action = menu.addAction("🗑️ Delete Image")
        menu.addSeparator()
        preview_action = menu.addAction("🔍 Preview Full Size")

        action = menu.exec_(self.mapToGlobal(pos))
        if action == crop_action:
            self.crop_requested.emit(self.image_path)
        elif action == bg_action:
            self.remove_bg_requested.emit(self.image_path)
        elif action == delete_action:
            self.delete_requested.emit(self.image_path)
        elif action == preview_action:
            self.clicked.emit(self.image_path)
