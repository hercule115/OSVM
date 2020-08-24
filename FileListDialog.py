#!/usr/bin/env python
import wx
import wx.html

import sys
import os
import builtins as __builtin__
import inspect
import time

arf = {'P6122903.JPG': ['P6122903.JPG', 1540707, 20684, '', '/DCIM/100OLYMP', 0, 1591972676, 33980, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P6122903.JPG'], 'P6222917.JPG': ['P6222917.JPG', 1526373, 20694, '', '/DCIM/100OLYMP', 0, 1592857130, 45657, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P6222917.JPG'], 'P6122905.JPG': ['P6122905.JPG', 1569905, 20684, '', '/DCIM/100OLYMP', 0, 1591972710, 33999, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P6122905.JPG'], 'P6122906.JPG': ['P6122906.JPG', 1581845, 20684, '', '/DCIM/100OLYMP', 0, 1591972718, 34003, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P6122906.JPG'], 'P6192907.JPG': ['P6192907.JPG', 1595332, 20691, '', '/DCIM/100OLYMP', 0, 1592595358, 44157, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P6192907.JPG'], 'P6192908.MOV': ['P6192908.MOV', 160772737, 20691, '', '/DCIM/100OLYMP', 0, 1592595422, 44193, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P6192908.MOV'], 'P6192909.MOV': ['P6192909.MOV', 69761438, 20691, '', '/DCIM/100OLYMP', 0, 1592595458, 44211, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P6192909.MOV'], 'P6192910.MOV': ['P6192910.MOV', 36626840, 20691, '', '/DCIM/100OLYMP', 0, 1592595498, 44233, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P6192910.MOV'], 'P6222918.JPG': ['P6222918.JPG', 1564139, 20694, '', '/DCIM/100OLYMP', 0, 1592857142, 45665, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P6222918.JPG'], 'P6222919.JPG': ['P6222919.JPG', 1586228, 20694, '', '/DCIM/100OLYMP', 0, 1592857174, 45681, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P6222919.JPG'], 'P6222920.JPG': ['P6222920.JPG', 1617634, 20694, '', '/DCIM/100OLYMP', 0, 1592857206, 45699, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P6222920.JPG'], 'P7032921.JPG': ['P7032921.JPG', 1522484, 20707, '', '/DCIM/100OLYMP', 0, 1593782206, 31255, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7032921.JPG'], 'P7032922.JPG': ['P7032922.JPG', 1573158, 20707, '', '/DCIM/100OLYMP', 0, 1593782216, 31260, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7032922.JPG'], 'P7032923.JPG': ['P7032923.JPG', 1584483, 20707, '', '/DCIM/100OLYMP', 0, 1593782256, 31282, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7032923.JPG'], 'P7032924.JPG': ['P7032924.JPG', 1545806, 20707, '', '/DCIM/100OLYMP', 0, 1593782328, 31320, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7032924.JPG'], 'P7032925.JPG': ['P7032925.JPG', 1575738, 20707, '', '/DCIM/100OLYMP', 0, 1593782362, 31339, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7032925.JPG'], 'P7032926.JPG': ['P7032926.JPG', 1584559, 20707, '', '/DCIM/100OLYMP', 0, 1593782550, 31439, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7032926.JPG'], 'P7032927.JPG': ['P7032927.JPG', 1555093, 20707, '', '/DCIM/100OLYMP', 0, 1593782704, 31522, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7032927.JPG'], 'P7032928.JPG': ['P7032928.JPG', 1559790, 20707, '', '/DCIM/100OLYMP', 0, 1593782786, 31565, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7032928.JPG'], 'P7032929.JPG': ['P7032929.JPG', 1444393, 20707, '', '/DCIM/100OLYMP', 0, 1593782792, 31568, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7032929.JPG'], 'P7032930.JPG': ['P7032930.JPG', 1579009, 20707, '', '/DCIM/100OLYMP', 0, 1593782812, 31578, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7032930.JPG'], 'P7032931.JPG': ['P7032931.JPG', 1562267, 20707, '', '/DCIM/100OLYMP', 0, 1593782886, 31619, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7032931.JPG'], 'P7032932.JPG': ['P7032932.JPG', 1534940, 20707, '', '/DCIM/100OLYMP', 0, 1593782916, 31634, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7032932.JPG'], 'P7032933.JPG': ['P7032933.JPG', 1565996, 20707, '', '/DCIM/100OLYMP', 0, 1593783020, 31690, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7032933.JPG'], 'P7032934.JPG': ['P7032934.JPG', 1621677, 20707, '', '/DCIM/100OLYMP', 0, 1593783262, 31819, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7032934.JPG'], 'P7062935.JPG': ['P7062935.JPG', 1543674, 20710, '', '/DCIM/100OLYMP', 0, 1594058294, 40775, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7062935.JPG'], 'P7062936.JPG': ['P7062936.JPG', 1599056, 20710, '', '/DCIM/100OLYMP', 0, 1594058304, 40780, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7062936.JPG'], 'P7062937.JPG': ['P7062937.JPG', 1396515, 20710, '', '/DCIM/100OLYMP', 0, 1594058346, 40803, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7062937.JPG'], 'P7062938.JPG': ['P7062938.JPG', 1411348, 20710, '', '/DCIM/100OLYMP', 0, 1594058350, 40805, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7062938.JPG'], 'P8222963.JPG': ['P8222963.JPG', 1556700, 20758, '', '/DCIM/100OLYMP', 0, 1598117332, 39834, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8222963.JPG'], 'P7062940.JPG': ['P7062940.JPG', 1605537, 20710, '', '/DCIM/100OLYMP', 0, 1594067946, 46307, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7062940.JPG'], 'P8062942.JPG': ['P8062942.JPG', 1510120, 20742, '', '/DCIM/100OLYMP', 0, 1596706614, 23707, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8062942.JPG'], 'P8062943.JPG': ['P8062943.JPG', 1568628, 20742, '', '/DCIM/100OLYMP', 0, 1596706624, 23714, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8062943.JPG'], 'P8062944.JPG': ['P8062944.JPG', 1529403, 20742, '', '/DCIM/100OLYMP', 0, 1596706646, 23725, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8062944.JPG'], 'P8062945.JPG': ['P8062945.JPG', 1542927, 20742, '', '/DCIM/100OLYMP', 0, 1596706654, 23729, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8062945.JPG'], 'P8132946.JPG': ['P8132946.JPG', 1601629, 20749, '', '/DCIM/100OLYMP', 0, 1597344002, 42241, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8132946.JPG'], 'P8132947.JPG': ['P8132947.JPG', 1568646, 20749, '', '/DCIM/100OLYMP', 0, 1597344010, 42245, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8132947.JPG'], 'P8132948.JPG': ['P8132948.JPG', 1613852, 20749, '', '/DCIM/100OLYMP', 0, 1597344050, 42265, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8132948.JPG'], 'P8132949.JPG': ['P8132949.JPG', 1603910, 20749, '', '/DCIM/100OLYMP', 0, 1597344472, 42490, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8132949.JPG'], 'P8132950.JPG': ['P8132950.JPG', 1611900, 20749, '', '/DCIM/100OLYMP', 0, 1597344486, 42499, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8132950.JPG'], 'P8132951.JPG': ['P8132951.JPG', 1528022, 20749, '', '/DCIM/100OLYMP', 0, 1597344494, 42503, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8132951.JPG'], 'P8132952.JPG': ['P8132952.JPG', 1524311, 20749, '', '/DCIM/100OLYMP', 0, 1597344500, 42506, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8132952.JPG'], 'P8172953.JPG': ['P8172953.JPG', 1549834, 20753, '', '/DCIM/100OLYMP', 0, 1597681354, 37585, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8172953.JPG'], 'P8172954.JPG': ['P8172954.JPG', 1622843, 20753, '', '/DCIM/100OLYMP', 0, 1597681366, 37591, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8172954.JPG'], 'P8172955.JPG': ['P8172955.JPG', 1610373, 20753, '', '/DCIM/100OLYMP', 0, 1597681376, 37596, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8172955.JPG'], 'P8172956.JPG': ['P8172956.JPG', 1473405, 20753, '', '/DCIM/100OLYMP', 0, 1597681384, 37602, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8172956.JPG'], 'P8172957.JPG': ['P8172957.JPG', 1615422, 20753, '', '/DCIM/100OLYMP', 0, 1597681398, 37609, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8172957.JPG'], 'P8172958.JPG': ['P8172958.JPG', 1531210, 20753, '', '/DCIM/100OLYMP', 0, 1597681406, 37613, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8172958.JPG'], 'P8202959.JPG': ['P8202959.JPG', 1551187, 20756, '', '/DCIM/100OLYMP', 0, 1597946146, 40695, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8202959.JPG'], 'P8202960.JPG': ['P8202960.JPG', 1579996, 20756, '', '/DCIM/100OLYMP', 0, 1597946160, 40704, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8202960.JPG'], 'P8202961.JPG': ['P8202961.JPG', 1559961, 20756, '', '/DCIM/100OLYMP', 0, 1597946168, 40708, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8202961.JPG'], 'P8222964.JPG': ['P8222964.JPG', 1539852, 20758, '', '/DCIM/100OLYMP', 0, 1598117350, 39845, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8222964.JPG'], 'P8222965.JPG': ['P8222965.JPG', 1494416, 20758, '', '/DCIM/100OLYMP', 0, 1598117362, 39851, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8222965.JPG'], 'P8232966.JPG': ['P8232966.JPG', 1538041, 20759, '', '/DCIM/100OLYMP', 0, 1598171028, 21240, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8232966.JPG']}

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

    # items.append('<style type="text/css">')
    # items.append('  body {')
    # items.append('    color: purple;')
    # items.append('    background-color: #d8da3d }')
    # items.append('  </style>')
    
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
        
