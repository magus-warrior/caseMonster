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
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    NumericProperty,
    StringProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from ui import actions
from ui.assets import icon_path
from ui.dialogs import InfoPopup, SettingsPopup, open_help_guide
from ui.history import ClipboardHistory
from ui.main_frame import (
    CLIPBOARD_POLL_SECONDS,
    DEFAULT_HISTORY_LIMIT,
    describe_history,
    ensure_history_limit,
)
from ui.styles import BACKGROUND_COLOUR, FOREGROUND_COLOUR
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
        Logger.info("CaseMonster: build() starting")
        try:
            Builder.load_file(str(_KV_PATH))
        except Exception:  # pragma: no cover - runtime diagnostics
            Logger.exception("CaseMonster: failed to load KV definition at %s", _KV_PATH)
            raise

        self.title = "caseMonster"
        icon = icon_path("logoico.ico") or icon_path("logo.png")
        if icon:
            Logger.info("CaseMonster: applying window icon from %s", icon)
            self.icon = icon
        else:
            Logger.warning("CaseMonster: no icon asset could be located")

        Window.clearcolor = BACKGROUND_COLOUR
        min_width, min_height = 620, 180
        Window.minimum_width = min_width
        Window.minimum_height = min_height
        # Ensure the initial window footprint matches the compact defaults instead
        # of Kivy's 800x600 fallback, while guarding against future regressions
        # that might shrink the window below the enforced minimum dimensions.
        requested_width, requested_height = min_width, min_height
        Window.size = (
            max(requested_width, min_width),
            max(requested_height, min_height),
        )

        self._load_preferences()
        self._refresh_history()
        self._apply_always_on_top()
        self._bind_window_events()

        root = CaseMonsterRoot()
        Logger.info("CaseMonster: starting clipboard poll every %.2fs", CLIPBOARD_POLL_SECONDS)
        self._clipboard_event = Clock.schedule_interval(
            self._poll_clipboard, CLIPBOARD_POLL_SECONDS
        )
        return root

    def on_start(self):
        Logger.info("CaseMonster: on_start() invoked")
        if self._tray is None:
            tray = CaseMonsterTray(self)
            Logger.info(
                "CaseMonster: tray availability = %s",
                tray.available,
            )
            if tray.start():
                Logger.info("CaseMonster: tray started successfully")
                tray.update_window_visibility(self._window_visible)
                tray.update_always_on_top(self.always_on_top)
                self._tray = tray
            else:
                Logger.warning("CaseMonster: tray could not be initialised")

    def on_stop(self):
        Logger.info("CaseMonster: stopping application")
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
        Logger.info("CaseMonster: loading preferences from section '%s'", section)
        if config.has_option(section, "always_on_top"):
            self.always_on_top = config.getboolean(section, "always_on_top")
        if config.has_option(section, "history_limit"):
            try:
                limit = ensure_history_limit(config.getint(section, "history_limit"))
            except (TypeError, ValueError):
                Logger.warning(
                    "CaseMonster: invalid history limit in config; restoring default"
                )
                limit = DEFAULT_HISTORY_LIMIT
                self.history_limit = limit
                self.history.update_limit(limit)
                self._write_preferences()
            else:
                self.history_limit = limit
                self.history.update_limit(limit)
                Logger.info(
                    "CaseMonster: history limit set to %s (config)",
                    limit,
                )
        else:
            self.history.update_limit(DEFAULT_HISTORY_LIMIT)
            Logger.info(
                "CaseMonster: history limit defaulted to %s",
                DEFAULT_HISTORY_LIMIT,
            )

    def _write_preferences(self) -> None:
        section = "preferences"
        self.config.set(section, "always_on_top", "1" if self.always_on_top else "0")
        self.config.set(section, "history_limit", str(int(self.history_limit)))
        self.config.write()
        Logger.info(
            "CaseMonster: wrote preferences (always_on_top=%s, history_limit=%s)",
            self.always_on_top,
            self.history_limit,
        )

    def _apply_always_on_top(self) -> None:
        Logger.info("CaseMonster: applying always_on_top=%s", self.always_on_top)
        try:
            Window.topmost = bool(self.always_on_top)
        except Exception:  # pragma: no cover - platform dependent attribute
            Logger.warning("CaseMonster: window manager does not support 'topmost'")
        if self._tray is not None:
            self._tray.update_always_on_top(self.always_on_top)

    def _bind_window_events(self) -> None:
        Logger.info("CaseMonster: binding window visibility events")
        for event_name in ("on_show", "on_restore"):
            try:
                Window.bind(**{event_name: self._on_window_shown})
            except TypeError:  # pragma: no cover - not all platforms expose events
                Logger.debug(
                    "CaseMonster: window event '%s' not supported on this platform",
                    event_name,
                )
        for event_name in ("on_hide", "on_minimize"):
            try:
                Window.bind(**{event_name: self._on_window_hidden})
            except TypeError:  # pragma: no cover - not all platforms expose events
                Logger.debug(
                    "CaseMonster: window event '%s' not supported on this platform",
                    event_name,
                )

    def _on_window_shown(self, *_args) -> None:
        Logger.info("CaseMonster: window shown")
        self._set_window_visibility(True)

    def _on_window_hidden(self, *_args) -> None:
        Logger.info("CaseMonster: window hidden")
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
            Logger.warning("CaseMonster: clipboard unavailable")
            return None
        except AttributeError:
            Logger.exception("CaseMonster: clipboard backend missing attribute")
            return None
        except Exception:  # pragma: no cover - clipboard can fail unexpectedly
            Logger.exception("CaseMonster: unexpected clipboard error")
            return None
        Logger.debug("CaseMonster: clipboard text read (%d chars)", len(value or ""))
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
        Logger.info("CaseMonster: running action '%s'", mode)
        selection = self.history_selection
        source_text = None
        if 0 < selection <= len(self._history_entries):
            source_text = self._history_entries[selection - 1]
        try:
            result = actions.run(mode, source_text=source_text)
        except ClipboardUnavailable as exc:
            Logger.warning("CaseMonster: automation unavailable: %s", exc)
            self._show_info(
                title="Clipboard automation unavailable",
                message=(
                    "caseMonster needs access to automation dependencies such as "
                    "pyautogui (and the system clipboard) to run actions.\n\n"
                    f"Details: {exc}"
                ),
            )
            return
        except KeyboardInterrupt:
            Logger.warning("CaseMonster: action '%s' interrupted", mode)
            self._show_info(
                title="Action interrupted",
                message="The clipboard automation was interrupted before it finished.",
            )
            return
        except Exception:
            Logger.exception("CaseMonster: action '%s' failed", mode)
            self._show_info(
                title="Action failed",
                message=(
                    "Something went wrong while running that action. "
                    "Check the log for details."
                ),
            )
            return
        if not result:
            Logger.info("CaseMonster: action '%s' produced no result", mode)
            return
        original, transformed = result
        self.history.record(original)
        self.history.record(transformed)
        self._refresh_history(selected_text=source_text)

    def _show_info(self, *, title: str, message: str) -> None:
        popup = InfoPopup(title=title, message=message)
        popup.open()

    def open_settings(self) -> None:
        Logger.info("CaseMonster: opening settings popup")
        popup = SettingsPopup(
            always_on_top=self.always_on_top,
            on_toggle_always_on_top=self.set_always_on_top,
            on_hide_window=self.hide_window,
        )
        popup.open()

    def open_help(self) -> None:
        Logger.info("CaseMonster: opening help guide")
        popup = open_help_guide()
        if popup is not None:
            popup.open()

    def hide_window(self) -> None:
        Logger.info("CaseMonster: hiding window")
        try:
            Window.minimize()
        except Exception:  # pragma: no cover - platform dependent
            try:
                Window.hide()
            except Exception:
                Logger.warning("CaseMonster: window hide not supported")
        self._set_window_visibility(False)

    def show_window(self) -> None:
        Logger.info("CaseMonster: showing window")
        try:
            Window.restore()
        except Exception:  # pragma: no cover - platform dependent
            Logger.debug("CaseMonster: window restore not supported")
        try:
            Window.show()
        except Exception:  # pragma: no cover - platform dependent
            Logger.debug("CaseMonster: window show not supported")
        try:
            Window.raise_window()
        except Exception:  # pragma: no cover - platform dependent
            Logger.debug("CaseMonster: window raise not supported")
        self._set_window_visibility(True)


def launch_app() -> int:
    Logger.info("CaseMonster: launching application")
    try:
        CaseMonsterApp().run()
    except Exception:  # pragma: no cover - diagnostic output for runtime errors
        Logger.exception("CaseMonster: application terminated due to an error")
        raise
    Logger.info("CaseMonster: application exited cleanly")
    return 0


__all__ = ["CaseMonsterApp", "CaseMonsterRoot", "launch_app"]


if __name__ == "__main__":  # pragma: no cover - manual launch helper
    raise SystemExit(launch_app())
