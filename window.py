"""wxPython GUI for caseMonster."""

from __future__ import annotations

from pathlib import Path
import webbrowser

import wx

from main import lower_case, title_case, upper_case, funky_case

# Colour and typography palette
BACKGROUND_COLOUR = wx.Colour(18, 23, 34)
FOREGROUND_COLOUR = wx.Colour(235, 238, 245)
ACCENT_PRIMARY = wx.Colour(92, 143, 255)
ACCENT_SECONDARY = wx.Colour(83, 201, 176)
ACCENT_NEUTRAL = wx.Colour(104, 114, 134)
CONTAINER_BACKGROUND = wx.Colour(30, 38, 54)
CONTAINER_BORDER = wx.Colour(60, 72, 96)
SUBTLE_TEXT = wx.Colour(180, 190, 206)

BASE_FONT = wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Segoe UI")
HEADLINE_FONT = wx.Font(15, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Segoe UI Semibold")
BUTTON_FONT = wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Segoe UI")
CAPTION_FONT = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT, False, "Segoe UI")


class RoundedPanel(wx.Panel):
    """Panel that draws a rounded rectangle background and subtle border."""

    def __init__(self, parent: wx.Window, radius: int = 14, padding: int = 16):
        super().__init__(parent, style=wx.BORDER_NONE)
        self.radius = radius
        self.padding = padding
        self.SetBackgroundColour(CONTAINER_BACKGROUND)
        self.Bind(wx.EVT_PAINT, self._on_paint)

        self._content_sizer = wx.BoxSizer(wx.VERTICAL)
        wrapper = wx.BoxSizer(wx.VERTICAL)
        wrapper.Add(self._content_sizer, 1, wx.EXPAND | wx.ALL, self.padding)
        self.SetSizer(wrapper)

    @property
    def content_sizer(self) -> wx.BoxSizer:
        return self._content_sizer

    def Add(self, window: wx.Window, proportion=0, flag=0, border=0):
        self._content_sizer.Add(window, proportion, flag, border)

    def AddSpacer(self, size: int):
        self._content_sizer.AddSpacer(size)

    def _on_paint(self, event: wx.PaintEvent):
        size = self.GetClientSize()
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
        dc.Clear()

        gc = wx.GraphicsContext.Create(dc)
        if gc:
            path = gc.CreatePath()
            path.AddRoundedRectangle(0, 0, size.width, size.height, self.radius)
            gc.SetPen(wx.Pen(CONTAINER_BORDER, 1))
            gc.SetBrush(wx.Brush(CONTAINER_BACKGROUND))
            gc.DrawPath(path)
        event.Skip(False)


class MONSTERcase(wx.Frame):
    def __init__(self, parent: wx.Window | None):
        super().__init__(
            parent,
            id=wx.ID_ANY,
            title="WarpTyme - CASEmonster",
            pos=wx.DefaultPosition,
            size=wx.Size(360, 420),
            style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL,
        )

        self.SetBackgroundColour(BACKGROUND_COLOUR)
        self.SetForegroundColour(FOREGROUND_COLOUR)
        self.SetFont(BASE_FONT)
        self.SetSizeHints(minW=320, minH=360)
        self.SetMinSize(wx.Size(320, 360))

        frame_sizer = wx.BoxSizer(wx.VERTICAL)

        self.content_panel = wx.Panel(self)
        self.content_panel.SetBackgroundColour(BACKGROUND_COLOUR)
        self.content_panel.SetForegroundColour(FOREGROUND_COLOUR)
        self.content_panel.SetFont(BASE_FONT)
        frame_sizer.Add(self.content_panel, 1, wx.EXPAND | wx.ALL, 16)

        panel_sizer = wx.BoxSizer(wx.VERTICAL)

        logo_bitmap = self._load_logo_bitmap()
        if logo_bitmap:
            self.logo = wx.StaticBitmap(self.content_panel, wx.ID_ANY, logo_bitmap)
            panel_sizer.Add(self.logo, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 14)

        headline = wx.StaticText(self.content_panel, label="Transform your clipboard text")
        headline.SetFont(HEADLINE_FONT)
        headline.SetForegroundColour(FOREGROUND_COLOUR)
        panel_sizer.Add(headline, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 20)

        action_container = RoundedPanel(self.content_panel)
        action_container.SetForegroundColour(FOREGROUND_COLOUR)
        container_sizer = action_container.content_sizer

        caption = wx.StaticText(action_container, label="Choose how you'd like to stylize the copied text.")
        caption.SetFont(CAPTION_FONT)
        caption.SetForegroundColour(SUBTLE_TEXT)
        container_sizer.Add(caption, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 12)

        buttons_sizer = wx.BoxSizer(wx.VERTICAL)

        self.upperButton = self._create_button(action_container, "Upper", ACCENT_PRIMARY)
        buttons_sizer.Add(self.upperButton, 0, wx.EXPAND | wx.BOTTOM, 10)

        self.titleButton = self._create_button(action_container, "Title", ACCENT_SECONDARY)
        buttons_sizer.Add(self.titleButton, 0, wx.EXPAND | wx.BOTTOM, 10)

        self.lowerButton = self._create_button(action_container, "Lower", ACCENT_NEUTRAL)
        buttons_sizer.Add(self.lowerButton, 0, wx.EXPAND | wx.BOTTOM, 10)

        self.funkyButton = self._create_button(action_container, "Sentence", ACCENT_PRIMARY)
        funky_font = wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_BOLD, False, "Segoe UI")
        self.funkyButton.SetFont(funky_font)
        buttons_sizer.Add(self.funkyButton, 0, wx.EXPAND)

        container_sizer.Add(buttons_sizer, 0, wx.EXPAND)

        panel_sizer.Add(action_container, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)
        panel_sizer.AddStretchSpacer(1)

        self.content_panel.SetSizer(panel_sizer)
        self.SetSizer(frame_sizer)

        self._apply_shadow_effect()

        self.Layout()

        self.m_menubar4 = wx.MenuBar(0)
        self.m_menu1 = wx.Menu()
        self.m_menuItem1 = wx.MenuItem(self.m_menu1, wx.ID_ANY, "How to use", wx.EmptyString, wx.ITEM_NORMAL)
        self.m_menu1.Append(self.m_menuItem1)

        self.m_menubar4.Append(self.m_menu1, "Help")

        self.SetMenuBar(self.m_menubar4)

        self.Centre(wx.BOTH)

        # Connect Events
        self.upperButton.Bind(wx.EVT_BUTTON, self.upperButtonOnButtonClick)
        self.titleButton.Bind(wx.EVT_BUTTON, self.titleButtonOnButtonClick)
        self.lowerButton.Bind(wx.EVT_BUTTON, self.lowerButtonOnButtonClick)
        self.funkyButton.Bind(wx.EVT_BUTTON, self.funkyButtonOnButtonClick)
        self.Bind(wx.EVT_MENU, self.m_menuItem1OnMenuSelection, id=self.m_menuItem1.GetId())

    def _apply_shadow_effect(self):
        """Add a subtle drop shadow for floating utility feel where supported."""

        if "WX_MAC" in wx.PlatformInfo:
            return
        try:
            self.SetTransparent(245)
        except wx.NotImplementedError:
            pass

    def _load_logo_bitmap(self) -> wx.Bitmap | None:
        logo_path = Path(__file__).with_name("logo.png")
        if not logo_path.exists():
            return None

        image = wx.Image(str(logo_path))
        image.SetMaskColour(255, 255, 255)
        return image.ConvertToBitmap()

    def _create_button(self, parent: wx.Window, label: str, colour: wx.Colour) -> wx.Button:
        button = wx.Button(parent, wx.ID_ANY, label, style=wx.BORDER_NONE)
        button.SetFont(BUTTON_FONT)
        button.SetForegroundColour(FOREGROUND_COLOUR)
        button.SetBackgroundColour(colour)
        button.SetMinSize(wx.Size(220, 44))
        button.Bind(wx.EVT_ENTER_WINDOW, lambda evt, btn=button, col=colour: self._on_button_hover(btn, col))
        button.Bind(wx.EVT_LEAVE_WINDOW, lambda evt, btn=button, col=colour: self._on_button_leave(btn, col))
        return button

    def _on_button_hover(self, button: wx.Button, base_colour: wx.Colour):
        button.SetBackgroundColour(self._hover_colour(base_colour))
        button.Refresh()

    def _on_button_leave(self, button: wx.Button, base_colour: wx.Colour):
        button.SetBackgroundColour(base_colour)
        button.Refresh()

    def _hover_colour(self, colour: wx.Colour) -> wx.Colour:
        lighten = 18
        r = min(colour.Red() + lighten, 255)
        g = min(colour.Green() + lighten, 255)
        b = min(colour.Blue() + lighten, 255)
        return wx.Colour(r, g, b)

    def __del__(self):
        pass

    # Virtual event handlers, override them in your derived class
    def upperButtonOnButtonClick(self, event: wx.CommandEvent):
        upper_case()
        event.Skip()

    def lowerButtonOnButtonClick(self, event: wx.CommandEvent):
        lower_case()
        event.Skip()

    def titleButtonOnButtonClick(self, event: wx.CommandEvent):
        title_case()
        event.Skip()

    def funkyButtonOnButtonClick(self, event: wx.CommandEvent):
        funky_case()
        event.Skip()

    def m_menuItem1OnMenuSelection(self, event: wx.CommandEvent):
        help_file = Path(__file__).with_name("help.txt")
        if not help_file.exists():
            wx.LogError(f"Help file not found: {help_file}")
            return

        try:
            webbrowser.open(help_file.resolve().as_uri())
        except Exception as exc:  # pragma: no cover - logged for diagnostics
            wx.LogError(f"Unable to open help file: {exc}")
        event.Skip()


if __name__ == "__main__":
    app = wx.App()
    frame = MONSTERcase(None)
    frame.Show(True)
    app.MainLoop()