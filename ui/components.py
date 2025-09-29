"""Reusable UI building blocks for the caseMonster desktop app."""

from __future__ import annotations

from typing import Sequence

import wx

from . import styles


class RoundedPanel(wx.Panel):
    """Panel that draws a rounded rectangle background and subtle border."""

    def __init__(
        self,
        parent: wx.Window,
        *,
        radius: int = 16,
        padding: int = 20,
        background: wx.Colour | None = None,
    ) -> None:
        super().__init__(parent, style=wx.BORDER_NONE)
        self._radius = radius
        self._padding = padding
        self._background = background or styles.CONTAINER_BACKGROUND

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)

        self._content_sizer = wx.BoxSizer(wx.VERTICAL)
        wrapper = wx.BoxSizer(wx.VERTICAL)
        wrapper.Add(self._content_sizer, 1, wx.EXPAND | wx.ALL, self._padding)
        self.SetSizer(wrapper)

    @property
    def content_sizer(self) -> wx.BoxSizer:
        return self._content_sizer

    def Add(self, window: wx.Window, proportion: int = 0, flag: int = 0, border: int = 0):
        self._content_sizer.Add(window, proportion, flag, border)

    def AddSpacer(self, size: int):
        self._content_sizer.AddSpacer(size)

    def _on_paint(self, event: wx.PaintEvent) -> None:
        size = self.GetClientSize()
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
        dc.Clear()

        gc = wx.GraphicsContext.Create(dc)
        if gc:
            path = gc.CreatePath()
            path.AddRoundedRectangle(
                0,
                0,
                size.width,
                size.height,
                self._radius,
            )
            gc.SetPen(wx.Pen(styles.CONTAINER_BORDER, 1))
            gc.SetBrush(wx.Brush(self._background))
            gc.DrawPath(path)
        event.Skip(False)


class AccentButton(wx.Button):
    """Rounded, colour-forward call-to-action button used in the main grid."""

    def __init__(self, parent: wx.Window, label: str, colour: wx.Colour):
        style = wx.BORDER_NONE | wx.BU_EXACTFIT
        super().__init__(parent, wx.ID_ANY, label, style=style)

        self._base_colour = colour
        self._hover_colour = styles.lighten_colour(colour, 24)
        self._pressed_colour = styles.lighten_colour(colour, 8)
        self._radius = 12

        self.SetMinSize(wx.Size(160, 54))
        self.SetFont(styles.get_font("button"))
        self.SetForegroundColour(styles.FOREGROUND_COLOUR)
        self.SetBackgroundColour(self._base_colour)

        self.Bind(wx.EVT_ENTER_WINDOW, self._on_hover)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_press)
        self.Bind(wx.EVT_LEFT_UP, self._on_release)
        self.Bind(wx.EVT_PAINT, self._on_paint)

    def _set_colour(self, colour: wx.Colour) -> None:
        self.SetBackgroundColour(colour)
        self.Refresh()

    def _on_hover(self, event: wx.MouseEvent) -> None:
        self._set_colour(self._hover_colour)
        event.Skip()

    def _on_leave(self, event: wx.MouseEvent) -> None:
        self._set_colour(self._base_colour)
        event.Skip()

    def _on_press(self, event: wx.MouseEvent) -> None:
        self._set_colour(self._pressed_colour)
        event.Skip()

    def _on_release(self, event: wx.MouseEvent) -> None:
        inside = self.GetClientRect().Contains(event.GetPosition())
        self._set_colour(self._hover_colour if inside else self._base_colour)
        event.Skip()

    def _on_paint(self, event: wx.PaintEvent):
        size = self.GetClientSize()
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
        dc.Clear()

        gc = wx.GraphicsContext.Create(dc)
        if gc:
            path = gc.CreatePath()
            path.AddRoundedRectangle(0, 0, size.width, size.height, self._radius)
            gc.SetPen(wx.Pen(styles.lighten_colour(self.GetBackgroundColour(), 6), 1))
            gc.SetBrush(wx.Brush(self.GetBackgroundColour()))
            gc.DrawPath(path)

            label = self.GetLabel()
            gc.SetFont(styles.get_font("button"), styles.FOREGROUND_COLOUR)
            tw, th = gc.GetTextExtent(label)
            gc.DrawText(label, (size.width - tw) / 2, (size.height - th) / 2)
        else:  # pragma: no cover - fallback
            super().DoEraseBackground(dc)
        event.Skip(False)


class FeatureList(wx.Panel):
    """Render a vertical bullet list with subtle accent icons."""

    def __init__(self, parent: wx.Window, items: Sequence[str]):
        super().__init__(parent, style=wx.BORDER_NONE)
        styles.apply_default_theme(self)
        self.SetBackgroundColour(styles.CONTAINER_BACKGROUND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        for item in items:
            row = wx.BoxSizer(wx.HORIZONTAL)
            bullet = wx.StaticText(self, label="•")
            bullet.SetFont(styles.get_font("headline"))
            bullet.SetForegroundColour(styles.ACCENT_TERTIARY)
            row.Add(bullet, 0, wx.RIGHT, 8)

            text = wx.StaticText(self, label=item)
            text.Wrap(280)
            text.SetFont(styles.get_font("caption"))
            text.SetForegroundColour(styles.SUBTLE_TEXT)
            row.Add(text, 1)

            sizer.Add(row, 0, wx.BOTTOM | wx.EXPAND, 6)

        self.SetSizer(sizer)


def create_caption(parent: wx.Window, label: str) -> wx.StaticText:
    widget = wx.StaticText(parent, label=label)
    widget.SetFont(styles.get_font("caption"))
    widget.SetForegroundColour(styles.SUBTLE_TEXT)
    return widget


def create_section_heading(parent: wx.Window, label: str) -> wx.StaticText:
    widget = wx.StaticText(parent, label=label)
    widget.SetFont(styles.get_font("headline"))
    widget.SetForegroundColour(styles.FOREGROUND_COLOUR)
    return widget


__all__ = [
    "RoundedPanel",
    "AccentButton",
    "FeatureList",
    "create_caption",
    "create_section_heading",
]
