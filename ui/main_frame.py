"""Main application window for caseMonster."""

from __future__ import annotations

import wx

from . import actions, styles
from .assets import load_bitmap, load_icon
from .components import (
    AccentButton,
    FeatureList,
    RoundedPanel,
    create_caption,
    create_section_heading,
)
from .dialogs import SettingsDialog, open_help_guide
from .taskbar import CaseMonsterTaskBarIcon


class HeroPanel(RoundedPanel):
    """Hero-style header that introduces the application purpose."""

    def __init__(self, parent: wx.Window):
        background = styles.lighten_colour(styles.CONTAINER_BACKGROUND, 12)
        super().__init__(parent, radius=22, padding=24, background=background)
        self.SetBackgroundColour(background)

        layout = wx.BoxSizer(wx.HORIZONTAL)
        column = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(self, label="Clipboard stylist")
        title.SetFont(styles.get_font("headline"))
        title.SetForegroundColour(styles.FOREGROUND_COLOUR)
        column.Add(title, 0)

        subtitle = create_caption(
            self,
            "Convert your copied text into the perfect tone before you paste it anywhere.",
        )
        subtitle.Wrap(260)
        column.Add(subtitle, 0, wx.TOP, 4)

        self._status = create_caption(self, "Always on top: on")
        self._status.SetForegroundColour(styles.ACCENT_SECONDARY)
        column.Add(self._status, 0, wx.TOP, 12)

        layout.Add(column, 1, wx.EXPAND)

        bitmap = load_bitmap('logo.png')
        if bitmap:
            image = wx.StaticBitmap(self, wx.ID_ANY, bitmap)
            layout.Add(image, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 16)

        self.content_sizer.Add(layout, 0, wx.EXPAND)

    def update_status(self, always_on_top: bool) -> None:
        state = "on" if always_on_top else "off"
        self._status.SetLabel(f"Always on top: {state}")


class CaseMonsterFrame(wx.Frame):
    """Top-level window with the modernised clipboard tooling UI."""

    def __init__(self, parent: wx.Window | None):
        self._config = wx.Config(appName="caseMonster", vendorName="WarpTyme")
        if self._config.HasEntry("always_on_top"):
            self.always_on_top = self._config.ReadBool("always_on_top")
        else:
            self.always_on_top = True

        base_style = wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX
        style = base_style | (wx.STAY_ON_TOP if self.always_on_top else 0)

        super().__init__(
            parent,
            id=wx.ID_ANY,
            title="caseMonster",
            pos=wx.DefaultPosition,
            size=wx.Size(520, 600),
            style=style,
        )

        styles.apply_default_theme(self)
        self.SetSizeHints(minW=500, minH=520)
        self.SetIcon(load_icon('logoico.ico'))

        self._taskbar_icon: CaseMonsterTaskBarIcon | None = None

        frame_sizer = wx.BoxSizer(wx.VERTICAL)

        self.content_panel = wx.Panel(self)
        styles.apply_default_theme(self.content_panel)
        frame_sizer.Add(self.content_panel, 1, wx.EXPAND | wx.ALL, 26)

        content = wx.BoxSizer(wx.VERTICAL)
        content.AddStretchSpacer()

        hero = HeroPanel(self.content_panel)
        content.Add(hero, 0, wx.EXPAND)
        content.AddSpacer(24)
        self._hero = hero

        action_panel = RoundedPanel(self.content_panel, padding=24)
        action_panel.SetForegroundColour(styles.FOREGROUND_COLOUR)
        action_panel.SetBackgroundColour(styles.CONTAINER_BACKGROUND)
        panel_body = action_panel.content_sizer

        heading_row = wx.BoxSizer(wx.HORIZONTAL)
        heading_col = wx.BoxSizer(wx.VERTICAL)

        heading = create_section_heading(action_panel, "Pick a transformation")
        heading_col.Add(heading, 0)

        caption = create_caption(
            action_panel,
            "caseMonster grabs your selected text, applies the style, and pastes it back instantly.",
        )
        caption.Wrap(320)
        heading_col.Add(caption, 0, wx.TOP, 4)
        heading_row.Add(heading_col, 1, wx.ALIGN_CENTER_VERTICAL)

        self.settings_button = AccentButton(
            action_panel,
            "⚙ Settings",
            styles.ACCENT_NEUTRAL,
        )
        self.settings_button.SetMinSize(wx.Size(150, 48))
        heading_row.Add(self.settings_button, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 12)

        panel_body.Add(heading_row, 0, wx.EXPAND)
        panel_body.AddSpacer(16)

        button_grid = wx.FlexGridSizer(0, 2, 12, 12)
        button_grid.AddGrowableCol(0, 1)
        button_grid.AddGrowableCol(1, 1)

        self.upper_button = AccentButton(action_panel, "UPPERCASE", styles.ACCENT_PRIMARY)
        button_grid.Add(self.upper_button, 0, wx.EXPAND)

        self.title_button = AccentButton(action_panel, "Title Case", styles.ACCENT_SECONDARY)
        button_grid.Add(self.title_button, 0, wx.EXPAND)

        self.lower_button = AccentButton(action_panel, "lowercase", styles.ACCENT_NEUTRAL)
        button_grid.Add(self.lower_button, 0, wx.EXPAND)

        self.funky_button = AccentButton(action_panel, "Sentence case", styles.ACCENT_TERTIARY)
        button_grid.Add(self.funky_button, 0, wx.EXPAND)

        panel_body.Add(button_grid, 0, wx.EXPAND)

        helper_caption = create_caption(
            action_panel,
            "Tip: Use the tray icon for a single click conversion even when the window is hidden.",
        )
        helper_caption.Wrap(320)
        panel_body.Add(helper_caption, 0, wx.TOP, 18)

        content.Add(action_panel, 0, wx.EXPAND)
        content.AddSpacer(24)

        insights_panel = RoundedPanel(self.content_panel, padding=20)
        insights_panel.SetBackgroundColour(styles.CONTAINER_BACKGROUND)
        insights_body = insights_panel.content_sizer

        insights_body.Add(create_section_heading(insights_panel, "Why people love caseMonster"), 0)
        insights_body.AddSpacer(12)
        insights_body.Add(
            FeatureList(
                insights_panel,
                [
                    "Instantly toggles between styles without touching formatting menus.",
                    "Remembers your always-on-top preference for effortless workflows.",
                    "Works from the tray so you can keep your workspace uncluttered.",
                ],
            ),
            0,
            wx.EXPAND,
        )

        content.Add(insights_panel, 0, wx.EXPAND)
        content.AddSpacer(24)

        footer = create_caption(
            self.content_panel,
            "Need help? Choose Help → How to use or right-click the tray icon for quick actions.",
        )
        footer.Wrap(360)
        content.Add(footer, 0, wx.ALIGN_CENTER_HORIZONTAL)

        content.AddStretchSpacer()

        self.content_panel.SetSizer(content)
        self.SetSizer(frame_sizer)

        self._apply_shadow_effect()

        self.Layout()

        menubar = wx.MenuBar()
        help_menu = wx.Menu()
        self._help_item = help_menu.Append(wx.ID_ANY, "How to use")
        menubar.Append(help_menu, "Help")
        self.SetMenuBar(menubar)

        self.Centre(wx.BOTH)

        # Event bindings
        self.upper_button.Bind(wx.EVT_BUTTON, lambda event: self._run_action("upper", event))
        self.lower_button.Bind(wx.EVT_BUTTON, lambda event: self._run_action("lower", event))
        self.title_button.Bind(wx.EVT_BUTTON, lambda event: self._run_action("title", event))
        self.funky_button.Bind(wx.EVT_BUTTON, lambda event: self._run_action("sentence", event))
        self.settings_button.Bind(wx.EVT_BUTTON, self._on_settings_clicked)
        self.Bind(wx.EVT_MENU, self._on_help_requested, self._help_item)
        self.Bind(wx.EVT_CLOSE, self._on_close)

        self._taskbar_icon = CaseMonsterTaskBarIcon(self)

        self._hero.update_status(self.always_on_top)

    def _apply_shadow_effect(self):
        if "WX_MAC" in wx.PlatformInfo:
            return
        try:
            self.SetTransparent(245)
        except wx.NotImplementedError:
            pass

    def _run_action(self, mode: str, event: wx.CommandEvent):
        actions.run(mode)
        event.Skip()

    def set_always_on_top(self, enabled: bool) -> None:
        self.always_on_top = enabled
        style = self.GetWindowStyleFlag()
        if enabled:
            style |= wx.STAY_ON_TOP
        else:
            style &= ~wx.STAY_ON_TOP
        self.SetWindowStyleFlag(style)
        if enabled:
            self.Raise()
        self._config.WriteBool("always_on_top", self.always_on_top)
        self._config.Flush()
        self._hero.update_status(self.always_on_top)

    def _on_settings_clicked(self, event: wx.CommandEvent):
        dialog = SettingsDialog(self, self.always_on_top)
        result = dialog.ShowModal()
        if result == wx.ID_OK:
            self.set_always_on_top(dialog.always_on_top)
            if dialog.hide_requested:
                self.Hide()
        dialog.Destroy()
        event.Skip()

    def _on_help_requested(self, event: wx.CommandEvent):
        open_help_guide(self)
        event.Skip()

    def _on_close(self, event: wx.CloseEvent):
        self._config.WriteBool("always_on_top", self.always_on_top)
        self._config.Flush()
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
