from pathlib import Path
import sys
import types

import pytest

stub = types.SimpleNamespace()
sys.modules.setdefault("pyautogui", stub)
sys.modules.setdefault("pyperclip", types.SimpleNamespace(copy=lambda *_: None, paste=lambda: ""))

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import convert_text


@pytest.mark.parametrize(
    "source, expected",
    [
        ("you and i.", "You and I."),
        ("you and i!", "You and I!"),
        ("you and i?", "You and I?"),
        ("you and i\n", "You and I"),
    ],
)
def test_sentence_case_pronoun_i_followed_by_punctuation(source: str, expected: str) -> None:
    assert convert_text(source, "sentence") == expected
