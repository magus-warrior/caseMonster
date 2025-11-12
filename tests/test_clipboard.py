import importlib
import sys
import types
from pathlib import Path

import pytest


class DummyClipboard:
    value = ""

    @classmethod
    def copy(cls, text):
        cls.value = text

    @classmethod
    def paste(cls):
        return cls.value


def _reload_clipboard(monkeypatch, *, pyperclip=None, kivy_clipboard=None):
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    for name in [
        "clipboard",
        "pyperclip",
        "kivy",
        "kivy.core",
        "kivy.core.clipboard",
    ]:
        sys.modules.pop(name, None)

    if pyperclip is not None:
        monkeypatch.setitem(sys.modules, "pyperclip", pyperclip)

    if kivy_clipboard is not None:
        kivy_module = types.ModuleType("kivy")
        kivy_module.__path__ = []  # mark as package
        kivy_core_module = types.ModuleType("kivy.core")
        kivy_core_module.__path__ = []
        kivy_clipboard_module = types.ModuleType("kivy.core.clipboard")
        kivy_clipboard_module.Clipboard = kivy_clipboard
        monkeypatch.setitem(sys.modules, "kivy", kivy_module)
        monkeypatch.setitem(sys.modules, "kivy.core", kivy_core_module)
        monkeypatch.setitem(sys.modules, "kivy.core.clipboard", kivy_clipboard_module)

    return importlib.import_module("clipboard")


def test_pyperclip_backend(monkeypatch):
    recorded = {"value": None}

    fake = types.SimpleNamespace(
        copy=lambda text: recorded.__setitem__("value", text),
        paste=lambda: "from-pyperclip",
    )

    module = _reload_clipboard(monkeypatch, pyperclip=fake)

    module.copy("hello")
    assert recorded["value"] == "hello"
    assert module.paste() == "from-pyperclip"


def test_kivy_fallback(monkeypatch):
    DummyClipboard.value = ""
    module = _reload_clipboard(monkeypatch, kivy_clipboard=DummyClipboard)

    module.copy("fallback")
    assert DummyClipboard.value == "fallback"
    DummyClipboard.value = "clipboard-value"
    assert module.paste() == "clipboard-value"


def test_no_backend_raises(monkeypatch):
    module = _reload_clipboard(monkeypatch)

    with pytest.raises(module.ClipboardUnavailable):
        module.copy("text")

    with pytest.raises(module.ClipboardUnavailable):
        module.paste()
