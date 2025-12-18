"""
Kollect-It Product Manager - Modern Theme Module
Dark theme with Gold/Amber accent colors.

Color Scheme: Dark charcoal background with warm gold accents
- Professional, high-end antiques/collectibles aesthetic
- Good contrast and readability
- Consistent visual hierarchy
"""


class ModernPalette:
    """Modern dark theme with gold/amber accents."""

    # ============================================
    # BACKGROUNDS - Deep charcoal tones
    # ============================================
    BACKGROUND = "#1a1b26"       # Main background (deep navy-black)
    SURFACE = "#24283b"          # Card/panel background
    SURFACE_LIGHT = "#2f3349"    # Hover states, elevated surfaces
    SURFACE_DARK = "#16161e"     # Deeper areas (log, code blocks)

    # ============================================
    # PRIMARY ACCENT - Gold/Amber (warm, premium feel)
    # ============================================
    PRIMARY = "#f59e0b"          # Main gold accent
    PRIMARY_DARK = "#d97706"     # Darker gold (hover)
    PRIMARY_LIGHT = "#fbbf24"    # Lighter gold (highlights)

    # ============================================
    # SECONDARY ACCENT - Warm orange
    # ============================================
    SECONDARY = "#ea580c"        # Orange accent
    SECONDARY_DARK = "#c2410c"   # Darker orange

    # ============================================
    # TEXT COLORS
    # ============================================
    TEXT = "#e2e8f0"             # Primary text (soft white)
    TEXT_SECONDARY = "#94a3b8"   # Secondary text (muted)
    TEXT_MUTED = "#64748b"       # Muted/placeholder text
    TEXT_DARK = "#1e293b"        # Dark text (on light backgrounds)

    # ============================================
    # BORDERS
    # ============================================
    BORDER = "#3b4261"           # Standard border
    BORDER_LIGHT = "#4c5578"     # Lighter border
    BORDER_FOCUS = "#f59e0b"     # Focus state (gold)

    # ============================================
    # STATUS COLORS
    # ============================================
    SUCCESS = "#22c55e"          # Green
    SUCCESS_DARK = "#16a34a"
    WARNING = "#eab308"          # Yellow
    ERROR = "#ef4444"            # Red
    ERROR_DARK = "#dc2626"
    INFO = "#3b82f6"             # Blue

    # ============================================
    # BUTTON COLORS - Clear hierarchy
    # ============================================
    # Primary buttons (main actions)
    BTN_PRIMARY_BG = "#f59e0b"
    BTN_PRIMARY_HOVER = "#d97706"
    BTN_PRIMARY_TEXT = "#1a1b26"

    # Secondary buttons (supporting actions)
    BTN_SECONDARY_BG = "#3b4261"
    BTN_SECONDARY_HOVER = "#4c5578"
    BTN_SECONDARY_TEXT = "#e2e8f0"

    # Tertiary/Utility buttons (minor actions)
    BTN_UTILITY_BG = "transparent"
    BTN_UTILITY_BORDER = "#3b4261"
    BTN_UTILITY_HOVER = "#2f3349"

    # Success button (Upload, Export)
    BTN_SUCCESS_BG = "#22c55e"
    BTN_SUCCESS_HOVER = "#16a34a"

    # Danger button
    BTN_DANGER_BG = "#ef4444"
    BTN_DANGER_HOVER = "#dc2626"

    @classmethod
    def get_color(cls, name: str) -> str:
        """Get a color value by name from the palette."""
        return getattr(cls, name.upper(), cls.TEXT)

    @classmethod
    def get_stylesheet(cls) -> str:
        return f"""
            /* ============================================
               GLOBAL STYLES
               ============================================ */
            QMainWindow, QWidget {{
                background-color: {cls.BACKGROUND};
                color: {cls.TEXT};
                font-family: 'Segoe UI', 'SF Pro Display', Arial, sans-serif;
                font-size: 14px;
            }}

            /* ============================================
               GROUP BOXES - Section containers
               ============================================ */
            QGroupBox {{
                background-color: {cls.SURFACE};
                border: 1px solid {cls.BORDER};
                border-radius: 8px;
                margin-top: 14px;
                padding: 14px;
                padding-top: 24px;
                font-weight: 600;
                font-size: 14px;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 14px;
                top: 4px;
                padding: 0 10px;
                color: {cls.PRIMARY};
                font-size: 14px;
                font-weight: bold;
            }}

            /* ============================================
               BUTTONS - Primary (Gold - Main Actions)
               ============================================ */
            QPushButton {{
                background-color: {cls.BTN_SECONDARY_BG};
                color: {cls.TEXT};
                border: 1px solid {cls.BORDER};
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 14px;
                min-height: 20px;
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

            /* Primary action buttons - Gold */
            QPushButton[primary="true"],
            QPushButton#primaryButton {{
                background-color: {cls.PRIMARY};
                color: {cls.TEXT_DARK};
                border: none;
                font-weight: bold;
            }}

            QPushButton[primary="true"]:hover,
            QPushButton#primaryButton:hover {{
                background-color: {cls.PRIMARY_DARK};
            }}

            /* Success buttons - Green */
            QPushButton[success="true"],
            QPushButton#successButton {{
                background-color: {cls.SUCCESS};
                color: {cls.TEXT_DARK};
                border: none;
                font-weight: bold;
            }}

            QPushButton[success="true"]:hover,
            QPushButton#successButton:hover {{
                background-color: {cls.SUCCESS_DARK};
            }}

            /* Danger buttons - Red */
            QPushButton[danger="true"],
            QPushButton#dangerButton {{
                background-color: {cls.ERROR};
                color: white;
                border: none;
            }}

            QPushButton[danger="true"]:hover,
            QPushButton#dangerButton:hover {{
                background-color: {cls.ERROR_DARK};
            }}

            /* ============================================
               INPUT FIELDS
               ============================================ */
            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
                background-color: {cls.SURFACE_DARK};
                border: 1px solid {cls.BORDER};
                border-radius: 6px;
                padding: 10px 12px;
                color: {cls.TEXT};
                font-size: 14px;
                min-height: 20px;
                selection-background-color: {cls.PRIMARY};
                selection-color: {cls.TEXT_DARK};
            }}

            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, 
            QDoubleSpinBox:focus, QComboBox:focus {{
                border: 2px solid {cls.PRIMARY};
                background-color: {cls.SURFACE};
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
                background: transparent;
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
                border-radius: 6px;
                color: {cls.TEXT};
                selection-background-color: {cls.PRIMARY};
                selection-color: {cls.TEXT_DARK};
                padding: 4px;
                outline: none;
            }}

            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                min-height: 28px;
                border-radius: 4px;
            }}

            QComboBox QAbstractItemView::item:hover {{
                background-color: {cls.SURFACE_LIGHT};
            }}

            QComboBox QAbstractItemView::item:selected {{
                background-color: {cls.PRIMARY};
                color: {cls.TEXT_DARK};
            }}

            /* ============================================
               SPIN BOXES - Number inputs
               ============================================ */
            QSpinBox::up-button, QDoubleSpinBox::up-button {{
                background-color: {cls.SURFACE_LIGHT};
                border: none;
                border-top-right-radius: 5px;
                width: 22px;
                subcontrol-position: top right;
            }}

            QSpinBox::down-button, QDoubleSpinBox::down-button {{
                background-color: {cls.SURFACE_LIGHT};
                border: none;
                border-bottom-right-radius: 5px;
                width: 22px;
                subcontrol-position: bottom right;
            }}

            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
                background-color: {cls.PRIMARY};
            }}

            QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 5px solid {cls.TEXT_SECONDARY};
                width: 0; height: 0;
            }}

            QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {cls.TEXT_SECONDARY};
                width: 0; height: 0;
            }}

            /* ============================================
               PROGRESS BAR
               ============================================ */
            QProgressBar {{
                background-color: {cls.SURFACE_DARK};
                border: none;
                border-radius: 6px;
                height: 14px;
                text-align: center;
                font-size: 12px;
                font-weight: bold;
                color: {cls.TEXT};
            }}

            QProgressBar::chunk {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {cls.PRIMARY_DARK},
                    stop:1 {cls.PRIMARY}
                );
                border-radius: 6px;
            }}

            /* ============================================
               LIST WIDGET
               ============================================ */
            QListWidget {{
                background-color: {cls.SURFACE_DARK};
                border: 1px solid {cls.BORDER};
                border-radius: 6px;
                padding: 4px;
                outline: none;
            }}

            QListWidget::item {{
                padding: 10px;
                border-radius: 4px;
                margin: 2px 0;
            }}

            QListWidget::item:selected {{
                background-color: {cls.PRIMARY};
                color: {cls.TEXT_DARK};
            }}

            QListWidget::item:hover:!selected {{
                background-color: {cls.SURFACE_LIGHT};
            }}

            /* ============================================
               TABS
               ============================================ */
            QTabWidget::pane {{
                background-color: {cls.SURFACE};
                border: 1px solid {cls.BORDER};
                border-radius: 8px;
                top: -1px;
            }}

            QTabBar::tab {{
                background-color: transparent;
                color: {cls.TEXT_SECONDARY};
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                border: 1px solid transparent;
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
               SCROLL BARS
               ============================================ */
            QScrollBar:vertical {{
                background-color: {cls.SURFACE_DARK};
                width: 12px;
                border-radius: 6px;
                margin: 2px;
            }}

            QScrollBar::handle:vertical {{
                background-color: {cls.BORDER};
                border-radius: 6px;
                min-height: 30px;
            }}

            QScrollBar::handle:vertical:hover {{
                background-color: {cls.PRIMARY};
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            QScrollBar::horizontal {{
                background-color: {cls.SURFACE_DARK};
                height: 12px;
                border-radius: 6px;
                margin: 2px;
            }}

            QScrollBar::handle:horizontal {{
                background-color: {cls.BORDER};
                border-radius: 6px;
                min-width: 30px;
            }}

            QScrollBar::handle:horizontal:hover {{
                background-color: {cls.PRIMARY};
            }}

            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}

            /* ============================================
               LABELS
               ============================================ */
            QLabel {{
                color: {cls.TEXT};
                font-size: 14px;
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
                background-color: {cls.SURFACE_DARK};
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
                height: 6px;
                background-color: {cls.SURFACE_DARK};
                border-radius: 3px;
            }}

            QSlider::handle:horizontal {{
                width: 18px;
                height: 18px;
                margin: -6px 0;
                background-color: {cls.PRIMARY};
                border-radius: 9px;
            }}

            QSlider::handle:horizontal:hover {{
                background-color: {cls.PRIMARY_LIGHT};
            }}

            QSlider::sub-page:horizontal {{
                background-color: {cls.PRIMARY};
                border-radius: 3px;
            }}

            /* ============================================
               STATUS BAR
               ============================================ */
            QStatusBar {{
                background-color: {cls.SURFACE_DARK};
                color: {cls.TEXT_SECONDARY};
                font-size: 13px;
                padding: 6px 12px;
                border-top: 1px solid {cls.BORDER};
            }}

            /* ============================================
               MENU BAR
               ============================================ */
            QMenuBar {{
                background-color: {cls.SURFACE};
                color: {cls.TEXT};
                padding: 4px;
                font-size: 14px;
                border-bottom: 1px solid {cls.BORDER};
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
                border: 1px solid {cls.BORDER};
                border-radius: 8px;
                padding: 6px;
            }}

            QMenu::item {{
                padding: 10px 24px;
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

            /* ============================================
               TOOLBAR
               ============================================ */
            QToolBar {{
                background-color: {cls.SURFACE};
                border: none;
                spacing: 8px;
                padding: 8px;
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

            QToolBar QToolButton:pressed {{
                background-color: {cls.PRIMARY};
                color: {cls.TEXT_DARK};
            }}

            /* ============================================
               TEXT EDIT - Activity log, descriptions
               ============================================ */
            QTextEdit {{
                font-size: 14px;
                line-height: 1.5;
            }}

            QTextEdit[readOnly="true"] {{
                background-color: {cls.SURFACE_DARK};
            }}

            /* ============================================
               FORM LABELS
               ============================================ */
            QFormLayout QLabel {{
                font-size: 14px;
                font-weight: 500;
                color: {cls.TEXT_SECONDARY};
                min-width: 100px;
            }}

            /* ============================================
               TOOLTIPS
               ============================================ */
            QToolTip {{
                background-color: {cls.SURFACE};
                color: {cls.TEXT};
                border: 1px solid {cls.BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }}

            /* ============================================
               SCROLL AREA
               ============================================ */
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}

            QScrollArea > QWidget > QWidget {{
                background-color: transparent;
            }}

            /* ============================================
               FRAMES (Drop Zone, Image Grid)
               ============================================ */
            QFrame {{
                background-color: {cls.SURFACE};
                border-radius: 8px;
            }}

            /* ============================================
               DIALOG
               ============================================ */
            QDialog {{
                background-color: {cls.BACKGROUND};
            }}

            QDialogButtonBox QPushButton {{
                min-width: 80px;
            }}
        """


# Backwards compatibility alias
DarkPalette = ModernPalette


def get_color(name: str) -> str:
    """Get a color value by name from the palette."""
    return getattr(ModernPalette, name.upper(), ModernPalette.TEXT)
