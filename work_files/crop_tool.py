#!/usr/bin/env python3
"""
Improved Crop Tool Module
Interactive image cropping dialog with:
- Full original image display (no auto-scaling that cuts the image)
- Visible crop frame with 4 independent edge handles from the start
- Restore to original functionality
"""

import shutil
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QComboBox, QWidget, QSizePolicy,
    QScrollArea, QCheckBox, QGroupBox, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt, QRect, QPoint, QSize, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QBrush, QCursor

from PIL import Image


class CropOverlay(QWidget):
    """
    Transparent overlay widget for crop selection with visible handles.
    Displays a crop frame with 4 independent draggable edges.
    """
    
    crop_changed = pyqtSignal(QRect)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        
        # Crop rectangle (in widget coordinates)
        self.crop_rect = QRect()
        
        # Handle properties
        self.handle_size = 12  # Size of corner handles
        self.edge_thickness = 6  # Thickness of edge hit area
        
        # Dragging state
        self.dragging = None  # "top", "bottom", "left", "right", "top_left", etc., or "move"
        self.drag_start = QPoint()
        self.rect_at_drag_start = QRect()
        
        # Aspect ratio constraint
        self.aspect_ratio = None
        
        # Visual settings
        self.show_grid = True
        self.grid_type = "rule_of_thirds"
        
        # Colors
        self.overlay_color = QColor(0, 0, 0, 150)  # Semi-transparent black for outside crop
        self.handle_color = QColor(255, 255, 255)  # White handles
        self.border_color = QColor(233, 69, 96)  # Primary accent color
        self.grid_color = QColor(255, 255, 255, 100)  # Semi-transparent white grid
    
    def set_initial_crop(self, rect: QRect):
        """Set the initial crop rectangle (usually full image bounds)."""
        self.crop_rect = rect.normalized()
        self.update()
        self.crop_changed.emit(self.crop_rect)
    
    def set_aspect_ratio(self, aspect: Optional[Tuple[int, int]]):
        """Set aspect ratio constraint."""
        self.aspect_ratio = aspect
    
    def reset_to_full(self, bounds: QRect):
        """Reset crop to full image bounds."""
        self.crop_rect = bounds.normalized()
        self.update()
        self.crop_changed.emit(self.crop_rect)
    
    def paintEvent(self, event):
        """Paint the crop overlay with handles and grid."""
        if not self.crop_rect.isValid():
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        widget_rect = self.rect()
        crop = self.crop_rect
        
        # Draw semi-transparent overlay outside crop area
        painter.setBrush(QBrush(self.overlay_color))
        painter.setPen(Qt.NoPen)
        
        # Top region
        painter.drawRect(0, 0, widget_rect.width(), crop.top())
        # Bottom region
        painter.drawRect(0, crop.bottom(), widget_rect.width(), widget_rect.height() - crop.bottom())
        # Left region (between top and bottom overlays)
        painter.drawRect(0, crop.top(), crop.left(), crop.height())
        # Right region (between top and bottom overlays)
        painter.drawRect(crop.right(), crop.top(), widget_rect.width() - crop.right(), crop.height())
        
        # Draw crop border
        painter.setPen(QPen(self.border_color, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(crop)
        
        # Draw grid if enabled
        if self.show_grid:
            painter.setPen(QPen(self.grid_color, 1, Qt.DashLine))
            
            if self.grid_type == "rule_of_thirds":
                third_w = crop.width() // 3
                third_h = crop.height() // 3
                
                for i in range(1, 3):
                    x = crop.x() + third_w * i
                    y = crop.y() + third_h * i
                    painter.drawLine(x, crop.top(), x, crop.bottom())
                    painter.drawLine(crop.left(), y, crop.right(), y)
            else:
                fifth_w = crop.width() // 5
                fifth_h = crop.height() // 5
                
                for i in range(1, 5):
                    x = crop.x() + fifth_w * i
                    y = crop.y() + fifth_h * i
                    painter.drawLine(x, crop.top(), x, crop.bottom())
                    painter.drawLine(crop.left(), y, crop.right(), y)
        
        # Draw edge handles (lines on each edge)
        painter.setPen(QPen(self.handle_color, 3))
        edge_len = 40  # Length of edge handle indicator
        
        # Top edge handle (center)
        mid_x = crop.x() + crop.width() // 2
        painter.drawLine(mid_x - edge_len // 2, crop.top(), mid_x + edge_len // 2, crop.top())
        
        # Bottom edge handle (center)
        painter.drawLine(mid_x - edge_len // 2, crop.bottom(), mid_x + edge_len // 2, crop.bottom())
        
        # Left edge handle (center)
        mid_y = crop.y() + crop.height() // 2
        painter.drawLine(crop.left(), mid_y - edge_len // 2, crop.left(), mid_y + edge_len // 2)
        
        # Right edge handle (center)
        painter.drawLine(crop.right(), mid_y - edge_len // 2, crop.right(), mid_y + edge_len // 2)
        
        # Draw corner handles (small squares)
        painter.setBrush(QBrush(self.handle_color))
        painter.setPen(QPen(self.border_color, 1))
        hs = self.handle_size
        
        # Top-left
        painter.drawRect(crop.left() - hs // 2, crop.top() - hs // 2, hs, hs)
        # Top-right
        painter.drawRect(crop.right() - hs // 2, crop.top() - hs // 2, hs, hs)
        # Bottom-left
        painter.drawRect(crop.left() - hs // 2, crop.bottom() - hs // 2, hs, hs)
        # Bottom-right
        painter.drawRect(crop.right() - hs // 2, crop.bottom() - hs // 2, hs, hs)
        
        painter.end()
    
    def _get_handle_at(self, pos: QPoint) -> Optional[str]:
        """Determine which handle (if any) is at the given position."""
        if not self.crop_rect.isValid():
            return None
        
        r = self.crop_rect
        x, y = pos.x(), pos.y()
        hs = self.handle_size
        et = self.edge_thickness
        
        # Check corners first (they take priority)
        if abs(x - r.left()) < hs and abs(y - r.top()) < hs:
            return "top_left"
        if abs(x - r.right()) < hs and abs(y - r.top()) < hs:
            return "top_right"
        if abs(x - r.left()) < hs and abs(y - r.bottom()) < hs:
            return "bottom_left"
        if abs(x - r.right()) < hs and abs(y - r.bottom()) < hs:
            return "bottom_right"
        
        # Check edges
        if abs(y - r.top()) < et and r.left() < x < r.right():
            return "top"
        if abs(y - r.bottom()) < et and r.left() < x < r.right():
            return "bottom"
        if abs(x - r.left()) < et and r.top() < y < r.bottom():
            return "left"
        if abs(x - r.right()) < et and r.top() < y < r.bottom():
            return "right"
        
        # Check if inside crop area (for moving)
        if r.contains(pos):
            return "move"
        
        return None
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            handle = self._get_handle_at(event.pos())
            if handle:
                self.dragging = handle
                self.drag_start = event.pos()
                self.rect_at_drag_start = QRect(self.crop_rect)
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            self._handle_drag(event.pos())
        else:
            # Update cursor based on position
            handle = self._get_handle_at(event.pos())
            if handle in ["left", "right"]:
                self.setCursor(Qt.SizeHorCursor)
            elif handle in ["top", "bottom"]:
                self.setCursor(Qt.SizeVerCursor)
            elif handle in ["top_left", "bottom_right"]:
                self.setCursor(Qt.SizeFDiagCursor)
            elif handle in ["top_right", "bottom_left"]:
                self.setCursor(Qt.SizeBDiagCursor)
            elif handle == "move":
                self.setCursor(Qt.SizeAllCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = None
            self.crop_changed.emit(self.crop_rect)
    
    def _handle_drag(self, pos: QPoint):
        """Handle dragging of edges/corners."""
        r = self.rect_at_drag_start
        delta = pos - self.drag_start
        
        new_left = r.left()
        new_top = r.top()
        new_right = r.right()
        new_bottom = r.bottom()
        
        min_size = 50  # Minimum crop size
        
        if self.dragging == "move":
            # Move the entire rectangle
            new_rect = r.translated(delta)
            # Constrain to widget bounds
            if new_rect.left() < 0:
                new_rect.moveLeft(0)
            if new_rect.top() < 0:
                new_rect.moveTop(0)
            if new_rect.right() > self.width():
                new_rect.moveRight(self.width())
            if new_rect.bottom() > self.height():
                new_rect.moveBottom(self.height())
            self.crop_rect = new_rect
        else:
            # Resize based on which handle is being dragged
            if "left" in self.dragging:
                new_left = min(r.left() + delta.x(), new_right - min_size)
                new_left = max(0, new_left)
            if "right" in self.dragging:
                new_right = max(r.right() + delta.x(), new_left + min_size)
                new_right = min(self.width(), new_right)
            if "top" in self.dragging:
                new_top = min(r.top() + delta.y(), new_bottom - min_size)
                new_top = max(0, new_top)
            if "bottom" in self.dragging:
                new_bottom = max(r.bottom() + delta.y(), new_top + min_size)
                new_bottom = min(self.height(), new_bottom)
            
            self.crop_rect = QRect(
                QPoint(int(new_left), int(new_top)),
                QPoint(int(new_right), int(new_bottom))
            ).normalized()
        
        self.update()
        self.crop_changed.emit(self.crop_rect)


class ImageLabel(QLabel):
    """Simple label for displaying the image."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scale_factor = 1.0
        self.original_pixmap = None
    
    def set_image(self, pixmap: QPixmap, scale: float = 1.0):
        """Set the image with optional scaling."""
        self.original_pixmap = pixmap
        self.scale_factor = scale
        
        if scale != 1.0:
            scaled = pixmap.scaled(
                int(pixmap.width() * scale),
                int(pixmap.height() * scale),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.setPixmap(scaled)
            self.setFixedSize(scaled.size())
        else:
            self.setPixmap(pixmap)
            self.setFixedSize(pixmap.size())


class CropDialog(QDialog):
    """
    Improved image cropping dialog with:
    - Full original image display
    - Visible crop frame with draggable edges from the start
    - Restore to original functionality
    """
    
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = Path(image_path)
        self.original_image = None
        self.current_rotation = 0
        self.output_path = None
        self.backup_path = None
        
        self.setWindowTitle(f"Crop Image - {self.image_path.name}")
        self.setMinimumSize(1000, 800)
        
        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
                color: #ffffff;
            }
            QGroupBox {
                background-color: #1a1a2e;
                border: 1px solid #3d3d5c;
                border-radius: 8px;
                margin-top: 12px;
                padding: 12px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #e94560;
            }
            QPushButton {
                background-color: #e94560;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c73e54;
            }
            QPushButton:disabled {
                background-color: #3d3d5c;
                color: #6b6b8a;
            }
            QComboBox {
                background-color: #1a1a2e;
                border: 2px solid #3d3d5c;
                border-radius: 6px;
                padding: 6px 12px;
                color: white;
            }
            QCheckBox {
                color: white;
            }
            QLabel {
                color: white;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: #1a1a2e;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                width: 18px;
                height: 18px;
                margin: -5px 0;
                background: #e94560;
                border-radius: 9px;
            }
            QScrollArea {
                background-color: #0f0f1a;
                border: 2px solid #3d3d5c;
                border-radius: 8px;
            }
        """)
        
        self.setup_ui()
        self.load_image()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Toolbar area
        toolbar = QHBoxLayout()
        
        # Rotation controls
        rotate_group = QGroupBox("Rotation")
        rotate_layout = QHBoxLayout(rotate_group)
        
        self.rotate_left_btn = QPushButton("↶ 90°")
        self.rotate_left_btn.clicked.connect(lambda: self.rotate(-90))
        rotate_layout.addWidget(self.rotate_left_btn)
        
        self.rotate_right_btn = QPushButton("↷ 90°")
        self.rotate_right_btn.clicked.connect(lambda: self.rotate(90))
        rotate_layout.addWidget(self.rotate_right_btn)
        
        self.flip_h_btn = QPushButton("⇆ Flip H")
        self.flip_h_btn.clicked.connect(lambda: self.flip("horizontal"))
        rotate_layout.addWidget(self.flip_h_btn)
        
        self.flip_v_btn = QPushButton("⇅ Flip V")
        self.flip_v_btn.clicked.connect(lambda: self.flip("vertical"))
        rotate_layout.addWidget(self.flip_v_btn)
        
        toolbar.addWidget(rotate_group)
        
        # Aspect ratio controls
        aspect_group = QGroupBox("Aspect Ratio")
        aspect_layout = QHBoxLayout(aspect_group)
        
        self.aspect_combo = QComboBox()
        self.aspect_combo.addItems([
            "Free",
            "1:1 Square",
            "4:3",
            "3:4",
            "16:9",
            "9:16",
            "3:2",
            "2:3"
        ])
        self.aspect_combo.currentIndexChanged.connect(self.on_aspect_changed)
        aspect_layout.addWidget(self.aspect_combo)
        
        toolbar.addWidget(aspect_group)
        
        # Grid controls
        grid_group = QGroupBox("Grid Overlay")
        grid_layout = QHBoxLayout(grid_group)
        
        self.grid_check = QCheckBox("Show Grid")
        self.grid_check.setChecked(True)
        self.grid_check.stateChanged.connect(self.toggle_grid)
        grid_layout.addWidget(self.grid_check)
        
        self.grid_combo = QComboBox()
        self.grid_combo.addItems(["Rule of Thirds", "Grid 5x5"])
        self.grid_combo.currentIndexChanged.connect(self.change_grid_type)
        grid_layout.addWidget(self.grid_combo)
        
        toolbar.addWidget(grid_group)
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # Image area with scroll and overlay
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        
        # Container for image and overlay
        self.image_container = QWidget()
        container_layout = QVBoxLayout(self.image_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Image label
        self.image_label = ImageLabel()
        
        # Crop overlay (positioned on top of image)
        self.crop_overlay = CropOverlay(self.image_label)
        self.crop_overlay.crop_changed.connect(self.on_crop_changed)
        
        self.scroll_area.setWidget(self.image_label)
        layout.addWidget(self.scroll_area, stretch=1)
        
        # Zoom controls
        zoom_layout = QHBoxLayout()
        
        zoom_layout.addWidget(QLabel("Zoom:"))
        
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(25, 200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        zoom_layout.addWidget(self.zoom_slider)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setMinimumWidth(50)
        zoom_layout.addWidget(self.zoom_label)
        
        self.fit_btn = QPushButton("Fit to Window")
        self.fit_btn.clicked.connect(self.fit_to_window)
        zoom_layout.addWidget(self.fit_btn)
        
        self.actual_btn = QPushButton("100%")
        self.actual_btn.clicked.connect(self.show_actual_size)
        zoom_layout.addWidget(self.actual_btn)
        
        self.reset_crop_btn = QPushButton("Reset Crop")
        self.reset_crop_btn.clicked.connect(self.reset_crop_to_full)
        self.reset_crop_btn.setStyleSheet("""
            QPushButton {
                background-color: #0f3460;
            }
            QPushButton:hover {
                background-color: #1f4470;
            }
        """)
        zoom_layout.addWidget(self.reset_crop_btn)
        
        layout.addLayout(zoom_layout)
        
        # Info area
        info_layout = QHBoxLayout()
        
        self.size_label = QLabel("Original: -- x --")
        info_layout.addWidget(self.size_label)
        
        self.crop_size_label = QLabel("Crop: -- x --")
        info_layout.addWidget(self.crop_size_label)
        
        info_layout.addStretch()
        
        layout.addLayout(info_layout)
        
        # Dialog buttons
        btn_layout = QHBoxLayout()
        
        self.restore_btn = QPushButton("🔄 Restore Original")
        self.restore_btn.clicked.connect(self.restore_original)
        self.restore_btn.setStyleSheet("""
            QPushButton {
                background-color: #48bb78;
            }
            QPushButton:hover {
                background-color: #38a169;
            }
        """)
        self.restore_btn.setEnabled(False)  # Enabled only if backup exists
        btn_layout.addWidget(self.restore_btn)
        
        btn_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d5c;
            }
            QPushButton:hover {
                background-color: #4d4d6c;
            }
        """)
        btn_layout.addWidget(self.cancel_btn)
        
        self.apply_btn = QPushButton("Apply Crop")
        self.apply_btn.clicked.connect(self.apply_crop)
        btn_layout.addWidget(self.apply_btn)
        
        layout.addLayout(btn_layout)
    
    def load_image(self):
        """Load the image for editing."""
        self.original_image = Image.open(self.image_path)
        
        # Check for existing backup
        self.backup_path = self.image_path.parent / ".originals" / f"{self.image_path.stem}_original{self.image_path.suffix}"
        self.restore_btn.setEnabled(self.backup_path.exists())
        
        w, h = self.original_image.size
        self.size_label.setText(f"Original: {w} x {h}")
        
        # Display at 100% initially (full size)
        self.update_display()
        
        # Initialize crop overlay to full image
        QTimer.singleShot(100, self.init_crop_overlay)
    
    def init_crop_overlay(self):
        """Initialize crop overlay after image is displayed."""
        if self.image_label.pixmap():
            size = self.image_label.pixmap().size()
            self.crop_overlay.setGeometry(0, 0, size.width(), size.height())
            self.crop_overlay.set_initial_crop(QRect(0, 0, size.width(), size.height()))
            self.crop_overlay.show()
    
    def update_display(self):
        """Update the displayed image."""
        if not self.original_image:
            return
        
        # Apply rotation
        img = self.original_image
        if self.current_rotation != 0:
            img = img.rotate(-self.current_rotation, expand=True)
        
        # Convert to QPixmap
        if img.mode == "RGBA":
            qim = QImage(
                img.tobytes("raw", "RGBA"),
                img.width, img.height,
                QImage.Format_RGBA8888
            )
        else:
            img_rgb = img.convert("RGB")
            qim = QImage(
                img_rgb.tobytes("raw", "RGB"),
                img_rgb.width, img_rgb.height,
                QImage.Format_RGB888
            )
        
        pixmap = QPixmap.fromImage(qim)
        
        # Apply zoom
        zoom = self.zoom_slider.value() / 100
        self.image_label.set_image(pixmap, zoom)
        
        # Update crop overlay size
        if self.image_label.pixmap():
            size = self.image_label.pixmap().size()
            self.crop_overlay.setGeometry(0, 0, size.width(), size.height())
            
            # Scale crop rect if zoom changed
            if self.crop_overlay.crop_rect.isValid():
                # Keep proportional crop
                pass
            else:
                self.crop_overlay.set_initial_crop(QRect(0, 0, size.width(), size.height()))
    
    def on_crop_changed(self, rect: QRect):
        """Handle crop rectangle changes."""
        if not rect.isValid():
            self.crop_size_label.setText("Crop: -- x --")
            return
        
        # Convert to original image coordinates
        zoom = self.zoom_slider.value() / 100
        orig_w = int(rect.width() / zoom)
        orig_h = int(rect.height() / zoom)
        self.crop_size_label.setText(f"Crop: {orig_w} x {orig_h}")
    
    def reset_crop_to_full(self):
        """Reset crop selection to full image."""
        if self.image_label.pixmap():
            size = self.image_label.pixmap().size()
            self.crop_overlay.reset_to_full(QRect(0, 0, size.width(), size.height()))
    
    def show_actual_size(self):
        """Show image at 100% zoom."""
        self.zoom_slider.setValue(100)
    
    def rotate(self, degrees: int):
        """Rotate the image."""
        self.current_rotation = (self.current_rotation + degrees) % 360
        self.update_display()
        self.reset_crop_to_full()
    
    def flip(self, direction: str):
        """Flip the image."""
        if direction == "horizontal":
            self.original_image = self.original_image.transpose(Image.FLIP_LEFT_RIGHT)
        else:
            self.original_image = self.original_image.transpose(Image.FLIP_TOP_BOTTOM)
        
        self.update_display()
        self.reset_crop_to_full()
    
    def on_zoom_changed(self, value: int):
        """Handle zoom slider change."""
        self.zoom_label.setText(f"{value}%")
        
        # Remember current crop proportions
        old_rect = self.crop_overlay.crop_rect
        old_zoom = getattr(self, '_last_zoom', 100) / 100
        
        self.update_display()
        
        # Scale crop to new zoom
        if old_rect.isValid():
            new_zoom = value / 100
            scale = new_zoom / old_zoom if old_zoom > 0 else 1
            
            new_rect = QRect(
                int(old_rect.x() * scale),
                int(old_rect.y() * scale),
                int(old_rect.width() * scale),
                int(old_rect.height() * scale)
            )
            
            # Ensure within bounds
            if self.image_label.pixmap():
                size = self.image_label.pixmap().size()
                new_rect = new_rect.intersected(QRect(0, 0, size.width(), size.height()))
            
            self.crop_overlay.crop_rect = new_rect
            self.crop_overlay.update()
            self.on_crop_changed(new_rect)
        
        self._last_zoom = value
    
    def fit_to_window(self):
        """Fit image to window size."""
        if not self.original_image:
            return
        
        scroll_size = self.scroll_area.size()
        img_size = self.original_image.size
        
        zoom_w = (scroll_size.width() - 40) / img_size[0] * 100
        zoom_h = (scroll_size.height() - 40) / img_size[1] * 100
        
        fit_zoom = int(min(zoom_w, zoom_h, 200))
        self.zoom_slider.setValue(fit_zoom)
    
    def on_aspect_changed(self, index: int):
        """Handle aspect ratio selection."""
        aspect_map = {
            0: None,
            1: (1, 1),
            2: (4, 3),
            3: (3, 4),
            4: (16, 9),
            5: (9, 16),
            6: (3, 2),
            7: (2, 3)
        }
        
        self.crop_overlay.set_aspect_ratio(aspect_map.get(index))
    
    def toggle_grid(self, state: int):
        """Toggle grid overlay."""
        self.crop_overlay.show_grid = state == Qt.Checked
        self.crop_overlay.update()
    
    def change_grid_type(self, index: int):
        """Change grid type."""
        self.crop_overlay.grid_type = "rule_of_thirds" if index == 0 else "grid"
        self.crop_overlay.update()
    
    def restore_original(self):
        """Restore the original image from backup."""
        if not self.backup_path or not self.backup_path.exists():
            QMessageBox.warning(self, "No Backup", "No original backup found for this image.")
            return
        
        reply = QMessageBox.question(
            self, "Restore Original",
            f"Restore the original version of this image?\n\nThis will replace the current file:\n{self.image_path}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                shutil.copy2(self.backup_path, self.image_path)
                self.original_image = Image.open(self.image_path)
                self.current_rotation = 0
                self.update_display()
                self.reset_crop_to_full()
                
                w, h = self.original_image.size
                self.size_label.setText(f"Original: {w} x {h}")
                
                QMessageBox.information(self, "Restored", "Original image has been restored.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to restore: {e}")
    
    def apply_crop(self):
        """Apply the crop and save."""
        crop_rect = self.crop_overlay.crop_rect
        
        # Convert from display coordinates to original image coordinates
        zoom = self.zoom_slider.value() / 100
        
        if not crop_rect.isValid() or crop_rect.isEmpty():
            # No crop - just save with rotation
            img = self.original_image
            if self.current_rotation != 0:
                img = img.rotate(-self.current_rotation, expand=True)
        else:
            # Apply rotation first
            img = self.original_image
            if self.current_rotation != 0:
                img = img.rotate(-self.current_rotation, expand=True)
            
            # Convert crop rect to original coordinates
            orig_rect = QRect(
                int(crop_rect.x() / zoom),
                int(crop_rect.y() / zoom),
                int(crop_rect.width() / zoom),
                int(crop_rect.height() / zoom)
            )
            
            # Apply crop
            box = (
                max(0, orig_rect.x()),
                max(0, orig_rect.y()),
                min(img.width, orig_rect.x() + orig_rect.width()),
                min(img.height, orig_rect.y() + orig_rect.height())
            )
            img = img.crop(box)
        
        # Create backup of original before saving
        backup_dir = self.image_path.parent / ".originals"
        backup_dir.mkdir(exist_ok=True)
        
        backup_file = backup_dir / f"{self.image_path.stem}_original{self.image_path.suffix}"
        if not backup_file.exists():
            # Only backup if no backup exists yet
            shutil.copy2(self.image_path, backup_file)
        
        # Save to processed folder
        output_dir = self.image_path.parent / "processed"
        output_dir.mkdir(exist_ok=True)
        
        self.output_path = output_dir / f"{self.image_path.stem}-cropped.webp"
        
        # Convert to RGB if needed
        if img.mode in ("RGBA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            if img.mode == "RGBA":
                background.paste(img, mask=img.split()[-1])
            img = background
        
        img.save(self.output_path, format="WEBP", quality=90)
        
        self.accept()
    
    def get_cropped_path(self) -> Optional[str]:
        """Get the path to the cropped image."""
        return str(self.output_path) if self.output_path else None
