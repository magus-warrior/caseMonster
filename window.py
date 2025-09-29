"""wxPython GUI for caseMonster."""

from __future__ import annotations

import platform
from pathlib import Path
from typing import Callable
import webbrowser

import wx
import wx.adv

from main import funky_case, lower_case, title_case, upper_case

if platform.system() == "Windows":
    try:
        from platform_integration import windows as win_integration
    except Exception:  # pragma: no cover - defensive guard
        win_integration = None
else:  # pragma: no cover - non-Windows platforms
    win_integration = None

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


class SettingsDialog(wx.Dialog):
    """Lightweight settings dialog for common preferences."""

    def __init__(self, parent: wx.Window, always_on_top: bool):
        super().__init__(parent, title="caseMonster settings")

        self.hide_requested = False
        self._always_checkbox = wx.CheckBox(
            self, label="Keep the floating window always on top"
        )
        self._always_checkbox.SetValue(always_on_top)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self._always_checkbox, 0, wx.ALL | wx.EXPAND, 10)

        hide_button = wx.Button(self, wx.ID_ANY, "Hide main window")
        hide_button.Bind(wx.EVT_BUTTON, self._on_hide_clicked)
        main_sizer.Add(hide_button, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)

        if win_integration is not None:
            register_button = wx.Button(
                self,
                wx.ID_ANY,
                "Register Windows Explorer context menu entries",
            )
            register_button.Bind(wx.EVT_BUTTON, self._on_register_context_menu)
            main_sizer.Add(register_button, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)

            unregister_button = wx.Button(
                self,
                wx.ID_ANY,
                "Remove Explorer context menu entries",
            )
            unregister_button.Bind(wx.EVT_BUTTON, self._on_unregister_context_menu)
            main_sizer.Add(
                unregister_button, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10
            )

        button_sizer = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        if button_sizer:
            ok_button = button_sizer.GetAffirmativeButton()
            if ok_button:
                ok_button.SetLabel("Save")
            main_sizer.Add(button_sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 10)

        self.SetSizerAndFit(main_sizer)
        self.SetMinSize(wx.Size(380, self.GetSize().height))

    def _on_hide_clicked(self, event: wx.CommandEvent):
        self.hide_requested = True
        self.EndModal(wx.ID_OK)
        event.Skip()

    def _on_register_context_menu(self, event: wx.CommandEvent):
        assert win_integration is not None
        try:
            win_integration.register_context_menu()
            wx.MessageBox(
                "Context menu entries registered. You may need to restart Explorer.",
                "caseMonster",
                style=wx.OK | wx.ICON_INFORMATION,
            )
        except Exception as exc:  # pragma: no cover - runtime diagnostics
            wx.MessageBox(
                f"Unable to register context menu entries:\n{exc}",
                "caseMonster",
                style=wx.OK | wx.ICON_ERROR,
            )
        event.Skip()

    def _on_unregister_context_menu(self, event: wx.CommandEvent):
        assert win_integration is not None
        try:
            win_integration.unregister_context_menu()
            wx.MessageBox(
                "Context menu entries removed.",
                "caseMonster",
                style=wx.OK | wx.ICON_INFORMATION,
            )
        except Exception as exc:  # pragma: no cover - runtime diagnostics
            wx.MessageBox(
                f"Unable to remove context menu entries:\n{exc}",
                "caseMonster",
                style=wx.OK | wx.ICON_ERROR,
            )
        event.Skip()

    @property
    def always_on_top(self) -> bool:
        return self._always_checkbox.GetValue()


class CaseMonsterTaskBarIcon(wx.adv.TaskBarIcon):
    """Taskbar/tray icon exposing quick actions."""

    def __init__(self, frame: "MONSTERcase"):
        super().__init__()
        self._frame = frame
        icon = self._load_icon()
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

    def _load_icon(self) -> wx.Icon:
        icon_path = Path(__file__).with_name("logoico.ico")
        icon = wx.Icon()
        if icon_path.exists():
            icon.LoadFile(str(icon_path), wx.BITMAP_TYPE_ICO)
        return icon

    def _make_conversion_handler(self, mode: str) -> Callable[[wx.CommandEvent], None]:
        def handler(event: wx.CommandEvent) -> None:
            self._frame.run_conversion(mode)
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


class MONSTERcase(wx.Frame):
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
            title="WarpTyme - CASEmonster",
            pos=wx.DefaultPosition,
            size=wx.Size(360, 420),
            style=style,
        )

        self._taskbar_icon: "CaseMonsterTaskBarIcon" | None = None

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

        headline_row = wx.BoxSizer(wx.HORIZONTAL)
        headline = wx.StaticText(
            self.content_panel, label="Transform your clipboard text"
        )
        headline.SetFont(HEADLINE_FONT)
        headline.SetForegroundColour(FOREGROUND_COLOUR)
        headline_row.AddStretchSpacer()
        headline_row.Add(headline, 0, wx.ALIGN_CENTER_VERTICAL)
        headline_row.AddStretchSpacer()

        self.settingsButton = wx.Button(self.content_panel, wx.ID_ANY, "⚙ Settings")
        self.settingsButton.SetFont(BUTTON_FONT)
        self.settingsButton.SetForegroundColour(FOREGROUND_COLOUR)
        self.settingsButton.SetBackgroundColour(CONTAINER_BACKGROUND)
        self.settingsButton.Bind(wx.EVT_BUTTON, self.on_settings_clicked)
        headline_row.Add(self.settingsButton, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 12)

        panel_sizer.Add(headline_row, 0, wx.EXPAND | wx.BOTTOM, 20)

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
        self.Bind(wx.EVT_CLOSE, self._on_close)

        self._taskbar_icon = CaseMonsterTaskBarIcon(self)

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
        if hasattr(self, "_taskbar_icon") and self._taskbar_icon:
            self._taskbar_icon.Destroy()

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

    def run_conversion(self, mode: str) -> None:
        actions: dict[str, Callable[[], None]] = {
            "upper": upper_case,
            "lower": lower_case,
            "title": title_case,
            "sentence": funky_case,
        }
        action = actions.get(mode)
        if action is not None:
            action()

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

    def on_settings_clicked(self, event: wx.CommandEvent):
        dialog = SettingsDialog(self, self.always_on_top)
        result = dialog.ShowModal()
        if result == wx.ID_OK:
            self.set_always_on_top(dialog.always_on_top)
            if dialog.hide_requested:
                self.Hide()
        dialog.Destroy()
        event.Skip()

    def _on_close(self, event: wx.CloseEvent):
        self._config.WriteBool("always_on_top", self.always_on_top)
        self._config.Flush()
        if self._taskbar_icon:
            self._taskbar_icon.Destroy()
            self._taskbar_icon = None
        event.Skip()


if __name__ == "__main__":
    app = wx.App()
    frame = MONSTERcase(None)
    frame.Show(True)
    app.MainLoop()
