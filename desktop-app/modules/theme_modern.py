"""
Kollect-It Product Manager - Professional Theme
Elegant dark theme with warm amber accents.
14px base font size for readability.
"""


class ModernPalette:
    """Professional dark theme with warm amber/gold accents."""

    # ============================================
    # BACKGROUNDS
    # ============================================
    BACKGROUND = "#1a1d23"
    SURFACE = "#22262e"
    SURFACE_LIGHT = "#2a2f38"
    SURFACE_DARK = "#15171c"

    # ============================================
    # PRIMARY ACCENT - Warm Amber/Gold
    # ============================================
    PRIMARY = "#d4a574"
    PRIMARY_LIGHT = "#e5b989"
    PRIMARY_DARK = "#b8895c"

    # ============================================
    # SECONDARY ACCENT
    # ============================================
    SECONDARY = "#c4956a"
    SECONDARY_DARK = "#a67d52"

    # ============================================
    # TEXT COLORS
    # ============================================
    TEXT = "#e8e6e3"
    TEXT_SECONDARY = "#9ca3af"
    TEXT_MUTED = "#6b7280"
    TEXT_DARK = "#1a1d23"

    # ============================================
    # BORDERS
    # ============================================
    BORDER = "#363b44"
    BORDER_LIGHT = "#464c58"
    BORDER_FOCUS = "#d4a574"

    # ============================================
    # STATUS COLORS
    # ============================================
    SUCCESS = "#7eb77f"
    SUCCESS_DARK = "#5a9a5b"
    WARNING = "#e5c07b"
    WARNING_DARK = "#d4a84b"
    ERROR = "#e06c75"
    ERROR_DARK = "#c55a63"
    INFO = "#61afef"

    # ============================================
    # BUTTON COLORS
    # ============================================
    BTN_PRIMARY_BG = "#d4a574"
    BTN_PRIMARY_HOVER = "#e5b989"
    BTN_PRIMARY_TEXT = "#1a1d23"

    BTN_SECONDARY_BG = "#363b44"
    BTN_SECONDARY_HOVER = "#464c58"
    BTN_SECONDARY_TEXT = "#e8e6e3"

    BTN_SUCCESS_BG = "#d4a574"
    BTN_SUCCESS_HOVER = "#e5b989"
    BTN_SUCCESS_TEXT = "#1a1d23"

    @classmethod
    def get_stylesheet(cls) -> str:
        return f"""
            * {{
                font-family: 'Segoe UI', -apple-system, sans-serif;
                font-size: 14px;
            }}

            QMainWindow, QWidget {{
                background-color: {cls.BACKGROUND};
                color: {cls.TEXT};
                font-size: 14px;
            }}

            QGroupBox {{
                background-color: {cls.SURFACE};
                border: 1px solid {cls.BORDER};
                border-radius: 6px;
                margin-top: 10px;
                padding: 10px;
                padding-top: 22px;
                font-size: 14px;
                font-weight: 600;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                top: 2px;
                padding: 0 8px;
                color: {cls.PRIMARY};
                font-size: 14px;
                font-weight: 600;
            }}

            QPushButton {{
                background-color: {cls.BTN_SECONDARY_BG};
                color: {cls.TEXT};
                border: 1px solid {cls.BORDER};
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
                min-height: 18px;
            }}

            QPushButton:hover {{
                background-color: {cls.BTN_SECONDARY_HOVER};
                border-color: {cls.BORDER_LIGHT};
            }}

            QPushButton:pressed {{
                background-color: {cls.SURFACE_DARK};
            }}

            QPushButton:disabled {{
                background-color: {cls.SURFACE};
                color: {cls.TEXT_MUTED};
                border-color: {cls.BORDER};
            }}

            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
                background-color: {cls.SURFACE_DARK};
                border: 1px solid {cls.BORDER};
                border-radius: 4px;
                padding: 7px 10px;
                color: {cls.TEXT};
                font-size: 14px;
                min-height: 16px;
                selection-background-color: {cls.PRIMARY};
                selection-color: {cls.TEXT_DARK};
            }}

            QLineEdit:focus, QTextEdit:focus, 
            QSpinBox:focus, QDoubleSpinBox:focus, 
            QComboBox:focus {{
                border: 1px solid {cls.PRIMARY};
            }}

            QComboBox {{
                padding-right: 26px;
            }}

            QComboBox::drop-down {{
                border: none;
                width: 26px;
            }}

            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {cls.TEXT_SECONDARY};
                margin-right: 10px;
            }}

            QComboBox QAbstractItemView {{
                background-color: {cls.SURFACE};
                border: 1px solid {cls.BORDER};
                border-radius: 4px;
                padding: 4px;
                font-size: 14px;
                selection-background-color: {cls.PRIMARY};
                selection-color: {cls.TEXT_DARK};
                outline: none;
            }}

            QComboBox QAbstractItemView::item {{
                padding: 6px 10px;
                min-height: 22px;
            }}

            QSpinBox::up-button, QDoubleSpinBox::up-button {{
                background-color: {cls.SURFACE_LIGHT};
                border: none;
                border-top-right-radius: 3px;
                width: 20px;
            }}

            QSpinBox::down-button, QDoubleSpinBox::down-button {{
                background-color: {cls.SURFACE_LIGHT};
                border: none;
                border-bottom-right-radius: 3px;
                width: 20px;
            }}

            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
                background-color: {cls.PRIMARY};
            }}

            QProgressBar {{
                background-color: {cls.SURFACE_DARK};
                border: none;
                border-radius: 5px;
                height: 12px;
                text-align: center;
                font-size: 12px;
                color: {cls.TEXT};
            }}

            QProgressBar::chunk {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {cls.PRIMARY_DARK},
                    stop:1 {cls.PRIMARY}
                );
                border-radius: 5px;
            }}

            QTabWidget::pane {{
                background-color: {cls.SURFACE};
                border: 1px solid {cls.BORDER};
                border-radius: 4px;
                top: -1px;
            }}

            QTabBar::tab {{
                background-color: transparent;
                color: {cls.TEXT_SECONDARY};
                padding: 10px 18px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 14px;
                font-weight: 500;
            }}

            QTabBar::tab:selected {{
                background-color: {cls.SURFACE};
                color: {cls.PRIMARY};
                border: 1px solid {cls.BORDER};
                border-bottom: none;
            }}

            QTabBar::tab:hover:!selected {{
                background-color: {cls.SURFACE_LIGHT};
                color: {cls.TEXT};
            }}

            QScrollBar:vertical {{
                background-color: {cls.SURFACE_DARK};
                width: 12px;
                border-radius: 6px;
                margin: 2px;
            }}

            QScrollBar::handle:vertical {{
                background-color: {cls.BORDER};
                border-radius: 6px;
                min-height: 28px;
            }}

            QScrollBar::handle:vertical:hover {{
                background-color: {cls.PRIMARY};
            }}

            QScrollBar::add-line:vertical, 
            QScrollBar::sub-line:vertical {{
                height: 0;
            }}

            QScrollBar:horizontal {{
                background-color: {cls.SURFACE_DARK};
                height: 12px;
                border-radius: 6px;
                margin: 2px;
            }}

            QScrollBar::handle:horizontal {{
                background-color: {cls.BORDER};
                border-radius: 6px;
                min-width: 28px;
            }}

            QScrollBar::handle:horizontal:hover {{
                background-color: {cls.PRIMARY};
            }}

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{
                width: 0;
            }}

            QLabel {{
                color: {cls.TEXT};
                font-size: 14px;
                background: transparent;
            }}

            QCheckBox {{
                color: {cls.TEXT};
                spacing: 8px;
                font-size: 14px;
            }}

            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid {cls.BORDER};
                background-color: {cls.SURFACE_DARK};
            }}

            QCheckBox::indicator:checked {{
                background-color: {cls.PRIMARY};
                border-color: {cls.PRIMARY};
            }}

            QSlider::groove:horizontal {{
                height: 6px;
                background-color: {cls.SURFACE_DARK};
                border-radius: 3px;
            }}

            QSlider::handle:horizontal {{
                width: 16px;
                height: 16px;
                margin: -5px 0;
                background-color: {cls.PRIMARY};
                border-radius: 8px;
            }}

            QSlider::sub-page:horizontal {{
                background-color: {cls.PRIMARY};
                border-radius: 3px;
            }}

            QStatusBar {{
                background-color: {cls.SURFACE_DARK};
                color: {cls.TEXT_SECONDARY};
                font-size: 13px;
                padding: 5px 10px;
                border-top: 1px solid {cls.BORDER};
            }}

            QMenuBar {{
                background-color: {cls.SURFACE};
                color: {cls.TEXT};
                padding: 4px;
                font-size: 14px;
                border-bottom: 1px solid {cls.BORDER};
            }}

            QMenuBar::item {{
                padding: 6px 12px;
                border-radius: 4px;
            }}

            QMenuBar::item:selected {{
                background-color: {cls.SURFACE_LIGHT};
            }}

            QMenu {{
                background-color: {cls.SURFACE};
                border: 1px solid {cls.BORDER};
                border-radius: 6px;
                padding: 6px;
                font-size: 14px;
            }}

            QMenu::item {{
                padding: 8px 24px;
                border-radius: 4px;
            }}

            QMenu::item:selected {{
                background-color: {cls.PRIMARY};
                color: {cls.TEXT_DARK};
            }}

            QMenu::separator {{
                height: 1px;
                background-color: {cls.BORDER};
                margin: 6px 10px;
            }}

            QToolBar {{
                background-color: {cls.SURFACE};
                border: none;
                spacing: 6px;
                padding: 6px;
                border-bottom: 1px solid {cls.BORDER};
            }}

            QToolBar QToolButton {{
                background-color: transparent;
                color: {cls.TEXT};
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 14px;
            }}

            QToolBar QToolButton:hover {{
                background-color: {cls.SURFACE_LIGHT};
            }}

            QListWidget {{
                background-color: {cls.SURFACE_DARK};
                border: 1px solid {cls.BORDER};
                border-radius: 4px;
                padding: 4px;
                font-size: 14px;
                outline: none;
            }}

            QListWidget::item {{
                padding: 8px 10px;
                border-radius: 4px;
                margin: 2px 0;
            }}

            QListWidget::item:selected {{
                background-color: {cls.PRIMARY};
                color: {cls.TEXT_DARK};
            }}

            QToolTip {{
                background-color: {cls.SURFACE};
                color: {cls.TEXT};
                border: 1px solid {cls.BORDER};
                border-radius: 4px;
                padding: 8px 10px;
                font-size: 13px;
            }}

            QScrollArea {{
                background-color: transparent;
                border: none;
            }}

            QFrame {{
                background-color: {cls.SURFACE};
                border-radius: 6px;
            }}

            QDialog {{
                background-color: {cls.BACKGROUND};
            }}

            QMessageBox {{
                background-color: {cls.BACKGROUND};
            }}

            QMessageBox QLabel {{
                font-size: 14px;
                color: {cls.TEXT};
            }}
        """


def get_color(name: str) -> str:
    """Get a color by name from the palette."""
    return getattr(ModernPalette, name.upper(), '#ffffff')


# Backwards compatibility
DarkPalette = ModernPalette
