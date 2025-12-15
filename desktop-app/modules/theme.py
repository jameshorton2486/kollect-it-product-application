#!/usr/bin/env python3
"""
Theme Module
Dark theme color palette and stylesheet for the Kollect-It Product Manager.
"""


class DarkPalette:
    """Dark theme color palette for the application - IMPROVED READABILITY."""

    # Backgrounds - slightly lighter for better contrast
    BACKGROUND = "#1e1e2e"       # Main background
    SURFACE = "#1a1a2e"          # Card/panel background
    SURFACE_LIGHT = "#252542"    # Hover states

    # Primary colors
    PRIMARY = "#e94560"          # Accent color
    PRIMARY_DARK = "#c73e54"     # Darker accent
    SECONDARY = "#0f3460"        # Secondary accent

    # Text colors - IMPROVED CONTRAST
    TEXT = "#ffffff"             # Primary text - pure white
    TEXT_SECONDARY = "#b4b4b4"   # Secondary text - lighter
    TEXT_MUTED = "#8888a0"       # Muted/placeholder text

    # Borders
    BORDER = "#3d3d5c"           # Border color - more visible
    BORDER_FOCUS = "#e94560"     # Focus border

    # Status colors
    SUCCESS = "#4ade80"          # Brighter green
    WARNING = "#fbbf24"          # Brighter yellow
    ERROR = "#f87171"            # Error red
    INFO = "#60a5fa"             # Info blue

    @classmethod
    def get_stylesheet(cls) -> str:
        """Generate the complete application stylesheet."""
        return f"""
            /* ============================================
               GLOBAL STYLES - Larger base font
               ============================================ */
            QMainWindow, QWidget {{
                background-color: {cls.BACKGROUND};
                color: {cls.TEXT};
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
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
                font-size: 17px;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                top: 4px;
                padding: 0 10px;
                color: {cls.PRIMARY};
                font-size: 17px;
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
                font-size: 16px;
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
                font-size: 16px;
                min-height: 20px;
            }}

            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, 
            QDoubleSpinBox:focus, QComboBox:focus {{
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
                font-size: 16px;
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
                font-size: 13px;
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
                font-size: 16px;
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
                font-size: 16px;
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
                font-size: 16px;
            }}

            QLabel.title {{
                font-size: 30px;
                font-weight: bold;
                color: {cls.PRIMARY};
            }}

            QLabel.subtitle {{
                font-size: 18px;
                color: {cls.TEXT_SECONDARY};
            }}

            QLabel.section-header {{
                font-size: 18px;
                font-weight: bold;
                color: {cls.PRIMARY};
            }}

            /* ============================================
               CHECKBOXES
               ============================================ */
            QCheckBox {{
                color: {cls.TEXT};
                spacing: 10px;
                font-size: 16px;
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
                font-size: 15px;
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
                font-size: 16px;
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
                font-size: 16px;
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
                font-size: 16px;
            }}

            QToolBar QToolButton:hover {{
                background-color: {cls.SURFACE_LIGHT};
            }}

            /* ============================================
               TEXT EDIT - Activity log, descriptions
               ============================================ */
            QTextEdit {{
                font-size: 16px;
                line-height: 1.5;
            }}

            /* ============================================
               FORM LABELS - Row labels
               ============================================ */
            QFormLayout QLabel {{
                font-size: 16px;
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
                font-size: 15px;
            }}
        """
