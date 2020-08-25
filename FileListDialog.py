#!/usr/bin/env python
import wx
import wx.html

import sys
import os
import builtins as __builtin__
import inspect
import time

moduleList = {'osvmGlobals':'globs'}

for k,v in moduleList.items():
    print('Loading: %s as %s' % (k,v))
    mod = __import__(k, fromlist=[None])
    globals()[v] = globals().pop('mod')	# Rename module in globals()

####
#print(__name__)

# Build a HTML table to display a sorted list of files passed as first parameter
def buildHTMLTable(fList, sortField, sortDir):
    myprint('Sorting criteria: Field: %d. Direction: %s' % (sortField, sortDir))
    # Sort data by sortField
    fileList = sorted(fList, key=lambda x: int(x[1][sortField]), reverse=sortDir)
    #print(fileList)
    
    items = list()
    items.append('<html>')
    items.append('<body>')

    items.append('<table cellspacing="10" cellpadding="5" style="text-align:right">')
    
    headerList = ['#', 'FILENAME', 'SIZE', 'DATE', 'TIME', 'TOTAL SIZE']

    items.append('<tr style="background-color: #fedcba">')
    for h in headerList:
        items.append('<th style="color: white">%s</th>' % h)
    items.append('</tr>')
    
    rows = 0
    totalSize = 0
    for v in fileList:
        t1 = secondsTohms(v[1][globs.F_DATEINSECS])
        d1 = secondsTodby(v[1][globs.F_DATEINSECS])
        
        if (rows % 2):
            items.append('<tr style="background-color: #c2a8e8">')
        else:
            items.append('<tr style="background-color: #c2d4e4">')
        rows += 1
        totalSize += v[1][globs.F_SIZE]
        for f in rows,v[1][globs.F_NAME],humanBytes(v[1][globs.F_SIZE]),d1,t1:
            items.append('<td>%s</td>' % f)
        items.append('<td style="background-color: #abcdef">%s</td>' % humanBytes(totalSize))
        items.append('</tr>')

    items.append('</table>')
    items.append('</body>')
    items.append('</html>')
    
    return(''.join(items))

class HtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id, size=(400,400)):
        wx.html.HtmlWindow.__init__(self, parent, id, size=size)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()

    # def OnLinkClicked(self, link):
    #     wx.LaunchDefaultBrowser(link.GetHref())

class FileListDialog(wx.Dialog):
    def __init__(self, parent):
        myStyle = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
        wx.Dialog.__init__(self, None, wx.ID_ANY, "List of Files", style=myStyle)

        # DONT CHANGE ORDER !!!
        self.FILE_TYPES = ['All Remote Files', 'All Local Files', 'Remote Files Not Synced']
                
        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self,
                               size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        # Create a HTML window
        self.hwin = HtmlWindow(parent=self.panel1, id=wx.ID_ANY, size=(800,600))

        # Build HTML Table with data from availRemoteFiles. Sorted by Date
        htmlTable = buildHTMLTable(list(globs.availRemoteFiles.items()), globs.F_DATEINSECS, False)
        print(htmlTable)

        # Display the HTML page
        self.hwin.SetPage(htmlTable)

        # Box Sizer to contain all buttons
        self.btnBS = wx.BoxSizer(orient=wx.HORIZONTAL)

        # File Selector to select the list of files to show: All files/Missing remote files
        self.fileTypesChoice = wx.Choice(choices=[v for v in self.FILE_TYPES],
                                         parent=self.panel1, style=0)
        self.fileTypesChoice.SetToolTip('Select type of files to show')
        self.fileTypesChoice.SetStringSelection(self.FILE_TYPES[0])
        self.fileTypesChoice.Bind(wx.EVT_CHOICE, lambda evt: self.OnParamsSelector(evt))

        self.btnBS.Add(self.fileTypesChoice, 0, border=0, flag=wx.EXPAND)
        self.btnBS.Add(8, 0, 0, border=0, flag=wx.EXPAND)
        
        # Button to close the Help dialog
        self.btnClose = wx.Button(label='Close', id=wx.ID_CLOSE, parent=self.panel1, style=0)
        self.btnClose.Bind(wx.EVT_BUTTON, self.OnBtnClose)

        # RadioButton for sorting criteria
        sortTypes = [('Sort by Date', globs.F_DATEINSECS), ('Sort by Size', globs.F_SIZE)]
        self.sortRadioButtons = {}
        i = 0
        for st in sortTypes:
            btn = wx.RadioButton(parent=self.panel1, 
                                 label=st[0],
                                 style=(wx.RB_GROUP if i==0 else 0))
            btn.Bind(wx.EVT_RADIOBUTTON, self.OnParamsSelector)
            if i == 0:
                btn.SetValue(True)
            self.sortRadioButtons[st] = btn
            self.btnBS.Add(btn, 0, border=0, flag=wx.EXPAND)
            self.btnBS.Add(8, 0, 0, border=0, flag=wx.EXPAND)
            i += 1

        # RadioButton for sorting order (Asc/Desc)
        sortOrder = [('Ascending', False), ('Descending', True)]
        self.sortDirRadioButtons = {}
        i = 0
        for st in sortOrder:
            btn = wx.RadioButton(parent=self.panel1, 
                                 label=st[0],
                                 style=(wx.RB_GROUP if i==0 else 0))
            btn.Bind(wx.EVT_RADIOBUTTON, self.OnParamsSelector)
            if i == 0:
                btn.SetValue(True)
            self.sortDirRadioButtons[st] = btn
            self.btnBS.Add(btn, 0, border=0, flag=wx.EXPAND)
            self.btnBS.Add(8, 0, 0, border=0, flag=wx.EXPAND)
            i += 1
            
        self.btnBS.AddStretchSpacer(prop=1)
        self.btnBS.Add(self.btnClose, 0, border=0, flag=wx.EXPAND|wx.ALIGN_RIGHT)

        # Everything in a BoxSizer
        self.topBS = wx.BoxSizer(orient=wx.VERTICAL)
        self.topBS.Add(self.btnBS, 0, border=5, flag=wx.EXPAND|wx.ALL)
        self.topBS.Add(4, 4, 0, border=0, flag=0)
        self.topBS.Add(self.hwin, 0, border=0, flag=0)
        
        self.panel1.SetSizerAndFit(self.topBS)
        self.SetClientSize(self.topBS.GetSize())
        self.Centre()
        self.SetFocus()

    def getSortingParams(self):
        for k1,v1 in self.sortRadioButtons.items():
            if v1.GetValue():
                break
        for k2,v2 in self.sortDirRadioButtons.items():
            if v2.GetValue():
                break
        myprint('Sorting Parameters: Field: %s Order: %s' % (k1[0],k2[0]))
        return(k1[1],k2[1])
        
    def OnBtnClose(self, event):
        self.Close()
        event.Skip()

    def OnParamsSelector(self, event):
        idx = self.fileTypesChoice.GetSelection()
        self.fileType = self.FILE_TYPES[idx]

        c1,c2 = self.getSortingParams()
        
        if self.fileType == 'All Remote Files':
            htmlTable = buildHTMLTable(list(globs.availRemoteFiles.items()), c1, c2)
        elif self.fileType == 'All Local Files':
            htmlTable = buildHTMLTable(list(globs.localFileInfos.items()), c1, c2)
        else:
            # Build a list of local files. Format:(filename, size)
            localFilesList = [(x[1][0],x[1][1]) for x in list(globs.localFileInfos.items())]
            #print(localFilesList)
            # Build a list of remote files. Format:(filename, size)
            remoteFilesList = [(x[1][0],x[1][1]) for x in globs.availRemoteFiles.items()]
            #print(remoteFilesList)
            # Get missing files list
            tmp = listDiff2(remoteFilesList, localFilesList)
            # Build a dictionary from list above
            dictDiff = dict()
            for e in tmp:
                dictDiff[e[0]] = globs.availRemoteFiles[e[0]]
            htmlTable = buildHTMLTable(list(dictDiff.items()), c1, c2)
        # Set HTML Page
        self.hwin.SetPage(htmlTable)
        event.Skip()

########################
def module_path(local_function):
    ''' returns the module path without the use of __file__.  
    Requires a function defined locally in the module.
    from http://stackoverflow.com/questions/729583/getting-file-path-of-imported-module'''
    return os.path.abspath(inspect.getsourcefile(local_function))

def myprint(*args, **kwargs):
    """My custom print() function."""
    # Adding new arguments to the print function signature 
    # is probably a bad idea.
    # Instead consider testing if custom argument keywords
    # are present in kwargs
    __builtin__.print('%s():' % inspect.stack()[1][3], *args, **kwargs)

def secondsTohms(t):
    d = time.strftime('%H:%M:%S', time.localtime(t))
    return d

def secondsTodmy(t):
    d = time.strftime('%d/%m/%y', time.localtime(t))
    return d

def secondsTodby(t):
    d = time.strftime('%d %b %y', time.localtime(t))
    return d

def humanBytes(size):
    power = float(2**10)     # 2**10 = 1024
    n = 0
    power_labels = {0 : 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size = float(size / power)
        n += 1
    return '%s %s' % (('%.2f' % size).rstrip('0').rstrip('.'), power_labels[n])

# Build a list containing elements NOT in common to parameters
def listDiff(li1, li2): 
    l = [i for i in li1 + li2 if i not in li1 or i not in li2] 
    return l

# Build a list containing elements of list1 NOT in list2
def listDiff2(li1, li2): 
    l = [i for i in li1 if i not in li2] 
    return l

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)
        
        dlg = FileListDialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.Destroy()

def main():
    globs.availRemoteFiles['P6122903.JPG'] = ['P6122903.JPG', 1540707, 1591972676, '', '/DCIM/100OLYMP', 0, 20684, 33980, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P6122903.JPG']
    globs.availRemoteFiles['P8232966.JPG'] = ['P8232966.JPG', 1538041, 1598171028, '', '/DCIM/100OLYMP', 0, 20759, 21240, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8232966.JPG']
    globs.availRemoteFiles['P7032921.JPG'] = ['P7032921.JPG', 1522484, 1593782206, '', '/DCIM/100OLYMP', 0, 20707, 31255, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7032921.JPG']
    globs.availRemoteFiles['P7062936.JPG'] = ['P7062936.JPG', 1599056, 1594058304, '', '/DCIM/100OLYMP', 0, 20710, 40780, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7062936.JPG']

    globs.localFileInfos['P8232966.JPG'] = ['P8232966.JPG',1538041,1598171028,'foo']
    globs.localFileInfos['P7032921.JPG'] = ['P7032921.JPG',1522484,1593782206,'bar']
    
    # Create frame, passing globals instance as parameter
    app = wx.App(False)
    frame = MyFrame(None, -1, title="Test")
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
        
