"""System tray integration for the Kivy UI."""

from __future__ import annotations

import threading
from typing import Callable, Optional

from kivy.clock import Clock

from ui import actions
from ui.assets import icon_path

try:  # pragma: no cover - optional dependency guard
    import pystray
    from pystray import Menu, MenuItem
except Exception:  # pragma: no cover - fallback when tray is unavailable
    pystray = None
    Menu = MenuItem = None

try:  # pragma: no cover - optional dependency guard
    from PIL import Image
except Exception:  # pragma: no cover - pillow missing in runtime environment
    Image = None


_ACTION_LABELS = (
    ("Upper case", "upper"),
    ("Lower case", "lower"),
    ("Title case", "title"),
    ("Sentence case", "sentence"),
)


class CaseMonsterTray:
    """Manage the system tray icon and its menu."""

    def __init__(self, app) -> None:
        self._app = app
        self._icon: Optional[pystray.Icon] = None
        self._icon_ready = threading.Event()
        self._window_visible = bool(getattr(app, "window_visible", True))
        self._always_on_top = bool(getattr(app, "always_on_top", True))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @property
    def available(self) -> bool:
        return bool(pystray and Image)

    def start(self) -> bool:
        if not self.available:
            return False
        image = self._load_icon_image()
        if image is None:
            return False
        menu = self._build_menu()
        icon = pystray.Icon("caseMonster", image, "caseMonster", menu)
        icon.run_detached(self._on_icon_ready)
        self._icon = icon
        return True

    def stop(self) -> None:
        if self._icon is None:
            return
        try:
            self._icon.visible = False
        except Exception:  # pragma: no cover - backend specific attribute
            pass
        try:
            self._icon.stop()
        except Exception:  # pragma: no cover - backend specific teardown
            pass
        self._icon_ready.clear()
        self._icon = None

    def update_window_visibility(self, visible: bool) -> None:
        if not self.available or self._icon is None:
            return
        self._window_visible = bool(visible)
        self._refresh_menu()

    def update_always_on_top(self, enabled: bool) -> None:
        if not self.available or self._icon is None:
            return
        self._always_on_top = bool(enabled)
        self._refresh_menu()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _on_icon_ready(self, icon: pystray.Icon) -> None:
        self._icon_ready.set()
        try:
            icon.visible = True
        except Exception:  # pragma: no cover - backend specific attribute
            pass

    def _load_icon_image(self):
        if Image is None:
            return None
        icon_file = icon_path("logoico.ico") or icon_path("logo.png")
        if icon_file:
            try:
                image = Image.open(icon_file)
                return image.convert("RGBA")
            except Exception:
                pass
        try:
            return Image.new("RGBA", (64, 64), (28, 27, 35, 255))
        except Exception:
            return None

    def _refresh_menu(self) -> None:
        if not self._icon_ready.is_set() or self._icon is None:
            return
        self._icon.menu = self._build_menu()
        try:
            self._icon.update_menu()
        except Exception:  # pragma: no cover - optional in some backends
            pass

    def _build_menu(self) -> Menu:
        return Menu(
            *(self._action_item(label, mode) for label, mode in _ACTION_LABELS),
            Menu.SEPARATOR,
            self._visibility_item(),
            MenuItem(
                "Always on top",
                self._toggle_always_on_top,
                checked=lambda _: self._always_on_top,
            ),
            MenuItem("Exit", self._exit_application),
        )

    def _action_item(self, label: str, mode: str) -> MenuItem:
        return MenuItem(label, self._run_action(mode))

    def _visibility_item(self) -> MenuItem:
        label = "Hide window" if self._window_visible else "Show window"
        return MenuItem(label, self._toggle_window_visibility, default=True)

    def _run_action(self, mode: str) -> Callable[[Optional[pystray.Icon], Optional[pystray.MenuItem]], None]:
        def callback(_icon, _item):
            Clock.schedule_once(lambda _dt: actions.run(mode), 0)

        return callback

    def _toggle_window_visibility(self, _icon, _item) -> None:
        def toggle(_dt):
            if getattr(self._app, "window_visible", False):
                self._app.hide_window()
            else:
                self._app.show_window()

        Clock.schedule_once(toggle, 0)

    def _toggle_always_on_top(self, _icon, _item) -> None:
        Clock.schedule_once(lambda _dt: self._app.set_always_on_top(not self._always_on_top), 0)

    def _exit_application(self, _icon, _item) -> None:
        Clock.schedule_once(lambda _dt: self._app.stop(), 0)


__all__ = ["CaseMonsterTray"]

