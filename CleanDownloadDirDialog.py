#!/usr/bin/env python
import wx

import sys
import os
import builtins as __builtin__
import inspect
import glob

import osvmGlobals

####
print(__name__)

####
class CleanDownloadDirDialog(wx.Dialog):
    """
    Creates and displays a dialog that allows the user to
    selectively clean the download directory
    """
    def __init__(self, parent, download, globs):
        self.parent = parent
        self.downloadDir = download

        myprint(self.downloadDir)

        myStyle = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
        wx.Dialog.__init__(self, None, wx.ID_ANY, 'Select Files To Clean', style=myStyle)

        # Initialize the Dialog
        self._initialize(globs)

        self.panel1.SetSizerAndFit(self.topBoxSizer)
        self.SetClientSize(self.topBoxSizer.GetSize())
        self.Centre()

    def _initialize(self, globs):
        """
        Create and layout the widgets in the dialog
        """
        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self,
                               size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        # Create top level box sizer
        self.topBoxSizer = wx.BoxSizer(orient=wx.VERTICAL)

        # GridSizer to contains the various controls
        self.gbs = wx.GridBagSizer(hgap=10,vgap=5)

        # List containing various info for each file types to clean
        self.itemList = list()

        # Header 
        lineno = 0
        w0 = wx.StaticText(self.panel1)
        lbl = "<span foreground='blue'>File Types</span>"
        w0.SetLabelMarkup(lbl)
        self.gbs.Add(w0, pos=(lineno,0), border=0, flag=wx.EXPAND)

        w1 = wx.StaticText(self.panel1) # total counter
        lbl = "<span foreground='blue'>%s</span>" % 'Count'
        w1.SetLabelMarkup(lbl)
        self.gbs.Add(w1, pos=(lineno,1), border=0, flag=wx.ALIGN_RIGHT)

        w2 = wx.StaticText(self.panel1) # total size
        lbl = "<span foreground='blue'>%s</span>" % 'Size'
        w2.SetLabelMarkup(lbl)
        self.gbs.Add(w2, pos=(lineno,2), border=0, flag=wx.ALIGN_RIGHT)
        
        self.itemList.append((w0,w1,w2))

        lineno = 1
        for k in globs.CLEAN_FILETYPES.keys():
            w0 = wx.CheckBox(self.panel1, label=k)
            w0.SetValue(False)
            w0.Bind(wx.EVT_CHECKBOX, lambda evt, temp=globs: self.OnFileType(evt, temp))
            
            globs.CLEAN_FILETYPES[k], s = folderSize(self.downloadDir, k, True) 
            size = humanBytes(s)
            
            w1 = wx.StaticText(self.panel1) # counter
            w1.SetFont(wx.Font(12, wx.SWISS, wx.ITALIC, wx.NORMAL, False))
            lbl = "<span foreground='grey'>%s</span>" % str(globs.CLEAN_FILETYPES[k])
            w1.SetLabelMarkup(lbl)

            w2 = wx.StaticText(self.panel1) # size
            w2.SetFont(wx.Font(12, wx.SWISS, wx.ITALIC, wx.NORMAL, False))
            lbl = "<span foreground='grey'>%s</span>" % (size)
            w2.SetLabelMarkup(lbl)

            self.gbs.Add(w0, pos=(lineno,0), border=0, flag=wx.EXPAND)
            self.gbs.Add(w1, pos=(lineno,1), border=0, flag=wx.ALIGN_LEFT)
            self.gbs.Add(w2, pos=(lineno,2), border=0, flag=wx.ALIGN_LEFT)
            
            self.itemList.append((w0,w1,w2,s,size,globs.CLEAN_FILETYPES[k]))
            lineno += 1
        
        lineno += 1 # blank line separator
        
        # Row for total
        w0 = wx.StaticText(self.panel1)
        w0.SetFont(wx.Font(12, wx.SWISS, wx.ITALIC, wx.NORMAL, False))
        lbl = "<span foreground='red'>Total space to be freed</span>"
        w0.SetLabelMarkup(lbl)
        self.gbs.Add(w0, pos=(lineno,0), border=0, flag=wx.EXPAND)

        w1 = wx.StaticText(self.panel1) # total counter
        w1.SetFont(wx.Font(12, wx.SWISS, wx.ITALIC, wx.NORMAL, False))
        lbl = "<span foreground='red'>%s</span>" % ''
        w1.SetLabelMarkup(lbl)
        self.gbs.Add(w1, pos=(lineno,1), border=0, flag=wx.ALIGN_LEFT)

        w2 = wx.StaticText(self.panel1) # total size
        w2.SetFont(wx.Font(12, wx.SWISS, wx.ITALIC, wx.NORMAL, False))
        lbl = "<span foreground='red'>%s</span>" % ''
        w2.SetLabelMarkup(lbl)
        self.gbs.Add(w2, pos=(lineno,2), border=0, flag=wx.ALIGN_LEFT)
        
        self.itemList.append((w0,w1,w2))

        # Buttons at bottom
        self.btnCancel = wx.Button(id=wx.ID_CANCEL, parent=self.panel1, style=0)
        self.btnCancel.SetToolTip('Cancel')
        self.btnCancel.SetDefault()
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnBtnCancel)

        self.btnApply = wx.Button(id=wx.ID_APPLY, parent=self.panel1, style=0)
        self.btnApply.SetToolTip('Apply changes')
        self.btnApply.Bind(wx.EVT_BUTTON, lambda evt, temp=globs: self.OnBtnApply(evt,temp))

        # Put all buttons in a BoxSizer
        self.bottombs = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.bottombs.Add(self.btnCancel, 0, border=0, flag=0)
        self.bottombs.Add(8, 4, 0, border=0, flag=0)
        self.bottombs.Add(self.btnApply, 0, border=0, flag=0)
        
        # Add all sizers in the top box sizer
        self.topBoxSizer.Add(self.gbs, 0, border=10, flag=wx.ALL | wx.EXPAND)
        self.topBoxSizer.Add(4, 4, 1, border=0, flag=wx.EXPAND)
        self.topBoxSizer.Add(self.bottombs, 0, border=10, flag=wx.ALL | wx.ALIGN_RIGHT)

    def OnFileType(self, event, globs):
        w0 = event.GetEventObject() # Checkbox widget
        item = [x for x in self.itemList if x[0] == w0]
        w1   = item[0][1]    # StaticText widget
        w2   = item[0][2]    # StaticText widget
        s    = item[0][3]    # Size as int
        size = item[0][4]    # Size as str
        nb   = item[0][5]    # Nb files as int
        if w0.GetValue():
            lbl1 = "<span foreground='blue'>%s</span>" % str(nb)
            lbl2 = "<span foreground='blue'>%s</span>" % size
        else:
            lbl1 = "<span foreground='grey'>%s</span>" % str(nb)
            lbl2 = "<span foreground='grey'>%s</span>" % size
        w1.SetFont(wx.Font(12, wx.SWISS, wx.ITALIC, wx.NORMAL, False))
        w2.SetFont(wx.Font(12, wx.SWISS, wx.ITALIC, wx.NORMAL, False))
        w1.SetLabelMarkup(lbl1)
        w2.SetLabelMarkup(lbl2)

        # Update total row
        sizeTotal = nbTotal = 0
        for x in self.itemList[1:-1]:	# Skip header and Total lines
            w0 = x[0]  # wx.Checkbox
            s  = x[3]  # Size as int
            n  = x[5]  # Nbfiles as int
            if w0.GetValue():
                sizeTotal += s
                nbTotal += n
            
        if nbTotal == 0: nbTotal = '  '
        w1 = self.itemList[-1][1] # StaticText widget for total counter
        w1.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        lbl = "<span foreground='red'>%s</span>" % nbTotal
        w1.SetLabelMarkup(lbl)

        w2 = self.itemList[-1][2] # StaticText widget for total size
        if sizeTotal == 0:
            sizeTotal = '      '
        else:
            sizeTotal = humanBytes(sizeTotal)
        w2.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        lbl = "<span foreground='red'>%s</span>" % sizeTotal
        w2.SetLabelMarkup(lbl)

    def OnBtnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)
        event.Skip()

    def OnBtnApply(self, event, globs):
        i = 1 # Skip header
        for k in globs.CLEAN_FILETYPES.keys():
            if self.itemList[i][0].GetValue():  # wx.Checkbox
                myprint('Cleaning %s files' % k)
                for f in [y for x in os.walk(self.downloadDir) for y in glob.glob(os.path.join(x[0], '*.%s' % k))]:
                    myprint('Removing: %s' % f)
            i += 1
        self.EndModal(wx.ID_APPLY)
        event.Skip()


####
#
# Get folder size (in bytes) on the disk for files matching suffixes
# Recurse controls recursion
# ex: folderSize('/a/b/c', '.jpg'))
def folderSize(folder, suffixes, recurse):
    totalSize = 0
    fileCount = 0
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if item.lower().endswith(suffixes.lower()) and os.path.isfile(itempath):
            totalSize += os.path.getsize(itempath)
            fileCount += 1 # bump file counter
        elif os.path.isdir(itempath) and recurse:
                    c,s = folderSize(itempath, suffixes, recurse)
                    fileCount += c
                    totalSize  += s
                    
    return fileCount, totalSize

        
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
        dlg = CleanDownloadDirDialog(self, download=globs.downloadDir, globs=globs)
        ret = dlg.ShowModal()
        dlg.Destroy()

        self.Show()
        
def main():
    # Create Globals instance
    g = osvmGlobals.myGlobals()

    g.downloadDir = '/Users/didier/SynologyDrive/Photo/Olympus TG4'
#    g.downloadDir = '.'
    g.thumbDir = os.path.join(g.downloadDir, '.thumbnails')
#    g.thumbDir = ('.')
        
    # Create DemoFrame frame, passing globals instance as parameter
    app = wx.App(False)
    frame = MyFrame(None, -1, title="Test", globs=g)
    frame.Show()
    app.MainLoop()

def humanBytes(size):
    power = float(2**10)     # 2**10 = 1024
    n = 0
    power_labels = {0 : 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size = float(size / power)
        n += 1
    return '%s %s' % (('%.2f' % size).rstrip('0').rstrip('.'), power_labels[n])

if __name__ == "__main__":
    main()
