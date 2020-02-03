#!/usr/bin/env python
import wx

import sys
import os
import builtins as __builtin__
import inspect

#import osvmGlobals
moduleList = ['osvmGlobals']

for m in moduleList:
    print('Loading: %s' % m)
    mod = __import__(m, fromlist=[None])
    globals()[m] = globals().pop('mod')	# Rename module in globals()

####
#print(__name__)

class ColorLED(wx.Control):
    """
    Creates a LED widget. State is controlled by SetState()/GetState() methods
    """
    def __init__(self, parent, globs, color, id=-1, style=wx.NO_BORDER):
        size = (17, 17)
        wx.Control.__init__(self, parent, id, size, (-1,-1), style)
        self.MinSize = size
        self._color = color
        self.SetState(globs, color)
        self.Bind(wx.EVT_PAINT, self.OnPaint, self)
        
    def SetState(self, globs, color):
        self._color = color
        ascii_led_header = (
            '/* XPM */\n',
            'static char * led_xpm[] = {\n',
            '"17 17 3 1",\n',
            '"0 c None", \n',
            '"* c #FFFFFF",\n')

        ascii_led_footer = (
            '"000000XXXXX000000",\n',
            '"0000XXXXXXXXX0000",\n',
            '"000XXXXXXXXXXX000",\n',
            '"00XXXXXXXXXXXXX00",\n',
            '"0XXXXXX**XXXXXXX0",\n',
            '"0XXXX***XXXXXXXX0",\n',
            '"XXXXX**XXXXXXXXXX",\n',
            '"XXXX**XXXXXXXXXXX",\n',
            '"XXXXXXXXXXXXXXXXX",\n',
            '"XXXXXXXXXXXXXXXXX",\n',
            '"XXXXXXXXXXXXXXXXX",\n',
            '"0XXXXXXXXXXXXXXX0",\n',
            '"0XXXXXXXXXXXXXXX0",\n',
            '"00XXXXXXXXXXXXX00",\n',
            '"000XXXXXXXXXXX000",\n',
            '"0000XXXXXXXXX0000",\n',
            '"000000XXXXX000000"};\n')

        xpmFilePath = os.path.join(globs.tmpDir, 'LED_%s.xpm' % color)
        if not os.path.exists(xpmFilePath):
        # Create an XPM file with desired color
            f = open(xpmFilePath, 'w')
            for l in ascii_led_header:
                f.write(l)
            f.write('"X c %s",\n' % color)
            for l in ascii_led_footer:
                f.write(l)
            f.close()

        self.bmp = wx.Bitmap(xpmFilePath, type=wx.BITMAP_TYPE_XPM)
        self.Refresh()
        
    def GetState(self):
        return self._color
    
    State = property(GetState, SetState)
    
    def OnPaint(self, e):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0, True)
        
def myprint(*args, **kwargs):
    """My custom print() function."""
    # Adding new arguments to the print function signature 
    # is probably a bad idea.
    # Instead consider testing if custom argument keywords
    # are present in kwargs
    __builtin__.print('%s():' % inspect.stack()[1][3], *args, **kwargs)

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title, globs):
        wx.Frame.__init__(self, parent, id, title)
        panel = wx.Panel(self)

        topBoxSizer = wx.BoxSizer(orient=wx.VERTICAL)
        fgs = wx.FlexGridSizer(cols=3, hgap=8, vgap=8)
        gbs = wx.GridBagSizer(hgap=15,vgap=0)        
        topBoxSizer.Add(gbs, 0, border=10, flag=wx.ALL | wx.EXPAND)
        topBoxSizer.Add(fgs, 0, border=10, flag=wx.ALL | wx.EXPAND)

        RED = '#DC0A0A'
        GREEN = '#0ADC0A'
        ORANGE = '#FAC800'
        self.ledsColours = [GREEN,ORANGE,RED]
        self.ledsColoursLen = len(self.ledsColours)
        
        led = ColorLED(panel, globs, RED)
        gbs.Add(led, pos=(0,0), flag=wx.ALL | wx.EXPAND, border=5)
        led = ColorLED(panel, globs, GREEN)
        gbs.Add(led, pos=(0,1), flag=wx.ALL | wx.EXPAND, border=5)
        led = ColorLED(panel, globs, ORANGE)
        gbs.Add(led, pos=(0,2), flag=wx.ALL | wx.EXPAND, border=5)

        self.led0 = ColorLED(panel, globs, GREEN)
        self.led1 = ColorLED(panel, globs, ORANGE)
        self.led2 = ColorLED(panel, globs, RED)
        gbs.Add(self.led0, pos=(1,0), flag=wx.ALL | wx.EXPAND, border=5)
        gbs.Add(self.led1, pos=(1,1), flag=wx.ALL | wx.EXPAND, border=5)
        gbs.Add(self.led2, pos=(1,2), flag=wx.ALL | wx.EXPAND, border=5)

        self.idx = 0
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, lambda evt,temp=globs: self.OnTimer(evt,temp), self.timer)
        self.timer.Start(globs.TIMER6_FREQ)
        
        panel.SetSizerAndFit(topBoxSizer)
        self.SetClientSize(topBoxSizer.GetSize())
        self.Centre()
            
        self.Show()

    def OnTimer(self, event, globs):
        self.led0.SetState(globs, self.ledsColours[self.idx%self.ledsColoursLen])
        self.idx += 1
        self.led1.SetState(globs, self.ledsColours[self.idx%self.ledsColoursLen])
        self.idx += 1
        self.led2.SetState(globs, self.ledsColours[self.idx%self.ledsColoursLen])
        self.idx += 2

def main():
    # Create Globals instance
    g = osvmGlobals.myGlobals()
    g.tmpDir = '/tmp'

    
    # Create DemoFrame frame, passing globals instance as parameter
    app = wx.App(False)

    frame = MyFrame(None, -1, title="Test", globs=g)
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
