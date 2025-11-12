"""Utility helpers shared by the Kivy interface."""

from __future__ import annotations

from typing import Iterable, List


CLIPBOARD_POLL_SECONDS = 0.75
DEFAULT_HISTORY_LIMIT = 10
MAX_HISTORY_LABEL_LENGTH = 48


def format_history_label(text: str, *, max_length: int = MAX_HISTORY_LABEL_LENGTH) -> str:
    """Return a human friendly label for the clipboard history dropdown."""

    collapsed = " ".join(line.strip() for line in text.splitlines()).strip()
    if not collapsed:
        collapsed = "(whitespace)"
    if len(collapsed) > max_length:
        collapsed = collapsed[: max_length - 1] + "…"
    return collapsed


def ensure_history_limit(value: int, *, minimum: int = 1, maximum: int = 50) -> int:
    """Clamp the history limit within a reasonable range."""

    return max(minimum, min(maximum, value))


def describe_history(items: Iterable[str]) -> List[str]:
    """Return formatted history labels prefixed with the current selection entry."""

    return ["Current selection"] + [format_history_label(item) for item in items]


__all__ = [
    "CLIPBOARD_POLL_SECONDS",
    "DEFAULT_HISTORY_LIMIT",
    "MAX_HISTORY_LABEL_LENGTH",
    "format_history_label",
    "ensure_history_limit",
    "describe_history",
]
