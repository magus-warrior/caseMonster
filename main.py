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

import pyautogui as pya
import pyperclip

from platform_utils import primary_modifier_key, supports_alt_tab


Transform = Callable[[str], str]


def _cap_sentences(text: str) -> str:
    sentences = text.split(".")
    transformed = ["".join(_cap_first_letter(list(sentence))) for sentence in sentences]
    return _cap_special(".".join(transformed).strip())


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

    return "".join(fin).strip()


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
                and index + 1 < len(characters)
                and characters[index + 1] == " "
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


def _maybe_switch_window():
    if supports_alt_tab():
        pya.hotkey("alt", "tab")
        time.sleep(0.01)


def _copy_selection():
    pyperclip.copy("")
    pya.hotkey(MODIFIER_KEY, "c")
    time.sleep(0.01)


def _paste_selection():
    pya.hotkey(MODIFIER_KEY, "v")
    time.sleep(0.01)


def transform_clipboard(transform: Transform) -> None:
    _maybe_switch_window()
    _copy_selection()
    pyperclip.copy(transform(pyperclip.paste()))
    _paste_selection()
    time.sleep(0.01)


def upper_case():
    transform_clipboard(TRANSFORMS["upper"])


def lower_case():
    transform_clipboard(TRANSFORMS["lower"])


def title_case():
    transform_clipboard(TRANSFORMS["title"])


def funky_case():
    transform_clipboard(TRANSFORMS["sentence"])


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

    pyperclip.copy(convert_text(pyperclip.paste(), args.convert))
    return 0


def main(argv: list[str] | None = None) -> int:
    return _cli(argv or sys.argv[1:])


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
