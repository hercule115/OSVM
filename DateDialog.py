#!/usr/bin/env python
import wx
import wx.adv

import sys
import os
import builtins as __builtin__
import inspect
import time
import datetime

#import osvmGlobals
moduleList = ['osvmGlobals']

for m in moduleList:
    print('Loading: %s' % m)
    mod = __import__(m, fromlist=[None])
    globals()[m] = globals().pop('mod')	# Rename module in globals()

####
#print(__name__)

### class dateDialog
class DateDialog(wx.Dialog):
    """
    Creates and displays a dialog to select a date
    """
    def __init__(self, parent,fromdate, todate, globs):
        myStyle = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
        wx.Dialog.__init__(self, None, wx.ID_ANY, 'Date Selector', style=myStyle)

        self.fromdate = fromdate
        self.todate = todate

        self._initialize()

        self.panel1.SetSizerAndFit(self.topBoxSizer)
        self.SetClientSize(self.topBoxSizer.GetSize())
        self.Centre()

    def _initialize(self):
        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self, size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        self.wintitle = wx.StaticText(self.panel1)
        t = 'Select a Date in the Calendar: '
        m = "<big><span foreground='blue'>%s</span></big>" % t
        self.wintitle.SetLabelMarkup(m)

        self.dpc = wx.adv.GenericCalendarCtrl(self.panel1, style = wx.adv.DP_DEFAULT | wx.adv.DP_SHOWCENTURY | wx.adv.DP_ALLOWNONE)
        self.dpc.EnableMonthChange(True)
        d1 = wx.DateTime.FromDMY(int(self.fromdate.split('/')[1]),
                                 int(self.fromdate.split('/')[0]) - 1,	# Month starts from 0
                                 int(self.fromdate.split('/')[2]))
        d2 = wx.DateTime.FromDMY(int(self.todate.split('/')[1]),
                                 int(self.todate.split('/')[0]) - 1,	# Month starts from 0
                                 int(self.todate.split('/')[2]))
        self.dpc.SetDateRange(lowerdate=d1, upperdate=d2)
        self.dpc.Bind(wx.adv.EVT_CALENDAR, self.OnCalendarChanged)

        # widgets at the Bottom 
        # Cancel button
        self.btnCancel = wx.Button(id=wx.ID_CANCEL, parent=self.panel1, style=0)
        self.btnCancel.SetToolTip('Discard changes')
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnBtnCancel)

        # Close button
        self.btnClose = wx.Button(id=wx.ID_CLOSE, parent=self.panel1, style=0)
        self.btnClose.SetToolTip('Close this network')
        self.btnClose.Bind(wx.EVT_BUTTON, self.OnBtnClose)

        self._init_sizers()

    def _init_topBoxSizer_Items(self, parent):
        parent.Add(self.titleBoxSizer, 0, border=10, flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER)
        parent.Add(self.mainBoxSizer, 1, border=10, flag=wx.EXPAND | wx.ALL)
        parent.Add(self.bottomBoxSizer, 0, border=10, flag=wx.ALL | wx.ALIGN_RIGHT)

    def _init_titleBoxSizer_Items(self, parent):
        parent.Add(0, 4, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.wintitle, 1, border=0, flag=wx.EXPAND)
        parent.Add(0, 4, 0, border=0, flag=wx.EXPAND)

    def _init_mainBoxSizer_Items(self, parent):
        parent.Add(self.dpc, 0, border=0, flag=wx.EXPAND | wx.ALL)

    def _init_bottomBoxSizer_Items(self, parent):
        parent.Add(self.btnCancel, 0, border=0, flag=wx.EXPAND)
        parent.Add(4, 4, border=0, flag=wx.EXPAND)
        parent.Add(self.btnClose, 0, border=0, flag=wx.EXPAND)

    def _init_sizers(self):
        # Create box sizers
        self.topBoxSizer    = wx.BoxSizer(orient=wx.VERTICAL)
        self.titleBoxSizer  = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.mainBoxSizer   = wx.BoxSizer(orient=wx.VERTICAL)
        self.bottomBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        # Initialize each sizer
        self._init_topBoxSizer_Items(self.topBoxSizer)
        self._init_titleBoxSizer_Items(self.titleBoxSizer)
        self._init_mainBoxSizer_Items(self.mainBoxSizer)
        self._init_bottomBoxSizer_Items(self.bottomBoxSizer)

    def OnCalendarChanged(self, event):
        myprint(self.dpc.GetDate())

    def OnBtnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBtnClose(self, event):
        myprint(self.dpc.GetDate())
        self.EndModal(wx.ID_OK)

########################
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

        today = datetime.date.today()
        remNewestDate = today.strftime("%m/%d/%Y")
        remOldestDate = '01/01/1970'

        dlg = DateDialog(self, remOldestDate, remNewestDate, globs)
        ret = dlg.ShowModal()
        dlg.Destroy()

        self.Show()

def main():
    # Create Globals instance
    g = osvmGlobals.myGlobals()

    g.viewMode = True
    
    # Create DemoFrame frame, passing globals instance as parameter
    app = wx.App(False)
    frame = MyFrame(None, -1, title="Test", globs=g)
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
