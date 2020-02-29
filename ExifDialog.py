#!/usr/bin/env python
import wx

import sys
import os
import builtins as __builtin__
import inspect
import ast

moduleList = {'osvmGlobals':'globs'}

for k,v in moduleList.items():
    print('Loading: %s as %s' % (k,v))
    mod = __import__(k, fromlist=[None])
    globals()[v] = globals().pop('mod')	# Rename module in globals()

####
#print(__name__)

class ExifDialog(wx.Dialog):
    """
    Creates and displays a dialog box to display the Exif data from a picture
    """
    def __init__(self, parent, filePath, exifDataAsStr):
        """
        Initialize the dialog box
        """
        self.parent = parent
        self.fileName = os.path.basename(filePath)
        self.exifData = ast.literal_eval(exifDataAsStr)
          
        myStyle = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
        wx.Dialog.__init__(self, None, wx.ID_ANY, '%s - Exif Data' % self.fileName, style=myStyle)

        self._initialize()

        self.panel1.SetSizerAndFit(self.topBS)
        self.SetClientSize(self.topBS.GetSize())
        self.Centre()

    # top box sizer
    def _init_topBS_Items(self, parent):
        parent.Add(self.exifBS, 0, border=5, flag=wx.ALL) #wx.EXPAND | 
        parent.Add(4, 4, border=0, flag=0)
        if self.gpsCoordinates:
            parent.Add(self.gpsCoordsBS, 0, border=5, flag=wx.ALL)
        parent.Add(4, 4, border=0, flag=0)
        parent.Add(self.bottomBS, 0, border=5, flag= wx.ALL | wx.ALIGN_RIGHT)

    # Exif Tags/Value in Grid Sizer
    def _init_exifBS_Items(self, parent):
        parent.Add(self.exifGS, 0, border=5, flag= wx.EXPAND)

    def _init_exifGS_Items(self, parent):
        del self.exifData[None]
        for elem in sorted(list(self.exifData.items())): # elem is a tuple (k,v)
            k = elem[0]
            v = elem[1]
            if type(v).__name__ == 'dict':    # Some values (GPSinfo) could be a sub-dict
                for elem in sorted(list(v.items())): # elem is a tuple (k,v)
                    k = elem[0]
                    v = elem[1]
                    bs1 = wx.BoxSizer(orient=wx.HORIZONTAL)
                    kST = wx.StaticText(label=str(k), parent=self.panel1)
                    vST = wx.StaticText(label=str(v).strip(), parent=self.panel1)
                    bs1.Add(kST, 0, border=5, flag=wx.EXPAND|wx.ALL)
                    bs1.AddStretchSpacer(prop=1)
                    bs1.Add(vST, 0, border=5, flag=wx.EXPAND|wx.ALL| wx.ALIGN_RIGHT)
                    parent.Add(bs1, border=0, flag=wx.ALL | wx.EXPAND)
            else:
                bs1 = wx.BoxSizer(orient=wx.HORIZONTAL)
                kST = wx.StaticText(label=str(k), parent=self.panel1)
                vST = wx.StaticText(label=str(v).strip(), parent=self.panel1)
                bs1.Add(kST, 0, border=5, flag=wx.EXPAND|wx.ALL)
                bs1.AddStretchSpacer(prop=1)
                bs1.Add(vST, 0, border=5, flag=wx.EXPAND|wx.ALL| wx.ALIGN_RIGHT)
                parent.Add(bs1, border=0, flag=wx.ALL | wx.EXPAND)

    # Bottom items
    def _init_bottomBS_Items(self, parent):
        parent.Add(4, 4, border=0, flag=wx.EXPAND)
        parent.Add(self.btnClose, 0, border=5, flag=wx.ALL)

    def _init_sizers(self):
        self.topBS = wx.BoxSizer(orient=wx.VERTICAL)
        # Exif Data staticBoxSizer
        self.exifBS = wx.StaticBoxSizer(box=self.staticBox2, orient=wx.VERTICAL)

        dictLen = 0
        for (k,v) in self.exifData.items():
            if type(v).__name__ == 'dict':
                dictLen += len(v)
            else:
                dictLen += 1
        gsNumCols = 4
        gsNumRows = (dictLen / gsNumCols) + 1
        self.exifGS = wx.GridSizer(cols=gsNumCols, hgap=0, rows=gsNumRows, vgap=2)

        # GPS Coordinates if available
        self.gpsCoordinates = getDecimalCoordinates(self.exifData['GPSInfo'])
        if self.gpsCoordinates:
            self.gpsCoordsBS = wx.BoxSizer(orient=wx.HORIZONTAL)
            self.gpsLabelST  = wx.StaticText(label='GPS Coordinates:', parent=self.panel1)
            self.gpsCoordsST = wx.StaticText(label=str(self.gpsCoordinates), parent=self.panel1)
            self.gpsCoordsBS.Add(self.gpsLabelST, 0, border=5, flag=wx.EXPAND|wx.ALL)
            self.gpsCoordsBS.Add(4,0)
            self.gpsCoordsBS.Add(self.gpsCoordsST, 0, border=5, flag=wx.EXPAND|wx.ALL)
            #print('GPS info =',self.gpsCoordinates)

        # Bottom button boxSizer
        self.bottomBS = wx.BoxSizer(orient=wx.HORIZONTAL)

        # Initialize each sizer
        self._init_topBS_Items(self.topBS)
        self._init_exifBS_Items(self.exifBS)
        self._init_exifGS_Items(self.exifGS)
        self._init_bottomBS_Items(self.bottomBS)

    """
    Create and layout the widgets in the dialog
    """
    def _initialize(self):
        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self,
                               size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        #### Misc 
        self.staticBox2 = wx.StaticBox(id=wx.ID_ANY, label=' Exif Data ', 
                                       parent=self.panel1, style=0)

        self.btnClose = wx.Button(id=wx.ID_CLOSE, parent=self.panel1, style=0)
        self.btnClose.SetToolTip('Close this Dialog')
        self.btnClose.SetDefault()
        self.btnClose.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnClose(evt))

        self._init_sizers()

    #### Events ####
    def OnBtnClose(self, event):
        self.EndModal(wx.ID_CLOSE)
        event.Skip()

########################
def myprint(*args, **kwargs):
    """My custom print() function."""
    # Adding new arguments to the print function signature 
    # is probably a bad idea.
    # Instead consider testing if custom argument keywords
    # are present in kwargs
    __builtin__.print('%s():' % inspect.stack()[1][3], *args, **kwargs)

# Browse a directory, looking for filenames ending with: JPG, MOV, ORF, MPO, MP4
def listLocalFiles(dir, hidden=False, relative=True, suffixes=('jpg', 'mov', 'orf', 'mpo', 'mp4')):
    myprint('Looking for files with suffix:', suffixes)
    nodes = []
    try:
        for fname in os.listdir(dir):
            if not hidden and fname.startswith('.'):
                continue
            if not fname.lower().endswith(suffixes):
                continue
            if not relative:
                fname = os.path.join(dir, fname)
            nodes.append(fname)
        nodes.sort()
    except:
        myprint("Error: Can't browse:", dir)
    return nodes

def getExifData(filename):
    try:
        exif_data = {}
        for (k,v) in Image.open(filename)._getexif().items():
            decoded = TAGS.get(k)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in v:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = v[t]
                exif_data[decoded] = gps_data
            else:
                if decoded in TAGS_TO_SKIP:
                    continue
                exif_data[decoded] = v
    except IOError:
        myprint('got IOError')
        return None
    except:
        myprint('No Exif tags')
        return None
    else:
        return exif_data

# Build a dict from data read from file    
def buildDictFromFile(filename):
    tags = {}
    with open(filename) as fh:
        for line in fh:
            tag,value = line.strip().split(':', 1)
            tags[tag] = value.strip()
    return tags

def getDecimalCoordinates(gpsInfo):
    gpsCoords = dict()
    for key in ['Latitude', 'Longitude']:
        if 'GPS'+key in gpsInfo and 'GPS'+key+'Ref' in gpsInfo:
            e = gpsInfo['GPS'+key]
            ref = gpsInfo['GPS'+key+'Ref']
            gpsCoords[key] = (e[0][0]/e[0][1] +
                              e[1][0]/e[1][1] / 60 +
                              e[2][0]/e[2][1] / 3600 ) * (-1 if ref in ['S','W'] else 1)

    if 'Latitude' in gpsCoords and 'Longitude' in gpsCoords:
        return [gpsCoords['Latitude'], gpsCoords['Longitude']]
    else:
        return None

def saveExifDataFromImages(exifFilePath):
    exifDataDict = dict()
  
    fileList = listLocalFiles(globs.osvmDownloadDir, hidden=False, relative=False, suffixes=('jpg'))
    for f in fileList:
        exifData = getExifData(f)
        if not exifData:
            myprint('Unable to get Exif data from file %s' % f)
            continue
        # Update global dictionary containing exif data for all files
        exifDataDict[os.path.basename(f)] = str(exifData)

    # Create a file containing all exif data for all files
    with open(exifFilePath, 'w') as fh:
        for (k,v) in exifDataDict.items():
            fh.write('%s:%s\r\n' % (k,v))
    
class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)
        panel = wx.Panel(self)
        
        exifFilePath = os.path.join(globs.osvmDownloadDir,globs.exifFile)
        if not os.path.exists(exifFilePath):
            myprint('%s does not exist. Creating' % exifFilePath)
            saveExifDataFromImages(exifFilePath)
        # Load data from file
        exifData = buildDictFromFile(exifFilePath)

        fileName = 'P2272477.JPG'        
        filePath = os.path.join(globs.osvmDownloadDir,fileName)
        dlg = ExifDialog(self, filePath, exifData[fileName])
        ret = dlg.ShowModal()
        dlg.Destroy()

        self.Show()

def main():
    # Init Globals instance
    globs.osvmDownloadDir = '/Users/didier/SynologyDrive/Photo/TEST'

    # Create DemoFrame frame, passing globals instance as parameter
    app = wx.App(False)
    frame = MyFrame(None, -1, title="Test")
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
