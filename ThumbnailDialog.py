#!/usr/bin/env python
import wx

import sys
import os
import builtins as __builtin__
import inspect
import glob

import osvmGlobals

####
#print(__name__)

####
class ThumbnailDialog(wx.Dialog):
    """
    Creates and displays a dialog to show a thumbnail
    """
    def __init__(self, parent, thumbnail, globs):
        """
        Initialize the dialog box
        """
        self.parent = parent
        self.thumbFilePath = thumbnail
        self.PhotoMaxSize = 240
 
        myStyle = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
        wx.Dialog.__init__(self, None, wx.ID_ANY, 'Thumbnail Viewer', style=myStyle)

        self._initialize()

        self.panel1.SetSizerAndFit(self.topBoxSizer)
        self.SetClientSize(self.topBoxSizer.GetSize())
        self.Centre()

    def _initialize(self):
        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self,
                               size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        img = wx.Image(240,240)
        self.imageCtrl = wx.StaticBitmap(self.panel1, wx.ID_ANY, wx.Bitmap(img))
        #  bottom buttons
        self.btnClose = wx.Button(id=wx.ID_ANY, label='Close', parent=self.panel1, style=0)
        self.btnClose.SetToolTip('Exit this Dialog')
        self.btnClose.Bind(wx.EVT_BUTTON, self.OnBtnClose)

        self._init_sizers()
        self._view_thumbnail()

    def _init_sizers(self):
        self.topBoxSizer = wx.BoxSizer(orient=wx.VERTICAL)

        self.mainSizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.mainSizer.Add(wx.StaticLine(self.panel1, wx.ID_ANY), 0, wx.ALL|wx.EXPAND, 5)
        self.mainSizer.Add(self.imageCtrl, 0, wx.ALL, 5)
        self.mainSizer.Add(wx.StaticLine(self.panel1, wx.ID_ANY), 0, wx.ALL|wx.EXPAND, 5)

        # Sizer containing the bottom buttons
        self.bottomBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.bottomBoxSizer.Add(4, 4, 1, border=0, flag=wx.EXPAND)
        self.bottomBoxSizer.Add(self.btnClose, 0, border=0, flag=0)

        self.topBoxSizer.Add(self.mainSizer, 0, border=5, flag=wx.EXPAND | wx.ALL)
        self.topBoxSizer.Add(self.bottomBoxSizer, 0, border=5, flag=wx.EXPAND | wx.ALL)

    def _view_thumbnail(self):
        filepath = self.thumbFilePath
        img = wx.Image(filepath, wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        W = img.GetWidth()
        H = img.GetHeight()
        if W > H:
            NewW = self.PhotoMaxSize
            NewH = self.PhotoMaxSize * H / W
        else:
            NewH = self.PhotoMaxSize
            NewW = self.PhotoMaxSize * W / H
        img = img.Scale(NewW, NewH)
 
        self.imageCtrl.SetBitmap(wx.Bitmap(img))
        self.panel1.Refresh()
 
    def OnBtnClose(self, event):
        self.EndModal(wx.ID_OK)
        event.Skip()

####
class MyFrame(wx.Frame):
    def __init__(self, parent, id, title, globs):
        wx.Frame.__init__(self, parent, id, title)
        panel = wx.Panel(self)
        thumbnail = os.path.join( os.getcwd(), 'images', 'plus-32.jpg')
        dlg = ThumbnailDialog(self, thumbnail=thumbnail, globs=globs)
        ret = dlg.ShowModal()
        dlg.Destroy()

        self.Show()
        
def main():
    # Create Globals instance
    g = osvmGlobals.myGlobals()

    # Create DemoFrame frame, passing globals instance as parameter
    app = wx.App(False)
    frame = MyFrame(None, -1, title="Test", globs=g)
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    def myprint(*args, **kwargs):
        """My custom print() function."""
        # Adding new arguments to the print function signature 
        # is probably a bad idea.
        # Instead consider testing if custom argument keywords
        # are present in kwargs
        __builtin__.print('%s():' % inspect.stack()[1][3], *args, **kwargs)

    main()
