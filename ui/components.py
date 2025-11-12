"""Reusable Kivy widgets styled for the caseMonster desktop UI."""

from __future__ import annotations

from typing import Any

from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from . import styles


class RoundedPanel(BoxLayout):
    """Panel with rounded corners and a subtle border."""

    background_color = ListProperty(styles.CONTAINER_BACKGROUND)
    border_color = ListProperty(styles.CONTAINER_BORDER)
    radius = NumericProperty(16)
    border_width = NumericProperty(1)

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault(
            "padding",
            (dp(20), dp(20), dp(20), dp(20)),
        )
        kwargs.setdefault("spacing", dp(12))
        super().__init__(**kwargs)
        self.bind(
            pos=self._update_canvas,
            size=self._update_canvas,
            background_color=self._update_canvas,
            border_color=self._update_canvas,
        )
        self._update_canvas()

    def _update_canvas(self, *args: Any) -> None:
        radius = [dp(self.radius)] * 4
        border = dp(self.border_width)
        self.canvas.before.clear()
        with self.canvas.before:
            Color(rgba=self.border_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=radius)
            Color(rgba=self.background_color)
            RoundedRectangle(
                pos=(self.x + border, self.y + border),
                size=(self.width - 2 * border, self.height - 2 * border),
                radius=radius,
            )


class AccentButton(Button):
    """Rounded button styled with the accent palette."""

    button_color = ListProperty(styles.ACCENT_PRIMARY)

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (dp(176), dp(56)))
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.color = styles.BUTTON_TEXT_COLOUR
        self.font_size = "16sp"
        self._reset_background()
        self.bind(on_press=self._on_press, on_release=self._on_release)

    def _reset_background(self) -> None:
        self.background_color = self.button_color

    def _on_press(self, *args: Any) -> None:
        self.background_color = styles.darken_colour(self.button_color, 0.12)

    def _on_release(self, *args: Any) -> None:
        self._reset_background()


def create_caption(parent: Any, label: str) -> Label:
    """Return a caption-styled label for compatibility with legacy code."""

    caption = Label(
        text=label,
        color=styles.SUBTLE_TEXT,
        size_hint_y=None,
        halign="left",
        valign="top",
    )
    caption.bind(size=lambda inst, _: setattr(inst, "text_size", inst.size))
    caption.height = caption.texture_size[1] if caption.texture_size else dp(16)
    return caption


__all__ = ["RoundedPanel", "AccentButton", "create_caption"]
