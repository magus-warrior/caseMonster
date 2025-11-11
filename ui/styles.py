"""Material-inspired colour palette and typography helpers for the UI."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Tuple

import wx

# Core Material palette for a light, airy interface
BACKGROUND_COLOUR = wx.Colour(244, 244, 250)
FOREGROUND_COLOUR = wx.Colour(34, 39, 49)
ACCENT_PRIMARY = wx.Colour(103, 80, 164)
ACCENT_SECONDARY = wx.Colour(30, 131, 114)
ACCENT_TERTIARY = wx.Colour(233, 136, 64)
ACCENT_NEUTRAL = wx.Colour(93, 105, 128)
CONTAINER_BACKGROUND = wx.Colour(255, 255, 255)
CONTAINER_BORDER = wx.Colour(219, 225, 236)
SUBTLE_TEXT = wx.Colour(112, 118, 138)
BORDER_SUBTLE = wx.Colour(206, 212, 226)
BUTTON_TEXT_COLOUR = wx.Colour(255, 255, 255)
SURFACE_TINT = wx.Colour(236, 232, 248)
SURFACE_HIGHLIGHT = wx.Colour(229, 242, 249)
SHADOW_COLOUR = wx.Colour(15, 23, 42)

# Elevation presets used by cards and buttons. Each tuple contains (offset, alpha)
# pairs which are drawn as layered rounded rectangles to create a soft shadow.
ELEVATION_SHADOWS: Dict[int, Tuple[Tuple[int, int], ...]] = {
    1: ((6, 20), (3, 28)),
    2: ((8, 16), (4, 26), (2, 34)),
}


@dataclass(frozen=True)
class FontDefinition:
    """Declarative description of a UI font role."""

    point_size: int
    weight: int
    face_names: Tuple[str, ...]
    style: int = wx.FONTSTYLE_NORMAL
    family: int = wx.FONTFAMILY_SWISS
    underline: bool = False


_SANS_SERIF_STACK: Tuple[str, ...] = (
    "Google Sans",
    "Roboto",
    "Product Sans",
    "Segoe UI",
    "Inter",
    "Noto Sans",
    "Helvetica",
    "Arial",
)

_SANS_SERIF_BOLD: Tuple[str, ...] = (
    "Google Sans Display",
    "Roboto",
    "Segoe UI Semibold",
    "Segoe UI",
    "Inter",
    "Noto Sans",
    "Helvetica Neue",
    "Arial",
)

_FONT_DEFINITIONS: Dict[str, FontDefinition] = {
    "base": FontDefinition(11, wx.FONTWEIGHT_NORMAL, _SANS_SERIF_STACK),
    "headline": FontDefinition(18, wx.FONTWEIGHT_BOLD, _SANS_SERIF_BOLD),
    "button": FontDefinition(12, wx.FONTWEIGHT_BOLD, _SANS_SERIF_BOLD),
    "display": FontDefinition(26, wx.FONTWEIGHT_BOLD, _SANS_SERIF_BOLD),
    "caption": FontDefinition(10, wx.FONTWEIGHT_NORMAL, _SANS_SERIF_STACK),
    "mono": FontDefinition(10, wx.FONTWEIGHT_NORMAL, (
        "JetBrains Mono",
        "Roboto Mono",
        "Cascadia Code",
        "Consolas",
        "Courier New",
    )),
}


def lighten_colour(colour: wx.Colour, amount: int = 16) -> wx.Colour:
    """Return a lighter variant of the provided colour."""

    r = min(colour.Red() + amount, 255)
    g = min(colour.Green() + amount, 255)
    b = min(colour.Blue() + amount, 255)
    return wx.Colour(r, g, b, colour.Alpha())


def darken_colour(colour: wx.Colour, amount: int = 16) -> wx.Colour:
    """Return a darker variant of the provided colour."""

    r = max(colour.Red() - amount, 0)
    g = max(colour.Green() - amount, 0)
    b = max(colour.Blue() - amount, 0)
    return wx.Colour(r, g, b, colour.Alpha())


@lru_cache(maxsize=None)
def get_font(role: str) -> wx.Font:
    """Fetch the wx.Font for a given semantic role, creating it lazily."""

    definition = _FONT_DEFINITIONS.get(role)
    if definition is None:  # pragma: no cover - defensive guard
        raise KeyError(f"Unknown font role: {role}")

    last_error: RuntimeError | None = None
    for face_name in definition.face_names:
        font = wx.Font(
            definition.point_size,
            definition.family,
            definition.style,
            definition.weight,
            definition.underline,
            face_name,
        )
        if font.IsOk():
            return font
        last_error = RuntimeError(f"Unable to create font for role '{role}' with face '{face_name}'")

    font = wx.Font(
        definition.point_size,
        definition.family,
        definition.style,
        definition.weight,
        definition.underline,
        "",
    )
    if font.IsOk():
        return font

    if last_error is not None:  # pragma: no cover - defensive guard
        raise last_error
    raise RuntimeError(f"Unable to create font for role '{role}'")


def apply_default_theme(window: wx.Window) -> None:
    """Apply the base colour palette and font to a window hierarchy."""

    window.SetBackgroundColour(BACKGROUND_COLOUR)
    window.SetForegroundColour(FOREGROUND_COLOUR)
    window.SetFont(get_font("base"))


__all__ = [
    "BACKGROUND_COLOUR",
    "FOREGROUND_COLOUR",
    "ACCENT_PRIMARY",
    "ACCENT_SECONDARY",
    "ACCENT_TERTIARY",
    "ACCENT_NEUTRAL",
    "CONTAINER_BACKGROUND",
    "CONTAINER_BORDER",
    "SUBTLE_TEXT",
    "BORDER_SUBTLE",
    "BUTTON_TEXT_COLOUR",
    "SURFACE_TINT",
    "SURFACE_HIGHLIGHT",
    "SHADOW_COLOUR",
    "ELEVATION_SHADOWS",
    "lighten_colour",
    "darken_colour",
    "get_font",
    "apply_default_theme",
]
