"""
Kollect-It Product Manager - Theme Module
Dark theme color palette and stylesheet for the application.

Button Hierarchy:
- Primary: Main action (Export Package, Generate AI) - Pink accent
        try:
        # Build stylesheet using placeholder replacement (no f-strings)
        template = """
            /* GLOBAL STYLES */
            QMainWindow, QWidget {
                background-color: $BACKGROUND$;
                color: $TEXT$;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }

            /* GROUP BOXES */
            QGroupBox {
                background-color: $SURFACE$;
                border: 1px solid $BORDER$;
                border-radius: 6px;
                margin-top: 12px;
                padding: 12px;
                padding-top: 20px;
                font-weight: bold;
                font-size: 13px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                top: 2px;
                padding: 0 8px;
                color: $PRIMARY$;
                font-size: 13px;
                font-weight: bold;
            }

            /* BUTTONS - Default (Secondary) */
            QPushButton {
                background-color: $BTN_SECONDARY_BG$;
                color: $TEXT_SECONDARY$;
                border: 1px solid $BORDER$;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 13px;
                min-height: 18px;
            }

            QPushButton:hover {
                background-color: $BTN_SECONDARY_HOVER$;
                color: $TEXT$;
                border-color: $TEXT_MUTED$;
            }

            QPushButton:pressed {
                background-color: $SURFACE$;
            }

            QPushButton:disabled {
                background-color: #2a2a3a;
                color: #5a5a6a;
                border-color: #3a3a4a;
            }

            /* PRIMARY BUTTONS */
            QPushButton[class="primary"],
            QPushButton#exportBtn,
            QPushButton#generateDescBtn,
            QPushButton#generateValuationBtn,
            QPushButton#newProductBtn {
                background-color: $PRIMARY$;
                color: white;
                border: none;
                font-weight: bold;
            }

            QPushButton[class="primary"]:hover,
            QPushButton#exportBtn:hover,
            QPushButton#generateDescBtn:hover,
            QPushButton#generateValuationBtn:hover,
            QPushButton#newProductBtn:hover {
                background-color: $PRIMARY_DARK$;
                color: white;
            }

            /* UTILITY BUTTONS */
            QPushButton[class="utility"],
            QPushButton#cropBtn,
            QPushButton#removeBgBtn,
            QPushButton#optimizeBtn {
                background-color: transparent;
                color: $TEXT_SECONDARY$;
                border: 1px solid $BORDER$;
            }

            QPushButton[class="utility"]:hover,
            QPushButton#cropBtn:hover,
            QPushButton#removeBgBtn:hover,
            QPushButton#optimizeBtn:hover {
                background-color: $BTN_UTILITY_HOVER$;
                color: $TEXT$;
                border-color: $TEXT_MUTED$;
            }

            /* INPUT FIELDS */
            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: $SURFACE$;
                border: 1px solid $BORDER$;
                border-radius: 4px;
                padding: 6px 10px;
                color: $TEXT$;
                font-size: 13px;
                min-height: 16px;
            }

            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus,
            QDoubleSpinBox:focus, QComboBox:focus {
                border-color: $PRIMARY$;
                background-color: #1e1e32;
            }

            QLineEdit::placeholder, QTextEdit::placeholder {
                color: $TEXT_MUTED$;
            }

            /* COMBO BOX */
            QComboBox {
                padding-right: 24px;
            }

            QComboBox::drop-down {
                border: none;
                width: 24px;
            }

            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid $TEXT$;
                margin-right: 8px;
            }

            QComboBox QAbstractItemView {
                background-color: $SURFACE$;
                border: 1px solid $BORDER$;
                border-radius: 4px;
                color: $TEXT$;
                selection-background-color: $SURFACE_LIGHT$;
                padding: 4px;
                font-size: 13px;
            }

            QComboBox QAbstractItemView::item {
                padding: 6px 10px;
                min-height: 22px;
            }

            QComboBox QAbstractItemView::item:hover {
                background-color: $SURFACE_LIGHT$;
            }

            /* SPIN BOXES */
            QSpinBox::up-button, QDoubleSpinBox::up-button,
            QSpinBox::down-button, QDoubleSpinBox::down-button {
                background-color: $SURFACE_LIGHT$;
                border: none;
                width: 20px;
            }

            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: $PRIMARY$;
            }

            /* PROGRESS BAR */
            QProgressBar {
                background-color: $SURFACE$;
                border: none;
                border-radius: 4px;
                height: 10px;
                text-align: center;
                font-size: 11px;
                color: $TEXT$;
            }

            QProgressBar::chunk {
                background-color: $PRIMARY$;
                border-radius: 4px;
            }

            /* LIST WIDGET */
            QListWidget {
                background-color: $SURFACE$;
                border: 1px solid $BORDER$;
                border-radius: 4px;
                padding: 4px;
                font-size: 13px;
            }

            QListWidget::item {
                padding: 6px;
                border-radius: 3px;
                margin: 1px 0;
            }

            QListWidget::item:selected {
                background-color: $SURFACE_LIGHT$;
                color: $TEXT$;
            }

            QListWidget::item:hover {
                background-color: $SECONDARY$;
            }

            /* TABS */
            QTabWidget::pane {
                background-color: $SURFACE$;
                border: 1px solid $BORDER$;
                border-radius: 6px;
                top: -1px;
            }

            QTabBar::tab {
                background-color: $SURFACE$;
                color: $TEXT_SECONDARY$;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 13px;
                font-weight: bold;
                border: 1px solid transparent;
                border-bottom: none;
            }

            QTabBar::tab:selected {
                background-color: #1f2937;
                color: $PRIMARY$;
                border-color: $BORDER$;
                border-bottom: 2px solid $PRIMARY$;
            }

            QTabBar::tab:hover:!selected {
                background-color: $SURFACE_LIGHT$;
                color: $TEXT$;
            }

            /* SCROLL BARS */
            QScrollBar:vertical {
                background-color: $SURFACE$;
                width: 12px;
                border-radius: 6px;
                margin: 2px;
            }

            QScrollBar::handle:vertical {
                background-color: $BORDER$;
                border-radius: 6px;
                min-height: 30px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: $TEXT_MUTED$;
            }

            QScrollBar:horizontal {
                background-color: $SURFACE$;
                height: 12px;
                border-radius: 6px;
                margin: 2px;
            }

            QScrollBar::handle:horizontal {
                background-color: $BORDER$;
                border-radius: 6px;
                min-width: 30px;
            }

            /* LABELS */
            QLabel {
                color: $TEXT$;
                font-size: 13px;
            }

            /* CHECKBOXES */
            QCheckBox {
                color: $TEXT$;
                spacing: 8px;
                font-size: 13px;
            }

            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 1px solid $BORDER$;
                background-color: $SURFACE$;
            }

            QCheckBox::indicator:checked {
                background-color: $PRIMARY$;
                border-color: $PRIMARY$;
            }

            QCheckBox::indicator:hover {
                border-color: $PRIMARY$;
            }

            /* SLIDERS */
            QSlider::groove:horizontal {
                height: 6px;
                background-color: $SURFACE$;
                border-radius: 3px;
            }

            QSlider::handle:horizontal {
                width: 16px;
                height: 16px;
                margin: -5px 0;
                background-color: $PRIMARY$;
                border-radius: 8px;
            }

            QSlider::handle:horizontal:hover {
                background-color: $PRIMARY_DARK$;
            }

            QSlider::sub-page:horizontal {
                background-color: $PRIMARY$;
                border-radius: 3px;
            }

            /* STATUS BAR */
            QStatusBar {
                background-color: $SURFACE$;
                color: $TEXT$;
                font-size: 12px;
                padding: 4px;
                border-top: 1px solid $BORDER$;
            }

            /* MENU BAR */
            QMenuBar {
                background-color: $SURFACE$;
                color: $TEXT$;
                padding: 4px;
                font-size: 13px;
            }

            QMenuBar::item {
                padding: 6px 12px;
                border-radius: 4px;
            }

            QMenuBar::item:selected {
                background-color: $SURFACE_LIGHT$;
            }

            QMenu {
                background-color: $SURFACE$;
                border: 1px solid $BORDER$;
                border-radius: 6px;
                padding: 4px;
                font-size: 13px;
            }

            QMenu::item {
                padding: 8px 24px;
                border-radius: 4px;
            }

            QMenu::item:selected {
                background-color: $SURFACE_LIGHT$;
            }

            QMenu::separator {
                height: 1px;
                background-color: $BORDER$;
                margin: 4px 8px;
            }

            /* TOOLBAR */
            QToolBar {
                background-color: $SURFACE$;
                border: none;
                spacing: 8px;
                padding: 6px;
                border-bottom: 1px solid $BORDER$;
            }

            QToolBar QToolButton {
                background-color: transparent;
                color: $TEXT$;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 13px;
            }

            QToolBar QToolButton:hover {
                background-color: $SURFACE_LIGHT$;
            }

            /* TEXT EDIT */
            QTextEdit {
                font-size: 13px;
                line-height: 1.4;
            }

            QTextEdit#activityLog {
                background-color: #0f172a;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                border: 1px solid $BORDER$;
            }

            /* FORM LABELS */
            QFormLayout QLabel {
                font-size: 13px;
                font-weight: 500;
                color: $TEXT_SECONDARY$;
                min-width: 80px;
            }

            /* TOOLTIPS */
            QToolTip {
                background-color: $SURFACE_LIGHT$;
                color: $TEXT$;
                border: 1px solid $BORDER$;
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
            }
        """

        # Replace placeholders with palette values
        replacements = {
            "$BACKGROUND$": cls.BACKGROUND,
            "$SURFACE$": cls.SURFACE,
            "$SURFACE_LIGHT$": cls.SURFACE_LIGHT,
            "$PRIMARY$": cls.PRIMARY,
            "$PRIMARY_DARK$": cls.PRIMARY_DARK,
            "$SECONDARY$": cls.SECONDARY,
            "$TEXT$": cls.TEXT,
            "$TEXT_SECONDARY$": cls.TEXT_SECONDARY,
            "$TEXT_MUTED$": cls.TEXT_MUTED,
            "$BORDER$": cls.BORDER,
            "$BTN_SECONDARY_BG$": cls.BTN_SECONDARY_BG,
            "$BTN_SECONDARY_HOVER$": cls.BTN_SECONDARY_HOVER,
            "$BTN_UTILITY_HOVER$": cls.BTN_UTILITY_HOVER,
        }
        result = template
        for ph, val in replacements.items():
            result = result.replace(ph, val)
        return result
            /* ============================================
               DROP ZONE
               ============================================ */
            QFrame#dropZone {{{{
                background-color: {cls.SURFACE};
                border: 2px dashed {cls.BORDER};
                border-radius: 10px;
            }}}}

            QFrame#dropZone:hover {{{{
                border-color: {cls.PRIMARY};
            }}}}

            /* ============================================
               IMAGE THUMBNAILS
               ============================================ */
            QLabel#thumbnail {{{{
                background-color: {cls.SURFACE};
                border: 2px solid {cls.BORDER};
                border-radius: 6px;
                padding: 3px;
            }}}}

            QLabel#thumbnail:hover {{{{
                border-color: {cls.PRIMARY};
                background-color: {cls.SURFACE_LIGHT};
            }}}}

            QLabel#thumbnail[selected="true"] {{{{
                border: 3px solid {cls.PRIMARY};
            }}}}
        """
            # Normalize all escaped braces to single braces
            css = template.replace("{{{{", "{").replace("}}}}", "}").replace("{{", "{").replace("}}", "}")
            # Replace palette placeholders like {cls.BACKGROUND} with actual values
            for name in [
                "BACKGROUND","SURFACE","SURFACE_LIGHT","PRIMARY","PRIMARY_DARK","SECONDARY",
                "TEXT","TEXT_SECONDARY","TEXT_MUTED","BORDER","BORDER_FOCUS","SUCCESS",
                "WARNING","ERROR","INFO","BTN_SECONDARY_BG","BTN_SECONDARY_HOVER",
                "BTN_UTILITY_BG","BTN_UTILITY_BORDER","BTN_UTILITY_HOVER"
            ]:
                css = css.replace(f"{{cls.{name}}}", getattr(cls, name))
            return css
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Theme stylesheet build error: {e}")
            return (
                "QWidget {"
                f"background-color: {cls.BACKGROUND};"
                f"color: {cls.TEXT};"
                "font-family: 'Segoe UI', Arial, sans-serif;"
                "font-size: 13px;"
                "}"
                "QPushButton {"
                f"background-color: {cls.BTN_SECONDARY_BG};"
                f"color: {cls.TEXT_SECONDARY};"
                f"border: 1px solid {cls.BORDER};"
                "border-radius: 4px;"
                "padding: 8px 16px;"
                "}"
                "QPushButton#exportBtn, QPushButton#generateDescBtn, QPushButton#generateValuationBtn {"
                f"background-color: {cls.PRIMARY};"
                "color: white;"
                "border: none;"
                "}"
            )
    def get_stylesheet_alt(cls) -> str:
        try:
            css = f"""
            /* ============================================
               GLOBAL STYLES - 13px base font
               ============================================ */
            QMainWindow, QWidget {{{{
                background-color: {cls.BACKGROUND};
                color: {cls.TEXT};
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }}}}

            /* ============================================
               GROUP BOXES - Section containers
               ============================================ */
            QGroupBox {{{{
                background-color: {cls.SURFACE};
                border: 1px solid {cls.BORDER};
                border-radius: 6px;
                margin-top: 12px;
                padding: 12px;
                padding-top: 20px;
                font-weight: bold;
                font-size: 13px;
            }}}}

            QGroupBox::title {{{{
                subcontrol-origin: margin;
                left: 12px;
                top: 2px;
                padding: 0 8px;
                color: {cls.PRIMARY};
                font-size: 13px;
                font-weight: bold;
            }}}}

            /* ============================================
               BUTTONS - Three-Tier Hierarchy
               ============================================ */

            /* Default button style (Secondary) */
            QPushButton {{{{
                background-color: {cls.BTN_SECONDARY_BG};
                color: {cls.TEXT_SECONDARY};
                border: 1px solid {cls.BORDER};
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 13px;
                min-height: 18px;
            }}}}

            QPushButton:hover {{{{
                background-color: {cls.BTN_SECONDARY_HOVER};
                color: {cls.TEXT};
                border-color: {cls.TEXT_MUTED};
            }}}}

            QPushButton:pressed {{{{
                background-color: {cls.SURFACE};
            }}}}

            QPushButton:disabled {{{{
                background-color: #2a2a3a;
                color: #5a5a6a;
                border-color: #3a3a4a;
            }}}}

            /* Primary action buttons - Pink accent */
            QPushButton[class="primary"],
            QPushButton#exportBtn,
            QPushButton#generateDescBtn,
            QPushButton#generateValuationBtn,
            QPushButton#newProductBtn {{{{
                background-color: {cls.PRIMARY};
                color: white;
                border: none;
                font-weight: bold;
            }}}}

            QPushButton[class="primary"]:hover,
            QPushButton#exportBtn:hover,
            QPushButton#generateDescBtn:hover,
            QPushButton#generateValuationBtn:hover,
            QPushButton#newProductBtn:hover {{{{
                background-color: {cls.PRIMARY_DARK};
                color: white;
            }}}}

            QPushButton[class="primary"]:pressed,
            QPushButton#exportBtn:pressed,
            QPushButton#generateDescBtn:pressed,
            QPushButton#generateValuationBtn:pressed,
            QPushButton#newProductBtn:pressed {{{{
                background-color: #a83246;
            }}}}

            /* Utility buttons - Subtle/outline style */
            QPushButton[class="utility"],
            QPushButton#cropBtn,
            QPushButton#removeBgBtn,
            QPushButton#optimizeBtn {{{{
                background-color: transparent;
                color: {cls.TEXT_SECONDARY};
                border: 1px solid {cls.BORDER};
            }}}}

            QPushButton[class="utility"]:hover,
            QPushButton#cropBtn:hover,
            QPushButton#removeBgBtn:hover,
            QPushButton#optimizeBtn:hover {{{{
                background-color: {cls.BTN_UTILITY_HOVER};
                color: {cls.TEXT};
                border-color: {cls.TEXT_MUTED};
            }}}}

            /* ============================================
               INPUT FIELDS
               ============================================ */
            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{{{
                background-color: {cls.SURFACE};
                border: 1px solid {cls.BORDER};
                border-radius: 4px;
                padding: 6px 10px;
                color: {cls.TEXT};
                font-size: 13px;
                min-height: 16px;
            }}}}

            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{{{
                border-color: {cls.PRIMARY};
                background-color: #1e1e32;
            }}}}

            QLineEdit::placeholder, QTextEdit::placeholder {{{{
                color: {cls.TEXT_MUTED};
            }}}}

            /* ============================================
               COMBO BOX - Dropdown styling
               ============================================ */
            QComboBox {{{{
                padding-right: 24px;
            }}}}

            QComboBox::drop-down {{{{
                border: none;
                width: 24px;
            }}}}

            QComboBox::down-arrow {{{{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {cls.TEXT};
                margin-right: 8px;
            }}}}

            QComboBox QAbstractItemView {{{{
                background-color: {cls.SURFACE};
                border: 1px solid {cls.BORDER};
                border-radius: 4px;
                color: {cls.TEXT};
                selection-background-color: {cls.SURFACE_LIGHT};
                padding: 4px;
                font-size: 13px;
            }}}}

            QComboBox QAbstractItemView::item {{{{
                padding: 6px 10px;
                min-height: 22px;
            }}}}

            QComboBox QAbstractItemView::item:hover {{{{
                background-color: {cls.SURFACE_LIGHT};
            }}}}

            /* ============================================
               SPIN BOXES - Number inputs
               ============================================ */
            QSpinBox::up-button, QDoubleSpinBox::up-button,
            QSpinBox::down-button, QDoubleSpinBox::down-button {{{{
                background-color: {cls.SURFACE_LIGHT};
                border: none;
                width: 20px;
            }}}}

            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{{{
                background-color: {cls.PRIMARY};
            }}}}

            /* ============================================
               PROGRESS BAR
               ============================================ */
            QProgressBar {{{{
                background-color: {cls.SURFACE};
                border: none;
                border-radius: 4px;
                height: 10px;
                text-align: center;
                font-size: 11px;
                color: {cls.TEXT};
            }}}}

            QProgressBar::chunk {{{{
                background-color: {cls.PRIMARY};
                border-radius: 4px;
            }}}}

            /* ============================================
               LIST WIDGET - File lists
               ============================================ */
            QListWidget {{{{
                background-color: {cls.SURFACE};
                border: 1px solid {cls.BORDER};
                border-radius: 4px;
                padding: 4px;
                font-size: 13px;
            }}}}

            QListWidget::item {{{{
                padding: 6px;
                border-radius: 3px;
                margin: 1px 0;
            }}}}

            QListWidget::item:selected {{{{
                background-color: {cls.SURFACE_LIGHT};
                color: {cls.TEXT};
            }}}}

            QListWidget::item:hover {{{{
                background-color: {cls.SECONDARY};
            }}}}

            /* ============================================
               TABS - Navigation tabs
               ============================================ */
            QTabWidget::pane {{{{
                background-color: {cls.SURFACE};
                border: 1px solid {cls.BORDER};
                border-radius: 6px;
                top: -1px;
            }}}}

            QTabBar::tab {{{{
                background-color: {cls.SURFACE};
                color: {cls.TEXT_SECONDARY};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 13px;
                font-weight: bold;
                border: 1px solid transparent;
                border-bottom: none;
            }}}}

            QTabBar::tab:selected {{{{
                background-color: #1f2937;
                color: {cls.PRIMARY};
                border-color: {cls.BORDER};
                border-bottom: 2px solid {cls.PRIMARY};
            }}}}

            QTabBar::tab:hover:!selected {{{{
                background-color: {cls.SURFACE_LIGHT};
                color: {cls.TEXT};
            }}}}

            /* ============================================
               SCROLL BARS
               ============================================ */
            QScrollBar:vertical {{{{
                background-color: {cls.SURFACE};
                width: 12px;
                border-radius: 6px;
                margin: 2px;
            }}}}

            QScrollBar::handle:vertical {{{{
                background-color: {cls.BORDER};
                border-radius: 6px;
                min-height: 30px;
            }}}}

            QScrollBar::handle:vertical:hover {{{{
                background-color: {cls.TEXT_MUTED};
            }}}}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{{{
                height: 0px;
            }}}}

            QScrollBar:horizontal {{{{
                background-color: {cls.SURFACE};
                height: 12px;
                border-radius: 6px;
                margin: 2px;
            }}}}

            QScrollBar::handle:horizontal {{{{
                background-color: {cls.BORDER};
                border-radius: 6px;
                min-width: 30px;
            }}}}

            /* ============================================
               LABELS
               ============================================ */
            QLabel {{{{
                color: {cls.TEXT};
                font-size: 13px;
            }}}}

            QLabel[class="title"] {{{{
                font-size: 22px;
                font-weight: bold;
                color: {cls.PRIMARY};
            }}}}

            QLabel[class="subtitle"] {{{{
                font-size: 14px;
                color: {cls.TEXT_SECONDARY};
            }}}}

            QLabel[class="section-header"] {{{{
                font-size: 14px;
                font-weight: bold;
                color: {cls.PRIMARY};
            }}}}

            /* ============================================
               CHECKBOXES
               ============================================ */
            QCheckBox {{{{
                color: {cls.TEXT};
                spacing: 8px;
                font-size: 13px;
            }}}}

            QCheckBox::indicator {{{{
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 1px solid {cls.BORDER};
                background-color: {cls.SURFACE};
            }}}}

            QCheckBox::indicator:checked {{{{
                background-color: {cls.PRIMARY};
                border-color: {cls.PRIMARY};
            }}}}

            QCheckBox::indicator:hover {{{{
                border-color: {cls.PRIMARY};
            }}}}

            /* ============================================
               SLIDERS
               ============================================ */
            QSlider::groove:horizontal {{{{
                height: 6px;
                background-color: {cls.SURFACE};
                border-radius: 3px;
            }}}}

            QSlider::handle:horizontal {{{{
                width: 16px;
                height: 16px;
                margin: -5px 0;
                background-color: {cls.PRIMARY};
                border-radius: 8px;
            }}}}

            QSlider::handle:horizontal:hover {{{{
                background-color: {cls.PRIMARY_DARK};
            }}}}

            QSlider::sub-page:horizontal {{{{
                background-color: {cls.PRIMARY};
                border-radius: 3px;
            }}}}

            /* ============================================
               STATUS BAR
               ============================================ */
            QStatusBar {{{{
                background-color: {cls.SURFACE};
                color: {cls.TEXT};
                font-size: 12px;
                padding: 4px;
                border-top: 1px solid {cls.BORDER};
            }}}}

            /* ============================================
               MENU BAR
               ============================================ */
            QMenuBar {{{{
                background-color: {cls.SURFACE};
                color: {cls.TEXT};
                padding: 4px;
                font-size: 13px;
            }}}}

            QMenuBar::item {{{{
                padding: 6px 12px;
                border-radius: 4px;
            }}}}

            QMenuBar::item:selected {{{{
                background-color: {cls.SURFACE_LIGHT};
            }}}}

            QMenu {{{{
                background-color: {cls.SURFACE};
                border: 1px solid {cls.BORDER};
                border-radius: 6px;
                padding: 4px;
                font-size: 13px;
            }}}}

            QMenu::item {{{{
                padding: 8px 24px;
                border-radius: 4px;
            }}}}

            QMenu::item:selected {{{{
                background-color: {cls.SURFACE_LIGHT};
            }}}}

            QMenu::separator {{{{
                height: 1px;
                background-color: {cls.BORDER};
                margin: 4px 8px;
            }}}}

            /* ============================================
               TOOLBAR
               ============================================ */
            QToolBar {{{{
                background-color: {cls.SURFACE};
                border: none;
                spacing: 8px;
                padding: 6px;
                border-bottom: 1px solid {cls.BORDER};
            }}}}

            QToolBar QToolButton {{{{
                background-color: transparent;
                color: {cls.TEXT};
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 13px;
            }}}}

            QToolBar QToolButton:hover {{{{
                background-color: {cls.SURFACE_LIGHT};
            }}}}

            /* ============================================
               TEXT EDIT - Descriptions
               ============================================ */
            QTextEdit {{{{
                font-size: 13px;
                line-height: 1.4;
            }}}}

            /* Activity Log - Darker, monospace */
            QTextEdit#activityLog {{{{
                background-color: #0f172a;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                border: 1px solid {cls.BORDER};
            }}}}

            /* ============================================
               FORM LABELS - Lighter color
               ============================================ */
            QFormLayout QLabel {{{{
                font-size: 13px;
                font-weight: 500;
                color: {cls.TEXT_SECONDARY};
                min-width: 80px;
            }}}}

            /* ============================================
               TOOLTIPS
               ============================================ */
            QToolTip {{{{
                background-color: {cls.SURFACE_LIGHT};
                color: {cls.TEXT};
                border: 1px solid {cls.BORDER};
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
            }}}}

            /* ============================================
               DROP ZONE
               ============================================ */
            QFrame#dropZone {{{{
                background-color: {cls.SURFACE};
                border: 2px dashed {cls.BORDER};
                border-radius: 10px;
            }}}}

            QFrame#dropZone:hover {{{{
                border-color: {cls.PRIMARY};
            }}}}

            /* ============================================
               IMAGE THUMBNAILS
               ============================================ */
            QLabel#thumbnail {{{{
                background-color: {cls.SURFACE};
                border: 2px solid {cls.BORDER};
                border-radius: 6px;
                padding: 3px;
            }}}}

            QLabel#thumbnail:hover {{{{
                border-color: {cls.PRIMARY};
                background-color: {cls.SURFACE_LIGHT};
            }}}}

            QLabel#thumbnail[selected="true"] {{{{
                border: 3px solid {cls.PRIMARY};
            }}}}
        """
            # Normalize escaped braces to single braces expected by Qt
            css = css.replace("{{{{", "{{").replace("}}}}", "}}")
            return css
        except Exception as e:
            # Fallback minimal stylesheet to keep app running and surface errors
            import logging
            logging.getLogger(__name__).error(f"Theme stylesheet build error: {e}")
            return f"""
                QWidget {{
                    background-color: {cls.BACKGROUND};
                    color: {cls.TEXT};
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 13px;
                }}
                QPushButton {{
                    background-color: {cls.BTN_SECONDARY_BG};
                    color: {cls.TEXT_SECONDARY};
                    border: 1px solid {cls.BORDER};
                    border-radius: 4px;
                    padding: 8px 16px;
                }}
                QPushButton#exportBtn, QPushButton#generateDescBtn, QPushButton#generateValuationBtn {{
                    background-color: {cls.PRIMARY};
                    color: white;
                    border: none;
                }}
            """


# Convenience function for getting colors directly
def get_color(name: str) -> str:
    """Get a color value by name from the palette."""
    return getattr(DarkPalette, name.upper(), DarkPalette.TEXT)


# Clean override: redefine DarkPalette to use placeholder replacement safely
class DarkPalette:
    """Dark theme color palette and stylesheet for the application.

    Clean implementation using string placeholders to avoid f-string brace issues.
    """

    # Backgrounds
    BACKGROUND = "#1e1e2e"
    SURFACE = "#1a1a2e"
    SURFACE_LIGHT = "#252542"

    # Primary colors
    PRIMARY = "#e94560"
    PRIMARY_DARK = "#c73e54"
    SECONDARY = "#0f3460"

    # Text colors
    TEXT = "#ffffff"
    TEXT_SECONDARY = "#b4b4b4"
    TEXT_MUTED = "#8888a0"

    # Borders
    BORDER = "#3d3d5c"
    BORDER_FOCUS = "#e94560"

    # Status colors
    SUCCESS = "#4ade80"
    WARNING = "#fbbf24"
    ERROR = "#f87171"
    INFO = "#60a5fa"

    # Button colors
    BTN_SECONDARY_BG = "#2b3145"
    BTN_SECONDARY_HOVER = "#3a4160"
    BTN_UTILITY_HOVER = "#252542"

    @classmethod
    def get_stylesheet(cls) -> str:
        template = """
            /* GLOBAL STYLES */
            QMainWindow, QWidget {
                background-color: $BACKGROUND$;
                color: $TEXT$;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }

            /* GROUP BOXES */
            QGroupBox {
                background-color: $SURFACE$;
                border: 1px solid $BORDER$;
                border-radius: 6px;
                margin-top: 12px;
                padding: 12px;
                padding-top: 20px;
                font-weight: bold;
                font-size: 13px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                top: 2px;
                padding: 0 8px;
                color: $PRIMARY$;
                font-size: 13px;
                font-weight: bold;
            }

            /* BUTTONS - Default (Secondary) */
            QPushButton {
                background-color: $BTN_SECONDARY_BG$;
                color: $TEXT_SECONDARY$;
                border: 1px solid $BORDER$;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 13px;
                min-height: 18px;
            }

            QPushButton:hover {
                background-color: $BTN_SECONDARY_HOVER$;
                color: $TEXT$;
                border-color: $TEXT_MUTED$;
            }

            QPushButton:pressed {
                background-color: $SURFACE$;
            }

            QPushButton:disabled {
                background-color: #2a2a3a;
                color: #5a5a6a;
                border-color: #3a3a4a;
            }

            /* PRIMARY BUTTONS */
            QPushButton[class="primary"],
            QPushButton#exportBtn,
            QPushButton#generateDescBtn,
            QPushButton#generateValuationBtn,
            QPushButton#newProductBtn {
                background-color: $PRIMARY$;
                color: white;
                border: none;
                font-weight: bold;
            }

            QPushButton[class="primary"]:hover,
            QPushButton#exportBtn:hover,
            QPushButton#generateDescBtn:hover,
            QPushButton#generateValuationBtn:hover,
            QPushButton#newProductBtn:hover {
                background-color: $PRIMARY_DARK$;
                color: white;
            }

            /* UTILITY BUTTONS */
            QPushButton[class="utility"],
            QPushButton#cropBtn,
            QPushButton#removeBgBtn,
            QPushButton#optimizeBtn {
                background-color: transparent;
                color: $TEXT_SECONDARY$;
                border: 1px solid $BORDER$;
            }

            QPushButton[class="utility"]:hover,
            QPushButton#cropBtn:hover,
            QPushButton#removeBgBtn:hover,
            QPushButton#optimizeBtn:hover {
                background-color: $BTN_UTILITY_HOVER$;
                color: $TEXT$;
                border-color: $TEXT_MUTED$;
            }

            /* INPUT FIELDS */
            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: $SURFACE$;
                border: 1px solid $BORDER$;
                border-radius: 4px;
                padding: 6px 10px;
                color: $TEXT$;
                font-size: 13px;
                min-height: 16px;
            }

            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus,
            QDoubleSpinBox:focus, QComboBox:focus {
                border-color: $PRIMARY$;
                background-color: #1e1e32;
            }

            QLineEdit::placeholder, QTextEdit::placeholder {
                color: $TEXT_MUTED$;
            }

            /* COMBO BOX */
            QComboBox {
                padding-right: 24px;
            }

            QComboBox::drop-down {
                border: none;
                width: 24px;
            }

            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid $TEXT$;
                margin-right: 8px;
            }

            QComboBox QAbstractItemView {
                background-color: $SURFACE$;
                border: 1px solid $BORDER$;
                border-radius: 4px;
                color: $TEXT$;
                selection-background-color: $SURFACE_LIGHT$;
                padding: 4px;
                font-size: 13px;
            }

            QComboBox QAbstractItemView::item {
                padding: 6px 10px;
                min-height: 22px;
            }

            QComboBox QAbstractItemView::item:hover {
                background-color: $SURFACE_LIGHT$;
            }

            /* SPIN BOXES */
            QSpinBox::up-button, QDoubleSpinBox::up-button,
            QSpinBox::down-button, QDoubleSpinBox::down-button {
                background-color: $SURFACE_LIGHT$;
                border: none;
                width: 20px;
            }

            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: $PRIMARY$;
            }

            /* PROGRESS BAR */
            QProgressBar {
                background-color: $SURFACE$;
                border: none;
                border-radius: 4px;
                height: 10px;
                text-align: center;
                font-size: 11px;
                color: $TEXT$;
            }

            QProgressBar::chunk {
                background-color: $PRIMARY$;
                border-radius: 4px;
            }

            /* LIST WIDGET */
            QListWidget {
                background-color: $SURFACE$;
                border: 1px solid $BORDER$;
                border-radius: 4px;
                padding: 4px;
                font-size: 13px;
            }

            QListWidget::item {
                padding: 6px;
                border-radius: 3px;
                margin: 1px 0;
            }

            QListWidget::item:selected {
                background-color: $SURFACE_LIGHT$;
                color: $TEXT$;
            }

            QListWidget::item:hover {
                background-color: $SECONDARY$;
            }

            /* TABS */
            QTabWidget::pane {
                background-color: $SURFACE$;
                border: 1px solid $BORDER$;
                border-radius: 6px;
                top: -1px;
            }

            QTabBar::tab {
                background-color: $SURFACE$;
                color: $TEXT_SECONDARY$;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 13px;
                font-weight: bold;
                border: 1px solid transparent;
                border-bottom: none;
            }

            QTabBar::tab:selected {
                background-color: #1f2937;
                color: $PRIMARY$;
                border-color: $BORDER$;
                border-bottom: 2px solid $PRIMARY$;
            }

            QTabBar::tab:hover:!selected {
                background-color: $SURFACE_LIGHT$;
                color: $TEXT$;
            }

            /* SCROLL BARS */
            QScrollBar:vertical {
                background-color: $SURFACE$;
                width: 12px;
                border-radius: 6px;
                margin: 2px;
            }

            QScrollBar::handle:vertical {
                background-color: $BORDER$;
                border-radius: 6px;
                min-height: 30px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: $TEXT_MUTED$;
            }

            QScrollBar:horizontal {
                background-color: $SURFACE$;
                height: 12px;
                border-radius: 6px;
                margin: 2px;
            }

            QScrollBar::handle:horizontal {
                background-color: $BORDER$;
                border-radius: 6px;
                min-width: 30px;
            }

            /* LABELS */
            QLabel {
                color: $TEXT$;
                font-size: 13px;
            }

            /* CHECKBOXES */
            QCheckBox {
                color: $TEXT$;
                spacing: 8px;
                font-size: 13px;
            }

            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 1px solid $BORDER$;
                background-color: $SURFACE$;
            }

            QCheckBox::indicator:checked {
                background-color: $PRIMARY$;
                border-color: $PRIMARY$;
            }

            QCheckBox::indicator:hover {
                border-color: $PRIMARY$;
            }

            /* SLIDERS */
            QSlider::groove:horizontal {
                height: 6px;
                background-color: $SURFACE$;
                border-radius: 3px;
            }

            QSlider::handle:horizontal {
                width: 16px;
                height: 16px;
                margin: -5px 0;
                background-color: $PRIMARY$;
                border-radius: 8px;
            }

            QSlider::handle:horizontal:hover {
                background-color: $PRIMARY_DARK$;
            }

            QSlider::sub-page:horizontal {
                background-color: $PRIMARY$;
                border-radius: 3px;
            }

            /* STATUS BAR */
            QStatusBar {
                background-color: $SURFACE$;
                color: $TEXT$;
                font-size: 12px;
                padding: 4px;
                border-top: 1px solid $BORDER$;
            }

            /* MENU BAR */
            QMenuBar {
                background-color: $SURFACE$;
                color: $TEXT$;
                padding: 4px;
                font-size: 13px;
            }

            QMenuBar::item {
                padding: 6px 12px;
                border-radius: 4px;
            }

            QMenuBar::item:selected {
                background-color: $SURFACE_LIGHT$;
            }

            QMenu {
                background-color: $SURFACE$;
                border: 1px solid $BORDER$;
                border-radius: 6px;
                padding: 4px;
                font-size: 13px;
            }

            QMenu::item {
                padding: 8px 24px;
                border-radius: 4px;
            }

            QMenu::item:selected {
                background-color: $SURFACE_LIGHT$;
            }

            QMenu::separator {
                height: 1px;
                background-color: $BORDER$;
                margin: 4px 8px;
            }

            /* TOOLBAR */
            QToolBar {
                background-color: $SURFACE$;
                border: none;
                spacing: 8px;
                padding: 6px;
                border-bottom: 1px solid $BORDER$;
            }

            QToolBar QToolButton {
                background-color: transparent;
                color: $TEXT$;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 13px;
            }

            QToolBar QToolButton:hover {
                background-color: $SURFACE_LIGHT$;
            }

            /* TEXT EDIT */
            QTextEdit {
                font-size: 13px;
                line-height: 1.4;
            }

            QTextEdit#activityLog {
                background-color: #0f172a;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                border: 1px solid $BORDER$;
            }

            /* FORM LABELS */
            QFormLayout QLabel {
                font-size: 13px;
                font-weight: 500;
                color: $TEXT_SECONDARY$;
                min-width: 80px;
            }

            /* TOOLTIPS */
            QToolTip {
                background-color: $SURFACE_LIGHT$;
                color: $TEXT$;
                border: 1px solid $BORDER$;
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
            }
        """

        replacements = {
            "$BACKGROUND$": cls.BACKGROUND,
            "$SURFACE$": cls.SURFACE,
            "$SURFACE_LIGHT$": cls.SURFACE_LIGHT,
            "$PRIMARY$": cls.PRIMARY,
            "$PRIMARY_DARK$": cls.PRIMARY_DARK,
            "$SECONDARY$": cls.SECONDARY,
            "$TEXT$": cls.TEXT,
            "$TEXT_SECONDARY$": cls.TEXT_SECONDARY,
            "$TEXT_MUTED$": cls.TEXT_MUTED,
            "$BORDER$": cls.BORDER,
            "$BTN_SECONDARY_BG$": cls.BTN_SECONDARY_BG,
            "$BTN_SECONDARY_HOVER$": cls.BTN_SECONDARY_HOVER,
            "$BTN_UTILITY_HOVER$": cls.BTN_UTILITY_HOVER,
        }
        css = template
        for k, v in replacements.items():
            css = css.replace(k, v)
        return css