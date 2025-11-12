"""Material-inspired palette and helpers adapted for the Kivy UI."""

from __future__ import annotations

from typing import Iterable

from kivy.utils import get_color_from_hex


BACKGROUND_COLOUR = get_color_from_hex("#f4f4fa")
FOREGROUND_COLOUR = get_color_from_hex("#222731")
ACCENT_PRIMARY = get_color_from_hex("#6750a4")
ACCENT_SECONDARY = get_color_from_hex("#1e8372")
ACCENT_TERTIARY = get_color_from_hex("#e98840")
ACCENT_NEUTRAL = get_color_from_hex("#5d6980")
CONTAINER_BACKGROUND = get_color_from_hex("#ffffff")
CONTAINER_BORDER = get_color_from_hex("#dbe1ec")
SUBTLE_TEXT = get_color_from_hex("#70768a")
BORDER_SUBTLE = get_color_from_hex("#ced4e2")
BUTTON_TEXT_COLOUR = get_color_from_hex("#ffffff")
SURFACE_TINT = get_color_from_hex("#ece8f8")
SURFACE_HIGHLIGHT = get_color_from_hex("#e5f2f9")
SHADOW_COLOUR = get_color_from_hex("#0f172a")


def _clamp(value: float) -> float:
    return min(max(value, 0.0), 1.0)


def lighten_colour(colour: Iterable[float], amount: float = 0.08) -> list[float]:
    """Return a lighter variant of the provided RGBA colour."""

    r, g, b, a = list(colour)
    return [_clamp(r + amount), _clamp(g + amount), _clamp(b + amount), a]


def darken_colour(colour: Iterable[float], amount: float = 0.08) -> list[float]:
    """Return a darker variant of the provided RGBA colour."""

    r, g, b, a = list(colour)
    return [_clamp(r - amount), _clamp(g - amount), _clamp(b - amount), a]


def apply_default_theme(widget) -> None:
    """Best-effort theming hook for legacy callers."""

    if hasattr(widget, "background_color"):
        widget.background_color = BACKGROUND_COLOUR
    if hasattr(widget, "color"):
        widget.color = FOREGROUND_COLOUR


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
    "lighten_colour",
    "darken_colour",
    "apply_default_theme",
]
