"""
Kollect-It Product Manager - Professional SaaS Theme
Modern, high-contrast dark theme with vibrant teal accents.

Design Philosophy:
- Deep charcoal backgrounds with clear visual hierarchy
- High-contrast text for excellent readability
- Vibrant teal/cyan accent for primary actions
- Clean spacing and modern rounded corners
- Subtle shadows and glows for depth
"""


class ModernPalette:
    """
    Professional SaaS Dashboard Theme
    High contrast, modern, accessible design
    """

    # ============================================
    # BACKGROUNDS - Deep charcoal with clear layers
    # ============================================
    BACKGROUND = "#0f0f0f"          # Deepest background (almost black)
    SURFACE = "#1a1a1a"             # Card/panel background
    SURFACE_ELEVATED = "#242424"    # Elevated elements (inputs, dropdowns)
    SURFACE_HOVER = "#2d2d2d"       # Hover states
    SURFACE_ACTIVE = "#333333"      # Active/pressed states

    # ============================================
    # PRIMARY ACCENT - Vibrant Teal/Cyan
    # ============================================
    PRIMARY = "#00d4aa"             # Main accent (vibrant teal)
    PRIMARY_DARK = "#00b894"        # Darker teal (hover)
    PRIMARY_LIGHT = "#55efc4"       # Lighter teal (highlights)
    PRIMARY_GLOW = "rgba(0, 212, 170, 0.3)"  # Focus glow

    # ============================================
    # SECONDARY ACCENT - Electric Blue
    # ============================================
    SECONDARY = "#0984e3"           # Electric blue
    SECONDARY_DARK = "#0770c2"      # Darker blue
    SECONDARY_LIGHT = "#74b9ff"     # Lighter blue

    # ============================================
    # TEXT COLORS - High contrast for readability
    # ============================================
    TEXT_PRIMARY = "#ffffff"        # Pure white for headers
    TEXT_SECONDARY = "#e0e0e0"      # Light gray for labels
    TEXT_MUTED = "#9e9e9e"          # Muted gray for hints
    TEXT_DISABLED = "#616161"       # Disabled text
    TEXT_DARK = "#121212"           # Dark text on light backgrounds

    # ============================================
    # BORDERS - Subtle definition
    # ============================================
    BORDER = "#333333"              # Standard border
    BORDER_LIGHT = "#444444"        # Lighter border
    BORDER_FOCUS = "#00d4aa"        # Focus border (teal)

    # ============================================
    # STATUS COLORS - Clear and distinct
    # ============================================
    SUCCESS = "#00b894"             # Green
    SUCCESS_BG = "rgba(0, 184, 148, 0.15)"
    WARNING = "#fdcb6e"             # Yellow
    WARNING_BG = "rgba(253, 203, 110, 0.15)"
    ERROR = "#e74c3c"               # Red
    ERROR_BG = "rgba(231, 76, 60, 0.15)"
    INFO = "#74b9ff"                # Blue
    INFO_BG = "rgba(116, 185, 255, 0.15)"

    # ============================================
    # BUTTON COLORS
    # ============================================
    BTN_PRIMARY_BG = "#00d4aa"
    BTN_PRIMARY_HOVER = "#00b894"
    BTN_PRIMARY_TEXT = "#121212"

    BTN_SECONDARY_BG = "#242424"
    BTN_SECONDARY_HOVER = "#333333"
    BTN_SECONDARY_BORDER = "#444444"

    BTN_GHOST_BG = "transparent"
    BTN_GHOST_HOVER = "#2d2d2d"
    BTN_GHOST_BORDER = "#444444"

    BTN_SUCCESS_BG = "#00b894"
    BTN_SUCCESS_HOVER = "#00a383"
    
    BTN_DANGER_BG = "#e74c3c"
    BTN_DANGER_HOVER = "#c0392b"

    @classmethod
    def get_color(cls, name: str) -> str:
        """Get a color value by name."""
        return getattr(cls, name.upper(), cls.TEXT_PRIMARY)

    @classmethod
    def get_stylesheet(cls) -> str:
        return f"""
            /* ============================================
               GLOBAL FOUNDATION
               Clean, modern base styles
               ============================================ */
            
            * {{
                font-family: 'Segoe UI', 'Inter', 'SF Pro Display', -apple-system, sans-serif;
            }}
            
            QMainWindow {{
                background-color: {cls.BACKGROUND};
            }}
            
            QWidget {{
                background-color: transparent;
                color: {cls.TEXT_PRIMARY};
                font-size: 14px;
                outline: none;
            }}

            /* ============================================
               GROUP BOXES - Card-style containers
               ============================================ */
            QGroupBox {{
                background-color: {cls.SURFACE};
                border: 1px solid {cls.BORDER};
                border-radius: 10px;
                margin-top: 20px;
                padding: 20px;
                padding-top: 35px;
                font-size: 14px;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                top: 6px;
                padding: 4px 12px;
                color: {cls.TEXT_PRIMARY};
                font-size: 15px;
                font-weight: 600;
                letter-spacing: 0.3px;
                background-color: transparent;
            }}

            /* ============================================
               BUTTONS - Clear visual hierarchy
               ============================================ */
            
            /* Default button style (secondary) */
            QPushButton {{
                background-color: {cls.BTN_SECONDARY_BG};
                color: {cls.TEXT_PRIMARY};
                border: 1px solid {cls.BTN_SECONDARY_BORDER};
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
                min-height: 22px;
            }}

            QPushButton:hover {{
                background-color: {cls.BTN_SECONDARY_HOVER};
                border-color: {cls.BORDER_LIGHT};
            }}

            QPushButton:pressed {{
                background-color: {cls.SURFACE_ACTIVE};
            }}

            QPushButton:disabled {{
                background-color: {cls.SURFACE};
                color: {cls.TEXT_DISABLED};
                border-color: {cls.BORDER};
            }}

            /* PRIMARY BUTTONS - Vibrant teal, main actions */
            QPushButton[primary="true"],
            QPushButton#generateDescBtn,
            QPushButton#generateValuationBtn,
            QPushButton#analyzeImagesBtn {{
                background-color: {cls.BTN_PRIMARY_BG};
                color: {cls.BTN_PRIMARY_TEXT};
                border: none;
                font-weight: 700;
            }}

            QPushButton[primary="true"]:hover,
            QPushButton#generateDescBtn:hover,
            QPushButton#generateValuationBtn:hover,
            QPushButton#analyzeImagesBtn:hover {{
                background-color: {cls.BTN_PRIMARY_HOVER};
            }}

            QPushButton[primary="true"]:pressed,
            QPushButton#generateDescBtn:pressed,
            QPushButton#generateValuationBtn:pressed,
            QPushButton#analyzeImagesBtn:pressed {{
                background-color: {cls.PRIMARY_DARK};
            }}

            /* SUCCESS BUTTONS - Green, positive actions */
            QPushButton[success="true"],
            QPushButton#uploadBtn,
            QPushButton#exportBtn,
            QPushButton#newProductBtn {{
                background-color: {cls.BTN_SUCCESS_BG};
                color: {cls.TEXT_DARK};
                border: none;
                font-weight: 700;
            }}

            QPushButton[success="true"]:hover,
            QPushButton#uploadBtn:hover,
            QPushButton#exportBtn:hover,
            QPushButton#newProductBtn:hover {{
                background-color: {cls.BTN_SUCCESS_HOVER};
            }}

            /* GHOST/OUTLINE BUTTONS - Secondary actions */
            QPushButton[ghost="true"],
            QPushButton#cropBtn,
            QPushButton#removeBgBtn,
            QPushButton#optimizeBtn {{
                background-color: transparent;
                color: {cls.TEXT_SECONDARY};
                border: 1px solid {cls.BTN_GHOST_BORDER};
            }}

            QPushButton[ghost="true"]:hover,
            QPushButton#cropBtn:hover,
            QPushButton#removeBgBtn:hover,
            QPushButton#optimizeBtn:hover {{
                background-color: {cls.BTN_GHOST_HOVER};
                color: {cls.TEXT_PRIMARY};
                border-color: {cls.PRIMARY};
            }}

            /* DANGER BUTTONS */
            QPushButton[danger="true"] {{
                background-color: {cls.BTN_DANGER_BG};
                color: white;
                border: none;
            }}

            QPushButton[danger="true"]:hover {{
                background-color: {cls.BTN_DANGER_HOVER};
            }}

            /* ============================================
               INPUT FIELDS - High contrast with focus glow
               ============================================ */
            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox {{
                background-color: {cls.SURFACE_ELEVATED};
                border: 1px solid {cls.BORDER};
                border-radius: 6px;
                padding: 12px 14px;
                color: {cls.TEXT_PRIMARY};
                font-size: 14px;
                min-height: 22px;
                selection-background-color: {cls.PRIMARY};
                selection-color: {cls.TEXT_DARK};
            }}

            QLineEdit:hover, QTextEdit:hover, 
            QSpinBox:hover, QDoubleSpinBox:hover {{
                border-color: {cls.BORDER_LIGHT};
            }}

            QLineEdit:focus, QTextEdit:focus, 
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border: 2px solid {cls.PRIMARY};
                padding: 11px 13px;
                background-color: {cls.SURFACE_HOVER};
            }}

            QLineEdit::placeholder, QTextEdit::placeholder {{
                color: {cls.TEXT_MUTED};
            }}

            /* ============================================
               COMBO BOX - Modern dropdown
               ============================================ */
            QComboBox {{
                background-color: {cls.SURFACE_ELEVATED};
                border: 1px solid {cls.BORDER};
                border-radius: 6px;
                padding: 12px 14px;
                padding-right: 35px;
                color: {cls.TEXT_PRIMARY};
                font-size: 14px;
                min-height: 22px;
            }}

            QComboBox:hover {{
                border-color: {cls.BORDER_LIGHT};
            }}

            QComboBox:focus {{
                border: 2px solid {cls.PRIMARY};
                padding: 11px 13px;
                padding-right: 34px;
            }}

            QComboBox::drop-down {{
                border: none;
                width: 35px;
                background: transparent;
            }}

            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {cls.TEXT_SECONDARY};
                margin-right: 12px;
            }}

            QComboBox::down-arrow:on {{
                border-top: 6px solid {cls.PRIMARY};
            }}

            QComboBox QAbstractItemView {{
                background-color: {cls.SURFACE};
                border: 1px solid {cls.BORDER};
                border-radius: 8px;
                color: {cls.TEXT_PRIMARY};
                padding: 6px;
                outline: none;
            }}

            QComboBox QAbstractItemView::item {{
                padding: 10px 14px;
                min-height: 32px;
                border-radius: 4px;
                margin: 2px;
            }}

            QComboBox QAbstractItemView::item:hover {{
                background-color: {cls.SURFACE_HOVER};
            }}

            QComboBox QAbstractItemView::item:selected {{
                background-color: {cls.PRIMARY};
                color: {cls.TEXT_DARK};
            }}

            /* ============================================
               SPIN BOXES - Number inputs
               ============================================ */
            QSpinBox::up-button, QDoubleSpinBox::up-button {{
                background-color: {cls.SURFACE_HOVER};
                border: none;
                border-top-right-radius: 5px;
                width: 24px;
            }}

            QSpinBox::down-button, QDoubleSpinBox::down-button {{
                background-color: {cls.SURFACE_HOVER};
                border: none;
                border-bottom-right-radius: 5px;
                width: 24px;
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
               PROGRESS BAR - Thin, modern, gradient
               ============================================ */
            QProgressBar {{
                background-color: {cls.SURFACE_ELEVATED};
                border: none;
                border-radius: 4px;
                height: 8px;
                text-align: center;
                font-size: 0px;
            }}

            QProgressBar::chunk {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {cls.PRIMARY_DARK},
                    stop:0.5 {cls.PRIMARY},
                    stop:1 {cls.PRIMARY_LIGHT}
                );
                border-radius: 4px;
            }}

            /* ============================================
               TABS - Clean underlined style
               ============================================ */
            QTabWidget::pane {{
                background-color: {cls.SURFACE};
                border: 1px solid {cls.BORDER};
                border-radius: 10px;
                top: -1px;
            }}

            QTabBar::tab {{
                background-color: transparent;
                color: {cls.TEXT_MUTED};
                padding: 14px 28px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                border: none;
                border-bottom: 3px solid transparent;
            }}

            QTabBar::tab:hover {{
                color: {cls.TEXT_SECONDARY};
                background-color: {cls.SURFACE_HOVER};
            }}

            QTabBar::tab:selected {{
                color: {cls.PRIMARY};
                background-color: {cls.SURFACE};
                border-bottom: 3px solid {cls.PRIMARY};
            }}

            /* ============================================
               SCROLL BARS - Minimal, modern
               ============================================ */
            QScrollBar:vertical {{
                background-color: transparent;
                width: 10px;
                margin: 4px 2px;
            }}

            QScrollBar::handle:vertical {{
                background-color: {cls.BORDER};
                border-radius: 5px;
                min-height: 40px;
            }}

            QScrollBar::handle:vertical:hover {{
                background-color: {cls.PRIMARY};
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}

            QScrollBar:horizontal {{
                background-color: transparent;
                height: 10px;
                margin: 2px 4px;
            }}

            QScrollBar::handle:horizontal {{
                background-color: {cls.BORDER};
                border-radius: 5px;
                min-width: 40px;
            }}

            QScrollBar::handle:horizontal:hover {{
                background-color: {cls.PRIMARY};
            }}

            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}

            /* ============================================
               LABELS - Clear hierarchy
               ============================================ */
            QLabel {{
                color: {cls.TEXT_SECONDARY};
                font-size: 14px;
                background: transparent;
            }}

            /* ============================================
               CHECKBOXES
               ============================================ */
            QCheckBox {{
                color: {cls.TEXT_SECONDARY};
                spacing: 10px;
                font-size: 14px;
            }}

            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid {cls.BORDER};
                background-color: {cls.SURFACE_ELEVATED};
            }}

            QCheckBox::indicator:hover {{
                border-color: {cls.PRIMARY};
            }}

            QCheckBox::indicator:checked {{
                background-color: {cls.PRIMARY};
                border-color: {cls.PRIMARY};
            }}

            /* ============================================
               SLIDERS
               ============================================ */
            QSlider::groove:horizontal {{
                height: 6px;
                background-color: {cls.SURFACE_ELEVATED};
                border-radius: 3px;
            }}

            QSlider::handle:horizontal {{
                width: 18px;
                height: 18px;
                margin: -6px 0;
                background-color: {cls.PRIMARY};
                border-radius: 9px;
                border: 2px solid {cls.PRIMARY_DARK};
            }}

            QSlider::handle:horizontal:hover {{
                background-color: {cls.PRIMARY_LIGHT};
            }}

            QSlider::sub-page:horizontal {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {cls.PRIMARY_DARK}, 
                    stop:1 {cls.PRIMARY}
                );
                border-radius: 3px;
            }}

            /* ============================================
               LIST WIDGET
               ============================================ */
            QListWidget {{
                background-color: {cls.SURFACE_ELEVATED};
                border: 1px solid {cls.BORDER};
                border-radius: 8px;
                padding: 6px;
                outline: none;
            }}

            QListWidget::item {{
                padding: 12px;
                border-radius: 6px;
                margin: 2px 0;
            }}

            QListWidget::item:selected {{
                background-color: {cls.PRIMARY};
                color: {cls.TEXT_DARK};
            }}

            QListWidget::item:hover:!selected {{
                background-color: {cls.SURFACE_HOVER};
            }}

            /* ============================================
               TEXT EDIT - Activity Log styling
               ============================================ */
            QTextEdit {{
                background-color: {cls.SURFACE_ELEVATED};
                border: 1px solid {cls.BORDER};
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                line-height: 1.6;
            }}

            QTextEdit#activityLog, QTextEdit[readOnly="true"] {{
                background-color: #0d0d0d;
                border: 1px solid {cls.BORDER};
                font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
                font-size: 13px;
                color: {cls.TEXT_SECONDARY};
            }}

            /* ============================================
               MENU BAR & MENUS
               ============================================ */
            QMenuBar {{
                background-color: {cls.SURFACE};
                color: {cls.TEXT_PRIMARY};
                padding: 6px 8px;
                font-size: 14px;
                border-bottom: 1px solid {cls.BORDER};
            }}

            QMenuBar::item {{
                padding: 8px 16px;
                border-radius: 6px;
            }}

            QMenuBar::item:selected {{
                background-color: {cls.SURFACE_HOVER};
            }}

            QMenu {{
                background-color: {cls.SURFACE};
                border: 1px solid {cls.BORDER};
                border-radius: 10px;
                padding: 8px;
            }}

            QMenu::item {{
                padding: 10px 24px;
                border-radius: 6px;
            }}

            QMenu::item:selected {{
                background-color: {cls.PRIMARY};
                color: {cls.TEXT_DARK};
            }}

            QMenu::separator {{
                height: 1px;
                background-color: {cls.BORDER};
                margin: 8px 12px;
            }}

            /* ============================================
               STATUS BAR
               ============================================ */
            QStatusBar {{
                background-color: {cls.SURFACE};
                color: {cls.TEXT_MUTED};
                font-size: 13px;
                padding: 8px 16px;
                border-top: 1px solid {cls.BORDER};
            }}

            QStatusBar QLabel {{
                color: {cls.TEXT_MUTED};
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
                color: {cls.TEXT_SECONDARY};
                padding: 10px 16px;
                border-radius: 6px;
                font-size: 14px;
            }}

            QToolBar QToolButton:hover {{
                background-color: {cls.SURFACE_HOVER};
                color: {cls.TEXT_PRIMARY};
            }}

            QToolBar QToolButton:pressed {{
                background-color: {cls.PRIMARY};
                color: {cls.TEXT_DARK};
            }}

            /* ============================================
               TOOLTIPS
               ============================================ */
            QToolTip {{
                background-color: {cls.SURFACE};
                color: {cls.TEXT_PRIMARY};
                border: 1px solid {cls.BORDER};
                border-radius: 6px;
                padding: 10px 14px;
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
               FRAMES
               ============================================ */
            QFrame {{
                background-color: {cls.SURFACE};
                border-radius: 10px;
            }}

            QFrame[frameShape="4"], QFrame[frameShape="5"] {{
                background-color: {cls.BORDER};
                max-height: 1px;
            }}

            /* ============================================
               DIALOG
               ============================================ */
            QDialog {{
                background-color: {cls.BACKGROUND};
            }}

            QDialogButtonBox QPushButton {{
                min-width: 90px;
            }}

            /* ============================================
               MESSAGE BOX
               ============================================ */
            QMessageBox {{
                background-color: {cls.SURFACE};
            }}

            QMessageBox QLabel {{
                color: {cls.TEXT_PRIMARY};
            }}

            /* ============================================
               SPLITTER
               ============================================ */
            QSplitter::handle {{
                background-color: {cls.BORDER};
            }}

            QSplitter::handle:horizontal {{
                width: 2px;
                margin: 0 8px;
            }}

            QSplitter::handle:vertical {{
                height: 2px;
                margin: 8px 0;
            }}

            QSplitter::handle:hover {{
                background-color: {cls.PRIMARY};
            }}
        """


# Backwards compatibility
DarkPalette = ModernPalette
SURFACE_ELEVATED = ModernPalette.SURFACE_ELEVATED


def get_color(name: str) -> str:
    """Get a color value by name from the palette."""
    return getattr(ModernPalette, name.upper(), ModernPalette.TEXT_PRIMARY)
