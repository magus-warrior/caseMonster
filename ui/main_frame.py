"""Thin floating toolbar hosting the caseMonster controls."""

from __future__ import annotations

from typing import Callable, Optional

import pyperclip
import wx

from . import actions, styles
from .assets import load_icon
from .history import ClipboardHistory
from .taskbar import CaseMonsterTaskBarIcon


class CaseMonsterFrame(wx.Frame):
    """Compact always-on-top toolbar for clipboard conversions."""

    _CLIPBOARD_POLL_MS = 750

    def __init__(self, parent: wx.Window | None):
        self._config = wx.Config(appName="caseMonster", vendorName="WarpTyme")
        if self._config.HasEntry("always_on_top"):
            self.always_on_top = self._config.ReadBool("always_on_top")
        else:
            self.always_on_top = True

        if self._config.HasEntry("history_limit"):
            history_limit = max(self._config.ReadInt("history_limit"), 1)
        else:
            history_limit = 10

        base_style = wx.CAPTION | wx.CLOSE_BOX | wx.FRAME_TOOL_WINDOW
        style = base_style | (wx.STAY_ON_TOP if self.always_on_top else 0)

        super().__init__(
            parent,
            id=wx.ID_ANY,
            title="caseMonster",
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=style,
        )

        styles.apply_default_theme(self)
        self.SetIcon(load_icon('logoico.ico'))

        min_size = self.FromDIP(wx.Size(620, 120))
        self.SetMinSize(min_size)
        self.SetInitialSize(min_size)

        self._history = ClipboardHistory(history_limit)
        self._history_entries: list[str] = []

        self._clipboard_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_clipboard_timer, self._clipboard_timer)
        self._clipboard_timer.Start(self._CLIPBOARD_POLL_MS)

        outer = wx.BoxSizer(wx.VERTICAL)
        padding = self.FromDIP(8)

        toolbar_panel = wx.Panel(self)
        styles.apply_default_theme(toolbar_panel)
        toolbar_panel.SetBackgroundColour(styles.CONTAINER_BACKGROUND)
        toolbar_panel.SetDoubleBuffered(True)

        content_sizer = wx.BoxSizer(wx.VERTICAL)
        content_padding = self.FromDIP(12)
        toolbar_panel.SetSizer(content_sizer)

        outer.Add(toolbar_panel, 1, wx.EXPAND | wx.ALL, padding)

        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        content_sizer.Add(header_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, content_padding)
        self.SetSizer(outer)

        brand = wx.StaticText(toolbar_panel, label="caseMonster")
        brand.SetFont(styles.get_font("button"))
        brand.SetForegroundColour(styles.ACCENT_PRIMARY)
        header_sizer.Add(brand, 0, wx.ALIGN_CENTER_VERTICAL)

        header_sizer.AddStretchSpacer()

        self._pin_toggle = wx.ToggleButton(toolbar_panel, label="On top")
        self._pin_toggle.SetValue(self.always_on_top)
        self._pin_toggle.Bind(wx.EVT_TOGGLEBUTTON, self._on_pin_toggled)
        self._pin_toggle.SetMinSize(self.FromDIP(wx.Size(96, 34)))
        header_sizer.Add(self._pin_toggle, 0, wx.ALIGN_CENTER_VERTICAL)

        content_sizer.AddSpacer(self.FromDIP(12))

        controls_sizer = wx.BoxSizer(wx.HORIZONTAL)
        content_sizer.Add(controls_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, content_padding)

        history_column = wx.BoxSizer(wx.VERTICAL)
        controls_sizer.Add(history_column, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, self.FromDIP(16))

        history_label = wx.StaticText(toolbar_panel, label="Clipboard history")
        history_label.SetForegroundColour(styles.SUBTLE_TEXT)
        history_column.Add(history_label, 0, wx.BOTTOM, self.FromDIP(4))

        self.history_choice = wx.Choice(toolbar_panel)
        self.history_choice.SetMinSize(self.FromDIP(wx.Size(260, 36)))
        history_column.Add(self.history_choice, 0, wx.EXPAND)

        history_limit_column = wx.BoxSizer(wx.VERTICAL)
        controls_sizer.Add(history_limit_column, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, self.FromDIP(20))

        limit_label = wx.StaticText(toolbar_panel, label="History limit")
        limit_label.SetForegroundColour(styles.SUBTLE_TEXT)
        history_limit_column.Add(limit_label, 0, wx.BOTTOM, self.FromDIP(4))

        self._history_spin = wx.SpinCtrl(toolbar_panel, min=1, max=50, initial=self._history.limit)
        self._history_spin.SetToolTip("Number of clipboard entries to keep")
        self._history_spin.Bind(wx.EVT_SPINCTRL, self._on_history_limit_changed)
        self._history_spin.Bind(wx.EVT_TEXT, self._on_history_limit_changed)
        self._history_spin.SetMinSize(self.FromDIP(wx.Size(96, 34)))
        history_limit_column.Add(self._history_spin, 0, wx.EXPAND)

        controls_sizer.AddStretchSpacer()

        buttons_column = wx.BoxSizer(wx.VERTICAL)
        controls_sizer.Add(buttons_column, 0, wx.ALIGN_CENTER_VERTICAL)

        button_specs = [
            ("Upper", "upper"),
            ("Title", "title"),
            ("Lower", "lower"),
            ("Sentence", "sentence"),
        ]

        self._buttons: dict[str, wx.Button] = {}
        buttons_row = wx.BoxSizer(wx.HORIZONTAL)
        buttons_column.Add(buttons_row, 0, wx.ALIGN_RIGHT)

        for index, (label, mode) in enumerate(button_specs):
            button = wx.Button(toolbar_panel, label=label)
            button.SetMinSize(self.FromDIP(wx.Size(110, 40)))
            button.Bind(wx.EVT_BUTTON, self._make_action_handler(mode))
            right_padding = self.FromDIP(8) if index < len(button_specs) - 1 else 0
            buttons_row.Add(button, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, right_padding)
            self._buttons[mode] = button

        self._taskbar_icon: CaseMonsterTaskBarIcon | None = CaseMonsterTaskBarIcon(self)

        self._apply_shadow_effect()
        self._refresh_history_choice()
        self.Centre(wx.BOTH)

        self.Bind(wx.EVT_CLOSE, self._on_close)

    def _make_action_handler(self, mode: str) -> Callable[[wx.CommandEvent], None]:
        def handler(event: wx.CommandEvent) -> None:
            self._run_action(mode)
            event.Skip()

        return handler

    def _format_history_label(self, text: str) -> str:
        collapsed = " ".join(line.strip() for line in text.splitlines())
        collapsed = collapsed.strip()
        if not collapsed:
            collapsed = "(whitespace)"
        max_length = 48
        if len(collapsed) > max_length:
            collapsed = collapsed[: max_length - 1] + "…"
        return collapsed

    def _refresh_history_choice(self, *, selected_text: Optional[str] = None) -> None:
        if selected_text is None and hasattr(self, "history_choice"):
            index = self.history_choice.GetSelection()
            if 0 < index <= len(self._history_entries):
                selected_text = self._history_entries[index - 1]

        self._history_entries = self._history.items
        labels = ["Current selection"] + [
            self._format_history_label(text) for text in self._history_entries
        ]
        self.history_choice.Set(labels)

        if selected_text and selected_text in self._history_entries:
            selection_index = self._history_entries.index(selected_text) + 1
        else:
            selection_index = 0

        if labels:
            self.history_choice.SetSelection(selection_index)

    def _run_action(self, mode: str) -> None:
        selection = self.history_choice.GetSelection()
        source_text = None
        if 0 < selection <= len(self._history_entries):
            source_text = self._history_entries[selection - 1]

        result = actions.run(mode, source_text=source_text)
        if result is None:
            return

        original, transformed = result
        self._history.record(original)
        self._history.record(transformed)
        self._refresh_history_choice(selected_text=source_text)

    def _on_pin_toggled(self, event: wx.CommandEvent) -> None:
        self.set_always_on_top(self._pin_toggle.GetValue())
        event.Skip()

    def _on_history_limit_changed(self, event: wx.CommandEvent) -> None:
        try:
            raw_value = int(self._history_spin.GetValue())
        except (TypeError, ValueError):
            return
        max_allowed = max(self._history_spin.GetMax(), 1)
        value = min(max(raw_value, 1), max_allowed)
        if self._history_spin.GetValue() != value:
            self._history_spin.SetValue(value)
        self._history.update_limit(value)
        self._refresh_history_choice()
        event.Skip()

    def _on_clipboard_timer(self, event: wx.TimerEvent) -> None:
        text = self._read_clipboard()
        if text is None:
            return
        before = self._history.items
        self._history.record(text)
        if self._history.items != before:
            self._refresh_history_choice()
        event.Skip()

    def _read_clipboard(self) -> Optional[str]:
        try:
            value = pyperclip.paste()
        except AttributeError:
            return None
        except Exception:  # pragma: no cover - clipboard access can fail unexpectedly
            return None
        return value or None

    def set_always_on_top(self, enabled: bool) -> None:
        self.always_on_top = bool(enabled)
        style = self.GetWindowStyleFlag()
        if enabled:
            style |= wx.STAY_ON_TOP
        else:
            style &= ~wx.STAY_ON_TOP
        self.SetWindowStyleFlag(style)
        if enabled:
            self.Raise()
        if self._pin_toggle.GetValue() != enabled:
            self._pin_toggle.SetValue(enabled)
        self._config.WriteBool("always_on_top", self.always_on_top)
        self._config.Flush()

    def _apply_shadow_effect(self) -> None:
        if "WX_MAC" in wx.PlatformInfo:
            return
        if "WXMSW" in wx.PlatformInfo:
            return
        try:
            self.SetTransparent(245)
        except wx.NotImplementedError:  # pragma: no cover - platform guard
            pass

    def _on_close(self, event: wx.CloseEvent) -> None:
        self._config.WriteBool("always_on_top", self.always_on_top)
        self._config.WriteInt("history_limit", self._history.limit)
        self._config.Flush()
        if self._clipboard_timer.IsRunning():
            self._clipboard_timer.Stop()
        if self._taskbar_icon:
            self._taskbar_icon.Destroy()
            self._taskbar_icon = None
        event.Skip()


def launch_app() -> int:
    app = wx.App()
    frame = CaseMonsterFrame(None)
    frame.Show(True)
    app.MainLoop()
    return 0


__all__ = ["CaseMonsterFrame", "launch_app"]
