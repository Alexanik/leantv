import sys
sys_platform = sys.platform

# UI Palette & Themes for TV Cleaner Desktop
BG_DARK = "#121318"
BG_CARD = "#1C1E26"
BG_CARD_LIGHT = "#242834"
BORDER_COLOR = "#2D3242"

TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#9DA5B4"
TEXT_MUTED = "#5C6370"

ACCENT_CYAN = "#00E5FF"
ACCENT_GREEN = "#00E676"
ACCENT_ORANGE = "#FF9100"
ACCENT_RED = "#FF5252"
ACCENT_PURPLE = "#7C4DFF"

FONT_FAMILY = "Segoe UI" if sys_platform == "win32" else ("SF Pro Display" if sys_platform == "darwin" else "DejaVu Sans")

