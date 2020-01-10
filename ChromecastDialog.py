#!/usr/bin/env python
import wx

import sys
import os
import builtins as __builtin__
import inspect

import osvmGlobals

####
print(__name__)


#### ChromecastDialog
class ChromecastDialog(wx.Dialog):
    """
    Creates and displays a dialog to select the Chromecast to use.
    """
    def __init__(self, globs):
        """
        Initialize the preferences dialog box
        """
        myStyle = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
        wx.Dialog.__init__(self, None, wx.ID_ANY, '%s - Chromecast Selector' % globs.myLongName, style=myStyle)

        self._initialize(globs)

        self.panel1.SetSizerAndFit(self.topBoxSizer)
        self.SetClientSize(self.topBoxSizer.GetSize())
        self.Centre()

    def _initialize(self, globs):
        self.cc = globs.chromecasts

        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self, size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        # Store all Chromecast information in a list
        self.ccProps = list()
        self.ccProps.append(('Device Name', 'Device URI', 'Device Model', 'Device Manufacturer'))

        dev = 1
        found = 0
        for cc in self.cc:
            self.ccProps.append((cc.name,cc.uri,cc.model_name,cc.device.manufacturer))
            myprint(cc.name,cc.device.uuid,globs.lastCastDeviceName,globs.lastCastDeviceUuid)
            if globs.lastCastDeviceName == cc.name and globs.lastCastDeviceUuid == str(cc.device.uuid):
                myprint('Found previous cast device %s' % cc.name)
                found = dev
            dev += 1

        self.ccProps.append(('None', '', '', ''))

        # Grid containing the information
        rows = len(self.ccProps)
        cols = len(self.ccProps[0])
        self.gsCc = wx.GridSizer(rows, cols, vgap=5, hgap=10)

        # Create all individual widgets in self.fields()
        self.fields = list()

        # first line header
        for i in range(len(self.ccProps[0])):
#            print(i,self.ccProps[0][i])
            field = wx.StaticText(self.panel1)
            field.SetLabelMarkup("<span foreground='blue'>%s</span>" % self.ccProps[0][i])
            self.fields.append(field)

        for i in range(1,rows):
            btn = wx.RadioButton(self.panel1, label=self.ccProps[i][0], style=(wx.RB_GROUP if not i else 0)) # cc name
            if (globs.castDevice and self.ccProps[i][0] == globs.castDevice.name) or (found and found == i) :
                btn.SetValue(True)

#            btn.Bind(wx.EVT_RADIOBUTTON, self.OnRadioButton)
            btn.Bind(wx.EVT_BUTTON, lambda evt, temp=globs: self.OnRadioButton(evt, temp))
            self.fields.append(btn)

            for j in range(1,len(self.ccProps[0])):
                self.fields.append(wx.StaticText(self.panel1, label=self.ccProps[i][j])) # cc information
        # Add all widgets in the grid
        for i in range(rows * cols):
            self.gsCc.Add(self.fields[i], proportion=0, flag=wx.EXPAND)

        # widgets at the Bottom 
        # Cancel button
        self.btnCancel = wx.Button(id=wx.ID_CANCEL, label='Cancel', parent=self.panel1, style=0)
        self.btnCancel.SetToolTip('Discard changes')
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnBtnCancel)

        # Close button
        self.btnClose = wx.Button(id=wx.ID_CLOSE, parent=self.panel1, style=0)
        self.btnClose.SetToolTip('Close this Dialog')
#        self.btnClose.Bind(wx.EVT_BUTTON, self.OnBtnClose)
        self.btnClose.Bind(wx.EVT_BUTTON, lambda evt, temp=globs: self.OnBtnClose(evt, temp))
        self.btnClose.SetDefault()

        self._init_sizers()

    def _init_topBoxSizer_Items(self, parent):
        parent.Add(self.propsBoxSizer, 1, border=10, flag=wx.EXPAND | wx.ALL)
        parent.Add(self.bottomBoxSizer, 0, border=10, flag=wx.ALL | wx.ALIGN_RIGHT)

    def _init_propsBoxSizer_Items(self, parent):
        parent.Add(self.gsCc, proportion=1, border=5, flag=wx.ALL|wx.EXPAND)

    def _init_bottomBoxSizer_Items(self, parent):
        parent.Add(self.btnCancel, 0, border=0, flag=wx.EXPAND)
        parent.Add(4, 4, border=0, flag=wx.EXPAND)
        parent.Add(self.btnClose, 0, border=0, flag=wx.EXPAND)

    def _init_sizers(self):
        # Create box sizers
        self.topBoxSizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.staticBox1 = wx.StaticBox(id=wx.ID_ANY, label=' Select a Chromecast to use ', 
                                       parent=self.panel1, style=0)
        self.propsBoxSizer = wx.StaticBoxSizer(box=self.staticBox1, orient=wx.HORIZONTAL)
        self.bottomBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        # Initialize each sizer
        self._init_topBoxSizer_Items(self.topBoxSizer)
        self._init_propsBoxSizer_Items(self.propsBoxSizer)
        self._init_bottomBoxSizer_Items(self.bottomBoxSizer)

    ## Events
    def OnRadioButton(self, event, globs):
        button = event.GetEventObject()
        #        print('Casting to: %s' % button.GetLabel())
        globs.castDevice = None
        for i in range(1,len(self.ccProps)):
            if self.ccProps[i][0] == button.GetLabel():
                if self.ccProps[i][0] == 'None':
                    globs.castDevice = None
                else:
                    globs.castDevice = globs.chromecasts[i-1] # -1 for header
                myprint('Using Cast Device:',globs.castDevice)
        event.Skip()

    def OnBtnClose(self, event, globs):
        for i in range(4,len(self.fields)-1,4):
            btn = self.fields[i]
            if btn.GetValue() == True:
                try:
                    globs.castDevice = globs.chromecasts[(i-4)%3]
                except:
                    globs.castDevice = None
                myprint('Using Cast Device:',globs.castDevice)
                break

        self.EndModal(wx.ID_OK)

    def OnBtnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)
        event.Skip()


########################
def initPyChromecast(globs):
    myprint('Looking for Chromecast devices...')
    globs.chromecasts = pychromecast.get_chromecasts(tries=3) 
    if not globs.chromecasts:
        msg = 'No Chromecast devices detected!'
        myprint(msg)
        dial = wx.MessageDialog(None, msg , 'Error', wx.OK | wx.ICON_ERROR)
        dial.ShowModal()
        return None

    myprint('Chromecasts Found:',globs.chromecasts)
    for x in globs.chromecasts:
        print(x)
        print(x.name)
        print(x.uri)
        print(x.model_name)
        print(x.device.manufacturer)
    
    dlg = ChromecastDialog(globs)
    ret = dlg.ShowModal()
    dlg.Destroy()
    if not globs.castDevice:
        myprint('No Chromecast devices detected!')
        return None

    myprint("Connecting to Chromecast: %s." % globs.castDevice.name)
    globs.castDevice.wait()

    mc = globs.castDevice.media_controller 
    return mc


########################
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

        initPyChromecast(globs)        

try:
    import pychromecast
except ImportError:
    msg = 'PyChromecast module not installed. Disabling Casting'
    print(msg)
    pycc = False
else:
    pycc = True
        
def main():
    # Create Globals instance
    g = globs.myGlobals()

    if not pycc:
        g.disabledModules.append(('PyChromecast',msg))
        g.pycc = False
        
    # Create DemoFrame frame, passing globals instance as parameter
    app = wx.App(False)
    frame = MyFrame(None, -1, title="Test", globs=g)
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
