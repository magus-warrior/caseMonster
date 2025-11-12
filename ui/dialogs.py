"""Popup dialogs implemented with Kivy widgets."""

from __future__ import annotations

import platform
import webbrowser
from pathlib import Path
from typing import Callable, Optional

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from . import styles
from .assets import get_asset_path

if platform.system() == "Windows":
    try:  # pragma: no cover - runtime integration
        from platform_integration import windows as win_integration
    except Exception:  # pragma: no cover - defensive guard
        win_integration = None
else:  # pragma: no cover - non-Windows platforms
    win_integration = None


class SettingsPopup(Popup):
    """Dialog exposing quick preferences and Windows shell integration."""

    def __init__(
        self,
        *,
        always_on_top: bool,
        on_toggle_always_on_top: Callable[[bool], None],
        on_hide_window: Callable[[], None],
    ) -> None:
        super().__init__(title="caseMonster preferences", auto_dismiss=False)
        self.size_hint = (0.55, None)
        self.height = dp(420)
        self._on_toggle = on_toggle_always_on_top
        self._on_hide_window = on_hide_window
        self._build_content(always_on_top)

    def _build_content(self, always_on_top: bool) -> None:
        container = BoxLayout(
            orientation="vertical",
            padding=(dp(20), dp(20), dp(20), dp(16)),
            spacing=dp(12),
        )

        intro = Label(
            text="Personalise how the floating window behaves on your desktop.",
            halign="left",
            valign="top",
            size_hint_y=None,
            color=styles.FOREGROUND_COLOUR,
        )
        intro.bind(size=lambda inst, _: setattr(inst, "text_size", inst.size))
        intro.height = dp(48)
        container.add_widget(intro)

        toggle_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(32))
        checkbox = CheckBox(active=always_on_top, size_hint=(None, None), size=(dp(28), dp(28)))
        checkbox.bind(active=lambda inst, value: self._on_toggle(bool(value)))
        toggle_row.add_widget(checkbox)
        toggle_label = Label(
            text="Keep the floating window always on top",
            halign="left",
            valign="middle",
            color=styles.FOREGROUND_COLOUR,
        )
        toggle_label.bind(size=lambda inst, _: setattr(inst, "text_size", inst.size))
        toggle_row.add_widget(toggle_label)
        container.add_widget(toggle_row)

        hide_button = Button(
            text="Hide the main window now",
            size_hint_y=None,
            height=dp(44),
        )
        hide_button.bind(on_release=lambda *_: self._request_hide())
        container.add_widget(hide_button)

        if win_integration is not None:
            divider = Widget(size_hint_y=None, height=dp(1))
            container.add_widget(divider)

            windows_label = Label(
                text="Windows Explorer integration",
                color=styles.SUBTLE_TEXT,
                size_hint_y=None,
                halign="left",
                valign="middle",
            )
            windows_label.bind(size=lambda inst, _: setattr(inst, "text_size", inst.size))
            windows_label.height = dp(24)
            container.add_widget(windows_label)

            register_button = Button(
                text="Register Explorer context menu entries",
                size_hint_y=None,
                height=dp(44),
            )
            register_button.bind(on_release=lambda *_: self._with_feedback(win_integration.register_context_menu))
            container.add_widget(register_button)

            unregister_button = Button(
                text="Remove Explorer context menu entries",
                size_hint_y=None,
                height=dp(44),
            )
            unregister_button.bind(on_release=lambda *_: self._with_feedback(win_integration.unregister_context_menu))
            container.add_widget(unregister_button)

        footer = Label(
            text="Need a refresher? The Help button opens the quick start guide.",
            halign="left",
            valign="top",
            color=styles.SUBTLE_TEXT,
            size_hint_y=None,
        )
        footer.bind(size=lambda inst, _: setattr(inst, "text_size", inst.size))
        footer.height = dp(44)
        container.add_widget(footer)

        actions = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(44), spacing=dp(12))
        actions.add_widget(Widget())

        save_button = Button(text="Close", size_hint=(None, None), size=(dp(96), dp(40)))
        save_button.bind(on_release=lambda *_: self.dismiss())
        actions.add_widget(save_button)
        container.add_widget(actions)

        self.content = container

    def _request_hide(self) -> None:
        self._on_hide_window()
        self.dismiss()

    def _with_feedback(self, action: Callable[[], None]) -> None:
        try:
            action()
        except Exception as exc:  # pragma: no cover - best effort diagnostics
            print(f"caseMonster: {exc}")


class HelpPopup(Popup):
    """Popup displaying the bundled quick start guide."""

    def __init__(self, *, help_path: Path) -> None:
        super().__init__(title="caseMonster quick start", size_hint=(0.6, 0.7))
        self._help_path = help_path
        self._build_content(help_path)

    def _build_content(self, help_path: Path) -> None:
        text = help_path.read_text(encoding="utf-8") if help_path.exists() else "Help file not found."

        root = BoxLayout(orientation="vertical", padding=(dp(20), dp(20), dp(20), dp(16)), spacing=dp(12))

        scroll = ScrollView()
        label = Label(
            text=text,
            halign="left",
            valign="top",
            color=styles.FOREGROUND_COLOUR,
            size_hint_y=None,
        )
        label.bind(texture_size=lambda inst, _: setattr(inst, "height", inst.texture_size[1]))
        label.bind(size=lambda inst, _: setattr(inst, "text_size", (inst.width, None)))
        scroll.add_widget(label)
        root.add_widget(scroll)

        actions = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(44), spacing=dp(12))
        open_button = Button(text="Open in default viewer", size_hint=(None, None), size=(dp(200), dp(40)))
        open_button.bind(on_release=lambda *_: self._open_external())
        actions.add_widget(open_button)

        actions.add_widget(Widget())

        close_button = Button(text="Close", size_hint=(None, None), size=(dp(96), dp(40)))
        close_button.bind(on_release=lambda *_: self.dismiss())
        actions.add_widget(close_button)

        root.add_widget(actions)
        self.content = root

    def _open_external(self) -> None:
        if not self._help_path.exists():
            return
        try:
            webbrowser.open(self._help_path.as_uri())
        except Exception as exc:  # pragma: no cover - diagnostic path
            print(f"caseMonster: unable to open help file: {exc}")


def open_help_guide() -> Optional[HelpPopup]:
    """Return a popup ready to display the bundled help file."""

    help_path = get_asset_path("help.txt").resolve()
    if not help_path.exists():
        print(f"caseMonster: Help file not found: {help_path}")
        return None
    return HelpPopup(help_path=help_path)


__all__ = ["SettingsPopup", "HelpPopup", "open_help_guide"]
