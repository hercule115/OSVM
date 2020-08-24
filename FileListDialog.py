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

def buildHTMLTable(sortField, sortDir):
    myprint('Sorting criteria: %d. Direction: %s' % (sortField, sortDir))
    # Sort data by sortField
    fileList = sorted(list(globs.availRemoteFiles.items()), key=lambda x: int(x[1][sortField]), reverse=sortDir)
    #print(fileList)
    
    items = list()
    items.append('<html>')
    items.append('<body>')

    items.append('<table cellspacing="10" cellpadding="5" style="text-align:right">')
    
    headerList = ['#', 'FILENAME', 'SIZE', 'DATE', 'TIME', 'TOTAL SIZE']

    items.append('<tr style="background-color: #7cc3a97d">')
    for h in headerList:
        items.append('<th style="color: white">%s</th>' % h)
    items.append('</tr>')
    
    rows = 0
    totalSize = 0
    for v in fileList:
        t1 = getHumanTime(v[1][globs.F_TIME])
        d1 = secondsTodby(v[1][globs.F_DATEINSECS])
        
        if (rows % 2):
            items.append('<tr style="background-color: #c2a8e8">')
        else:
            items.append('<tr style="background-color: #c2d4e4">')
        rows += 1
        totalSize += v[1][globs.F_SIZE]
        for f in rows,v[1][globs.F_NAME],humanBytes(v[1][globs.F_SIZE]),d1,t1,humanBytes(totalSize):
            items.append('<td>%s</td>' % f)
        items.append('</tr>')

    items.append('</table>')
    items.append('</body>')
    items.append('</html>')
    
    return(''.join(items))

class HtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id, size=(600,400)):
        wx.html.HtmlWindow.__init__(self, parent, id, size=size)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()

    def OnLinkClicked(self, link):
        wx.LaunchDefaultBrowser(link.GetHref())

class FileListDialog(wx.Dialog):
    def __init__(self, parent):
        myStyle = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
        wx.Dialog.__init__(self, None, wx.ID_ANY, "Available Files", style=myStyle)

        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self,
                               size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        # Create a HTML window
        self.hwin = HtmlWindow(parent=self.panel1, id=wx.ID_ANY, size=(800,600))

        # Build HTML Table with data from availRemoteFiles
        htmlTable = buildHTMLTable(globs.F_DATEINSECS, False)
        print(htmlTable)

        # Display the HTML page
        self.hwin.SetPage(htmlTable)

        # Box Sizer to contain all buttons
        self.btnBS = wx.BoxSizer(orient=wx.HORIZONTAL)
        
        # Button to close the Help dialog
        self.btnClose = wx.Button(label='Close', id=wx.ID_CLOSE, parent=self.panel1, style=0)
        self.btnClose.Bind(wx.EVT_BUTTON, self.OnBtnClose)

        # RadioButton for sorting criteria
        sortTypes = [('Sort by Date',globs.F_DATEINSECS), ('Sort by Size',globs.F_SIZE)]
        self.sortRadioButtons = {}
        i = 0
        for st in sortTypes:
            btn = wx.RadioButton(parent=self.panel1, 
                                 label=st[0],
                                 style=(wx.RB_GROUP if i==0 else 0))
            btn.Bind(wx.EVT_RADIOBUTTON, self.OnRadioButton)
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
            btn.Bind(wx.EVT_RADIOBUTTON, self.OnRadioButton)
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

    def OnBtnClose(self, event):
        self.Close()
        event.Skip()

    def OnRadioButton(self, event):
        for k1,v1 in self.sortRadioButtons.items():
            if v1.GetValue():
                break
        for k2,v2 in self.sortDirRadioButtons.items():
            if v2.GetValue():
                break

        myprint('Generating File List: %s Order: %s' % (k1[0],k2[0]))
        htmlTable = buildHTMLTable(k1[1],k2[1])
        # Display the HTML page
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

def getHumanDate(d):
    ''' return a string containing a date in human/readable format. '''

    #d = 19330 # 2/12/2017

    maskDay   = 0x1F	# "0000000000011111"
    maskMonth = 0x1E0	# "0000000111100000"
    maskYear  = 0xFE00	# "1111 1110 0000 0000"

    day   = (d & maskDay) >> 0
    month = (d & maskMonth) >> 5
    year  = ((d & maskYear) >> 9) + 1980
    humanDate = "%d/%d/%d" % (month,day,year)
    return humanDate

def getHumanTime(t):
    ''' return a string containing a time in human/readable format. '''

    maskSeconds = 0x001F # 0000000000011111
    maskMinutes = 0x07E0 # 0000011111100000
    maskHours   = 0xF800 # 1111100000000000

    hours   = ((t & maskHours) >> 11) # + 1 # XXX ???
    minutes = (t & maskMinutes) >> 5
    seconds = (t & maskSeconds) * 2

    humanTime = "%d:%d:%d" % (hours,minutes,seconds)
    return humanTime

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

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)

        dlg = FileListDialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.Destroy()

def main():
    globs.availRemoteFiles['P6122903.JPG'] = ['P6122903.JPG', 1540707, 20684, '', '/DCIM/100OLYMP', 0, 1591972676, 33980, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P6122903.JPG']
    globs.availRemoteFiles['P8232966.JPG'] = ['P8232966.JPG', 1538041, 20759, '', '/DCIM/100OLYMP', 0, 1598171028, 21240, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8232966.JPG']
    globs.availRemoteFiles['P7032921.JPG'] = ['P7032921.JPG', 1522484, 20707, '', '/DCIM/100OLYMP', 0, 1593782206, 31255, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7032921.JPG']
    globs.availRemoteFiles['P7062936.JPG'] = ['P7062936.JPG', 1599056, 20710, '', '/DCIM/100OLYMP', 0, 1594058304, 40780, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7062936.JPG']
#    globs.availRemoteFiles = arf
    
    # Create frame, passing globals instance as parameter
    app = wx.App(False)
    frame = MyFrame(None, -1, title="Test")
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
        
