"""Clipboard automation helpers for caseMonster.

Third-party dependencies:
- pyperclip (tested with 1.8.2)
- pyautogui (tested with 0.9.54)
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Callable

try:
    import pyautogui as _pyautogui
except Exception as exc:  # pragma: no cover - import guard for optional dependency
    _pyautogui = None
    _PYAUTOGUI_IMPORT_ERROR = exc
else:
    _PYAUTOGUI_IMPORT_ERROR = None

from clipboard import (
    ClipboardUnavailable,
    copy as clipboard_copy,
    paste as clipboard_paste,
)

from platform_utils import primary_modifier_key, supports_alt_tab


Transform = Callable[[str], str]


def _cap_sentences(text: str) -> str:
    sentences = text.split(".")
    transformed = ["".join(_cap_first_letter(list(sentence))) for sentence in sentences]
    result = _cap_special(".".join(transformed))

    trailing_newlines = len(text) - len(text.rstrip("\r\n"))
    leading_newlines = len(text) - len(text.lstrip("\r\n"))

    if trailing_newlines:
        if leading_newlines == 0:
            result = result.rstrip("\r\n")
        else:
            stripped = result.rstrip("\r\n")
            result = stripped + text[-trailing_newlines:]

    return result


def _cap_special(text: str) -> str:
    fin: list[str] = []
    caps = False

    for char in text:
        if char in ["\t", "\n", "\r"]:
            fin.append(char)
            caps = True
        elif caps:
            fin.append(char.upper())
            caps = False
        else:
            fin.append(char)

    return "".join(fin)


def _cap_first_letter(characters: list[str]) -> list[str]:
    fin_list: list[str] = []
    symbols = ["!", "?"]
    caps = True

    for index, char in enumerate(characters):
        if char == " ":
            fin_list.append(char)
        elif char in symbols:
            fin_list.append(char)
            caps = True
        elif char.isalpha() and caps:
            fin_list.append(char.upper())
            caps = False
        elif char.isalpha():
            if (
                char.lower() == "i"
                and fin_list
                and fin_list[-1] == " "
                and (
                    index + 1 == len(characters)
                    or characters[index + 1]
                    in [" ", ".", "!", "?", "\n"]
                )
            ):
                fin_list.append(char.upper())
            elif (
                char.lower() == "i"
                and index + 1 < len(characters)
                and characters[index + 1] in ["’", "'"]
            ):
                fin_list.append(char.upper())
            else:
                fin_list.append(char.lower())
        else:
            fin_list.append(char.lower())

    return fin_list


def funky(text: str) -> str:
    return _cap_sentences(text)


def _sentence_case(text: str) -> str:
    return funky(text.upper())


TRANSFORMS: dict[str, Transform] = {
    "upper": str.upper,
    "lower": str.lower,
    "title": str.title,
    "sentence": _sentence_case,
}


MODIFIER_KEY = primary_modifier_key()


def _require_automation_backend():
    if _pyautogui is None:
        raise ClipboardUnavailable(
            "pyautogui is required for clipboard automation. "
            "Install it with 'pip install pyautogui' to enable the GUI actions."
        ) from _PYAUTOGUI_IMPORT_ERROR
    return _pyautogui


def _maybe_switch_window():
    if supports_alt_tab():
        backend = _require_automation_backend()
        backend.hotkey("alt", "tab")
        time.sleep(0.01)


def _copy_selection():
    backend = _require_automation_backend()
    clipboard_copy("")
    backend.hotkey(MODIFIER_KEY, "c")
    time.sleep(0.01)


def _paste_selection():
    backend = _require_automation_backend()
    backend.hotkey(MODIFIER_KEY, "v")
    time.sleep(0.01)


def transform_clipboard(
    transform: Transform,
    source_text: str | None = None,
    *,
    paste: bool = True,
) -> tuple[str, str]:
    _maybe_switch_window()
    if source_text is None:
        _copy_selection()
        source_text = clipboard_paste()
    transformed = transform(source_text)
    clipboard_copy(transformed)
    if paste:
        _paste_selection()
    time.sleep(0.01)
    return source_text, transformed


def upper_case(source_text: str | None = None, *, paste: bool = True) -> tuple[str, str]:
    return transform_clipboard(TRANSFORMS["upper"], source_text, paste=paste)


def lower_case(source_text: str | None = None, *, paste: bool = True) -> tuple[str, str]:
    return transform_clipboard(TRANSFORMS["lower"], source_text, paste=paste)


def title_case(source_text: str | None = None, *, paste: bool = True) -> tuple[str, str]:
    return transform_clipboard(TRANSFORMS["title"], source_text, paste=paste)


def funky_case(source_text: str | None = None, *, paste: bool = True) -> tuple[str, str]:
    return transform_clipboard(TRANSFORMS["sentence"], source_text, paste=paste)


def convert_text(text: str, mode: str) -> str:
    try:
        transform = TRANSFORMS[mode]
    except KeyError as exc:  # pragma: no cover - defensive guard
        raise ValueError(f"Unsupported mode: {mode}") from exc
    return transform(text)


def _convert_file(path: Path, mode: str, in_place: bool) -> None:
    text = path.read_text(encoding="utf-8")
    transformed = convert_text(text, mode)
    if in_place:
        path.write_text(transformed, encoding="utf-8")
    else:
        sys.stdout.write(transformed)


def _cli(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="caseMonster text conversion utilities")
    parser.add_argument(
        "--convert",
        choices=sorted(TRANSFORMS.keys()),
        required=True,
        help="Conversion mode to apply",
    )
    parser.add_argument(
        "--target",
        type=Path,
        help="Optional path to a text file to convert. If omitted, uses the clipboard.",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="When used with --target, overwrite the file instead of printing to stdout.",
    )

    args = parser.parse_args(argv)

    if args.target:
        _convert_file(args.target, args.convert, args.in_place)
        return 0

    try:
        clipboard_copy(convert_text(clipboard_paste(), args.convert))
    except ClipboardUnavailable as exc:
        raise SystemExit(str(exc)) from exc
    return 0


def main(argv: list[str] | None = None) -> int:
    return _cli(argv or sys.argv[1:])


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
