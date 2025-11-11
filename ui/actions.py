"""Clipboard transformation actions exposed in the UI."""

from __future__ import annotations

from typing import Callable, Dict, Optional, Tuple

from main import funky_case, lower_case, title_case, upper_case

ActionResult = Tuple[str, str]
TransformAction = Callable[..., ActionResult]

ACTIONS: Dict[str, TransformAction] = {
    "upper": upper_case,
    "lower": lower_case,
    "title": title_case,
    "sentence": funky_case,
}


def run(
    mode: str,
    *,
    source_text: Optional[str] = None,
    paste: bool = True,
) -> Optional[ActionResult]:
    action = ACTIONS.get(mode)
    if action is None:
        return None
    return action(source_text=source_text, paste=paste)


__all__ = ["ACTIONS", "run", "ActionResult"]
