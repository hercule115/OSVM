#!/usr/bin/env python
import wx

import sys
import os
import builtins as __builtin__
import inspect

import osvmGlobals

####
#print(__name__)

####
# From A. Gavana FlatNoteBook Demo
class LogoPanel(wx.Panel):
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.CLIP_CHILDREN, globs=osvmGlobals.myGlobals):

        wx.Panel.__init__(self, parent, id, pos, size, style)
        print(globs.imgDir)
        self.SetBackgroundColour(wx.WHITE)
        imgpath = os.path.join(globs.imgDir, 'sad-smiley.png')
        self.bmp = wx.Bitmap(wx.Image(imgpath, wx.BITMAP_TYPE_PNG))

        self.bigfont = wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD, False)
        self.normalfont = wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD, True)
        self.smallfont = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD, False)

        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.topTitle = 'No File Detected'
        self.midTitle = 'D. Poirot'
        self.bottomTitle = '%s %s' % (globs.myName, globs.myVersion)

    def setLogoPanelTopTitle(self, title):
        self.topTitle = title

    def setLogoPanelMidTitle(self, title):
        self.midTitle = title

    def setLogoPanelBottomTitle(self, title):
        self.bottomTitle = title

    def OnSize(self, event):
        event.Skip()
        self.Refresh()
        
    def OnPaint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        self.DoDrawing(dc)    

    def DoDrawing(self, dc):
        dc.SetBackground(wx.WHITE_BRUSH)
        dc.Clear()
        
        w, h = self.GetClientSize()
        bmpW, bmpH = self.bmp.GetWidth(), self.bmp.GetHeight()
        xpos, ypos = int((w - bmpW)/2), int((h - bmpH)/2)
        
        dc.DrawBitmap(self.bmp, xpos, ypos, True)

        dc.SetFont(self.bigfont)
        dc.SetTextForeground(wx.BLUE)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.SetPen(wx.Pen(wx.BLUE, 2))
        
        tw, th = dc.GetTextExtent(self.topTitle)
        xpos = int((w - tw)/2)
        ypos = int(h/3)

        dc.DrawRoundedRectangle(xpos-5, ypos-3, tw+10, th+6, 3)
        dc.DrawText(self.topTitle, xpos, ypos)
        
        dc.SetFont(self.normalfont)
        dc.SetTextForeground(wx.RED)
        tw, th = dc.GetTextExtent(self.midTitle)
        xpos = int((w - tw)/2)
        ypos = int(2*h/3)
        dc.DrawText(self.midTitle, xpos, ypos)

        dc.SetFont(self.smallfont)
        tw, th = dc.GetTextExtent(self.bottomTitle)
        xpos = int((w - tw)/2)
        ypos = int(2*h/3 + 4*th/2)
        dc.DrawText(self.bottomTitle, xpos, ypos)
        

####
class MyFrame(wx.Frame):
    def __init__(self, parent, id, title, globs):
        wx.Frame.__init__(self, parent, id, title)
        print(globs)
        panel = LogoPanel(self, globs=globs)

        self.Show()
        
def main():
    # Create Globals instance
    g = osvmGlobals.myGlobals()
    
    g.imgDir = os.path.join(os.getcwd(), 'images')
    
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
