"""System tray integration for quick access."""

from __future__ import annotations

from typing import Callable

import wx
import wx.adv

from . import actions
from .assets import load_icon


class CaseMonsterTaskBarIcon(wx.adv.TaskBarIcon):
    """Taskbar/tray icon exposing quick actions."""

    def __init__(self, frame: "CaseMonsterFrame"):
        super().__init__()
        self._frame = frame
        icon = load_icon('logoico.ico')
        if icon.IsOk():
            self.SetIcon(icon, "caseMonster")
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_UP, self._on_left_click)

    def CreatePopupMenu(self) -> wx.Menu:
        menu = wx.Menu()

        conversions = [
            ("Upper", "upper"),
            ("Lower", "lower"),
            ("Title", "title"),
            ("Sentence", "sentence"),
        ]
        for label, mode in conversions:
            item = menu.Append(wx.ID_ANY, label)
            menu.Bind(wx.EVT_MENU, self._make_conversion_handler(mode), item)

        menu.AppendSeparator()

        show_item = menu.Append(wx.ID_ANY, "Show window")
        menu.Bind(wx.EVT_MENU, self._on_show, show_item)
        hide_item = menu.Append(wx.ID_ANY, "Hide window")
        menu.Bind(wx.EVT_MENU, self._on_hide, hide_item)

        always_item = menu.AppendCheckItem(wx.ID_ANY, "Always on top")
        always_item.Check(self._frame.always_on_top)
        menu.Bind(wx.EVT_MENU, self._on_toggle_always_on_top, always_item)

        menu.AppendSeparator()
        exit_item = menu.Append(wx.ID_EXIT, "Exit")
        menu.Bind(wx.EVT_MENU, self._on_exit, exit_item)

        return menu

    def _make_conversion_handler(self, mode: str) -> Callable[[wx.CommandEvent], None]:
        def handler(event: wx.CommandEvent) -> None:
            actions.run(mode)
            event.Skip()

        return handler

    def _on_show(self, event: wx.CommandEvent):
        self._frame.Show()
        self._frame.Raise()
        event.Skip()

    def _on_hide(self, event: wx.CommandEvent):
        self._frame.Hide()
        event.Skip()

    def _on_toggle_always_on_top(self, event: wx.CommandEvent):
        self._frame.set_always_on_top(not self._frame.always_on_top)
        event.Skip()

    def _on_exit(self, event: wx.CommandEvent):
        self._frame.Close(True)
        event.Skip()

    def _on_left_click(self, event: wx.CommandEvent):
        if self._frame.IsShown():
            self._frame.Raise()
        else:
            self._frame.Show()
            self._frame.Raise()
        event.Skip()

    def Destroy(self) -> None:  # pragma: no cover - GUI cleanup
        try:
            self.RemoveIcon()
        finally:
            super().Destroy()


__all__ = ["CaseMonsterTaskBarIcon"]
