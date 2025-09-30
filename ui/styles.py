"""Colour palette and typography helpers for the caseMonster UI."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Dict

import wx

# Core brand palette
BACKGROUND_COLOUR = wx.Colour(244, 247, 252)
FOREGROUND_COLOUR = wx.Colour(24, 32, 45)
ACCENT_PRIMARY = wx.Colour(64, 106, 255)
ACCENT_SECONDARY = wx.Colour(24, 151, 111)
ACCENT_TERTIARY = wx.Colour(230, 124, 48)
ACCENT_NEUTRAL = wx.Colour(101, 116, 139)
CONTAINER_BACKGROUND = wx.Colour(255, 255, 255)
CONTAINER_BORDER = wx.Colour(219, 225, 238)
SUBTLE_TEXT = wx.Colour(92, 106, 133)
BORDER_SUBTLE = wx.Colour(209, 216, 230)
BUTTON_TEXT_COLOUR = wx.Colour(255, 255, 255)


@dataclass(frozen=True)
class FontDefinition:
    """Declarative description of a UI font role."""

    point_size: int
    weight: int
    face_name: str
    style: int = wx.FONTSTYLE_NORMAL
    family: int = wx.FONTFAMILY_SWISS
    underline: bool = False


_FONT_DEFINITIONS: Dict[str, FontDefinition] = {
    "base": FontDefinition(11, wx.FONTWEIGHT_NORMAL, "Segoe UI"),
    "headline": FontDefinition(17, wx.FONTWEIGHT_BOLD, "Segoe UI Semibold"),
    "button": FontDefinition(11, wx.FONTWEIGHT_BOLD, "Segoe UI"),
    "caption": FontDefinition(10, wx.FONTWEIGHT_NORMAL, "Segoe UI"),
    "mono": FontDefinition(10, wx.FONTWEIGHT_NORMAL, "Cascadia Code"),
}


def lighten_colour(colour: wx.Colour, amount: int = 18) -> wx.Colour:
    """Return a lighter variant of the provided colour."""

    r = min(colour.Red() + amount, 255)
    g = min(colour.Green() + amount, 255)
    b = min(colour.Blue() + amount, 255)
    return wx.Colour(r, g, b)


@lru_cache(maxsize=None)
def get_font(role: str) -> wx.Font:
    """Fetch the wx.Font for a given semantic role, creating it lazily."""

    definition = _FONT_DEFINITIONS.get(role)
    if definition is None:  # pragma: no cover - defensive guard
        raise KeyError(f"Unknown font role: {role}")

    font = wx.Font(
        definition.point_size,
        definition.family,
        definition.style,
        definition.weight,
        definition.underline,
        definition.face_name,
    )
    if not font.IsOk():  # pragma: no cover - runtime guard
        raise RuntimeError(f"Unable to create font for role '{role}'")
    return font


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
    "lighten_colour",
    "get_font",
    "apply_default_theme",
]
