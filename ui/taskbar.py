"""Placeholder taskbar integration for the Kivy UI."""

from __future__ import annotations


class CaseMonsterTaskBarIcon:
    """Stub that documents the lack of native system tray support."""

    def __init__(self, *_, **__):
        self.available = False

    def Destroy(self) -> None:  # pragma: no cover - compatibility shim
        """Retained for backwards compatibility with the wx implementation."""

    def remove(self) -> None:  # pragma: no cover - compatibility shim
        """Alias maintained for API parity with the previous UI."""


__all__ = ["CaseMonsterTaskBarIcon"]
