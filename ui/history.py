"""Clipboard history bookkeeping for the caseMonster toolbar."""

from __future__ import annotations

from typing import Iterable, List


class ClipboardHistory:
    """In-memory ring buffer of recent clipboard entries."""

    def __init__(self, limit: int = 10) -> None:
        self._limit = max(1, limit)
        self._items: List[str] = []

    @property
    def limit(self) -> int:
        return self._limit

    @property
    def items(self) -> list[str]:
        """Return a copy of the current clipboard entries."""

        return list(self._items)

    def update_limit(self, limit: int) -> None:
        """Change the history size while keeping the newest entries."""

        self._limit = max(1, limit)
        if len(self._items) > self._limit:
            del self._items[self._limit :]

    def record(self, text: str | None) -> None:
        """Store a clipboard entry if it is non-empty."""

        if not text:
            return

        if text in self._items:
            self._items.remove(text)

        self._items.insert(0, text)
        if len(self._items) > self._limit:
            del self._items[self._limit :]

    def extend(self, values: Iterable[str]) -> None:
        """Add multiple clipboard entries preserving their order."""

        for value in values:
            self.record(value)


__all__ = ["ClipboardHistory"]
