# Cursor AI Prompt: Improve GUI Readability

## Overview

Improve the Kollect-It Product Manager GUI with:
1. **Larger text** throughout the application
2. **Better contrast** between text and backgrounds
3. **Clearer visual hierarchy**
4. **More readable placeholder text**

---

## FILE: `desktop-app/main.py`

### Update the `DarkPalette` Class

Find the `DarkPalette` class (around line 51) and replace the entire class with this improved version:

```python
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
```

---

## Additional Improvements

### Improve the Drop Zone Text

Find the `DropZone` class and update the `setup_ui` method. Look for where the labels are created:

```python
# Find and update these labels in DropZone.setup_ui():

# Main instruction label - make it larger
self.label = QLabel("Drag && Drop Product Folder Here")
self.label.setStyleSheet("""
    QLabel {
        color: #ffffff;
        font-size: 18px;
        font-weight: bold;
    }
""")

# Sub-instruction label
self.sub_label = QLabel("or click Browse to select a folder")
self.sub_label.setStyleSheet("""
    QLabel {
        color: #b4b4b4;
        font-size: 14px;
    }
""")
```

### Improve the Activity Log

Find where the activity log QTextEdit is created (search for "Activity Log" or "log_text"). Update its styling:

```python
# Activity log text area
self.log_text = QTextEdit()
self.log_text.setReadOnly(True)
self.log_text.setMinimumHeight(120)
self.log_text.setStyleSheet("""
    QTextEdit {
        background-color: #0f0f1a;
        border: 2px solid #3d3d5c;
        border-radius: 6px;
        color: #ffffff;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 13px;
        padding: 10px;
        line-height: 1.6;
    }
""")
```

### Update the Log Method for Colored Messages

Find the `log` method in the `KollectItApp` class and update it:

```python
def log(self, message: str, level: str = "info"):
    """Add a message to the activity log with timestamp and color coding."""
    from datetime import datetime
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
    
    self.log_text.append(formatted)
    
    # Auto-scroll to bottom
    scrollbar = self.log_text.verticalScrollBar()
    scrollbar.setValue(scrollbar.maximum())
```

### Improve Section Headers

For the "Product Images" header and similar section titles, add a helper method:

```python
def create_section_header(self, text: str) -> QLabel:
    """Create a styled section header label."""
    label = QLabel(text)
    label.setStyleSheet("""
        QLabel {
            color: #e94560;
            font-size: 16px;
            font-weight: bold;
            padding: 8px 0;
        }
    """)
    return label
```

Then use it when creating headers:

```python
# Instead of:
images_label = QLabel("Product Images")

# Use:
images_label = self.create_section_header("Product Images")
```

---

## Summary of Changes

| Element | Before | After |
|---------|--------|-------|
| Base font size | 13px | 14px |
| Primary text color | #eaeaea | #ffffff |
| Secondary text color | #a0a0a0 | #b4b4b4 |
| Placeholder text | #a0a0a0 | #8888a0 (new muted) |
| Border color | #2d3748 | #3d3d5c (more visible) |
| GroupBox title | 13px | 15px bold |
| Tab labels | Small | 14px bold |
| Button padding | 10px 20px | 12px 24px |
| Input padding | 8px 12px | 10px 14px |
| Progress bar height | 8px | 12px |
| Scrollbar width | 12px | 14px |
| Activity log | Tiny text | 13px monospace |

---

## Testing Checklist

After applying changes:

- [ ] All text is clearly readable
- [ ] Placeholder text is visible but muted
- [ ] Section headers (Product Images, Description, etc.) are prominent
- [ ] Buttons are easy to read and click
- [ ] Dropdown menus have readable text
- [ ] Activity log messages are legible
- [ ] Tab labels are clear
- [ ] Form labels are visible
- [ ] Progress bar percentage is readable
- [ ] Status bar text is visible

---

## Optional: Increase Window Size

If text is still too small, you can also increase the default window size. Find where `setMinimumSize` is called:

```python
# Current
self.setMinimumSize(1400, 900)

# Change to larger
self.setMinimumSize(1600, 1000)
```

---

## Note About rembg Warning

The warning you see:
```
Warning: rembg not installed. Background removal will use fallback method.
```

This is expected on Python 3.14 since rembg requires compiled dependencies. Options:
1. **Accept fallback** - Edge detection will be used (lower quality)
2. **Install Visual Studio Build Tools** - Then `pip install rembg`
3. **Use Python 3.12** - Has pre-built wheels available

The app will work fine without rembg - just with simpler background removal.

---

*Prompt created: December 12, 2025*
*Feature: GUI Readability Improvements*
