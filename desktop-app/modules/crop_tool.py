#!/usr/bin/env python3
"""
Crop Tool Module
Interactive image cropping dialog with various features.
"""

from pathlib import Path
from typing import Optional, Tuple
import json
import os

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QComboBox, QWidget, QRubberBand, QSizePolicy,
    QScrollArea, QCheckBox, QSpinBox, QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt, QRect, QPoint, QSize
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
            self.origin = event.pos()
            
            if not self.rubber_band:
                self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
            
            self.rubber_band.setGeometry(QRect(self.origin, QSize()))
            self.rubber_band.show()
    
    def mouseMoveEvent(self, event):
        if self.rubber_band and self.rubber_band.isVisible():
            rect = self._calculate_constrained_rect(self.origin, event.pos())
            self.rubber_band.setGeometry(rect)
            # Notify parent dialog of selection update
            if self.selection_callback:
                self.selection_callback(rect)
    
    def mouseReleaseEvent(self, event):
        if self.rubber_band and event.button() == Qt.LeftButton:
            self.crop_rect = self.rubber_band.geometry()
            # Notify parent dialog of selection update
            if self.selection_callback:
                self.selection_callback(self.crop_rect)
            self.update()
    
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
        # #region agent log
        log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".venv", ".cursor", "debug.log")
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"crop_tool.py:_calculate_constrained_rect","message":"Calculating constrained rect","data":{"has_aspect":self.aspect_ratio is not None,"aspect":self.aspect_ratio,"start":{"x":start.x(),"y":start.y()},"end":{"x":end.x(),"y":end.y()}},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"aspect-impl","hypothesisId":"A"}) + "\n")
        except Exception as e:
            pass  # Logging failure shouldn't break functionality
        # #endregion
        
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
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"crop_tool.py:_calculate_constrained_rect","message":"Before bounds check","data":{"rect_before":{"x":new_rect.x(),"y":new_rect.y(),"w":new_rect.width(),"h":new_rect.height()},"img_bounds":{"x":img_rect.x(),"y":img_rect.y(),"w":img_rect.width(),"h":img_rect.height()}},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"aspect-impl","hypothesisId":"C"}) + "\n")
        except: pass
        # #endregion
        
        # Adjust position to stay within bounds, maintaining aspect ratio
        if new_rect.left() < img_rect.left():
            new_rect.moveLeft(img_rect.left())
        if new_rect.top() < img_rect.top():
            new_rect.moveTop(img_rect.top())
        if new_rect.right() > img_rect.right():
            new_rect.moveRight(img_rect.right())
        if new_rect.bottom() > img_rect.bottom():
            new_rect.moveBottom(img_rect.bottom())
        
        # After moving, we may have broken aspect ratio - recalculate if needed
        # But first check if we're still within bounds with correct aspect ratio
        if new_rect.width() > 0 and new_rect.height() > 0:
            current_ratio = new_rect.width() / new_rect.height()
            if abs(current_ratio - target_ratio) > 0.01:  # Allow small floating point errors
                # Aspect ratio was broken by bounds adjustment - fix it
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({"location":"crop_tool.py:_calculate_constrained_rect","message":"Aspect ratio broken by bounds, fixing","data":{"broken_ratio":round(current_ratio, 3),"target_ratio":round(target_ratio, 3)},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"aspect-impl","hypothesisId":"C"}) + "\n")
                except: pass
                # #endregion
                
                # Recalculate dimensions to maintain aspect ratio
                # Use the smaller dimension to ensure we fit
                if new_rect.width() / target_ratio <= new_rect.height():
                    # Constrain by width
                    new_height = int(new_rect.width() / target_ratio)
                    new_rect.setHeight(new_height)
                else:
                    # Constrain by height
                    new_width = int(new_rect.height() * target_ratio)
                    new_rect.setWidth(new_width)
                
                # Re-check bounds after fixing aspect ratio
                if new_rect.right() > img_rect.right():
                    new_rect.moveRight(img_rect.right())
                    # May need to adjust height again
                    new_height = int(new_rect.width() / target_ratio)
                    if new_rect.top() + new_height <= img_rect.bottom():
                        new_rect.setHeight(new_height)
                    else:
                        # Can't fit with this width, constrain by height instead
                        new_rect.setHeight(img_rect.bottom() - new_rect.top())
                        new_rect.setWidth(int(new_rect.height() * target_ratio))
                        new_rect.moveRight(img_rect.right())
                
                if new_rect.bottom() > img_rect.bottom():
                    new_rect.moveBottom(img_rect.bottom())
                    # May need to adjust width again
                    new_width = int(new_rect.height() * target_ratio)
                    if new_rect.left() + new_width <= img_rect.right():
                        new_rect.setWidth(new_width)
                    else:
                        # Can't fit with this height, constrain by width instead
                        new_rect.setWidth(img_rect.right() - new_rect.left())
                        new_rect.setHeight(int(new_rect.width() / target_ratio))
                        new_rect.moveBottom(img_rect.bottom())
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                actual_ratio = new_rect.width() / max(new_rect.height(), 1) if new_rect.height() > 0 else 0
                f.write(json.dumps({"location":"crop_tool.py:_calculate_constrained_rect","message":"Constrained rect calculated","data":{"final_width":new_rect.width(),"final_height":new_rect.height(),"actual_ratio":round(actual_ratio, 3),"target_ratio":round(target_ratio, 3),"ratio_match":abs(actual_ratio - target_ratio) < 0.01},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"aspect-impl","hypothesisId":"A"}) + "\n")
        except: pass
        # #endregion
        
        return new_rect.normalized()
    
    def set_aspect_ratio(self, aspect_ratio: Optional[Tuple[int, int]]):
        """Set the aspect ratio constraint (None for free-form)."""
        # #region agent log
        log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".venv", ".cursor", "debug.log")
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"crop_tool.py:set_aspect_ratio","message":"Setting aspect ratio","data":{"aspect":aspect_ratio},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"aspect-impl","hypothesisId":"B"}) + "\n")
        except Exception as e:
            pass  # Logging failure shouldn't break functionality
        # #endregion
        self.aspect_ratio = aspect_ratio
        # Reset selection when aspect ratio changes
        self.reset_selection()
    
    def reset_selection(self):
        """Clear the crop selection."""
        if self.rubber_band:
            self.rubber_band.hide()
        self.crop_rect = QRect()
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
        scroll.setWidgetResizable(True)
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
    
    def update_crop_size_label(self, rect: QRect):
        """Update the crop size label with current selection dimensions."""
        # #region agent log
        log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".venv", ".cursor", "debug.log")
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"crop_tool.py:update_crop_size_label","message":"Updating crop size label","data":{"rect_valid":rect.isValid(),"rect_empty":rect.isEmpty(),"rect_size":{"w":rect.width(),"h":rect.height()},"aspect_ratio":self.crop_label.aspect_ratio},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"aspect-impl","hypothesisId":"D"}) + "\n")
        except Exception as e:
            pass  # Logging failure shouldn't break functionality
        # #endregion
        
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
                # Calculate actual ratio for verification
                actual_ratio = orig_rect.width() / max(orig_rect.height(), 1)
                target_ratio = w / h
                ratio_match = abs(actual_ratio - target_ratio) < 0.01
                
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({"location":"crop_tool.py:update_crop_size_label","message":"Label updated with aspect ratio","data":{"orig_size":{"w":orig_rect.width(),"h":orig_rect.height()},"target_ratio":round(target_ratio, 3),"actual_ratio":round(actual_ratio, 3),"ratio_match":ratio_match},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"aspect-impl","hypothesisId":"D"}) + "\n")
                except: pass
                # #endregion
                
                self.crop_size_label.setText(
                    f"Crop: {orig_rect.width()} x {orig_rect.height()} ({w}:{h})"
                )
            else:
                self.crop_size_label.setText(
                    f"Crop: {orig_rect.width()} x {orig_rect.height()}"
                )
        
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
    
    def load_image(self):
        """Load the image for editing."""
        self.original_image = Image.open(self.image_path)
        self.update_display()
        
        w, h = self.original_image.size
        self.size_label.setText(f"Original: {w} x {h}")
    
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
        # #region agent log
        log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".venv", ".cursor", "debug.log")
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"location":"crop_tool.py:on_aspect_changed","message":"Aspect ratio changed","data":{"index":index,"selection":self.aspect_combo.currentText()},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"aspect-impl","hypothesisId":"E"}) + "\n")
        except Exception as e:
            pass  # Logging failure shouldn't break functionality
        # #endregion
        
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
