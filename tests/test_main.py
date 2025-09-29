from pathlib import Path
import sys
import types

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

sys.modules.setdefault("pyautogui", types.SimpleNamespace(hotkey=lambda *_, **__: None))
sys.modules.setdefault(
    "pyperclip",
    types.SimpleNamespace(copy=lambda *_: None, paste=lambda: ""),
)

from main import convert_text


def test_sentence_case_preserves_leading_and_trailing_spaces():
    text = "  hello world.  "
    result = convert_text(text, "sentence")
    assert result == "  Hello world.  "


def test_sentence_case_preserves_newline_padding():
    text = "\nhello universe.\n"
    result = convert_text(text, "sentence")
    assert result == "\nHello universe.\n"
