#!/usr/bin/env python3
"""
Crop Tool Module
Interactive image cropping dialog with various features.
"""

from pathlib import Path
from typing import Optional, Tuple

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QComboBox, QWidget, QRubberBand, QSizePolicy,
    QScrollArea, QCheckBox, QSpinBox, QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt, QRect, QPoint, QSize, QTimer
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QTransform

from PIL import Image


class CropLabel(QLabel):
    """
    Custom QLabel with crop region selection.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)

        self.rubber_band = None
        self.origin = QPoint()
        self.crop_rect = QRect()
        self.scale_factor = 1.0
        self.original_size = QSize()

        # Resizing state
        self.resize_mode = None  # "top", "bottom", "left", "right", "top_left", etc.
        self.is_resizing = False
        self.handle_size = 10  # Detection radius for handles

        # Grid overlay
        self.show_grid = True
        self.grid_type = "rule_of_thirds"  # or "grid"

        # Aspect ratio constraint (None for free, or (width, height) tuple)
        self.aspect_ratio = None

        # Callback for selection updates
        self.selection_callback = None

    def set_image(self, pixmap: QPixmap, scale: float = 1.0):
        """Set the image and scale factor."""
        self.scale_factor = scale
        self.original_size = pixmap.size()

        if scale != 1.0:
            scaled = pixmap.scaled(
                pixmap.size() * scale,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.setPixmap(scaled)
        else:
            self.setPixmap(pixmap)

        self.adjustSize()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Check if clicking on an existing selection handle
            mode = self._get_resize_mode(event.pos())

            if mode:
                self.is_resizing = True
                self.resize_mode = mode
            else:
                # Start new selection
                self.is_resizing = False
                self.origin = event.pos()
                if not self.rubber_band:
                    self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
                self.rubber_band.setGeometry(QRect(self.origin, QSize()))
                self.rubber_band.show()

    def mouseMoveEvent(self, event):
        # Update cursor and resize mode when not dragging
        if not event.buttons() & Qt.LeftButton:
            mode = self._get_resize_mode(event.pos())
            if mode in ["left", "right"]:
                self.setCursor(Qt.SizeHorCursor)
            elif mode in ["top", "bottom"]:
                self.setCursor(Qt.SizeVerCursor)
            elif mode in ["top_left", "bottom_right"]:
                self.setCursor(Qt.SizeFDiagCursor)
            elif mode in ["top_right", "bottom_left"]:
                self.setCursor(Qt.SizeBDiagCursor)
            else:
                self.setCursor(Qt.CrossCursor)
            return

        # Handle dragging
        if self.is_resizing and self.crop_rect.isValid():
            self._handle_resize(event.pos())
        elif self.rubber_band and self.rubber_band.isVisible():
            # Creating new selection
            rect = self._calculate_constrained_rect(self.origin, event.pos())
            self.rubber_band.setGeometry(rect)
            # Notify parent dialog of selection update
            if self.selection_callback:
                self.selection_callback(rect)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.is_resizing:
                self.is_resizing = False
                self.resize_mode = None
            elif self.rubber_band:
                self.crop_rect = self.rubber_band.geometry()

            # Notify parent dialog of selection update
            if self.selection_callback:
                self.selection_callback(self.crop_rect)
            self.update()

    def _get_resize_mode(self, pos: QPoint) -> Optional[str]:
        """Determine resize mode based on mouse position relative to crop rect."""
        if not self.crop_rect.isValid():
            return None

        r = self.crop_rect
        x, y = pos.x(), pos.y()
        h = self.handle_size

        # Check corners first
        if abs(x - r.left()) < h and abs(y - r.top()) < h: return "top_left"
        if abs(x - r.right()) < h and abs(y - r.top()) < h: return "top_right"
        if abs(x - r.left()) < h and abs(y - r.bottom()) < h: return "bottom_left"
        if abs(x - r.right()) < h and abs(y - r.bottom()) < h: return "bottom_right"

        # Check sides
        if abs(x - r.left()) < h and r.top() < y < r.bottom(): return "left"
        if abs(x - r.right()) < h and r.top() < y < r.bottom(): return "right"
        if abs(y - r.top()) < h and r.left() < x < r.right(): return "top"
        if abs(y - r.bottom()) < h and r.left() < x < r.right(): return "bottom"

        return None

    def _handle_resize(self, pos: QPoint):
        """Handle resizing of the crop rectangle."""
        r = self.crop_rect
        mode = self.resize_mode

        left, top, right, bottom = r.left(), r.top(), r.right(), r.bottom()

        # Update coordinates based on handle being dragged
        if "left" in mode: left = min(pos.x(), right - 10)
        if "right" in mode: right = max(pos.x(), left + 10)
        if "top" in mode: top = min(pos.y(), bottom - 10)
        if "bottom" in mode: bottom = max(pos.y(), top + 10)

        new_rect = QRect(QPoint(left, top), QPoint(right, bottom)).normalized()

        # Apply bounds constraint
        new_rect = new_rect.intersected(self.rect())

        # TODO: Apply aspect ratio constraint if needed
        # For now, we allow free resizing which might break aspect ratio
        # If aspect ratio is strict, we would need to recalculate the other dimension

        self.crop_rect = new_rect
        if self.rubber_band:
            self.rubber_band.setGeometry(new_rect)

        if self.selection_callback:
            self.selection_callback(new_rect)

    def paintEvent(self, event):
        super().paintEvent(event)

        if self.show_grid and self.pixmap():
            painter = QPainter(self)
            painter.setPen(QPen(QColor(255, 255, 255, 100), 1, Qt.DashLine))

            rect = self.crop_rect if self.crop_rect.isValid() else self.rect()

            if self.grid_type == "rule_of_thirds":
                # Rule of thirds lines
                third_w = rect.width() // 3
                third_h = rect.height() // 3

                for i in range(1, 3):
                    # Vertical lines
                    x = rect.x() + third_w * i
                    painter.drawLine(x, rect.y(), x, rect.y() + rect.height())

                    # Horizontal lines
                    y = rect.y() + third_h * i
                    painter.drawLine(rect.x(), y, rect.x() + rect.width(), y)

            elif self.grid_type == "grid":
                # 5x5 grid
                cell_w = rect.width() // 5
                cell_h = rect.height() // 5

                for i in range(1, 5):
                    x = rect.x() + cell_w * i
                    y = rect.y() + cell_h * i
                    painter.drawLine(x, rect.y(), x, rect.y() + rect.height())
                    painter.drawLine(rect.x(), y, rect.x() + rect.width(), y)

            painter.end()

    def get_crop_rect_original(self) -> QRect:
        """Get crop rectangle in original image coordinates."""
        if not self.crop_rect.isValid():
            return QRect()

        return QRect(
            int(self.crop_rect.x() / self.scale_factor),
            int(self.crop_rect.y() / self.scale_factor),
            int(self.crop_rect.width() / self.scale_factor),
            int(self.crop_rect.height() / self.scale_factor)
        )

    def _calculate_constrained_rect(self, start: QPoint, end: QPoint) -> QRect:
        """
        Calculate crop rectangle with aspect ratio constraint.

        Args:
            start: Starting point of the selection
            end: Current mouse position

        Returns:
            QRect constrained to aspect ratio if set, otherwise free-form
        """
        if not self.aspect_ratio:
            # Free-form selection
            return QRect(start, end).normalized()

        # Calculate base rectangle
        base_rect = QRect(start, end).normalized()
        width = base_rect.width()
        height = base_rect.height()

        # Get aspect ratio
        aspect_w, aspect_h = self.aspect_ratio
        target_ratio = aspect_w / aspect_h

        # Calculate constrained dimensions
        if width / max(height, 1) > target_ratio:
            # Width is too large, constrain by width
            height = int(width / target_ratio)
        else:
            # Height is too large, constrain by height
            width = int(height * target_ratio)

        # Determine which corner to anchor (use the corner closest to start)
        dx = end.x() - start.x()
        dy = end.y() - start.y()

        # Calculate new position to keep the start point fixed
        if dx >= 0 and dy >= 0:
            # Dragging down-right: keep top-left
            new_rect = QRect(start.x(), start.y(), width, height)
        elif dx < 0 and dy >= 0:
            # Dragging down-left: keep top-right
            new_rect = QRect(start.x() - width, start.y(), width, height)
        elif dx >= 0 and dy < 0:
            # Dragging up-right: keep bottom-left
            new_rect = QRect(start.x(), start.y() - height, width, height)
        else:
            # Dragging up-left: keep bottom-right
            new_rect = QRect(start.x() - width, start.y() - height, width, height)

        # Ensure rectangle stays within image bounds while maintaining aspect ratio
        img_rect = self.rect()

        # First, ensure the rectangle fits within bounds by adjusting position
        # Use iterative approach to handle cases where one adjustment affects another
        max_iterations = 5
        for _ in range(max_iterations):
            adjusted = False

            # Check and fix left boundary
            if new_rect.left() < img_rect.left():
                new_rect.moveLeft(img_rect.left())
                adjusted = True

            # Check and fix top boundary
            if new_rect.top() < img_rect.top():
                new_rect.moveTop(img_rect.top())
                adjusted = True

            # Check and fix right boundary
            if new_rect.right() > img_rect.right():
                new_rect.moveRight(img_rect.right())
                adjusted = True

            # Check and fix bottom boundary
            if new_rect.bottom() > img_rect.bottom():
                new_rect.moveBottom(img_rect.bottom())
                adjusted = True

            # If no adjustments were needed, we're done
            if not adjusted:
                break

        # After bounds adjustment, check if we need to fix aspect ratio
        if new_rect.width() > 0 and new_rect.height() > 0:
            current_ratio = new_rect.width() / new_rect.height()
            if abs(current_ratio - target_ratio) > 0.01:  # Allow small floating point errors
                # Aspect ratio was broken by bounds adjustment - fix it
                # Calculate maximum available space from current position
                max_width = img_rect.right() - new_rect.left()
                max_height = img_rect.bottom() - new_rect.top()

                # Ensure we have valid space
                max_width = max(1, max_width)
                max_height = max(1, max_height)

                # Calculate dimensions that maintain aspect ratio and fit within available space
                width_by_height = int(max_height * target_ratio)
                height_by_width = int(max_width / target_ratio)

                # Choose the constraint that results in the largest rectangle that fits
                if width_by_height <= max_width:
                    # Constrain by height (width fits within available space)
                    new_width = width_by_height
                    new_height = max_height
                else:
                    # Constrain by width (height fits within available space)
                    new_width = max_width
                    new_height = height_by_width

                # Ensure dimensions are valid
                new_width = max(1, new_width)
                new_height = max(1, new_height)

                # Update dimensions while keeping the top-left corner fixed
                new_rect.setWidth(new_width)
                new_rect.setHeight(new_height)

        # Final bounds validation - ALWAYS execute to ensure rectangle is within bounds
        # This handles cases where aspect ratio is preserved but rectangle is still out-of-bounds
        # Use iterative approach again to handle interdependencies
        for _ in range(max_iterations):
            adjusted = False

            # If rectangle exceeds right boundary, move it left
            if new_rect.right() > img_rect.right():
                new_rect.moveLeft(img_rect.right() - new_rect.width())
                adjusted = True

            # If rectangle exceeds bottom boundary, move it up
            if new_rect.bottom() > img_rect.bottom():
                new_rect.moveTop(img_rect.bottom() - new_rect.height())
                adjusted = True

            # If rectangle is now too far left, move it right
            if new_rect.left() < img_rect.left():
                new_rect.moveLeft(img_rect.left())
                adjusted = True

            # If rectangle is now too far up, move it down
            if new_rect.top() < img_rect.top():
                new_rect.moveTop(img_rect.top())
                adjusted = True

            # If rectangle is too wide, shrink it (maintaining aspect ratio if needed)
            if new_rect.width() > img_rect.width():
                new_rect.setWidth(img_rect.width())
                if self.aspect_ratio:
                    new_rect.setHeight(int(new_rect.width() / target_ratio))
                adjusted = True

            # If rectangle is too tall, shrink it (maintaining aspect ratio if needed)
            if new_rect.height() > img_rect.height():
                new_rect.setHeight(img_rect.height())
                if self.aspect_ratio:
                    new_rect.setWidth(int(new_rect.height() * target_ratio))
                adjusted = True

            # If no adjustments were needed, we're done
            if not adjusted:
                break

        return new_rect.normalized()

    def set_aspect_ratio(self, aspect_ratio: Optional[Tuple[int, int]]):
        """Set the aspect ratio constraint (None for free-form)."""
        self.aspect_ratio = aspect_ratio
        # Reset selection when aspect ratio changes
        self.reset_selection()

    def reset_selection(self):
        """Clear the crop selection."""
        if self.rubber_band:
            self.rubber_band.hide()
            self.rubber_band = None  # Ensure rubber band is fully reset
        self.crop_rect = QRect()

        # Notify callback that selection is cleared
        if self.selection_callback:
            self.selection_callback(self.crop_rect)

        self.update()


class CropDialog(QDialog):
    """
    Image cropping dialog with rotation and aspect ratio controls.
    """

    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = Path(image_path)
        self.original_image = None
        self.current_rotation = 0
        self.output_path = None

        self.setWindowTitle(f"Crop Image - {self.image_path.name}")
        self.setMinimumSize(900, 700)

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

        # Image area with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(False)  # Allow widget to be larger than view
        scroll.setAlignment(Qt.AlignCenter)

        self.crop_label = CropLabel()
        self.crop_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.crop_label.selection_callback = self.update_crop_size_label
        scroll.setWidget(self.crop_label)

        layout.addWidget(scroll, stretch=1)

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

        self.fit_btn = QPushButton("Fit")
        self.fit_btn.clicked.connect(self.fit_to_window)
        zoom_layout.addWidget(self.fit_btn)

        self.reset_btn = QPushButton("Reset Selection")
        self.reset_btn.clicked.connect(self.crop_label.reset_selection)
        zoom_layout.addWidget(self.reset_btn)

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

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        btn_layout.addStretch()

        self.apply_btn = QPushButton("Apply Crop")
        self.apply_btn.clicked.connect(self.apply_crop)
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #e94560;
                color: white;
                font-weight: bold;
                padding: 10px 24px;
            }
        """)
        btn_layout.addWidget(self.apply_btn)

        layout.addLayout(btn_layout)

    def update_crop_size_label(self, rect: QRect):
        """Update the crop size label with current selection dimensions."""
        if not rect.isValid() or rect.isEmpty():
            if self.crop_label.aspect_ratio:
                w, h = self.crop_label.aspect_ratio
                self.crop_size_label.setText(f"Crop: {w}:{h} (constrained)")
            else:
                self.crop_size_label.setText("Crop: -- x --")
        else:
            # Convert to original image coordinates for display
            orig_rect = QRect(
                int(rect.x() / self.crop_label.scale_factor),
                int(rect.y() / self.crop_label.scale_factor),
                int(rect.width() / self.crop_label.scale_factor),
                int(rect.height() / self.crop_label.scale_factor)
            )
            if self.crop_label.aspect_ratio:
                w, h = self.crop_label.aspect_ratio
                self.crop_size_label.setText(
                    f"Crop: {orig_rect.width()} x {orig_rect.height()} ({w}:{h})"
                )
            else:
                self.crop_size_label.setText(
                    f"Crop: {orig_rect.width()} x {orig_rect.height()}"
                )

    def load_image(self):
        """Load the image for editing."""
        self.original_image = Image.open(self.image_path)
        self.update_display()

        w, h = self.original_image.size
        self.size_label.setText(f"Original: {w} x {h}")

        # Fit to window initially
        QTimer.singleShot(0, self.fit_to_window)

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
            img = img.convert("RGB")
            qim = QImage(
                img.tobytes("raw", "RGB"),
                img.width, img.height,
                QImage.Format_RGB888
            )

        pixmap = QPixmap.fromImage(qim)

        # Apply zoom
        zoom = self.zoom_slider.value() / 100
        self.crop_label.set_image(pixmap, zoom)

    def rotate(self, degrees: int):
        """Rotate the image."""
        self.current_rotation = (self.current_rotation + degrees) % 360
        self.crop_label.reset_selection()
        self.update_display()

    def flip(self, direction: str):
        """Flip the image."""
        if direction == "horizontal":
            self.original_image = self.original_image.transpose(Image.FLIP_LEFT_RIGHT)
        else:
            self.original_image = self.original_image.transpose(Image.FLIP_TOP_BOTTOM)

        self.crop_label.reset_selection()
        self.update_display()

    def on_zoom_changed(self, value: int):
        """Handle zoom slider change."""
        self.zoom_label.setText(f"{value}%")
        self.update_display()

    def fit_to_window(self):
        """Fit image to window."""
        if not self.original_image:
            return

        # Calculate fit zoom
        parent_size = self.crop_label.parent().size()
        img_size = self.original_image.size

        zoom_w = (parent_size.width() - 40) / img_size[0] * 100
        zoom_h = (parent_size.height() - 40) / img_size[1] * 100

        fit_zoom = min(zoom_w, zoom_h, 100)

        self.zoom_slider.setValue(int(fit_zoom))

    def on_aspect_changed(self, index: int):
        """Handle aspect ratio selection."""
        # Parse aspect ratio from selection
        aspect_map = {
            0: None,  # Free
            1: (1, 1),  # 1:1 Square
            2: (4, 3),  # 4:3
            3: (3, 4),  # 3:4
            4: (16, 9),  # 16:9
            5: (9, 16),  # 9:16
            6: (3, 2),  # 3:2
            7: (2, 3)   # 2:3
        }

        aspect_ratio = aspect_map.get(index)
        self.crop_label.set_aspect_ratio(aspect_ratio)

        # Update crop size label to show aspect ratio info
        if aspect_ratio:
            w, h = aspect_ratio
            self.crop_size_label.setText(f"Crop: {w}:{h} (constrained)")
        else:
            self.crop_size_label.setText("Crop: -- x --")

    def toggle_grid(self, state: int):
        """Toggle grid overlay."""
        self.crop_label.show_grid = state == Qt.Checked
        self.crop_label.update()

    def change_grid_type(self, index: int):
        """Change grid overlay type."""
        types = ["rule_of_thirds", "grid"]
        self.crop_label.grid_type = types[index]
        self.crop_label.update()

    def apply_crop(self):
        """Apply the crop and save."""
        crop_rect = self.crop_label.get_crop_rect_original()

        if not crop_rect.isValid() or crop_rect.isEmpty():
            # No crop selected - just save with rotation
            img = self.original_image
            if self.current_rotation != 0:
                img = img.rotate(-self.current_rotation, expand=True)
        else:
            # Apply rotation first
            img = self.original_image
            if self.current_rotation != 0:
                img = img.rotate(-self.current_rotation, expand=True)

            # Then crop
            box = (
                max(0, crop_rect.x()),
                max(0, crop_rect.y()),
                min(img.width, crop_rect.x() + crop_rect.width()),
                min(img.height, crop_rect.y() + crop_rect.height())
            )
            img = img.crop(box)

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
