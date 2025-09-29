from pathlib import Path
import webbrowser

from main import lower_case, title_case, upper_case, funky_case

# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-34-g2d20e717)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc


###########################################################################
## Class MONSTERcase
###########################################################################

class MONSTERcase(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"WarpTyme - CASEmonster", pos=wx.DefaultPosition,
                          size=wx.Size(350, 400), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        self.m_bitmap1 = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(u"logo.png", wx.BITMAP_TYPE_ANY),
                                         wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer1.Add(self.m_bitmap1, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        bSizer2 = wx.BoxSizer(wx.HORIZONTAL)

        self.upperButton = wx.Button(self, wx.ID_ANY, u"Upper", wx.DefaultPosition, wx.DefaultSize, 0)
        self.upperButton.SetFont(
            wx.Font(9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Arial"))

        bSizer2.Add(self.upperButton, 1, wx.ALL, 5)

        bSizer1.Add(bSizer2, 1, wx.EXPAND, 5)

        bSizer21 = wx.BoxSizer(wx.HORIZONTAL)

        self.titleButton = wx.Button(self, wx.ID_ANY, u"Title", wx.DefaultPosition, wx.DefaultSize, 0)
        self.titleButton.SetFont(
            wx.Font(9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Arial"))

        bSizer21.Add(self.titleButton, 1, wx.ALL, 5)

        bSizer1.Add(bSizer21, 1, wx.EXPAND, 5)

        bSizer211 = wx.BoxSizer(wx.HORIZONTAL)

        self.lowerButton = wx.Button(self, wx.ID_ANY, u"Lower", wx.DefaultPosition, wx.DefaultSize, 0)
        self.lowerButton.SetFont(
            wx.Font(9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Arial"))

        bSizer211.Add(self.lowerButton, 1, wx.ALL, 5)

        bSizer1.Add(bSizer211, 1, wx.EXPAND, 5)

        bSizer2111 = wx.BoxSizer(wx.HORIZONTAL)

        self.funkyButton = wx.Button(self, wx.ID_ANY, u"Sentence", wx.DefaultPosition, wx.DefaultSize, 0)
        self.funkyButton.SetFont(
            wx.Font(9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_HEAVY, False, "Arial Black"))

        bSizer2111.Add(self.funkyButton, 1, wx.ALL, 5)

        bSizer1.Add(bSizer2111, 1, wx.EXPAND, 5)

        self.SetSizer(bSizer1)
        self.Layout()
        self.m_menubar4 = wx.MenuBar(0)
        self.m_menu1 = wx.Menu()
        self.m_menuItem1 = wx.MenuItem(self.m_menu1, wx.ID_ANY, u"How to use", wx.EmptyString, wx.ITEM_NORMAL)
        self.m_menu1.Append(self.m_menuItem1)

        self.m_menubar4.Append(self.m_menu1, u"Help")

        self.SetMenuBar(self.m_menubar4)

        self.Centre(wx.BOTH)

        # Connect Events
        self.upperButton.Bind(wx.EVT_BUTTON, self.upperButtonOnButtonClick)
        self.titleButton.Bind(wx.EVT_BUTTON, self.titleButtonOnButtonClick)
        self.lowerButton.Bind(wx.EVT_BUTTON, self.lowerButtonOnButtonClick)
        self.funkyButton.Bind(wx.EVT_BUTTON, self.funkyButtonOnButtonClick)
        self.Bind(wx.EVT_MENU, self.m_menuItem1OnMenuSelection, id=self.m_menuItem1.GetId())

    def __del__(self):
        pass

    # Virtual event handlers, override them in your derived class


    def upperButtonOnButtonClick(self, event):
        upper_case()
        event.Skip()


    def lowerButtonOnButtonClick(self, event):
        lower_case()
        event.Skip()


    def titleButtonOnButtonClick(self, event):
        title_case()
        event.Skip()


    def funkyButtonOnButtonClick(self, event):
        funky_case()
        event.Skip()


    def m_menuItem1OnMenuSelection(self, event):
        help_file = Path(__file__).with_name("help.txt")
        if not help_file.exists():
            wx.LogError(f"Help file not found: {help_file}")
            return

        try:
            webbrowser.open(help_file.resolve().as_uri())
        except Exception as exc:
            wx.LogError(f"Unable to open help file: {exc}")
        event.Skip()


if __name__ == "__main__":
    app = wx.App()
    frame = MONSTERcase(None)
    frame.Show(True)
    app.MainLoop()



