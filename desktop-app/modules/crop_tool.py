#!/usr/bin/env python3
"""
Crop Tool Module - 4-Line Approach
Simple, intuitive cropping with 4 draggable boundary lines.

The user drags:
- Left line (vertical)
- Right line (vertical)
- Top line (horizontal)
- Bottom line (horizontal)

The crop area is the rectangle formed by these 4 lines.

UPDATED: 
- Now overwrites original file (with automatic backup to .originals/)
- Dialog is 15% LARGER (1150x920 instead of 1000x800)
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
from .theme_modern import ModernPalette


class CropLines(QWidget):
    """
    4-line crop overlay - simple and intuitive.

    Four draggable lines define the crop boundaries:
    - Left edge (vertical line)
    - Right edge (vertical line)
    - Top edge (horizontal line)
    - Bottom edge (horizontal line)
    """

    crop_changed = pyqtSignal(QRect)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)

        # Line positions (in pixels from edge)
        self.left_x = 0
        self.right_x = 100
        self.top_y = 0
        self.bottom_y = 100

        # Minimum crop size
        self.min_size = 50

        # Line properties
        self.line_thickness = 3
        self.handle_size = 20  # Size of the draggable handle area
        self.hit_area = 12  # How close mouse needs to be to grab a line

        # Dragging state
        self.dragging = None  # "left", "right", "top", "bottom", or None
        self.drag_start_pos = 0
        self.drag_start_value = 0

        # Visual settings
        self.show_grid = True

        # Colors - Use ModernPalette
        self.overlay_color = QColor(0, 0, 0, 160)  # Darker overlay
        # Parse hex color manually since QColor(string) might need '#'
        self.line_color = QColor(ModernPalette.PRIMARY)  
        self.handle_color = QColor(ModernPalette.TEXT)  
        self.grid_color = QColor(255, 255, 255, 80)  # Faint grid

    def set_bounds(self, width: int, height: int):
        """Set the image bounds and initialize crop to full image."""
        # Initialize with a small inset so the left/right/top/bottom handles
        # are visible and draggable (prevents handles sitting exactly on edges).
        inset_x = min(20, max(5, int(width * 0.02)))
        inset_y = min(20, max(5, int(height * 0.02)))

        self.left_x = inset_x
        self.right_x = max(inset_x + 100, width - inset_x)
        self.top_y = inset_y
        self.bottom_y = max(inset_y + 100, height - inset_y)
        self.update()
        self._emit_crop()

    def reset_to_full(self):
        """Reset crop lines to full image bounds."""
        inset_x = min(20, max(5, int(self.width() * 0.02)))
        inset_y = min(20, max(5, int(self.height() * 0.02)))

        self.left_x = inset_x
        self.right_x = max(inset_x + 100, self.width() - inset_x)
        self.top_y = inset_y
        self.bottom_y = max(inset_y + 100, self.height() - inset_y)
        self.update()
        self._emit_crop()

    def get_crop_rect(self) -> QRect:
        """Get the current crop rectangle."""
        return QRect(
            int(self.left_x),
            int(self.top_y),
            int(self.right_x - self.left_x),
            int(self.bottom_y - self.top_y)
        )

    def _emit_crop(self):
        """Emit the crop changed signal."""
        self.crop_changed.emit(self.get_crop_rect())

    def paintEvent(self, event):
        """Paint the crop overlay with 4 lines."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()

        # Draw darkened overlay outside crop area
        painter.setBrush(QBrush(self.overlay_color))
        painter.setPen(Qt.NoPen)

        # Top region (above top line)
        painter.drawRect(0, 0, w, int(self.top_y))

        # Bottom region (below bottom line)
        painter.drawRect(0, int(self.bottom_y), w, h - int(self.bottom_y))

        # Left region (between top and bottom)
        painter.drawRect(0, int(self.top_y), int(self.left_x), int(self.bottom_y - self.top_y))

        # Right region (between top and bottom)
        painter.drawRect(int(self.right_x), int(self.top_y), w - int(self.right_x), int(self.bottom_y - self.top_y))

        # Draw grid in crop area if enabled
        if self.show_grid:
            crop_w = self.right_x - self.left_x
            crop_h = self.bottom_y - self.top_y

            if crop_w > 0 and crop_h > 0:
                painter.setPen(QPen(self.grid_color, 1, Qt.DashLine))

                # Rule of thirds
                third_w = crop_w / 3
                third_h = crop_h / 3

                for i in range(1, 3):
                    # Vertical lines
                    x = self.left_x + third_w * i
                    painter.drawLine(int(x), int(self.top_y), int(x), int(self.bottom_y))

                    # Horizontal lines
                    y = self.top_y + third_h * i
                    painter.drawLine(int(self.left_x), int(y), int(self.right_x), int(y))

        # Draw the 4 crop lines with handles
        line_pen = QPen(self.line_color, self.line_thickness)
        painter.setPen(line_pen)

        # LEFT line (vertical)
        painter.drawLine(int(self.left_x), 0, int(self.left_x), h)

        # RIGHT line (vertical)
        painter.drawLine(int(self.right_x), 0, int(self.right_x), h)

        # TOP line (horizontal)
        painter.drawLine(0, int(self.top_y), w, int(self.top_y))

        # BOTTOM line (horizontal)
        painter.drawLine(0, int(self.bottom_y), w, int(self.bottom_y))

        # Draw handles (small rectangles on each line)
        painter.setBrush(QBrush(self.handle_color))
        painter.setPen(QPen(self.line_color, 2))

        handle_w = 8
        handle_h = 30

        # Left handle (centered vertically on crop area)
        mid_y = (self.top_y + self.bottom_y) / 2
        painter.drawRect(int(self.left_x - handle_w/2), int(mid_y - handle_h/2), handle_w, handle_h)

        # Right handle
        painter.drawRect(int(self.right_x - handle_w/2), int(mid_y - handle_h/2), handle_w, handle_h)

        # Top handle (centered horizontally on crop area)
        mid_x = (self.left_x + self.right_x) / 2
        painter.drawRect(int(mid_x - handle_h/2), int(self.top_y - handle_w/2), handle_h, handle_w)

        # Bottom handle
        painter.drawRect(int(mid_x - handle_h/2), int(self.bottom_y - handle_w/2), handle_h, handle_w)

        # Draw corner indicators
        corner_size = 15
        painter.setPen(QPen(self.handle_color, 3))

        # Top-left corner
        painter.drawLine(int(self.left_x), int(self.top_y), int(self.left_x + corner_size), int(self.top_y))
        painter.drawLine(int(self.left_x), int(self.top_y), int(self.left_x), int(self.top_y + corner_size))

        # Top-right corner
        painter.drawLine(int(self.right_x), int(self.top_y), int(self.right_x - corner_size), int(self.top_y))
        painter.drawLine(int(self.right_x), int(self.top_y), int(self.right_x), int(self.top_y + corner_size))

        # Bottom-left corner
        painter.drawLine(int(self.left_x), int(self.bottom_y), int(self.left_x + corner_size), int(self.bottom_y))
        painter.drawLine(int(self.left_x), int(self.bottom_y), int(self.left_x), int(self.bottom_y - corner_size))

        # Bottom-right corner
        painter.drawLine(int(self.right_x), int(self.bottom_y), int(self.right_x - corner_size), int(self.bottom_y))
        painter.drawLine(int(self.right_x), int(self.bottom_y), int(self.right_x), int(self.bottom_y - corner_size))

        painter.end()

    def _get_line_at(self, pos: QPoint) -> Optional[str]:
        """Determine which line (if any) the mouse is near."""
        x, y = pos.x(), pos.y()
        hit = self.hit_area

        # Check each line (prioritize the one closest to mouse)
        distances = {}

        # Left line - check if we're near it
        if abs(x - self.left_x) < hit:
            distances["left"] = abs(x - self.left_x)

        # Right line
        if abs(x - self.right_x) < hit:
            distances["right"] = abs(x - self.right_x)

        # Top line
        if abs(y - self.top_y) < hit:
            distances["top"] = abs(y - self.top_y)

        # Bottom line
        if abs(y - self.bottom_y) < hit:
            distances["bottom"] = abs(y - self.bottom_y)

        if not distances:
            return None

        # Return the closest line
        return min(distances, key=distances.get)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            line = self._get_line_at(event.pos())
            if line:
                self.dragging = line
                if line in ("left", "right"):
                    self.drag_start_pos = event.pos().x()
                    self.drag_start_value = self.left_x if line == "left" else self.right_x
                else:
                    self.drag_start_pos = event.pos().y()
                    self.drag_start_value = self.top_y if line == "top" else self.bottom_y

    def mouseMoveEvent(self, event):
        if self.dragging:
            self._handle_drag(event.pos())
        else:
            # Update cursor based on position
            line = self._get_line_at(event.pos())
            if line in ("left", "right"):
                self.setCursor(Qt.SizeHorCursor)
            elif line in ("top", "bottom"):
                self.setCursor(Qt.SizeVerCursor)
            else:
                self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = None
            self._emit_crop()

    def _handle_drag(self, pos: QPoint):
        """Handle line dragging."""
        if self.dragging == "left":
            delta = pos.x() - self.drag_start_pos
            new_x = self.drag_start_value + delta
            # Constrain: can't go past right line or out of bounds
            new_x = max(0, min(new_x, self.right_x - self.min_size))
            self.left_x = new_x

        elif self.dragging == "right":
            delta = pos.x() - self.drag_start_pos
            new_x = self.drag_start_value + delta
            # Constrain: can't go past left line or out of bounds
            new_x = max(self.left_x + self.min_size, min(new_x, self.width()))
            self.right_x = new_x

        elif self.dragging == "top":
            delta = pos.y() - self.drag_start_pos
            new_y = self.drag_start_value + delta
            # Constrain: can't go past bottom line or out of bounds
            new_y = max(0, min(new_y, self.bottom_y - self.min_size))
            self.top_y = new_y

        elif self.dragging == "bottom":
            delta = pos.y() - self.drag_start_pos
            new_y = self.drag_start_value + delta
            # Constrain: can't go past top line or out of bounds
            new_y = max(self.top_y + self.min_size, min(new_y, self.height()))
            self.bottom_y = new_y

        self.update()
        self._emit_crop()


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
    Image cropping dialog with 4-line crop interface.

    Simple, intuitive cropping:
    - Drag the LEFT line to set left boundary
    - Drag the RIGHT line to set right boundary
    - Drag the TOP line to set top boundary
    - Drag the BOTTOM line to set bottom boundary

    BEHAVIOR: Overwrites the original file (backup saved to .originals/)
    
    UPDATED: Dialog is 15% LARGER (1150x920 instead of 1000x800)
    """

    def __init__(self, image_path: str, parent=None, config: dict = None):
        super().__init__(parent)
        self.image_path = Path(image_path)
        self.original_image = None
        self.current_rotation = 0
        self.output_path = None
        self.backup_path = None
        self._initialized = False
        self.config = config or {}

        self.setWindowTitle(f"Crop Image - {self.image_path.name}")
        
        # ============================================
        # 15% LARGER DIALOG: 1000x800 → 1150x920
        # ============================================
        self.setMinimumSize(1150, 920)

        # Apply Modern Theme
        self.setStyleSheet(ModernPalette.get_stylesheet())

        self.setup_ui()
        self.load_image()

    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Instructions
        instructions = QLabel("Drag the colored lines to set crop boundaries")
        instructions.setStyleSheet(f"""
            QLabel {{
                color: {ModernPalette.PRIMARY};
                font-size: 16px;
                font-weight: bold;
                padding: 8px;
            }}
        """)
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)

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

        # Grid toggle
        grid_group = QGroupBox("Grid")
        grid_layout = QHBoxLayout(grid_group)

        self.grid_check = QCheckBox("Show Rule of Thirds")
        self.grid_check.setChecked(True)
        self.grid_check.stateChanged.connect(self.toggle_grid)
        grid_layout.addWidget(self.grid_check)

        toolbar.addWidget(grid_group)
        toolbar.addStretch()

        layout.addLayout(toolbar)

        # Image area with scroll and overlay
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setAlignment(Qt.AlignCenter)

        # Image label
        self.image_label = ImageLabel()

        # Crop overlay (4 lines)
        self.crop_overlay = CropLines(self.image_label)
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

        self.reset_crop_btn = QPushButton("Reset Crop")
        self.reset_crop_btn.clicked.connect(self.reset_crop_to_full)
        self.reset_crop_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernPalette.BTN_SECONDARY_BG};
                color: {ModernPalette.TEXT};
            }}
            QPushButton:hover {{
                background-color: {ModernPalette.BTN_SECONDARY_HOVER};
            }}
        """)
        zoom_layout.addWidget(self.reset_crop_btn)

        layout.addLayout(zoom_layout)

        # Info area
        info_layout = QHBoxLayout()

        self.size_label = QLabel("Original: -- x --")
        info_layout.addWidget(self.size_label)

        self.crop_size_label = QLabel("Crop: -- x --")
        self.crop_size_label.setStyleSheet(f"color: {ModernPalette.SUCCESS}; font-weight: bold;")
        info_layout.addWidget(self.crop_size_label)

        info_layout.addStretch()

        layout.addLayout(info_layout)

        # Dialog buttons
        btn_layout = QHBoxLayout()

        self.restore_btn = QPushButton("🔄 Restore Original")
        self.restore_btn.clicked.connect(self.restore_original)
        self.restore_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernPalette.SUCCESS};
                color: {ModernPalette.BACKGROUND};
                border: none;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #8ccf7c;
            }}
        """)
        self.restore_btn.setEnabled(False)
        btn_layout.addWidget(self.restore_btn)

        btn_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernPalette.SURFACE};
                border: 1px solid {ModernPalette.BORDER};
            }}
            QPushButton:hover {{
                background-color: {ModernPalette.SURFACE_LIGHT};
            }}
        """)
        btn_layout.addWidget(self.cancel_btn)

        self.apply_btn = QPushButton("💾 Save Changes")
        self.apply_btn.setToolTip("Save all changes (crop, rotation, flip)")
        self.apply_btn.clicked.connect(self.apply_crop)
        # Primary styling handled by global stylesheet if not overridden
        self.apply_btn.setProperty("variant", "primary")
        
        btn_layout.addWidget(self.apply_btn)

        layout.addLayout(btn_layout)

    def showEvent(self, event):
        """Handle dialog show event."""
        super().showEvent(event)
        QTimer.singleShot(100, self._auto_fit_and_init)

    def _auto_fit_and_init(self):
        """Auto-fit to window and initialize crop overlay."""
        if self._initialized:
            return
        self._initialized = True
        self.fit_to_window()
        QTimer.singleShot(50, self.init_crop_overlay)

    def load_image(self):
        """Load the image for editing."""
        print(f"[CropDialog] Loading image: {self.image_path}")
        self.original_image = Image.open(self.image_path)

        # Check for existing backup
        self.backup_path = self.image_path.parent / ".originals" / f"{self.image_path.stem}_original{self.image_path.suffix}"
        self.restore_btn.setEnabled(self.backup_path.exists())

        w, h = self.original_image.size
        self.size_label.setText(f"Original: {w} x {h}")
        print(f"[CropDialog] Image size: {w} x {h}")

        self.update_display()

    def init_crop_overlay(self):
        """Initialize crop overlay after image is displayed."""
        if self.image_label.pixmap():
            size = self.image_label.pixmap().size()
            self.crop_overlay.setGeometry(0, 0, size.width(), size.height())
            self.crop_overlay.set_bounds(size.width(), size.height())
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
        """Reset crop lines to full image."""
        self.crop_overlay.reset_to_full()

    def rotate(self, degrees: int):
        """Rotate the image."""
        self.current_rotation = (self.current_rotation + degrees) % 360
        self._initialized = False
        self.update_display()
        QTimer.singleShot(50, self._reinit_overlay)

    def _reinit_overlay(self):
        """Reinitialize overlay after rotation."""
        if self.image_label.pixmap():
            size = self.image_label.pixmap().size()
            self.crop_overlay.setGeometry(0, 0, size.width(), size.height())
            self.crop_overlay.set_bounds(size.width(), size.height())

    def flip(self, direction: str):
        """Flip the image."""
        if direction == "horizontal":
            self.original_image = self.original_image.transpose(Image.FLIP_LEFT_RIGHT)
        else:
            self.original_image = self.original_image.transpose(Image.FLIP_TOP_BOTTOM)

        self.update_display()
        self._reinit_overlay()

    def on_zoom_changed(self, value: int):
        """Handle zoom slider change."""
        self.zoom_label.setText(f"{value}%")

        # Store old crop proportions
        old_crop = self.crop_overlay.get_crop_rect()
        old_zoom = getattr(self, '_last_zoom', 100) / 100

        self.update_display()

        # Scale crop lines to new zoom
        if old_crop.isValid() and old_zoom > 0:
            new_zoom = value / 100
            scale = new_zoom / old_zoom

            self.crop_overlay.left_x = old_crop.left() * scale
            self.crop_overlay.right_x = old_crop.right() * scale
            self.crop_overlay.top_y = old_crop.top() * scale
            self.crop_overlay.bottom_y = old_crop.bottom() * scale

            # Ensure within bounds
            if self.image_label.pixmap():
                size = self.image_label.pixmap().size()
                self.crop_overlay.right_x = min(self.crop_overlay.right_x, size.width())
                self.crop_overlay.bottom_y = min(self.crop_overlay.bottom_y, size.height())

            self.crop_overlay.update()
            self.on_crop_changed(self.crop_overlay.get_crop_rect())

        self._last_zoom = value

    def fit_to_window(self):
        """Fit image to window size."""
        if not self.original_image:
            return

        scroll_size = self.scroll_area.viewport().size()
        if scroll_size.width() < 100 or scroll_size.height() < 100:
            scroll_size = QSize(1000, 600)  # Larger default for bigger dialog

        img_size = self.original_image.size

        if self.current_rotation in (90, 270):
            img_w, img_h = img_size[1], img_size[0]
        else:
            img_w, img_h = img_size[0], img_size[1]

        padding = 40
        zoom_w = (scroll_size.width() - padding) / img_w * 100
        zoom_h = (scroll_size.height() - padding) / img_h * 100

        fit_zoom = int(min(zoom_w, zoom_h, 100))
        fit_zoom = max(fit_zoom, 25)

        self.zoom_slider.setValue(fit_zoom)

    def toggle_grid(self, state: int):
        """Toggle grid overlay."""
        self.crop_overlay.show_grid = state == Qt.Checked
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
                self._initialized = False
                self.update_display()
                QTimer.singleShot(50, self._reinit_overlay)

                w, h = self.original_image.size
                self.size_label.setText(f"Original: {w} x {h}")

                QMessageBox.information(self, "Restored", "Original image has been restored.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to restore: {e}")

    def apply_crop(self):
        """Apply the crop and save - OVERWRITES ORIGINAL FILE."""
        print("[CropDialog] Applying crop...")

        crop_rect = self.crop_overlay.get_crop_rect()
        zoom = self.zoom_slider.value() / 100

        # Apply rotation first
        img = self.original_image
        if self.current_rotation != 0:
            img = img.rotate(-self.current_rotation, expand=True)
            print(f"[CropDialog] Applied rotation: {self.current_rotation}°")

        # Convert crop rect to original coordinates
        actual_crop_applied = False
        if crop_rect.isValid() and not crop_rect.isEmpty():
            orig_rect = QRect(
                int(crop_rect.x() / zoom),
                int(crop_rect.y() / zoom),
                int(crop_rect.width() / zoom),
                int(crop_rect.height() / zoom)
            )

            # Check if this is actually a crop (not full image)
            is_full_image = (
                orig_rect.x() <= 1 and
                orig_rect.y() <= 1 and
                orig_rect.width() >= img.width - 2 and
                orig_rect.height() >= img.height - 2
            )

            if not is_full_image:
                # Apply crop
                box = (
                    max(0, orig_rect.x()),
                    max(0, orig_rect.y()),
                    min(img.width, orig_rect.x() + orig_rect.width()),
                    min(img.height, orig_rect.y() + orig_rect.height())
                )
                print(f"[CropDialog] Crop box: {box}")
                img = img.crop(box)
                actual_crop_applied = True
                print(f"[CropDialog] Cropped to: {img.width} x {img.height}")

        # Create backup of original BEFORE saving
        backup_dir = self.image_path.parent / ".originals"
        backup_dir.mkdir(exist_ok=True)

        backup_file = backup_dir / f"{self.image_path.stem}_original{self.image_path.suffix}"
        if not backup_file.exists():
            print(f"[CropDialog] Creating backup: {backup_file}")
            shutil.copy2(self.image_path, backup_file)
        else:
            print(f"[CropDialog] Backup already exists: {backup_file}")

        # Convert to RGB if needed (for JPEG/WebP compatibility)
        if img.mode in ("RGBA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            if img.mode == "RGBA":
                background.paste(img, mask=img.split()[-1])
            img = background

        # SAVE DIRECTLY TO THE ORIGINAL FILE PATH
        try:
            # Determine format based on original extension
            ext = self.image_path.suffix.lower()
            if ext in ('.jpg', '.jpeg'):
                img.save(self.image_path, format="JPEG", quality=95)
            elif ext == '.png':
                img.save(self.image_path, format="PNG")
            elif ext == '.webp':
                img.save(self.image_path, format="WEBP", quality=95)
            else:
                # Default to JPEG for unknown formats
                img.save(self.image_path, format="JPEG", quality=95)

            print(f"[CropDialog] ✓ Saved to: {self.image_path}")
            self.output_path = self.image_path

        except Exception as e:
            print(f"[CropDialog] ✗ Error saving: {e}")
            QMessageBox.critical(self, "Save Error", f"Failed to save image:\n{e}")
            return

        # Enable restore button now that we have a backup
        self.restore_btn.setEnabled(True)

        self.accept()

    def get_cropped_path(self) -> Optional[str]:
        """Get the path to the cropped image."""
        return str(self.output_path) if self.output_path else None
