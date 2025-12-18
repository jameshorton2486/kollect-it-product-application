"""
Kollect-It Product Manager - Professional Theme
Clean, sophisticated design with excellent readability.
Medium-light background with rich teal and copper accents.
"""


class ModernPalette:
    """Professional theme - sophisticated and inviting."""

    # Backgrounds - Warm slate gray (NOT too dark)
    BACKGROUND = "#2d3142"      # Rich slate (medium dark)
    SURFACE = "#3d4259"         # Lighter surface  
    SURFACE_LIGHT = "#4f5672"   # Elevated elements
    SURFACE_ELEVATED = "#5c6488" # Cards, modals, hovers
    
    # Primary Accent - Rich Copper/Bronze
    PRIMARY = "#d4a574"         # Warm copper
    PRIMARY_DARK = "#b8895c"    # Deep bronze
    PRIMARY_LIGHT = "#e8c4a0"   # Light copper highlight
    
    # Secondary - Ocean Teal
    SECONDARY = "#5fb8b0"       # Rich teal
    SECONDARY_DARK = "#4a9e97"  # Deep teal
    
    # Accent - Soft Coral
    ACCENT = "#e8846b"          # Warm coral
    
    # Text - Clean whites and grays
    TEXT = "#f8f9fa"            # Pure white
    TEXT_SECONDARY = "#c5c9d4"  # Soft gray
    TEXT_MUTED = "#8a90a0"      # Muted gray
    TEXT_DARK = "#2d3142"       # For light backgrounds
    
    # Borders - Clean grays
    BORDER = "#525974"          # Medium border
    BORDER_FOCUS = "#d4a574"    # Copper focus ring
    BORDER_LIGHT = "#6b7394"    # Light border
    
    # Status Colors - Vibrant and clear
    SUCCESS = "#7dd3a8"         # Fresh mint green
    WARNING = "#f4c06b"         # Warm amber
    ERROR = "#e87c7c"           # Soft coral red
    INFO = "#6bb8e8"            # Sky blue

    # Button Specifics
    BTN_SECONDARY_BG = "#4f5672"
    BTN_SECONDARY_HOVER = "#5c6488"
    BTN_UTILITY_HOVER = "#4f5672"

    @classmethod
    def get_stylesheet(cls) -> str:
        """Generate the complete application stylesheet."""
        
        template = """
            /* ================================================
               KOLLECT-IT PROFESSIONAL THEME
               Clean Slate with Copper & Teal Accents
               ================================================ */

            /* GLOBAL STYLES */
            QMainWindow, QWidget {
                background-color: $BACKGROUND$;
                color: $TEXT$;
                font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
                font-size: 14px;
            }
            
            QDialog {
                background-color: $SURFACE$;
            }

            /* GROUP BOXES - Elegant cards with subtle depth */
            QGroupBox {
                background-color: $SURFACE$;
                border: 1px solid $BORDER$;
                border-radius: 12px;
                margin-top: 22px;
                padding: 20px;
                padding-top: 30px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 18px;
                top: 6px;
                padding: 4px 14px;
                color: $PRIMARY$;
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 0.8px;
                text-transform: uppercase;
                background-color: transparent;
            }

            /* BUTTONS - Polished styling */
            QPushButton {
                background-color: $BTN_SECONDARY_BG$;
                color: $TEXT$;
                border: 1px solid $BORDER$;
                border-radius: 8px;
                padding: 11px 22px;
                font-weight: 600;
                font-size: 14px;
                min-height: 22px;
            }

            QPushButton:hover {
                background-color: $BTN_SECONDARY_HOVER$;
                border-color: $BORDER_LIGHT$;
            }

            QPushButton:pressed {
                background-color: $SURFACE$;
                border-color: $PRIMARY$;
            }

            QPushButton:disabled {
                background-color: $SURFACE$;
                color: $TEXT_MUTED$;
                border-color: $BORDER$;
            }

            /* PRIMARY BUTTONS - Copper gradient */
            QPushButton[variant="primary"],
            QPushButton#exportBtn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 $PRIMARY$, stop:1 $PRIMARY_DARK$);
                color: $TEXT_DARK$;
                border: none;
                font-weight: 700;
                letter-spacing: 0.3px;
            }

            QPushButton[variant="primary"]:hover,
            QPushButton#exportBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 $PRIMARY_LIGHT$, stop:1 $PRIMARY$);
            }
            
            QPushButton[variant="primary"]:pressed,
            QPushButton#exportBtn:pressed {
                background-color: $PRIMARY_DARK$;
            }
            
            /* SECONDARY / ACTION BUTTONS - Teal */
            QPushButton[variant="secondary"],
            QPushButton#generateDescBtn,
            QPushButton#generateValuationBtn,
            QPushButton#newProductBtn,
            QPushButton#uploadBtn,
            QPushButton#optimizeBtn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 $SECONDARY$, stop:1 $SECONDARY_DARK$);
                color: $TEXT_DARK$;
                border: none;
                font-weight: 700;
            }

            QPushButton[variant="secondary"]:hover,
            QPushButton#generateDescBtn:hover,
            QPushButton#generateValuationBtn:hover,
            QPushButton#newProductBtn:hover,
            QPushButton#uploadBtn:hover,
            QPushButton#optimizeBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #72ccc4, stop:1 $SECONDARY$);
            }

            /* UTILITY BUTTONS - Subtle outline style */
            QPushButton[variant="utility"],
            QPushButton#cropBtn,
            QPushButton#removeBgBtn,
            QPushButton#analyzeImagesBtn {
                background-color: transparent;
                color: $TEXT_SECONDARY$;
                border: 1px solid $BORDER$;
            }

            QPushButton[variant="utility"]:hover,
            QPushButton#cropBtn:hover,
            QPushButton#removeBgBtn:hover,
            QPushButton#analyzeImagesBtn:hover {
                background-color: $BTN_UTILITY_HOVER$;
                color: $TEXT$;
                border-color: $PRIMARY$;
            }

            /* INPUT FIELDS - Clean and inviting */
            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: $SURFACE_LIGHT$;
                border: 1px solid $BORDER$;
                border-radius: 8px;
                padding: 11px 14px;
                color: $TEXT$;
                selection-background-color: $PRIMARY$;
                selection-color: $TEXT_DARK$;
                font-size: 14px;
            }

            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, 
            QDoubleSpinBox:focus, QComboBox:focus {
                border: 2px solid $BORDER_FOCUS$;
                background-color: $SURFACE_ELEVATED$;
                padding: 10px 13px;
            }
            
            QLineEdit::placeholder, QTextEdit::placeholder {
                color: $TEXT_MUTED$;
            }

            /* COMBO BOX - Modern dropdown */
            QComboBox {
                padding-right: 36px;
            }

            QComboBox::drop-down {
                border: none;
                width: 36px;
                border-left: 1px solid $BORDER$;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
                background-color: transparent;
            }

            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid $TEXT_SECONDARY$;
                margin-right: 12px;
            }
            
            QComboBox::down-arrow:on {
                border-top: none;
                border-bottom: 6px solid $PRIMARY$;
            }

            QComboBox QAbstractItemView {
                background-color: $SURFACE$;
                border: 1px solid $BORDER$;
                border-radius: 8px;
                color: $TEXT$;
                outline: none;
                padding: 8px;
            }

            QComboBox QAbstractItemView::item {
                padding: 11px 16px;
                border-radius: 6px;
                margin: 2px;
            }

            QComboBox QAbstractItemView::item:hover,
            QComboBox QAbstractItemView::item:selected {
                background-color: $SURFACE_LIGHT$;
                color: $PRIMARY$;
            }

            /* SPIN BOXES */
            QSpinBox::up-button, QDoubleSpinBox::up-button,
            QSpinBox::down-button, QDoubleSpinBox::down-button {
                background-color: transparent;
                border: none;
                width: 28px;
                border-radius: 4px;
            }

            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: $SURFACE_ELEVATED$;
            }
            
            /* PROGRESS BAR - Copper fill */
            QProgressBar {
                background-color: $SURFACE_LIGHT$;
                border: 1px solid $BORDER$;
                border-radius: 10px;
                height: 18px;
                text-align: center;
                color: $TEXT$;
                font-size: 12px;
                font-weight: 600;
            }

            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 $PRIMARY_DARK$, stop:0.5 $PRIMARY$, stop:1 $PRIMARY_LIGHT$);
                border-radius: 9px;
            }

            /* TAB WIDGET - Clean underlined tabs */
            QTabWidget::pane {
                background-color: $SURFACE$;
                border: 1px solid $BORDER$;
                border-radius: 12px;
                top: -1px; 
            }

            QTabBar::tab {
                background-color: transparent;
                color: $TEXT_SECONDARY$;
                padding: 14px 28px;
                margin-right: 4px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                font-weight: 600;
                border-bottom: 3px solid transparent;
            }

            QTabBar::tab:selected {
                background-color: $SURFACE$;
                color: $PRIMARY$;
                border-bottom: 3px solid $PRIMARY$;
            }

            QTabBar::tab:hover:!selected {
                background-color: $SURFACE_LIGHT$;
                color: $TEXT$;
            }

            /* SCROLL BARS - Sleek minimal */
            QScrollBar:vertical {
                background-color: $SURFACE$;
                width: 14px;
                margin: 4px 2px;
                border-radius: 7px;
            }

            QScrollBar::handle:vertical {
                background-color: $BORDER$;
                border-radius: 5px;
                min-height: 45px;
                margin: 2px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: $PRIMARY$;
            }
            
            QScrollBar:horizontal {
                background-color: $SURFACE$;
                height: 14px;
                margin: 2px 4px;
                border-radius: 7px;
            }

            QScrollBar::handle:horizontal {
                background-color: $BORDER$;
                border-radius: 5px;
                min-width: 45px;
                margin: 2px;
            }

            QScrollBar::handle:horizontal:hover {
                background-color: $PRIMARY$;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                height: 0px;
                width: 0px;
            }
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }

            /* CHECKBOXES - Modern toggle style */
            QCheckBox {
                spacing: 12px;
                color: $TEXT$;
                font-size: 14px;
            }

            QCheckBox::indicator {
                width: 22px;
                height: 22px;
                border-radius: 6px;
                border: 2px solid $BORDER$;
                background-color: $SURFACE_LIGHT$;
            }
            
            QCheckBox::indicator:hover {
                border-color: $PRIMARY$;
                background-color: $SURFACE_ELEVATED$;
            }

            QCheckBox::indicator:checked {
                background-color: $PRIMARY$;
                border-color: $PRIMARY$;
            }
            
            /* SLIDERS - Copper accent */
            QSlider::groove:horizontal {
                border: none;
                height: 8px;
                background: $SURFACE_LIGHT$;
                border-radius: 4px;
            }

            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 $PRIMARY_LIGHT$, stop:1 $PRIMARY$);
                border: 2px solid $PRIMARY_DARK$;
                width: 20px;
                height: 20px;
                margin: -7px 0;
                border-radius: 11px;
            }
            
            QSlider::handle:horizontal:hover {
                background: $PRIMARY_LIGHT$;
                border-color: $PRIMARY$;
            }
            
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 $SECONDARY_DARK$, stop:1 $SECONDARY$);
                border-radius: 4px;
            }

            /* MENUS - Elegant dropdowns */
            QMenuBar {
                background-color: $SURFACE$;
                border-bottom: 1px solid $BORDER$;
                padding: 6px;
            }
            
            QMenuBar::item {
                padding: 10px 16px;
                border-radius: 6px;
                color: $TEXT_SECONDARY$;
            }
            
            QMenuBar::item:selected {
                background-color: $SURFACE_LIGHT$;
                color: $TEXT$;
            }
            
            QMenu {
                background-color: $SURFACE$;
                border: 1px solid $BORDER$;
                border-radius: 10px;
                padding: 8px;
            }
            
            QMenu::item {
                padding: 12px 28px;
                border-radius: 6px;
            }
            
            QMenu::item:selected {
                background-color: $PRIMARY$;
                color: $TEXT_DARK$;
            }
            
            QMenu::separator {
                height: 1px;
                background-color: $BORDER$;
                margin: 8px 14px;
            }
            
            /* STATUS BAR - Clean footer */
            QStatusBar {
                background-color: $SURFACE$;
                border-top: 1px solid $BORDER$;
                color: $TEXT_SECONDARY$;
                font-size: 13px;
                padding: 6px;
            }
            
            /* TOOLBAR */
            QToolBar {
                background-color: $SURFACE$;
                border-bottom: 1px solid $BORDER$;
                spacing: 14px;
                padding: 10px;
            }
            
            QToolButton {
                border-radius: 8px;
                padding: 10px;
                color: $TEXT$;
            }
            
            QToolButton:hover {
                background-color: $SURFACE_LIGHT$;
            }
            
            /* LABELS */
            QLabel {
                color: $TEXT$;
            }
            
            /* ACTIVITY LOG - Terminal/Console style */
            QTextEdit#activityLog {
                background-color: #232736;
                border: 1px solid $BORDER$;
                border-radius: 10px;
                font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
                font-size: 13px;
                color: #a8b5c8;
                padding: 12px;
                line-height: 1.5;
            }
            
            /* LIST WIDGET */
            QListWidget {
                background-color: $SURFACE$;
                border: 1px solid $BORDER$;
                border-radius: 10px;
                padding: 8px;
            }
            
            QListWidget::item {
                padding: 12px;
                border-radius: 8px;
                margin: 3px;
            }
            
            QListWidget::item:selected {
                background-color: $PRIMARY$;
                color: $TEXT_DARK$;
            }
            
            QListWidget::item:hover:!selected {
                background-color: $SURFACE_LIGHT$;
            }
            
            /* FRAME - For image containers */
            QFrame {
                border-radius: 10px;
            }
            
            /* SCROLL AREA */
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            
            /* TOOL TIP - Floating labels */
            QToolTip {
                background-color: $SURFACE_ELEVATED$;
                color: $TEXT$;
                border: 1px solid $BORDER$;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
            }
            
            /* SPLITTER */
            QSplitter::handle {
                background-color: $BORDER$;
            }
            
            QSplitter::handle:horizontal {
                width: 3px;
            }
            
            QSplitter::handle:vertical {
                height: 3px;
            }
            
            QSplitter::handle:hover {
                background-color: $PRIMARY$;
            }
            
            /* MESSAGE BOX */
            QMessageBox {
                background-color: $SURFACE$;
            }
            
            QMessageBox QLabel {
                color: $TEXT$;
                font-size: 14px;
            }
            
            QMessageBox QPushButton {
                min-width: 90px;
            }
        """
        
        replacements = {
            "$BACKGROUND$": cls.BACKGROUND,
            "$SURFACE$": cls.SURFACE,
            "$SURFACE_LIGHT$": cls.SURFACE_LIGHT,
            "$SURFACE_ELEVATED$": cls.SURFACE_ELEVATED,
            "$PRIMARY$": cls.PRIMARY,
            "$PRIMARY_DARK$": cls.PRIMARY_DARK,
            "$PRIMARY_LIGHT$": cls.PRIMARY_LIGHT,
            "$SECONDARY$": cls.SECONDARY,
            "$SECONDARY_DARK$": cls.SECONDARY_DARK,
            "$ACCENT$": cls.ACCENT,
            "$TEXT$": cls.TEXT,
            "$TEXT_SECONDARY$": cls.TEXT_SECONDARY,
            "$TEXT_MUTED$": cls.TEXT_MUTED,
            "$TEXT_DARK$": cls.TEXT_DARK,
            "$BORDER$": cls.BORDER,
            "$BORDER_FOCUS$": cls.BORDER_FOCUS,
            "$BORDER_LIGHT$": cls.BORDER_LIGHT,
            "$SUCCESS$": cls.SUCCESS,
            "$WARNING$": cls.WARNING,
            "$ERROR$": cls.ERROR,
            "$INFO$": cls.INFO,
            "$BTN_SECONDARY_BG$": cls.BTN_SECONDARY_BG,
            "$BTN_SECONDARY_HOVER$": cls.BTN_SECONDARY_HOVER,
            "$BTN_UTILITY_HOVER$": cls.BTN_UTILITY_HOVER,
        }
        
        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)
            
        return result


def get_color(name: str) -> str:
    """Get a color value by name from the palette."""
    return getattr(ModernPalette, name.upper(), ModernPalette.TEXT)
