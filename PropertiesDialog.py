#!/usr/bin/env python
import wx

import sys
import os
import builtins as __builtin__
import inspect
import time
import platform
import subprocess

moduleList = {'osvmGlobals':'globs',
              'ExifDialog':'ExifDialog'}

for k,v in moduleList.items():
    print('Loading: %s as %s' % (k,v))
    mod = __import__(k, fromlist=[None])
    globals()[v] = globals().pop('mod')	# Rename module in globals()

####
#print(__name__)

#### Class PropertiesDialog
class PropertiesDialog(wx.Dialog):
    """
    Creates and displays a Package Properties dialog.
    """
    def __init__(self, parent, fileName):
        """
        Initialize the Properties dialog box
        """
        self.fileName = fileName
        self.fields = []

        myStyle = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
        wx.Dialog.__init__(self, None, wx.ID_ANY, 'File Properties: %s' % (self.fileName), style=myStyle)

        exifFilePath = os.path.join(globs.osvmDownloadDir, globs.exifFile)
        if not os.path.exists(exifFilePath):
            myprint('%s does not exist. Creating' % exifFilePath)
            ExifDialog.saveExifDataFromImages(exifFilePath)
        # Load data from file
        self.exifData = ExifDialog.buildDictFromFile(exifFilePath)
        
        self._initialize()

        self.panel1.SetSizerAndFit(self.topBoxSizer)
        self.SetClientSize(self.topBoxSizer.GetSize())
        self.Centre()

    """
    Create and layout the widgets in the dialog
    """
    def _initialize(self):
        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self, size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        # Copy Path button
        self.btnCopyPath = wx.Button(label='Copy Path', id=wx.ID_ANY, parent=self.panel1, style=0)
        self.btnCopyPath.SetToolTip('Copy the absolute pathname of the file in the clipboard')
        self.btnCopyPath.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnCopyPath(evt))

        # Exif Data button
        self.btnExif = wx.Button(label='Exif Data', id=wx.ID_ANY, parent=self.panel1, style=0)
        self.btnExif.SetToolTip('Show the Exif Data')
        self.btnExif.Bind(wx.EVT_BUTTON, self.OnBtnExif)
        try:
            entry = self.exifData[self.fileName]    # Exif data don't exist for filename
        except:
            self.btnExif.Disable()
        
        # Close button
        self.btnClose = wx.Button(id=wx.ID_CLOSE, parent=self.panel1, style=0)
        self.btnClose.SetToolTip('Close this Dialog')
        self.btnClose.Bind(wx.EVT_BUTTON, self.OnBtnClose)

        # self.btnClose.Bind(wx.EVT_KEY_DOWN, self.OnThumbKeyDown)
        # ac = [(wx.ACCEL_NORMAL, ord(' '), wx.ID_CLOSE)]
        # tbl = wx.AcceleratorTable(ac)
        # self.SetAcceleratorTable(tbl)
    
        # Retrieve information to display from the globals
        try:
            pkginfo1 = globs.availRemoteFiles[self.fileName]
        except:
            pkginfo1 = ["",-1,-1,-1,-1,-1,""]
        try:
            pkginfo2 = globs.localFileInfos[self.fileName]
        except:
            pkginfo2 = ["","","",""]

        # Local file attrs
        if pkginfo2[globs.F_NAME]:
            ldate = time.strftime('%d-%b-%Y %H:%M', time.localtime(pkginfo2[globs.F_DATEINSECS]))
            localFileSizeString1 = humanBytes(pkginfo2[globs.F_SIZE])
            localFileSizeString2 = '(%s bytes)' % str(pkginfo2[globs.F_SIZE])
        else:
            ldate = ''
            localFileSizeString1 = ''
            localFileSizeString2 = ''

        if globs.viewMode:
            props = [ ('File Name',	        str(self.fileName)),       # Must be first
                      ('Local File Date', 	ldate),
                      ('Local File Size', 	'%s %s' % (localFileSizeString1, localFileSizeString2)) ]
        else:
            # Remote file attrs
            rdate = time.strftime('%d-%b-%Y %H:%M', time.localtime(int(pkginfo1[globs.F_DATEINSECS])))
            remFileSizeString = humanBytes(pkginfo1[globs.F_SIZE])
            props = [ ('File Name',	        str(self.fileName)),       # Must be first
                      ('Remote File Date', 	rdate),
                      ('Remote File Size',	'%s (%s bytes)' % (remFileSizeString, str(pkginfo1[globs.F_SIZE]))),
                      ('Local File Date', 	ldate),
                      ('Local File Size', 	'%s %s' % (localFileSizeString1, localFileSizeString2)) ]

        # Grid containing the information
        rows = len(props)
        cols = 2
        self.fgsPkgProps = wx.FlexGridSizer(rows, cols, vgap=5, hgap=10)

        # Create all individual widgets
        for i in range(rows):
            self.fields.append(wx.StaticText(self.panel1, label=props[i][0]))
            self.fields.append(wx.TextCtrl(self.panel1, style=wx.TE_READONLY, size=wx.Size(170, 25), value=props[i][1]))

        for i in range(rows * cols):
            if i%2 :
                self.fgsPkgProps.Add(self.fields[i], proportion=0, flag=wx.EXPAND)
            else:
                self.fgsPkgProps.Add(self.fields[i], proportion=0, flag=wx.CENTER)

        # Grow the last row/column
        self.fgsPkgProps.AddGrowableRow(rows-1, 1)
        self.fgsPkgProps.AddGrowableCol(cols-1, 1)

        self._init_sizers()

    def _init_topBoxSizer_Items(self, parent):
        parent.Add(self.propsBoxSizer, 1, border=10,
                        flag=wx.EXPAND | wx.ALL)
        parent.Add(self.buttonsBoxSizer, 0, border=10,
                        flag=wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT)

    def _init_propsBoxSizer_Items(self, parent):
        parent.Add(self.fgsPkgProps, proportion=1, border=5, flag=wx.ALL|wx.EXPAND)

    def _init_buttonsBoxSizer_Items(self, parent):
        parent.Add(self.btnCopyPath, 1, border=0, flag=wx.ALIGN_LEFT)
        parent.AddStretchSpacer(prop=1)
        parent.Add(self.btnExif, 1, border=0, flag=wx.ALIGN_CENTER)
        parent.AddStretchSpacer(prop=1)
        parent.Add(self.btnClose, 1, border=0) #211 , flag=wx.ALIGN_RIGHT)

    def _init_sizers(self):
        # Create box sizers
        self.topBoxSizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.propsBoxSizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.buttonsBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        # Initialize each sizer
        self._init_topBoxSizer_Items(self.topBoxSizer)
        self._init_propsBoxSizer_Items(self.propsBoxSizer)
        self._init_buttonsBoxSizer_Items(self.buttonsBoxSizer)

    ## Events
    def OnBtnCopyPath(self, event):
        if globs.system == 'Darwin':
            data = os.path.join(globs.osvmDownloadDir, str(self.fileName)).replace(" ", "\\ ")
            subprocess.run("pbcopy", universal_newlines=True, input=data)
        event.Skip()

    def OnBtnExif(self, event):
        filePath = os.path.join(globs.osvmDownloadDir,self.fileName)
        dlg = ExifDialog.ExifDialog(self, filePath, self.exifData[self.fileName])
        dlg.ShowModal()
        dlg.Destroy()
        event.Skip()
        
    def OnBtnClose(self, event):
        self.Close()

    def OnThumbKeyDown(self, event):
        keycode = event.GetKeyCode()
        myprint('keycode=%d' % keycode)
        event.Skip()
        
########################
def humanBytes(size):
    power = float(2**10)     # 2**10 = 1024
    n = 0
    power_labels = {0 : 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size = float(size / power)
        n += 1
    return '%s %s' % (('%.2f' % size).rstrip('0').rstrip('.'), power_labels[n])

def myprint(*args, **kwargs):
    """My custom print() function."""
    # Adding new arguments to the print function signature 
    # is probably a bad idea.
    # Instead consider testing if custom argument keywords
    # are present in kwargs
    __builtin__.print('%s():' % inspect.stack()[1][3], *args, **kwargs)

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)

        fileName = '20200214_170528.jpg'
        filePath = os.path.join(globs.osvmDownloadDir, fileName)
        i = os.stat(filePath)
        fileSize = i.st_size
        fileDate = i.st_mtime # in seconds
        globs.localFileInfos[fileName] = [fileName,fileSize,fileDate,filePath]
        globs.localFilesSorted = sorted(list(globs.localFileInfos.items()), key=lambda x: int(x[1][globs.F_DATEINSECS]), reverse=globs.fileSortRecentFirst)
        
        dlg = PropertiesDialog(self, fileName)
        ret = dlg.ShowModal()
        dlg.Destroy()

        self.Destroy()
        
def main():
    # Init Globals instance
    globs.system = platform.system()		# Linux or Windows or MacOS (Darwin)
    globs.viewMode = True
    globs.osvmDownloadDir = '/Users/didier/SynologyDrive/Photo/TEST'
    
    # Create DemoFrame frame, passing globals instance as parameter
    app = wx.App(False)
    frame = MyFrame(None, -1, title="Test")
    frame.Show(True)
    app.MainLoop()
    print('End of main loop')
   
if __name__ == "__main__":
    main()
