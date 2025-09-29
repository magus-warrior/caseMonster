"""Utilities for detecting platform capabilities.

This module centralizes platform-specific decisions so that other modules
can rely on a consistent source of truth for shortcut keys and behaviour.
"""

from __future__ import annotations

import platform


_SYSTEM = platform.system()


def primary_modifier_key() -> str:
    """Return the primary modifier key used for shortcuts on this platform."""

    return "command" if _SYSTEM == "Darwin" else "ctrl"


def supports_alt_tab() -> bool:
    """Return True if the platform supports using Alt+Tab for window switching."""

    # macOS uses Command+Tab for application switching and invoking Alt+Tab can
    # trigger the wrong behaviour. Other desktop platforms typically support
    # Alt+Tab, so we keep it enabled there.
    return _SYSTEM != "Darwin"

