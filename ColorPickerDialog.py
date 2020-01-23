#!/usr/bin/env python
import wx

import sys
import math

import osvmGlobals

####
#print(__name__)

class ColorPickerDialog(wx.Dialog):
    """
    Creates and displays a dialog that allows the user to
    change the color settings for package status
    """
#    global fileColors
#    global FILE_COLORS_STATUS

    def __init__(self, parent, globs):
        """
        Initialize the dialog box
        """
        self.parent = parent
        myStyle = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
        wx.Dialog.__init__(self, None, wx.ID_ANY, '%s - Choose your colors' % globs.myName, style=myStyle)

        self._initialize(globs)

        self.panel1.SetSizerAndFit(self.topBoxSizer)
        self.SetClientSize(self.topBoxSizer.GetSize())
        self.Centre()

    def _initialize(self, globs):
        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self,
                               size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        #  bottom buttons
        self.btnReset = wx.Button(label='Reset', id=wx.ID_ANY, parent=self.panel1, style=0)
        self.btnReset.SetToolTip('Reset Colors')
        self.btnReset.Bind(wx.EVT_BUTTON, self.OnBtnReset)

        self.btnCancel = wx.Button(label='Cancel', id=wx.ID_ANY, parent=self.panel1, style=0)
        self.btnCancel.SetToolTip('Ignore changes')
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnBtnCancel)

        self.btnOK = wx.Button(id=wx.ID_ANY, label='OK', parent=self.panel1, style=0)
        self.btnOK.SetToolTip('Exit this Dialog')
        self.btnOK.Bind(wx.EVT_BUTTON, lambda evt, temp=globs: self.OnBtnOK(evt, temp))
        self.btnOK.Disable()

        self._cols = []
        # For each color/status: 
        #    create a sizer containing:
        #        - the type/name of color to tweak (text widget)
        #        - a ColorPicker
        for i in range(len(globs.fileColors)):
            # A Static Text in a box sizer used to center vertically...
            sts = wx.BoxSizer(orient=wx.VERTICAL)
            st = wx.StaticText(id=wx.ID_ANY, label=globs.FILE_COLORS_STATUS[i],
                               name=globs.FILE_COLORS_STATUS[i], parent=self.panel1, style=0)

            sts.Add(4, 4, 1, border=0, flag=wx.EXPAND)
            sts.Add(st, 0, border=0, flag=wx.EXPAND)
            sts.Add(4, 4, 1, border=0, flag=wx.EXPAND)

            sb = wx.StaticBox(id=wx.ID_ANY, label='', parent=self.panel1, style=0)
            defcol = globs.fileColors[i][0]
            cp = wx.ColourPickerCtrl(parent=self.panel1, id=wx.ID_ANY, colour=defcol, 
                                     style=wx.CLRP_DEFAULT_STYLE | wx.CLRP_SHOW_LABEL)
            cp.Bind( wx.EVT_COLOURPICKER_CHANGED, self.OnColourChanged)

            sbs = wx.StaticBoxSizer(box=sb, orient=wx.HORIZONTAL)
            sbs.Add(sts, 0, border=5, flag=wx.EXPAND | wx.ALL)    # Static Text
            sbs.Add(4, 4, 1, border=0, flag=wx.EXPAND)
            sbs.Add(cp, 0, border=5, flag=wx.EXPAND)    # Color Picker
            # Store [sizer, colorpicker] for this color
            self._cols.append([sbs, cp])

        self._init_sizers(globs)

    def _init_sizers(self, globs):
        self.topBoxSizer = wx.BoxSizer(orient=wx.VERTICAL)

        # GridSizer containing all the possible colors to tweak
        gsNumCols = 3
        gsNumRows = math.ceil(len(globs.fileColors) / gsNumCols) # round up
        self.gridSizer = wx.GridSizer(cols=gsNumCols, hgap=10, rows=gsNumRows, vgap=10)
        for w in self._cols:
            self.gridSizer.Add(w[0], proportion=0, border=5, flag=wx.EXPAND)

        # Sizer containing the 2 buttons
        self.bottomBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.bottomBoxSizer.Add(4, 4, 1, border=0, flag=wx.EXPAND)
        self.bottomBoxSizer.Add(self.btnReset, 0, border=0, flag=0)
        self.bottomBoxSizer.Add(4, 4, 1, border=0, flag=wx.EXPAND)
        self.bottomBoxSizer.Add(self.btnCancel, 0, border=0, flag=0)
        self.bottomBoxSizer.Add(8, 4, 0, border=0, flag=0)
        self.bottomBoxSizer.Add(self.btnOK, 0, border=0, flag=0)

        self.topBoxSizer.Add(self.gridSizer, 0, border=5, flag=wx.EXPAND | wx.ALL)
        self.topBoxSizer.Add(self.bottomBoxSizer, 0, border=5, flag=wx.EXPAND | wx.ALL)

    def OnColourChanged(self, event):
        #color = event.EventObject.GetColour()
        self.btnOK.SetDefault()
        self.btnOK.Enable()

    def OnBtnReset(self, event):
        global DEFAULT_FILE_COLORS

        i = 0
        for e in self._cols:
            cp = e[1]    # Color Picker
            cp.SetColour(DEFAULT_FILE_COLORS[i][0])
            i += 1
        self.btnOK.Enable()
            
    def OnBtnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)
        event.Skip()

    def OnBtnOK(self, event, globs):
        i = 0
        for e in self._cols:
            color = e[1].GetColour()
            globs.fileColors[i][0] = color    # update fileColors[]
            i += 1
        self.EndModal(wx.ID_OK)
        event.Skip()

        
class MyFrame(wx.Frame):
    def __init__(self, parent, id, title, globs):
        wx.Frame.__init__(self, parent, id, title)
        panel = wx.Panel(self)
        dlg = ColorPickerDialog(self, globs)
        ret = dlg.ShowModal()
        dlg.Destroy()

        self.Show()

def main():
    # Create Globals instance
    g = globs.myGlobals()

    # Create DemoFrame frame, passing globals instance as parameter
    app = wx.App(False)
    frame = MyFrame(None, -1, title="Test", globs=g)
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
