"""Windows Explorer integration helpers for caseMonster."""

from __future__ import annotations

import platform
import sys
from contextlib import suppress
from pathlib import Path

_IS_WINDOWS = platform.system() == "Windows"

if _IS_WINDOWS:  # pragma: no cover - exercised on Windows environments
    import winreg
else:  # pragma: no cover - imported but unused on non-Windows
    winreg = None  # type: ignore[assignment]


_CONTEXT_LOCATIONS = [
    r"Software\Classes\*\shell",
    r"Software\Classes\Directory\shell",
]

_MODES = {
    "upper": "Convert to UPPERCASE",
    "lower": "Convert to lowercase",
    "title": "Convert to Title Case",
    "sentence": "Convert to Sentence case",
}


def _ensure_windows() -> None:
    if not _IS_WINDOWS:  # pragma: no cover - guard for unsupported systems
        raise OSError("Windows shell integration is only available on Windows.")


def _python_executable() -> str:
    executable = Path(sys.executable)
    if executable.name.lower() == "python.exe":
        pythonw = executable.with_name("pythonw.exe")
        if pythonw.exists():
            return str(pythonw)
    return str(executable)


def register_context_menu(script_path: Path | None = None) -> None:
    """Register Explorer context menu entries for case conversions."""

    _ensure_windows()

    assert winreg is not None  # appease the type-checker

    script = script_path or Path(__file__).resolve().parents[1] / "main.py"
    icon_path = Path(__file__).resolve().parents[1] / "logoico.ico"
    python_exe = _python_executable()

    for base_key in _CONTEXT_LOCATIONS:
        for mode, description in _MODES.items():
            key_path = f"{base_key}\\caseMonster_{mode}"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                winreg.SetValueEx(key, None, 0, winreg.REG_SZ, description)
                if icon_path.exists():
                    winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, str(icon_path))
                command = (
                    f'"{python_exe}" "{script}" --convert {mode} --target "%1" --in-place'
                )
                with winreg.CreateKey(key, "command") as command_key:
                    winreg.SetValueEx(command_key, None, 0, winreg.REG_SZ, command)


def unregister_context_menu() -> None:
    """Remove the Explorer context menu entries added by this module."""

    _ensure_windows()

    assert winreg is not None  # appease the type-checker

    for base_key in _CONTEXT_LOCATIONS:
        for mode in _MODES:
            key_path = f"{base_key}\\caseMonster_{mode}"
            _delete_tree(winreg.HKEY_CURRENT_USER, key_path)


def _delete_tree(root: int, key_path: str) -> None:
    try:
        with winreg.OpenKey(root, key_path, 0, winreg.KEY_READ) as key:
            _delete_children(root, key_path, key)
    except FileNotFoundError:
        return
    with suppress(FileNotFoundError):
        winreg.DeleteKey(root, key_path)


def _delete_children(root: int, key_path: str, key: "winreg.HKEYType") -> None:
    index = 0
    while True:
        try:
            sub_key_name = winreg.EnumKey(key, index)
        except OSError:
            break
        _delete_tree(root, f"{key_path}\\{sub_key_name}")
        index += 1
