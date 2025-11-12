"""Kivy GUI entry point for caseMonster."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from clipboard import ClipboardUnavailable, paste as clipboard_paste
from kivy.app import App
from kivy.clock import Clock
from kivy.clock import ClockEvent
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout

from ui import actions
from ui.assets import icon_path
from ui.dialogs import SettingsPopup, open_help_guide
from ui.history import ClipboardHistory
from ui.main_frame import (
    CLIPBOARD_POLL_SECONDS,
    DEFAULT_HISTORY_LIMIT,
    describe_history,
    ensure_history_limit,
)
from ui.styles import BACKGROUND_COLOUR
from ui.tray import CaseMonsterTray

# Import styled widgets so that the KV language recognises them
from ui.components import AccentButton, RoundedPanel  # noqa: F401  # pylint: disable=unused-import


_KV_PATH = Path(__file__).resolve().parent / "ui" / "casemonster.kv"


class CaseMonsterRoot(BoxLayout):
    """Root layout container built from the KV definition."""


class CaseMonsterApp(App):
    """Kivy application hosting the floating clipboard controls."""

    always_on_top = BooleanProperty(True)
    history_limit = NumericProperty(DEFAULT_HISTORY_LIMIT)
    history_labels = ListProperty(["Current selection"])
    current_history_label = StringProperty("Current selection")
    history_selection = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.history = ClipboardHistory(DEFAULT_HISTORY_LIMIT)
        self._history_entries: list[str] = []
        self._clipboard_event: Optional[ClockEvent] = None
        self.use_kivy_settings = False
        self._tray: Optional[CaseMonsterTray] = None
        self._window_visible = True

    def build_config(self, config):
        config.setdefaults(
            "preferences",
            {
                "always_on_top": "1",
                "history_limit": str(DEFAULT_HISTORY_LIMIT),
            },
        )

    def build(self):
        Builder.load_file(str(_KV_PATH))
        self.title = "caseMonster"
        icon = icon_path("logoico.ico") or icon_path("logo.png")
        if icon:
            self.icon = icon

        Window.clearcolor = BACKGROUND_COLOUR
        Window.minimum_width = 620
        Window.minimum_height = 180

        self._load_preferences()
        self._refresh_history()
        self._apply_always_on_top()
        self._bind_window_events()

        root = CaseMonsterRoot()
        self._clipboard_event = Clock.schedule_interval(
            self._poll_clipboard, CLIPBOARD_POLL_SECONDS
        )
        return root

    def on_start(self):
        if self._tray is None:
            tray = CaseMonsterTray(self)
            if tray.start():
                tray.update_window_visibility(self._window_visible)
                tray.update_always_on_top(self.always_on_top)
                self._tray = tray

    def on_stop(self):
        if self._clipboard_event is not None:
            self._clipboard_event.cancel()
            self._clipboard_event = None
        self._write_preferences()
        if self._tray is not None:
            self._tray.stop()
            self._tray = None

    @property
    def window_visible(self) -> bool:
        return self._window_visible

    def toggle_window_visibility(self) -> None:
        if self.window_visible:
            self.hide_window()
        else:
            self.show_window()

    def _load_preferences(self) -> None:
        config = self.config
        section = "preferences"
        if config.has_option(section, "always_on_top"):
            self.always_on_top = config.getboolean(section, "always_on_top")
        if config.has_option(section, "history_limit"):
            limit = ensure_history_limit(config.getint(section, "history_limit"))
            self.history_limit = limit
            self.history.update_limit(limit)
        else:
            self.history.update_limit(DEFAULT_HISTORY_LIMIT)

    def _write_preferences(self) -> None:
        section = "preferences"
        self.config.set(section, "always_on_top", "1" if self.always_on_top else "0")
        self.config.set(section, "history_limit", str(int(self.history_limit)))
        self.config.write()

    def _apply_always_on_top(self) -> None:
        try:
            Window.topmost = bool(self.always_on_top)
        except Exception:  # pragma: no cover - platform dependent attribute
            pass
        if self._tray is not None:
            self._tray.update_always_on_top(self.always_on_top)

    def _bind_window_events(self) -> None:
        for event_name in ("on_show", "on_restore"):
            try:
                Window.bind(**{event_name: self._on_window_shown})
            except TypeError:  # pragma: no cover - not all platforms expose events
                pass
        for event_name in ("on_hide", "on_minimize"):
            try:
                Window.bind(**{event_name: self._on_window_hidden})
            except TypeError:  # pragma: no cover - not all platforms expose events
                pass

    def _on_window_shown(self, *_args) -> None:
        self._set_window_visibility(True)

    def _on_window_hidden(self, *_args) -> None:
        self._set_window_visibility(False)

    def _set_window_visibility(self, visible: bool) -> None:
        self._window_visible = bool(visible)
        if self._tray is not None:
            self._tray.update_window_visibility(self._window_visible)

    def _poll_clipboard(self, _dt: float) -> None:
        text = self._read_clipboard()
        if text is None:
            return
        previous = list(self._history_entries)
        self.history.record(text)
        if self.history.items != previous:
            self._refresh_history()

    def _read_clipboard(self) -> Optional[str]:
        try:
            value = clipboard_paste()
        except ClipboardUnavailable:
            return None
        except AttributeError:
            return None
        except Exception:  # pragma: no cover - clipboard can fail unexpectedly
            return None
        return value or None

    def _refresh_history(self, *, selected_text: Optional[str] = None) -> None:
        self._history_entries = self.history.items
        labels = describe_history(self._history_entries)
        if selected_text and selected_text in self._history_entries:
            selection_index = self._history_entries.index(selected_text) + 1
        else:
            selection_index = self.history_selection if self.history_selection < len(labels) else 0

        self.history_labels = labels
        if labels:
            self.history_selection = selection_index
            self.current_history_label = labels[selection_index]

    def select_history(self, label: str) -> None:
        if label not in self.history_labels:
            return
        self.history_selection = self.history_labels.index(label)
        self.current_history_label = label

    def set_always_on_top(self, enabled: bool) -> None:
        enabled = bool(enabled)
        if self.root:
            desired = "down" if enabled else "normal"
            if self.root.ids.pin_toggle.state != desired:
                self.root.ids.pin_toggle.state = desired
        if self.always_on_top == enabled:
            return
        self.always_on_top = enabled
        self._apply_always_on_top()
        self._write_preferences()

    def toggle_pin(self, state: str) -> None:
        self.set_always_on_top(state == "down")

    def update_history_limit(self, text: str) -> None:
        try:
            value = int(text)
        except (TypeError, ValueError):
            value = int(self.history_limit)
        value = ensure_history_limit(value)
        if value != self.history_limit:
            self.history_limit = value
            self.history.update_limit(value)
            self._refresh_history()
        self._write_preferences()
        if self.root:
            self.root.ids.history_limit_input.text = str(int(self.history_limit))

    def run_action(self, mode: str) -> None:
        selection = self.history_selection
        source_text = None
        if 0 < selection <= len(self._history_entries):
            source_text = self._history_entries[selection - 1]
        result = actions.run(mode, source_text=source_text)
        if not result:
            return
        original, transformed = result
        self.history.record(original)
        self.history.record(transformed)
        self._refresh_history(selected_text=source_text)

    def open_settings(self) -> None:
        popup = SettingsPopup(
            always_on_top=self.always_on_top,
            on_toggle_always_on_top=self.set_always_on_top,
            on_hide_window=self.hide_window,
        )
        popup.open()

    def open_help(self) -> None:
        popup = open_help_guide()
        if popup is not None:
            popup.open()

    def hide_window(self) -> None:
        try:
            Window.minimize()
        except Exception:  # pragma: no cover - platform dependent
            try:
                Window.hide()
            except Exception:
                pass
        self._set_window_visibility(False)

    def show_window(self) -> None:
        try:
            Window.restore()
        except Exception:  # pragma: no cover - platform dependent
            pass
        try:
            Window.show()
        except Exception:  # pragma: no cover - platform dependent
            pass
        try:
            Window.raise_window()
        except Exception:  # pragma: no cover - platform dependent
            pass
        self._set_window_visibility(True)


def launch_app() -> int:
    CaseMonsterApp().run()
    return 0


__all__ = ["CaseMonsterApp", "CaseMonsterRoot", "launch_app"]
