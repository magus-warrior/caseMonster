"""Clipboard transformation actions exposed in the UI."""

from __future__ import annotations

from typing import Callable, Dict

from main import funky_case, lower_case, title_case, upper_case

TransformAction = Callable[[], None]

ACTIONS: Dict[str, TransformAction] = {
    "upper": upper_case,
    "lower": lower_case,
    "title": title_case,
    "sentence": funky_case,
}


def run(mode: str) -> None:
    action = ACTIONS.get(mode)
    if action is not None:
        action()


__all__ = ["ACTIONS", "run"]
