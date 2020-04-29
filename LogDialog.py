I#!/usr/bin/env python
import wx

import sys
import os
import builtins as __builtin__
import inspect
import time
import platform
import subprocess
import threading, queue
from wx.lib.newevent import NewEvent

wxStdOut, EVT_STDDOUT = NewEvent()
wxWorkerDone, EVT_WORKER_DONE = NewEvent()
wxLogWindowClosing, EVT_LOG_WINDOW_CLOSED = NewEvent()

moduleList = {'osvmGlobals':'globs'}

for k,v in moduleList.items():
    print('Loading: %s as %s' % (k,v))
    mod = __import__(k, fromlist=[None])
    globals()[v] = globals().pop('mod')	# Rename module in globals()

    
####
#print(__name__)

#### Class LogDialog
class LogDialog(wx.Dialog):
    """
    Creates and displays a log window dialog.
    """
    def __init__(self, parent):
        """
        Initialize the dialog box
        """
        self.parent = parent
        
        myStyle = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
        wx.Dialog.__init__(self, None, wx.ID_ANY, 'Output Log', style=myStyle)

        self._initialize()

        self.panel1.SetSizerAndFit(self.topBoxSizer)
        #self.SetClientSize(self.topBoxSizer.GetSize())

    """
    Create and layout the widgets in the dialog
    """
    def _initialize(self):
        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self, size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        # Log output text control
        self.logTC = wx.TextCtrl(parent=self.panel1, style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.logTC.SetDefaultStyle(wx.TextAttr(wx.NullColour, wx.LIGHT_GREY))
        self.logTC.Bind(EVT_STDDOUT, self.OnUpdateLogTC)

        # Clear button
        self.btnClear = wx.Button(label='Clear Log', parent=self.panel1)
        self.btnClear.SetToolTip('Clear the content of this window')
        self.btnClear.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnClear(evt))

        # Copy button
        self.btnCopy = wx.Button(label='Copy Log', parent=self.panel1)
        self.btnCopy.SetToolTip('Copy the content of this window in the clipboard')
        self.btnCopy.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnCopy(evt))
        if globs.system != 'Darwin':
            self.btnCopy.Disable()

        # Save button
        self.btnSave = wx.Button(label='Save Log', parent=self.panel1)
        self.btnSave.SetToolTip('Save the content of this window in a file')
        self.btnSave.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnSave(evt))
            
        # Close button
        self.btnClose = wx.Button(id=wx.ID_CLOSE, parent=self.panel1)
        self.btnClose.SetToolTip('Close this Dialog')
        self.btnClose.Bind(wx.EVT_BUTTON, self.OnBtnClose)

        self.Bind(wx.EVT_CLOSE, self.OnEventClose) # Handle CLOSE event
        
        # Create box sizers
        self.btnBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.btnBoxSizer.Add(self.btnClear, 0, border=0, flag=wx.EXPAND)
        self.btnBoxSizer.AddStretchSpacer(prop=1)
        self.btnBoxSizer.Add(self.btnCopy, 0, border=0, flag=wx.EXPAND)
        self.btnBoxSizer.AddStretchSpacer(prop=1)
        self.btnBoxSizer.Add(self.btnSave, 0, border=0, flag=wx.EXPAND)
        self.btnBoxSizer.AddStretchSpacer(prop=1)
        self.btnBoxSizer.Add(self.btnClose, 0, border=0, flag=wx.EXPAND)        

        self.topBoxSizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.topBoxSizer.Add(self.logTC, 50, border=10, flag=wx.ALL|wx.EXPAND)
        self.topBoxSizer.AddStretchSpacer(prop=1)
        self.topBoxSizer.Add(self.btnBoxSizer, 0, border=10, flag=wx.ALL|wx.EXPAND)
        self.topBoxSizer.AddStretchSpacer(prop=1)
        
    def OnBtnClear(self, event):
        self.logTC.SetValue('')
        event.Skip()

    def OnEventClose(self, event):
        evt = wxLogWindowClosing()
        wx.PostEvent(self.parent, evt)
        self.Destroy()
        event.Skip()

    def OnBtnClose(self, event):
        evt = wxLogWindowClosing()
        wx.PostEvent(self.parent, evt)
        self.Destroy()
        event.Skip()

    def OnBtnSave(self, event):
        self.logTC.SaveFile(filename='osvm.log')        
        event.Skip()
        
    def OnUpdateLogTC(self, event):
        value = event.text
        self.logTC.AppendText(value)
        event.Skip()
        
    def OnBtnCopy(self, event):
        if globs.system == 'Darwin':
            data = self.logTC.GetValue()
            subprocess.run("pbcopy", universal_newlines=True, input=data)
        event.Skip()

def LongRunningProcess(lines_of_output):
    for x in range(lines_of_output):
        print("%d. I am a line of output (hi!)...." % x)
        time.sleep(0.5)
        
class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)
        self.requestQ = queue.Queue() #create queues
        self.resultQ = queue.Queue()
        self.logDlg = None
        
        self.panel1 = wx.Panel(self)
        
        self.logB = wx.Button(parent=self.panel1, id=wx.ID_ANY, label='Show Log') 
        self.logB.Bind(wx.EVT_BUTTON, self.OnBtnLog)

        self.logMsgB = wx.Button(parent=self.panel1, id=wx.ID_ANY, label='Generate Log Messages') 
        self.logMsgB.Bind(wx.EVT_BUTTON, self.OnBtnGenerateLogMsgs)

        self.exitB = wx.Button(parent=self.panel1, id=wx.ID_EXIT) 
        self.exitB.Bind(wx.EVT_BUTTON, self.OnBtnExit)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.logB, 1, wx.EXPAND)
        sizer.Add(self.logMsgB, 1, wx.EXPAND)
        sizer.Add(self.exitB, 1, wx.EXPAND)
        self.panel1.SetSizerAndFit(sizer)
        
        #thread
        self.worker = Worker(self, self.requestQ, self.resultQ)
        self.Bind(EVT_WORKER_DONE, self.OnWorkerDone)

        self.Bind(EVT_LOG_WINDOW_CLOSED, self.OnLogWindowClosed)
        
    def OnBtnExit(self, event):        
        if self.logDlg:
            self.logDlg.Close()
        self.Destroy()

    def OnLogWindowClosed(self, event):
        self.logB.SetLabel('Show Log')
        self.logDlg = None
        event.Skip()
        
    def OnBtnLog(self, event):
        button = event.GetEventObject()
        label = button.GetLabel()

        if label == 'Show Log':
            button.SetLabel('Close Log')
            self.logDlg = LogDialog(self)
            self.logDlg.Show()
        else:
            button.SetLabel('Show Log')
            self.logDlg.Destroy()
            self.logDlg = None
        
    def OnBtnGenerateLogMsgs(self, event):
        # If the Log window is not open, open it.
        if not self.logDlg:
            # Simulate a 'Show Log' event
            evt = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self.logB.GetId())
            evt.SetEventObject(self.logB)
            wx.PostEvent(self.logB, evt)
            wx.Yield()

        lines_of_output=10
        id = self.worker.beginTest(LongRunningProcess, lines_of_output)
        
    def OnWorkerDone(self, event):
        pass
        
class Worker(threading.Thread):
    requestID = 0
    def __init__(self, parent, requestQ, resultQ, **kwds):
        threading.Thread.__init__(self, **kwds) 
        self.setDaemon(True) 
        self.requestQ = requestQ
        self.resultQ = resultQ
        self.start() 
        
    def beginTest(self, callable, *args, **kwds):
        Worker.requestID += 1
        self.requestQ.put((Worker.requestID, callable, args, kwds))
        return Worker.requestID

    def run(self):
        while True:
            requestID, callable, args, kwds = self.requestQ.get()
            self.resultQ.put((requestID, callable(*args, **kwds))) 
            evt = wxWorkerDone()
            wx.PostEvent(wx.GetApp().frame, evt)
                               
class SysOutListener:
    def __init__(self, dup=True):
        self.dup = dup
        
    def write(self, string):
        if self.dup:
            sys.__stdout__.write(string)
        evt = wxStdOut(text=string)
        if wx.GetApp().frame.logDlg:
            wx.QueueEvent(wx.GetApp().frame.logDlg.logTC, evt)
        # else:
        #     sys.__stdout__.write('No Log window')
            
def myprint(*args, **kwargs):
    """My custom print() function."""
    # Adding new arguments to the print function signature 
    # is probably a bad idea.
    # Instead consider testing if custom argument keywords
    # are present in kwargs
    __builtin__.print('%s():' % inspect.stack()[1][3], *args, **kwargs)
            
class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, -1, 'Rebinding stdout')
        self.frame.Show(True)
        self.frame.Center()
        return True
 
# Entry point
if __name__ == '__main__':
    # Init Globals instance
    globs.system = platform.system()		# Linux or Windows or MacOS (Darwin)

    app = MyApp(0)
    sys.stdout = SysOutListener()
    app.MainLoop()
