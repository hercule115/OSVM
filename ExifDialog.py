#!/usr/bin/env python
import wx

import sys
import os
import builtins as __builtin__
import inspect
import ast

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

import math
from urllib.request import Request, urlopen
from urllib.error import URLError
from io import BytesIO
from PIL import Image

# Skip them
TAGS_TO_SKIP = ['Artist', 'Copyright', 'MakerNote', 'PrintImageMatching', 'UserComment']

moduleList = {
    'osvmGlobals':'globs',
    'MediaViewerDialog':'MediaViewerDialog'
}

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
            parent.Add(self.gpsBS, 0, border=5, flag=wx.ALL)
        parent.Add(4, 4, border=0, flag=0)
        parent.Add(self.bottomBS, 0, border=5, flag= wx.ALL | wx.ALIGN_RIGHT)

    # Exif Tags/Value in Grid Sizer
    def _init_exifBS_Items(self, parent):
        parent.Add(self.exifGS, 0, border=5, flag= wx.EXPAND)

    def _init_exifGS_Items(self, parent):
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
                    bs1.Add(vST, 0, border=5, flag=wx.EXPAND|wx.ALL)#211 | wx.ALIGN_RIGHT)
                    parent.Add(bs1, border=0, flag=wx.ALL | wx.EXPAND)
            else:
                bs1 = wx.BoxSizer(orient=wx.HORIZONTAL)
                kST = wx.StaticText(label=str(k), parent=self.panel1)
                vST = wx.StaticText(label=str(v).strip(), parent=self.panel1)
                bs1.Add(kST, 0, border=5, flag=wx.EXPAND|wx.ALL)
                bs1.AddStretchSpacer(prop=1)
                bs1.Add(vST, 0, border=5, flag=wx.EXPAND|wx.ALL)#211 | wx.ALIGN_RIGHT)
                parent.Add(bs1, border=0, flag=wx.ALL | wx.EXPAND)

    # GPS Coordinates and map
    def _init_gpsBS_Items(self, parent):
        parent.Add(self.gpsLabelST, 0, border=5, flag=wx.EXPAND|wx.ALL)
        parent.Add(4,0)
        parent.Add(self.gpsCoordsST, 0, border=5, flag=wx.EXPAND|wx.ALL)
        parent.Add(4, 0)
        parent.Add(self.btnShowMap, 0, border=5, flag=wx.ALL)        

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

        # Bottom button boxSizer
        self.bottomBS = wx.BoxSizer(orient=wx.HORIZONTAL)

        # Initialize each sizer
        self._init_topBS_Items(self.topBS)
        self._init_exifBS_Items(self.exifBS)
        self._init_exifGS_Items(self.exifGS)
        if self.gpsCoordinates:
            self._init_gpsBS_Items(self.gpsBS)
        self._init_bottomBS_Items(self.bottomBS)

    """
    Create and layout the widgets in the dialog
    """
    def _initialize(self):
        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self,
                               size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        #### Misc 
        self.staticBox2 = wx.StaticBox(label=' Exif Data ', parent=self.panel1, style=0)

        # GPS Coordinates if available
        try:
            self.gpsCoordinates = getDecimalCoordinates(self.exifData['GPSInfo'])
        except:
            myprint('No GPSInfo in Exif Data for %s' % self.fileName)
            self.gpsCoordinates = None
        else:
            #print('GPS info =',self.gpsCoordinates)
            if self.gpsCoordinates:
                self.gpsBS = wx.BoxSizer(orient=wx.HORIZONTAL)
                self.gpsLabelST  = wx.StaticText(label='GPS Coordinates:', parent=self.panel1)
                self.gpsCoordsST = wx.StaticText(label=str(self.gpsCoordinates), parent=self.panel1)

                self.btnShowMap = wx.Button(label='Show Map', parent=self.panel1, style=0)
                self.btnShowMap.SetToolTip('Show GPS Coordinates on a map')
                self.btnShowMap.Bind(wx.EVT_BUTTON, self.OnBtnShowMap)

        self.btnClose = wx.Button(id=wx.ID_CLOSE, parent=self.panel1, style=0)
        self.btnClose.SetToolTip('Close this Dialog')
        self.btnClose.SetDefault()
        self.btnClose.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnClose(evt))

        self._init_sizers()

    #### Events ####
    def OnBtnShowMap(self, event):
        latitude = self.gpsCoordinates[0]
        longitude = self.gpsCoordinates[1]
        img = getMapImage(latitude, longitude, 0.04,  0.05, 13)
        if not img:
            myprint('Unable to download map for %s' % str(self.gpsCoordinates))
            event.Skip()
            return
        mapPath = os.path.join(globs.tmpDir, 'im1.png')
        img.save(mapPath)

        globs.localFileInfos['im1.png'] = ['im1.png', 0, 0, '']    
        globs.localFilesSorted = sorted(list(globs.localFileInfos.items()), key=lambda x: int(x[1][globs.F_DATEINSECS]), reverse=globs.fileSortRecentFirst)
        
        dlg = MediaViewerDialog.MediaViewerDialog(self, mapPath)
        dlg.ShowModal()
        dlg.Destroy()
        event.Skip()

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
                if decoded == None or decoded in TAGS_TO_SKIP:
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

# Build a dict from data read from cache file
def buildDictFromFile(filename):
    tags = {}
    try:
        fh = open(filename, "r")
        try:
            for line in fh:
                tag,value = line.strip().split(':', 1)
                tags[tag] = value.strip()
            myprint('Exif Dict Length:%d' % len(tags))
        finally:
            fh.close()
            return tags
    except IOError as e:
        msg = "I/O error: %s %s" % ("({0}): {1}".format(e.errno, e.strerror),filename)
        myprint(msg)
        return tags

    # with open(filename) as fh:
    #     for line in fh:
    #         tag,value = line.strip().split(':', 1)
    #         tags[tag] = value.strip()
    # #myprint('Exif Dict Length:%d' % len(tags))
    # return tags

def saveFileFromDict(exifDataDict, exifFilePath):
    # Update exif data cache file
    myprint('Updating Exif Data File from dict')
    with open(exifFilePath, 'w') as fh:
        for (k,v) in exifDataDict.items():
            fh.write('%s:%s\r\n' % (k,v))

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
    saveFileFromDict(exifDataDict, exifFilePath)
    # with open(exifFilePath, 'w') as fh:
    #     for (k,v) in exifDataDict.items():
    #         fh.write('%s:%s\r\n' % (k,v))

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


def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def num2deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)

def getMapImage(lat_deg, lon_deg, delta_lat,  delta_long, zoom):
    HEADERS = {
        'User-Agent': 'OSVM User Agent 4.4.0',
        'From': 'd.poirot@libertysurf.fr'
    }
    smurl = r"http://a.tile.openstreetmap.org/{0}/{1}/{2}.png"
    xmin, ymax =deg2num(lat_deg, lon_deg, zoom)
    xmax, ymin =deg2num(lat_deg + delta_lat, lon_deg + delta_long, zoom)

    cluster = Image.new('RGB',((xmax-xmin+1)*256-1,(ymax-ymin+1)*256-1))
    for xtile in range(xmin, xmax+1):
        for ytile in range(ymin,  ymax+1):
            try:
                imgurl=smurl.format(zoom, xtile, ytile)
                myprint("Opening: " + imgurl)
                imgstr = urlopen(Request(imgurl, headers=HEADERS)).read()
                tile = Image.open(BytesIO(imgstr))
                cluster.paste(tile, box=((xtile-xmin)*256 ,  (ytile-ymin)*256))
            except URLError as e:
                myprint(e)
                myprint("Couldn't download image tile")
                msg = "Cannot download image tiles: %s. Check Internet connection." % ("{0}".format(e.strerror))
                dlg = wx.MessageDialog(None, msg, 'ERROR', wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                return None
    return cluster
    
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

        # Get exif data from info attributes
        size = (160,120)
        im = Image.open(os.path.join(globs.osvmDownloadDir,fileName))
        im.thumbnail(size, Image.ANTIALIAS)
        exif = im.info['exif']
        print(exif)
        im.save('%s-thumb.jpg' % (fileName), exif=exif)

        filePath = os.path.join(globs.osvmDownloadDir,fileName)
        dlg = ExifDialog(self, filePath, exifData[fileName])
        ret = dlg.ShowModal()
        dlg.Destroy()

        self.Show()

def main():
    # Init Globals instance
    globs.osvmDownloadDir = '/Users/didier/SynologyDrive/Photo/TEST'
    osvmdirpath = os.path.join(os.path.join(os.path.expanduser("~"), globs.osvmDir))
    if os.path.exists(osvmdirpath):
        if not os.path.isdir(osvmdirpath):
            myprint("%s must be a directory. Exit!" % (osvmdirpath))
            exit()
    else:
        try:
            os.mkdir(osvmdirpath)
        except OSError as e:
            msg = "Cannot create %s: %s" % (osvmdirpath, "{0}".format(e.strerror))
            print(msg)
            exit()

    globs.tmpDir = os.path.join(osvmdirpath, '.tmp')
    if not os.path.isdir(globs.tmpDir):
        try:
            os.mkdir(globs.tmpDir)
        except OSError as e:
            msg = "Cannot create %s: %s" % (globs.tmpDir, "{0}".format(e.strerror))
            myprint(msg)
            exit()

    # Create DemoFrame frame, passing globals instance as parameter
    app = wx.App(False)
    frame = MyFrame(None, -1, title="Test")
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
