"""Secondary windows and dialogs used by the UI."""

from __future__ import annotations

import platform
import webbrowser

import wx

from . import styles
from .assets import get_asset_path
from .components import RoundedPanel, create_caption

if platform.system() == "Windows":
    try:  # pragma: no cover - runtime integration
        from platform_integration import windows as win_integration
    except Exception:  # pragma: no cover - defensive guard
        win_integration = None
else:  # pragma: no cover - non-Windows platforms
    win_integration = None


class SettingsDialog(wx.Dialog):
    """Dialog that exposes quick preferences and platform options."""

    def __init__(self, parent: wx.Window, always_on_top: bool):
        super().__init__(parent, title="caseMonster preferences")

        styles.apply_default_theme(self)
        self.hide_requested = False

        container = RoundedPanel(self, padding=18)
        container.SetBackgroundColour(styles.CONTAINER_BACKGROUND)
        body = container.content_sizer

        title = wx.StaticText(container, label="Quick preferences")
        title.SetFont(styles.get_font("headline"))
        body.Add(title, 0, wx.BOTTOM, 6)

        description = create_caption(
            container,
            "Personalise how the floating window behaves on your desktop.",
        )
        body.Add(description, 0, wx.BOTTOM, 12)

        self._always_checkbox = wx.CheckBox(
            container, label="Keep the floating window always on top"
        )
        self._always_checkbox.SetValue(always_on_top)
        self._always_checkbox.SetFont(styles.get_font("base"))
        self._always_checkbox.SetForegroundColour(styles.FOREGROUND_COLOUR)
        body.Add(self._always_checkbox, 0, wx.BOTTOM, 12)

        hide_button = wx.Button(container, wx.ID_ANY, "Hide the main window now")
        hide_button.Bind(wx.EVT_BUTTON, self._on_hide_clicked)
        body.Add(hide_button, 0, wx.BOTTOM, 12)

        if win_integration is not None:
            divider = wx.StaticLine(container)
            body.Add(divider, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)

            windows_heading = wx.StaticText(
                container, label="Windows Explorer integration"
            )
            windows_heading.SetFont(styles.get_font("button"))
            windows_heading.SetForegroundColour(styles.SUBTLE_TEXT)
            body.Add(windows_heading, 0, wx.BOTTOM, 6)

            register_button = wx.Button(
                container,
                wx.ID_ANY,
                "Register Explorer context menu entries",
            )
            register_button.Bind(wx.EVT_BUTTON, self._on_register_context_menu)
            body.Add(register_button, 0, wx.BOTTOM, 6)

            unregister_button = wx.Button(
                container,
                wx.ID_ANY,
                "Remove Explorer context menu entries",
            )
            unregister_button.Bind(wx.EVT_BUTTON, self._on_unregister_context_menu)
            body.Add(unregister_button, 0, wx.BOTTOM, 6)

        footer = create_caption(
            container,
            "Need a refresher? The Help menu opens the quick start guide in your browser.",
        )
        footer.Wrap(360)
        body.Add(footer, 0, wx.TOP, 6)

        action_row = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        if action_row:
            action_row.Realize()
            ok_button = action_row.GetOkButton()
            if ok_button:
                ok_button.SetLabel("Save")
            body.Add(action_row, 0, wx.ALIGN_RIGHT | wx.TOP, 6)

        outer_sizer = wx.BoxSizer(wx.VERTICAL)
        outer_sizer.Add(container, 1, wx.EXPAND | wx.ALL, 14)
        self.SetSizerAndFit(outer_sizer)
        self.SetMinSize(wx.Size(420, self.GetSize().height))

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


def open_help_guide(parent: wx.Window) -> None:
    """Open the bundled help document in the platform browser."""

    help_path = get_asset_path("help.txt").resolve()
    if not help_path.exists():
        wx.LogError(f"Help file not found: {help_path}")
        return

    try:
        webbrowser.open(help_path.as_uri())
    except Exception as exc:  # pragma: no cover - runtime diagnostics
        wx.LogError(f"Unable to open help file: {exc}")


__all__ = ["SettingsDialog", "open_help_guide"]
