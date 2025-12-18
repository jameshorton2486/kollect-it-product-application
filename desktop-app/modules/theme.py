"""
Kollect-It Product Manager - Theme Module
Backwards compatibility wrapper for the modern theme.
"""

from .theme_modern import ModernPalette, get_color


class DarkPalette:
    """
    Legacy theme class - delegates to ModernPalette.
    Maintained for backwards compatibility.
    """

    # Map old names to new names
    BACKGROUND = ModernPalette.BACKGROUND
    SURFACE = ModernPalette.SURFACE
    SURFACE_LIGHT = ModernPalette.SURFACE_ELEVATED
    SURFACE_ELEVATED = ModernPalette.SURFACE_ELEVATED

    PRIMARY = ModernPalette.PRIMARY
    PRIMARY_DARK = ModernPalette.PRIMARY_DARK
    SECONDARY = ModernPalette.SECONDARY

    TEXT = ModernPalette.TEXT_PRIMARY
    TEXT_SECONDARY = ModernPalette.TEXT_SECONDARY
    TEXT_MUTED = ModernPalette.TEXT_MUTED

    BORDER = ModernPalette.BORDER
    BORDER_FOCUS = ModernPalette.BORDER_FOCUS

    SUCCESS = ModernPalette.SUCCESS
    WARNING = ModernPalette.WARNING
    ERROR = ModernPalette.ERROR
    INFO = ModernPalette.INFO

    BTN_SECONDARY_BG = ModernPalette.BTN_SECONDARY_BG
    BTN_SECONDARY_HOVER = ModernPalette.BTN_SECONDARY_HOVER
    BTN_UTILITY_HOVER = ModernPalette.SURFACE_HOVER

    @classmethod
    def get_stylesheet(cls) -> str:
        """Generate stylesheet - delegates to ModernPalette."""
        return ModernPalette.get_stylesheet()


# For backwards compatibility
KOLLECT_IT_THEME = DarkPalette.get_stylesheet()
