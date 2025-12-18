"""
Kollect-It Product Manager - Theme Module
Professional slate theme with copper and teal accents.
"""

# Import from the modern theme for consistency
from .theme_modern import ModernPalette, get_color


class DarkPalette:
    """Theme color palette for the application.
    
    This class maintains backwards compatibility while using the new
    professional color scheme from ModernPalette.
    """

    # Backgrounds - Warm slate gray
    BACKGROUND = "#2d3142"
    SURFACE = "#3d4259"
    SURFACE_LIGHT = "#4f5672"

    # Primary colors - Warm copper
    PRIMARY = "#d4a574"
    PRIMARY_DARK = "#b8895c"
    SECONDARY = "#5fb8b0"

    # Text colors
    TEXT = "#f8f9fa"
    TEXT_SECONDARY = "#c5c9d4"
    TEXT_MUTED = "#8a90a0"

    # Borders
    BORDER = "#525974"
    BORDER_FOCUS = "#d4a574"

    # Status colors
    SUCCESS = "#7dd3a8"
    WARNING = "#f4c06b"
    ERROR = "#e87c7c"
    INFO = "#6bb8e8"

    # Button colors
    BTN_SECONDARY_BG = "#4f5672"
    BTN_SECONDARY_HOVER = "#5c6488"
    BTN_UTILITY_HOVER = "#4f5672"

    @classmethod
    def get_stylesheet(cls) -> str:
        """Generate stylesheet - delegates to ModernPalette."""
        return ModernPalette.get_stylesheet()


# For backwards compatibility
KOLLECT_IT_THEME = DarkPalette.get_stylesheet()
