"""Clipboard utility functions with graceful fallbacks."""

from __future__ import annotations

from typing import Optional


class ClipboardUnavailable(RuntimeError):
    """Raised when no clipboard backend is available."""


try:  # pragma: no cover - import guard
    import pyperclip as _pyperclip  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    _pyperclip = None  # type: ignore[assignment]

try:  # pragma: no cover - import guard
    from kivy.core.clipboard import Clipboard as _KivyClipboard  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    _KivyClipboard = None  # type: ignore[assignment]


def _normalize_text(text: Optional[str]) -> str:
    return "" if text is None else str(text)


def copy(text: Optional[str]) -> None:
    """Copy *text* to the clipboard using the first available backend."""

    value = _normalize_text(text)

    if _pyperclip is not None:
        _pyperclip.copy(value)
        return

    if _KivyClipboard is not None:
        _KivyClipboard.copy(value)
        return

    raise ClipboardUnavailable(
        "No clipboard backend available. Install the 'pyperclip' dependency."
    )


def paste() -> str:
    """Return the current clipboard contents."""

    if _pyperclip is not None:
        try:
            value = _pyperclip.paste()
        except AttributeError:
            return ""
        except Exception as exc:  # pragma: no cover - defensive guard
            raise ClipboardUnavailable(str(exc)) from exc
        return _normalize_text(value)

    if _KivyClipboard is not None:
        try:
            value = _KivyClipboard.paste()
        except Exception as exc:  # pragma: no cover - backend specific errors
            raise ClipboardUnavailable(str(exc)) from exc
        return _normalize_text(value)

    raise ClipboardUnavailable(
        "No clipboard backend available. Install the 'pyperclip' dependency."
    )


def is_available() -> bool:
    """Return True if at least one clipboard backend is usable."""

    return _pyperclip is not None or _KivyClipboard is not None


__all__ = ["ClipboardUnavailable", "copy", "paste", "is_available"]
