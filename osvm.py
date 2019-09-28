#!/usr/bin/env python

_myName_     = 'OSVM'
_myLongName_ = 'Olympus Sync & View Manager'
_myVersion_  = '2.1.3'

import wx.lib.platebtn as platebtn

import sys

# Python version
__pythonVersion__ = (sys.version).split()[0]
if '2.' in __pythonVersion__:
    try:
        # for Python2
        from Tkinter import *   ## notice capitalized T in Tkinter 
    except ImportError:
        # for Python3
        from tkinter import *   ## notice lowercase 't' in tkinter here

    root = Tk()
    root.title("ERROR!")
    label = Label(root, text="\nERROR: %s requires Python 3.x to run.\n\n" % (_myName_))
    label.pack()
    root.mainloop()
    exit()

# XXX HACK to share the wx widget from 2.7 with python 3.6
sys.path.insert(0,'/usr/local/Cellar/wxmac/3.0.3.1_1/lib')

try:
    import wx
except ImportError:
    try: 
        root = Tk()
        root.title("ERROR!")
        label = Label(root, text="\nERROR: %s requires wxPython widgets to run.\n\n" % (_myName_) +
                      "wxPython is available at http://www.wxpython.org/\n\n" +
                      "%s has been developped and tested with python 3.6 and wxPython 4.0.1 (Cocoa)\n" % (_myName_))
        label.pack()
        root.mainloop()
        exit()
        #raise ImportError,"The wxPython module is required to run this program."
    except:
        print("ERROR: %s requires wxPython widgets to run.\n\n" % (_myName_)),\
        ("wxPython is available at http://www.wxpython.org/\n\n",) \
        ("%s has been developped and tested with python 3.6 and wxPython 4.0.1 (Cocoa)\n" % (_myName_))
        exit()

import argparse
import wx.html
import os
import inspect
from os.path import expanduser
from urllib.request import Request, urlopen
from urllib.error import URLError
import urllib.request, urllib.parse, urllib.error
import re
import configparser
import time
import threading
import platform
#import traceback
import subprocess
import shutil
import queue
import struct
import tempfile
import math
import wx.lib.colourdb as wb
import http.client
from urllib.parse import urlparse
from copy import deepcopy
import io
import wx.lib.scrolledpanel as scrolled
import wx.adv
import socket
import datetime
import glob
import ctypes

import simpleQRScanner

disabledModules= list()
try:
    import pychromecast
except ImportError:
        msg = 'PyChromeCast module not installed. Disabling Casting'
        print(msg)
        pycc = False
        disabledModules.append(('PyChromecast',msg))
else:
    pycc = True

try:
    import vlc # MediaViewer
except ImportError:
        msg = 'Vlc module not installed. Disabling Video Viewer'
        print(msg)
        vlcVideoViewer = False
        disabledModules.append(('VLC',msg))
else:
    vlcVideoViewer = True

try:
    import objc # WifiDialog
except ImportError:
        msg = 'Objc module not installed. Disabling Network Selector'
        print(msg)
        networkSelector = False
        disabledModules.append(('Objc',msg))
else:
    networkSelector = True

from PIL import Image

import wx.lib.agw.flatnotebook as fnb

CWSecurityModes = {
    0: '',
    1: 'WEP',
    2: 'WPA Personal',
    3: 'WPA Personal Mixed',
    4: 'WPA2 Personal',
    5: 'Personal',
    6: 'Dynamic WEP',
    7: 'WPA Enterprise',
    8: 'WPA Enterprise Mixed',
    9: 'WPA2 Enterprise',
    10: 'Enterprise',
    }

SERVER_HTTP_PORT = '8124'

__modPath__         = None
__system__          = None
__imgDir__          = None
__thumbDir__        = None
__tmpDir__          = None
__initFilePath__    = None
__logFilePath__     = None
__helpPath__        = None
__pythonBits__      = None
__pythonVersion__   = None

__system__ = platform.system()    # Linux or Windows or MacOS (Darwin)
__hostarch__ = platform.architecture()[0]    # 64bit or 32bit

if __system__ == 'Windows':
    try:
        #print 'Importing Windows win32 packages'
        import win32api
        import win32process
        import win32event
    except ImportError:
        from tkinter import *

        root = Tk()
        root.title("ERROR!")
        label = Label(root, text="\nERROR: %s requires win32 module to run.\n\n" % (_myName_) +
                      "win32 is available at http://sourceforge.net/projects/pywin32/files/pywin32/\n\n" +
                      "%s has been developped and tested with python 3.6, wxPython 4.0.1 and pywin32 219\n" % (_myName_))
        label.pack()
        root.mainloop()
        sys.exit()
        #raise ImportError,"The win32 modules are not installed."

# Constants
_osvmDir_          = '.osvm'		# In home directory
_initFile_        = 'osvm.ini'		# In _osvmDir_
_initFileBk_      = 'osvm.ini.bk'	# In _osvmDir_
_logFile_         = 'osvm-log.txt'	# In _osvmDir_
_iniFileVersion_  = '1'

# Default values for 'Reset Preferences'
DEFAULT_COMPACT_MODE = False
DEFAULT_ASK_BEFORE_COMMIT = True
DEFAULT_ASK_BEFORE_EXIT = True
DEFAULT_SAVE_PREFERENCES_ON_EXIT = True
DEFAULT_MAX_DOWNLOAD = 1
DEFAULT_OVERWRITE_LOCAL_FILES = False
DEFAULT_AUTO_SWITCH_TO_CAMERA_NETWORK = False
DEFAULT_OSVM_ROOT_URL  = 'http://192.168.0.10:80'
DEFAULT_OSVM_REM_BASE_DIR = '/DCIM'
DEFAULT_OSVM_DOWNLOAD_DIR = os.path.join(expanduser("~"), _osvmDir_, 'download')
DEFAULT_THUMB_GRID_NUM_COLS = 10
DEFAULT_THUMB_SCALE_FACTOR = 0.59
DEFAULT_SLIDESHOW_DELAY = 5
DEFAULT_SORT_ORDER = True # Mean More recent first

# Preferences file option keys
INI_VERSION = 'iniversion'
HTML_ROOT_FILE = 'htmlrootfile'
COMPACT_MODE = 'compactmode'
ASK_BEFORE_COMMIT = 'askbeforecommit'
ASK_BEFORE_EXIT = 'askbeforeexit'
SAVE_PREFS_ON_EXIT = 'savepreferencesonexit'
THUMB_GRID_COLUMNS = 'thumbnailgridcolumns'
THUMB_SCALE_FACTOR = 'thumbnailscalefactor'
OSVM_DOWNLOAD_DIR = 'osvmdownloaddir'
OSVM_FILES_DOWNLOAD_URL = 'osvmrooturl'
REM_BASE_DIR = "rembasedir"
MAX_DOWNLOAD = 'maxdownload'
OVERWRITE_LOCAL_FILES = 'overwritelocalfiles'
AUTO_SWITCH_TO_CAMERA_NETWORK = 'autoswitchtocameranetwork'
SS_DELAY = 'slideshowdelay'
LAST_CAST_DEVICE_NAME = 'lastcastdevicename'
LAST_CAST_DEVICE_UUID = 'lastcastdeviceuuid'
SORT_ORDER = 'filesortreverse'
FAVORITE_NETWORK = 'favoritenetwork'

# Globals Managed by Preferences / Frame # In _osvmDir_
htmlRootFile = 'htmlRootFile.html'
htmlDirFile  = 'htmlDirFile.html'

online = True
askBeforeCommit = True
askBeforeExit = True
savePreferencesOnExit = True
thumbnailGridColumns = DEFAULT_THUMB_GRID_NUM_COLS
thumbnailGridRows = 3
thumbnailScaleFactor = DEFAULT_THUMB_SCALE_FACTOR
osvmDownloadDir = DEFAULT_OSVM_DOWNLOAD_DIR
osvmFilesDownloadUrl = ''
maxDownload = DEFAULT_MAX_DOWNLOAD
overwriteLocalFiles = False
autoSwitchToFavoriteNetwork = False
rootUrl = DEFAULT_OSVM_ROOT_URL
remBaseDir = DEFAULT_OSVM_REM_BASE_DIR
ssDelay = DEFAULT_SLIDESHOW_DELAY
favoriteNetwork = ('','')  # Favorite Network, e.g. Camera
viewMode = False
autoViewMode = False
autoSyncMode = False
compactMode = False
useExternalViewer = False
httpServer = None
castMediaCtrl = None
slideShowNextIdx = 0
chromecasts = list() # List of available chromecast devices
castDevice = None # Selected chromecast
lastCastDeviceName = None
lastCastDeviceUuid = None
serverAddr = '0.0.0.0'
iface = None
allNetWorks = list() # List of all available networks
knownNetworks = list()
fileSortRecentFirst = DEFAULT_SORT_ORDER
installSubPanelsCount = 5

# List of root directories on the camera
rootDirList = []
rootDirCnt = 0

# Oldest and newest date of remote files on the camera
remOldestDate = ''
remNewestDate = ''

# Dict containing informations on the files available at remote/camera
availRemoteFiles = {}

# Common indexes to availRemoteFiles and localFileInfos.
[F_NAME, # common
 F_SIZE, # common
 F_DATE, # common
 F_PATH,
 F_DIRNAME,
 F_ATTR,
 F_DATEINSECS,
 F_TIME,
 F_THUMBURL] = [i for i in range(9)]

availRemoteFilesCnt =  0
availRemoteFilesSorted = {}	# Sorted copy of the dict above

# File Status
[FILE_NOT_INSTALLED,
 FILE_INSTALLED,
 FILE_OP_PENDING] = [i for i in range(3)]

# Colors to use for package buttons (bg,fg). 
# Will be updated at run-time with other colors
# Order must match "Package Status" e.g.:
# - Remote File (NOT_INSTALLED)
# - Local File  (INSTALLED)
# - Request pending (OP_PENDING)
fileColors = [[0,0],[wx.GREEN,wx.WHITE],[0,0]]
FILE_COLORS_STATUS = ["Remote File", "Local File", "Request pending"]
DEFAULT_FILE_COLORS = []

# Dictionary of local files
# key: fileName, value: [fileName, fileSize, fileDate, filePath]
localFileInfos = {}
[FINFO_NAME,
 FINFO_SIZE,
 FINFO_DATE,
 FINFO_PATH] = [i for i in range(4)]
localFilesCnt = 0
localFilesSorted = {}	# Sorted copy of the dict above

# Possible operations on a file
[FILE_DOWNLOAD,
 FILE_DELETE,
 FILE_SELECT,
 FILE_UNSELECT,] = [i for i in range(4)]

FILE_PROPERTIES = -3
FILE_SLIDESHOW = -4
OPERATION_NAMES = {FILE_DOWNLOAD:'DOWNLOAD', FILE_DELETE:'DELETE'}

# Max # of operations to commit in a single click
MAX_OPERATIONS = 2000

# Max delay interval for slideshow
MIN_SS_DELAY = 3
MAX_SS_DELAY = 11

# opList fields index
[OP_STATUS,     # status (busy=1/free=0)
 OP_FILENAME,   # remote file name (camera)
 OP_FILETYPE,	# JPG, MOV,...
 OP_TYPE,       # FILE_DOWNLOAD = 1  FILE_DELETE = 2
 OP_FILEPATH,   # full pathname of local file for download
 OP_SIZE,       # (size in bytes, block count)
 OP_FILEDATE,	# remote file date
 OP_REMURL,     # full remote url to download
 OP_INWGT,      # list of all assoc. widgets in InstallDialog frame
 OP_INCOUNT,    # current block counter for this op
 OP_INSTEP,     # Installation step
 OP_INLEDCOL,   # Installation LED color
 OP_INLEDSTATE, # Installation LED state: ON/BLINK/OFF
 OP_INTH,       # Installation thread
 OP_INTICKS,    # Installation elapsed time
 OP_LASTIDX] = [i for i in range(16)]    # Last index (must be last field)

# Execution Mode
MODE_DISABLED = 0
MODE_ENABLED  = 1

# Urllib read block size
URLLIB_READ_BLKSIZE = 8192

# Install Dialog constants
[INST_GAUGE,
 INST_ELAPTXT,
 INST_ELAPCNT,
 INST_REMTXT,
 INST_REMCNT,
 INST_STBOX,
 INST_OPBOXSZ,
 INST_GRDSZ,
 INST_LEDBOXSZ,
 INST_LEDLIST,
 INST_GKBOXSZ,
 INST_KEYTXT] = [i for i in range(12)]

TIMER1_FREQ  = 1000.0 # milliseconds
TICK_PER_SEC = 1000 / TIMER1_FREQ

TIMER2_FREQ = 200 # milliseconds
TIMER3_FREQ = 200 # milliseconds
TIMER4_FREQ = 100 # milliseconds
TIMER5_FREQ = 50 # milliseconds

# LEDs colours
LEDS_COLOURS = [['#929292', '#A8A8A8', '#9C9C9C', '#B7B7B7'], # grey
                ['#0ADC0A', '#0CFD0C', '#0BEB0B', '#0DFF0D'], # green
                ['#DC0A0A', '#FD0C0C', '#EB0B0B', '#FF0D0D'], # red
                ['#1E64B4', '#2373CF', '#206BC1', '#267DE1'], # steel blue (30, 100, 180)
                ['#FAC800', '#FFE600', '#FFD600', '#FFFA00']] # yellow

[LED_GREY,
 LED_GREEN,
 LED_RED,
 LED_BLUE,
 LED_ORANGE] = [i for i in range(5)]

[LED_OFF, LED_BLINK, LED_ON] = [i for i in range(3)]

# File Types to view/sync
FILETYPES = ['None', 'JPG', 'MOV', 'ALL']
FILETYPES_NOVLC = ['', 'JPG']

# File types to clean. For each type, a counter is provided (see folderSize())
CLEAN_FILETYPES = { 'JPG':0, 'MOV':0 }

# Wifi networks parameters (scanForNetworks())
[NET_SSID,
 NET_BSSID,
 NET_PASSWD,
 NET_RSSI,
 NET_CHANNEL,
 NET_SECURITY,
 NET_KNOWN,
 NET_FAVORITE,
 NET_NET] = [i for i in range(9)]

cameraConnected = True

ONEMEGA = 1024.0 * 1024.0
ONEKILO = 1024.0

ID_CONNECT_ERROR = 400

########################################
def dateInSeconds(d, t):
    ''' return a value containing a date in seconds since 1/1/70. '''
    maskDay   = 0x001F	# "0000000000011111"
    maskMonth = 0x01E0	# "0000000111100000"
    maskYear  = 0xFE00	# "1111 1110 0000 0000"

    day   = (d & maskDay) >> 0
    month = (d & maskMonth) >> 5
    year  = ((d & maskYear) >> 9) + 1980

    maskSeconds = 0x001F # 0000000000011111
    maskMinutes = 0x07E0 # 0000011111100000
    maskHours   = 0xF800 # 1111100000000000

    hours   = ((t & maskHours) >> 11) + 0 # XXX ???
    minutes = (t & maskMinutes) >> 5
    seconds = (t & maskSeconds) * 2

#    print (year, month, day, hours, minutes, seconds)
    t = datetime.datetime(year, month, day, min(hours,23), min(minutes,59), min(seconds,59))
    return time.mktime(t.timetuple())

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

def secondsToTime(t):
    d = time.strftime('%H:%M:%S', time.localtime(t))
    return d

def secondsTomdY(t):
    d = time.strftime('%m/%d/%Y', time.localtime(t))
    return d

def secondsTodmY(t):
    d = time.strftime('%d/%m/%Y', time.localtime(t))
    return d

def secondsTomdy(t):
    d = time.strftime('%m/%d/%y', time.localtime(t))
    return d

def secondsTodmy(t):
    d = time.strftime('%d/%m/%y', time.localtime(t))
    return d

def module_path(local_function):
   ''' returns the module path without the use of __file__.  
   Requires a function defined locally in the module.
   from http://stackoverflow.com/questions/729583/getting-file-path-of-imported-module'''
   return os.path.abspath(inspect.getsourcefile(local_function))

def cleanup():
    print ('cleanup(): Removing temporary files')
    if os.path.exists(htmlRootFile):
        try:
            os.remove(htmlRootFile)
        except:
            print('cleanup(): Failed to remove %s' % (htmlRootFile))

    if os.path.exists(htmlDirFile):
        try:
            os.remove(htmlDirFile)
        except:
            print('cleanup(): Failed to remove %s' % (htmlDirFile))

def printGlobals():
    global cameraConnected
    global compactMode, askBeforeCommit, askBeforeExit, overwriteLocalFiles, autoSwitchToFavoriteNetwork
    global savePreferencesOnExit
    global localFilesCnt
    global availRemoteFilesCnt
    global osvmDownloadDir
    global osvmFilesDownloadUrl
    global maxDownload
    global fileColors
    global ssDelay
    global knownNetworks
    global fileSortRecentFirst
    global favoriteNetwork

    print('compactMode: %s' % compactMode)
    print('askBeforeCommit: %s' % askBeforeCommit)
    print('askBeforeExit: %s' % askBeforeExit)
    print('overwriteLocalFiles: %s' % overwriteLocalFiles)
    print('autoSwitchToFavoriteNetwork: %s' % autoSwitchToFavoriteNetwork)
    print('cameraConnected: %s' % cameraConnected)
    print('maxDownload: %s' % maxDownload)
    print('localFilesCnt: %s' % localFilesCnt)
    print('availRemoteFilesCnt: %s' % availRemoteFilesCnt)
    print('savePreferencesOnExit: %s' % savePreferencesOnExit)
    print('osvmDownloadDir: %s' % osvmDownloadDir)
    print('osvmFilesDownloadUrl: %s' % osvmFilesDownloadUrl)
    print('fileColors:', fileColors)
    print('ssDelay:', ssDelay)
    print('knownNetworks:', knownNetworks)
    print('favoriteNetwork:', favoriteNetwork)
    print('fileSortRecentFirst:', fileSortRecentFirst)

def getTmpFile():
    f = tempfile.NamedTemporaryFile(delete=False)
    return f.name

def dumpOperationList(title, oplist):
    optype = ["NOT USED", "DOWNLOAD", "DELETE"]
    opstep = ["DOWNLOAD", "EXTRACT", "INSTALL"]
    i = 0
    print('**** Dump: %s ****' % title)
    for op in oplist:
#        print ('%d: STATUS: %d' % (i, op[OP_STATUS]))
        if op[OP_STATUS] != 0:
            print('*** %d ***' % (i))
            print('         File Name: %s' % op[OP_FILENAME])
            print('         File Type: %s' % op[OP_FILETYPE])
            print('         File Date: %s' % getHumanDate(op[OP_FILEDATE]))
            print('      Request Type: %s' % optype[op[OP_TYPE]])

            if op[OP_TYPE] != FILE_DELETE:
                print('      Local filename: %s' % op[OP_FILEPATH])
                print('     Remote File URL: %s' % op[OP_REMURL])
                print('    Remote File Size: %d/%d' % (op[OP_SIZE][0],op[OP_SIZE][1]))

            if op[OP_TYPE] != FILE_DELETE:
                print('    Current Transfer Block Counter: %d' % op[OP_INCOUNT])
                print('    Current Installation Step: %s' % opstep[op[OP_INSTEP]])

            if op[OP_INTH]:
                print('    Installation Thread: %s' % op[OP_INTH].name)
        i += 1

#
# Remove a local file. return -1 in case of failure
#
def removeFile(pathname):
    try:
        print('removeFile(): Deleting:',pathname)
        os.remove(pathname)
    except OSError as e:
        msg = "removeFile(): Cannot remove %s: %s" % (pathname, "{0}".format(e.strerror))
        print (msg)
        return -1
    return 0

#
# Create a symbolic link on source. return -1 in case of failure
#
def createSymLink(path, link):
    try:
        print('createSymLink():',path,link)
        os.symlink(path, link)
    except IOError as e:
        msg = "createSymLink(): I/O error: %s %s" % ("({0}): {1}".format(e.errno, e.strerror),link)
        print (msg)
        return -1
    return 0

#
# Get information about the filesystem in parameter
#
def diskUsage(path):
    st = os.statvfs(path)
    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    return (total, used, free)

#
# Get folder size (in bytes) on the disk for files matching suffixes
# Update CLEAN_FILETYPES dictionary with # of files 
# ex: folderSize('/a/b/c', ('.JPG', '.jpg', '.jpeg'))
def folderSize(folder, suffixes):
    global CLEAN_FILETYPES

    totalSize = 0
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if item.endswith(suffixes) and os.path.isfile(itempath):
            totalSize += os.path.getsize(itempath)
            CLEAN_FILETYPES[suffixes] += 1 # bump file counter
        elif os.path.isdir(itempath):
            totalSize += folderSize(itempath, suffixes)
    return totalSize

#
# Scan for networks, update the allNetworks list
#
def scanForNetworks():
    global allNetworks
    global knownNetworks
    global iface
    global favoriteNetwork

    setBusyCursor(True)
    networks, error = iface.scanForNetworksWithName_error_(None, None)
    setBusyCursor(False)
    if error:
        return error

    allNetworks = list()
    for n in networks:
        n_ssid         = n.ssid()
        n_rssi         = n.rssiValue()
        n_channel      = n.channel()
        n_bssid        = n.bssid()
        n_securityMode = CWSecurityModes[n.securityMode()]
        n_known = False
        n_favorite = False
        for kn in knownNetworks:
                ssid,bssid,passwd = kn.split(',')
                if n_ssid == ssid and n_bssid == bssid:
                    n_known = True
                    break
        if favoriteNetwork[NET_SSID] == n_ssid and favoriteNetwork[NET_BSSID] == n_bssid:
            n_favorite = True
        allNetworks.append((n_ssid,n_bssid,'',n_rssi,n_channel,n_securityMode,n_known,n_favorite,n))
    return None

#
# Update the knownNetworks global list if needed
#
def addKnownNetwork(ssid, bssid, password):
    global knownNetworks

    v = '%s,%s,%s' % (ssid,bssid,password)
    print('addKnownNetwork(): Adding %s' % v)

    for i in range(len(knownNetworks)):
        if knownNetworks[i] == v:
            print(v, 'is already known')
            return
    knownNetworks.append(v)
    print('addKnownNetwork(): Added %s' % v)

# 
# Remove a network from knownNetworks
#
def delKnownNetwork(ssid, bssid):
    global knownNetworks

    sub = '%s,%s' % (ssid,bssid)
    print('delKnownNetwork(): Removing %s' % sub)
    e = [s for s in knownNetworks if sub in s]
    knownNetworks.remove(e[0])
    print('delKnownNetwork(): Removed %s' % e)

def switchToFavoriteNetwork():
    global favoriteNetwork
    global allNetworks
    global knownNetworks
    global iface

    if iface.ssid() == favoriteNetwork[NET_SSID] and iface.bssid() == favoriteNetwork[NET_BSSID]:
        # Nothing to do
        return 0

    print('switchToFavoriteNetwork():Switching to favorite network:', favoriteNetwork)

    # Update network list
    error = scanForNetworks()
    if error:
        print(error)
        return -1

    # Check in all networks
    ssid = None
    for net in allNetworks:
        if net[NET_SSID] == favoriteNetwork[NET_SSID] and net[NET_BSSID] == favoriteNetwork[NET_BSSID]:
            for kn in knownNetworks: # kn='ssid,bssid,passwd'
                knParms = kn.split(',')
                if knParms[NET_SSID] == favoriteNetwork[NET_SSID] and knParms[NET_BSSID] == favoriteNetwork[NET_BSSID]:
                    ssid = knParms[NET_SSID]
                    bssid = knParms[NET_BSSID]
                    password = knParms[NET_PASSWD]
                    break
            break
    if ssid is None:
        print('switchToFavoriteNetwork(): Favorite network not found in networks list')
        return -1

    print('switchToFavoriteNetwork(): Connecting to known network %s, bssid %s password %s' 
          % (ssid, bssid, password))
    success, error = iface.associateToNetwork_password_error_(net[NET_NET], password, None)
    if success:
        return 0
    print(error)
    return -1

#
# Browse a directory, looking for filenames ending with: JPG, MOV, ORF, MPO
#
def listLocalFiles(dir, hidden=False, relative=True):
    nodes = []
    try:
        for nm in os.listdir(dir):
            if not hidden and nm.startswith('.'):
                continue

            if not nm.endswith(".JPG") and not nm.endswith(".MOV") and not nm.endswith(".ORF") and not nm.endswith(".MPO"):
                continue

            if not relative:
                nm = os.path.join(dir, nm)

            nodes.append(nm)

        nodes.sort()
    except:
        print("listLocalFiles(): Error: Can't browse:", dir)

    return nodes


# 
# Browse the Download directory.
# Output is a dictionary localFileInfos{} containing:
# - key: fileName#
# - value: list of info for this file
#
# Return # entry in the dictionary
def localFilesInfo(dirName):
    global localFileInfos
    global localFilesSorted
    global availRemoteFiles
    global viewMode
    global fileSortRecentFirst
    global cameraConnected

    print('localFilesInfo(): %s cameraConnected: %s' % (dirName, cameraConnected))
    localFileInfos = {}
    fileList = listLocalFiles(dirName, hidden=False)
    i = 0
    # Get local file informations: size, date,...
    # Cleanup the Download directory. Delete partially downloaded files
    for fileName in fileList:
        filePath = os.path.join(dirName, fileName)
        if os.path.islink(filePath):
            # Skip over symbolic links
            continue
        try:
            statinfo = os.stat(filePath)
            localFileSize = statinfo.st_size
        except:
            print('Error: os.stat()')
            continue

        if not viewMode and cameraConnected:
            try:
                remFileName = availRemoteFiles[fileName][F_NAME]
            except:
                # Local file does not exist anymore on remote/camera. Probably deleted...
                print('File %s not found on remote/camera. Deleting' % (fileName))
                os.remove(filePath)
                continue

#        if not viewMode:
#            try:
#                remFileSize = 0
#                remFileSize = availRemoteFiles[fileName][F_SIZE]
#            except:
#                # Local file does not exist anymore on remote/camera. Probably deleted...
#                print('File %s not found on remote/camera' % (fileName))
#                if not remFileSize:
#                    print('MUST DELETE EMPTY LOCAL FILE %s' % (fileName))
##os.remove(filePath)
#                    continue
#            else:
#                if localFileSize != remFileSize:
#                    print('MUST DELETE INCOMPLETE LOCAL FILE %s (%d)' % (fileName,localFileSize))
#                    os.remove(filePath)
#                    continue

        fileDate = statinfo.st_mtime # in seconds
        localFileInfos[fileName] = [fileName,localFileSize,fileDate,filePath]
        i += 1
    localFilesSorted = sorted(list(localFileInfos.items()), key=lambda x: int(x[1][F_DATE]), reverse=fileSortRecentFirst) #True)
    return i

def downloadThumbnail(e):
    global __thumbDir__
    global cameraConnected
    global rootUrl
    global remBaseDir
    global availRemoteFiles

    uri       = e[F_THUMBURL]
    thumbFile = e[F_NAME]
    thumbSize = e[F_SIZE]

    thumbnailPath = os.path.join(__thumbDir__, thumbFile)

    if os.path.isfile(thumbnailPath): 
        try: 
            f = open(thumbnailPath, 'r')
        except IOError:
            os.remove(thumbnailPath)
            print('downloadThumbnail(): %s: Cannot use existing thumbnail. Will download it' % (thumbFile))
        else:
            f.close()  # Using available local file
#            print('downloadThumbnail(): Using existing thumbnail %s' % (thumbFile))
            return 0

    if cameraConnected:
        print("downloadThumbnail(): Downloading %s from camera" % (thumbFile))
        try:
            response = urllib.request.urlopen(uri)
        except IOError as e:
            msg = "downloadThumbnail(): I/O error: Opening URL %s %s" % (uri, "({0}): {1}".format(e.errno, e.strerror))
            print(msg)
            cameraConnected = False

    if cameraConnected:
        tmp = response.read()

        try:
            print("downloadThumbnail(): Creating %s" % (thumbnailPath))
            out = open(thumbnailPath, 'wb')
            out.write(tmp)
            out.close()
            return 0
        except IOError as e:
            msg = "downloadThumbnail(): I/O error: Creating %s: %s" % (thumbnailPath, "({0}): {1}".format(e.errno, e.strerror))
            print (msg)
            return -1

def getRootDirInfo(rootDir, uri): # XXX
    global cameraConnected
    global rootUrl
    global remBaseDir
    global availRemoteFiles
    global htmlRootFile
    global htmlDirFile
    global availRemoteFilesSorted
    global fileSortRecentFirst

    if cameraConnected:
        print("getRootDirInfo(): Downloading from network: %s" % (uri))
        try:
            response = urllib.request.urlopen(uri)
        except IOError as e:
            msg = "getRootDirInfo(): I/O error: Opening URL %s %s" % (uri, "({0}): {1}".format(e.errno, e.strerror))
            print(msg)
            cameraConnected = False

    if cameraConnected:
        tmp = response.read()

        try:
            print("getRootDirInfo(): Opening: %s" % (htmlDirFile))
            out = open(htmlDirFile, 'wb')
            out.write(tmp)
            out.close()
        except IOError as e:
            msg = "getRootDirInfo(): I/O error: Opening %s: %s" % (htmlDirFile, "({0}): {1}".format(e.errno, e.strerror))
            print (msg)
            return -1
    else:
        print ("getRootDirInfo(): You are offline")
        return -1

    # Filter out unnecessary lines
    input = open(htmlDirFile, 'r')
    tmp = input.read()
    input.close()

    filterUrl = "%s/%s" % (remBaseDir,rootDir)     # e.g. /DCIM/100OLYMP   XXX
    tmp2 = [x for x in tmp.split('\n') if re.search(filterUrl, x)]

    # Example :
    # wlansd[0]="/DCIM/100OLYMP,PC020065.JPG,1482293,0,19330,31239";

    availRemoteFiles = {}
    i = 0
    for line in tmp2:
        info = line.split('=')[1][1:] # e.g.: /DCIM/100OLYMP,PC020065.JPG,1482293,0,19330,31239";
#        dirName  = /DCIM/100OLYMP
#        fileName = PC020065.JPG
#        fileSize = 1482293
#        fileAttr = 0
#        fileDate = 19330
#        t = 31239";

        fields = info.split(',')
        dirName,fileName,fileSize,fileAttr,fileDate,t = fields
        fileTime = int(t[:len(t)-2])		    	# remove trailing "; characters
        thumbnailUrl = "%s/get_thumbnail.cgi?DIR=%s/%s" % (rootUrl,dirName,fileName) # e.g: http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/PC020065.JPG
        availRemoteFiles[fileName] = [fileName, int(fileSize), int(fileDate), '', dirName, int(fileAttr), int(dateInSeconds(int(fileDate), int(fileTime))), int(fileTime), thumbnailUrl]

        i += 1

    print("getRootDirInfo(): %d files found" % i)

    # Sort the dict by date: Latest file first
    availRemoteFilesSorted = sorted(list(availRemoteFiles.items()), key=lambda x: int(x[1][F_DATEINSECS]), reverse=fileSortRecentFirst)
#    for e in availRemoteFilesSorted:
#        print("Detected remote file: %s size %d created %s %s %d" % (e[1][F_NAME],e[1][F_SIZE],getHumanDate(e[1][F_DATE]),getHumanTime(e[1][F_TIME]),int(e[1][F_DATEINSECS])))
    return i

def htmlRoot(rootUrl): # XXX
    global cameraConnected
    global remBaseDir
    global rootDirList
    global htmlRootFile

    if cameraConnected:
        print("htmlRoot(): Downloading from network: %s" % (rootUrl))
        try:
            response = urllib.request.urlopen(rootUrl,None,5)
        except IOError as e:
            msg = "htmlRoot(): I/O error: Opening URL %s %s" % (rootUrl, "({0}): {1}".format(e.errno, e.strerror))
            print (msg)
            cameraConnected = False

    if cameraConnected:
        tmp = response.read()
        try:
            print("Opening: %s" % (htmlRootFile))
            out = open(htmlRootFile, 'wb')
            out.write(tmp)
            out.close()
        except IOError as e:
            msg = "htmlRoot(): I/O error: Opening %s: %s" % (htmlRootFile, "({0}): {1}".format(e.errno, e.strerror))
            print (msg)
            return -1
    else:
        print ('htmlRoot(): You are offline')
        return -1

    # Filter out unnecessary lines
    input = open(htmlRootFile, 'r')
    tmp = input.read()
    input.close()

    baseRootDirs = [x for x in tmp.split('\n') if re.search(remBaseDir, x)]

    # Example :
    # wlansd[0]="/DCIM,100OLYMP,0,16,19311,45705";

    rootDirList = []
    i = 0
    for line in baseRootDirs:
        fields = line.split(',')
        foo1,dirName,foo2,dirAttr,dirDate,foo3 = fields
        if not int(dirAttr) & 0x10:
            print("Invalid entry %s. Skipping" % (dirName))
            continue
        rootDirList.append(dirName)
        i += 1

    print("%d root dirs found" % len(rootDirList))
    for d in rootDirList:
        print("Detected remote folder: %s" % d)
    return len(rootDirList)

def clearDirectory(dir):
    print('Deleting:',dir)
    if not os.path.isdir(dir):
        return
    shutil.rmtree(dir)

def updateFileDicts():
    global osvmFilesDownloadUrl
    global rootDirCnt
    global rootDirList
    global remBaseDir
    global localFilesCnt
    global availRemoteFilesCnt
    global availRemoteFiles
    global cameraConnected
    global localFilesSorted
    global localFilesSortedAsList
    global viewMode

    # Reset camera status. Will be updated if connection fails
    cameraConnected = True

    # Download the root HTML from the camera
    relRootUrl = '%s%s' % (osvmFilesDownloadUrl, remBaseDir)
    rootDirCnt =  htmlRoot(relRootUrl) # XXX
    print('updateFileDicts(): %d root directories available for download' % rootDirCnt)
    if rootDirCnt <= 0:
        availRemoteFilesCnt = 0
        cameraConnected = False
        availRemoteFiles.clear()
        availRemoteFilesSorted.clear()
    else:
        for d in rootDirList:
            uri = '%s%s/%s' % (osvmFilesDownloadUrl, remBaseDir, d)
            print("Querying URL %s..." % (uri))
            availRemoteFilesCnt = getRootDirInfo(d, uri)
            print("updateFileDicts():", availRemoteFilesCnt, "remote files available")

            for e in sorted(availRemoteFiles.values()):
                ret = downloadThumbnail(e)
                if ret:
                    print ("Error while downloading thumbnail.")
                    break

    # Detect local files
    localFilesCnt = localFilesInfo(osvmDownloadDir)
    print('updateFileDicts(): %d local files, %d remote files' % (localFilesCnt,availRemoteFilesCnt))
    return localFilesCnt,availRemoteFilesCnt

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")

def touch(path):
    with open(path, 'a'):
        os.utime(path, None)

####
def deleteLocalFiles(pDialog, opList):
    for op in opList:
        # If this operation is not used or not 'DELETE', skip it
        if not op[OP_STATUS] or op[OP_TYPE] != FILE_DELETE:
            continue
        filePath = op[OP_FILEPATH]
        (ret, msg) = deleteLocalFile(pDialog, filePath)

def downloadFile(op, pDialog):
    global overwriteLocalFiles
    global availRemoteFiles

    fileName   = op[OP_FILENAME]
    localFile  = op[OP_FILEPATH]
    remoteFile = op[OP_REMURL]
    remSize    = op[OP_SIZE][0]
    remBlocks  = op[OP_SIZE][1]
    thr        = op[OP_INTH]

    print('%s: downloadFile():' % thr.name, remoteFile, localFile, remSize, remBlocks)

    # Hack to use existing local file to save download time
    if not overwriteLocalFiles:
        print('%s: downloadFile(): Checking for local file: %s' % (thr.name, localFile))
        if os.path.isfile(localFile): 
            try: 
                f = open(localFile, 'r')
            except IOError:
                os.remove(localFile)
                print('%s: downloadFile(): Cannnot use existing local file %s. Will download' % (thr.name, fileName))
            else:
                f.close()
                # Should check local file size here...
                statinfo = os.stat(localFile)
                print("%s: downloadFile(): file: %s size: local: %d remote: %d" % (thr.name, fileName, statinfo.st_size, remSize))
                if statinfo.st_size != remSize:	
                    msg = "%s: downloadFile(): Local file %s has a wrong size (%d/%d). Deleting local file" % (thr.name, fileName, statinfo.st_size, remSize)
                    print (msg)
                    os.remove(localFile)
                else:
                    print('%s: downloadFile(): Skipping download. Using available local file: %s' % (thr.name, fileName))
                    return (0, '')

    try:
        out = open(localFile, 'wb')
    except IOError as e:
        msg = "%s: downloadFile(): I/O error: Opening output file %s %s" % (thr.name, localFile, "({0}): {1}".format(e.errno, e.strerror))
        print (msg)
        return (-1, msg)

    req = Request(remoteFile)
    try:
        response = urlopen(req)
    except URLError as e:
        if hasattr(e, 'reason'):
            print('Failed to reach the server/camera.')
            print('Reason: ', e.reason)
            return (-1, e.reason)
        elif hasattr(e, 'code'):
            print('The server/camera couldn\'t fulfill the request.')
            print('Error code: ', e.code)
            return (-1, e.code)
        else:
            pass            # everything is fine

    msg = "%s: downloadFile(): Starting transfer %s" % (thr.name,remoteFile)
    print (msg)

    blockSize = URLLIB_READ_BLKSIZE
    op[OP_INCOUNT] = 0
    keepGoing = True
    ret = 0
    while keepGoing:
        try:
            chunk = response.read(blockSize)

            if thr.isStopped():
                print('%s: downloadFile(): Thread stopped. Aborting transfer' % thr.name)
                ret = -2
                break
        except:
            print('%s: downloadFile(): Error: Downloading package' % thr.name)
            ret = -1
            break
        if not chunk: 
            # End of transfer
            print('%s: downloadFile(): End of transfer detected' % thr.name)
            wx.CallAfter(pDialog.updateCounter, op, 1)
            break
        out.write(chunk)
        op[OP_INCOUNT] += 1
        keepGoing = pDialog.keepGoing
        #print ('downloadFile(): blkno=',op[OP_INCOUNT],keepGoing)
    out.flush()
    out.close()

    # Sanity check:
    # Check if user has cancelled the transfer or wrong transfer size
    try:
        statinfo = os.stat(localFile)
    except:
        print('%s does not exist anymore' % localFile)
        return (ret, '')
    else:
        print("downloadFile():",keepGoing,statinfo.st_size,remSize)
        if not keepGoing or statinfo.st_size != remSize:	
            msg = "%s: downloadFile(): Downloaded file has a wrong size (%d/%d)" % (thr.name, statinfo.st_size, remSize)
            os.remove(localFile)
            return (ret, msg)
        elif statinfo.st_size == remSize:
            # Set modifiction date to date of media file
            d1 = getHumanDate(availRemoteFiles[fileName][F_DATE])
            t1 = getHumanTime(availRemoteFiles[fileName][F_TIME])

            m,d,y = d1.split('/')
            H,M,S = t1.split(':')

            dt = datetime.datetime(int(y),int(m),int(d),int(H),int(M),int(S)) # year, month, day, hour, min, sec
            modTime = time.mktime(dt.timetuple())
            os.utime(localFile, (modTime, modTime))

    return (ret, '')

# Delete local files if needed
def deleteLocalFile(pDialog, filePath):
    global localFilesCnt
    global osvmDownloadDir

    ret = 0    # error counter
    msg = 'Removing local file %s\n' % (filePath)
    wx.CallAfter(pDialog.installError, 0, msg)

    removeCmd = 'rm %s' % filePath.replace(" ", "\\ ")
    p = subprocess.Popen(removeCmd, shell=True, 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.STDOUT, 
                         universal_newlines=True)
    for line in p.stdout.readlines():
        msg += line.strip()
#    stdout, stderr = p.communicate()
#    output = stdout.decode('utf-8').splitlines()
    
    ret = p.wait()
    print('removeCmd =',removeCmd,'ret=',ret,'msg=',msg)
    if not ret:
        msg = "File %s successfully removed\n" % (filePath)
        localFilesCnt = localFilesInfo(osvmDownloadDir)

    wx.CallAfter(pDialog.installError, ret, msg)
    return (ret, msg)

# Return the background and foreground colors to paint a widget associated 
# to the given file
def fileColor(fileName):
    global localFileInfos
    global fileColors

    # Default color
    color = fileColors[FILE_NOT_INSTALLED]

    try:
        e = localFileInfos[fileName]
    except:
        return color

    color = fileColors[FILE_INSTALLED]
    return color

#
# Set/unset busy cursor (from thread)
#
def setBusyCursor(state):
    if state:
        wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)
    else:
        wx.EndBusyCursor()

# Dump object attributes
def dump(obj):
    for attr in dir(obj):
        print("obj.%s = %s" % (attr, getattr(obj, attr)))

def checkUrl(url):
    p = urlparse(url)
    conn = http.client.HTTPConnection(p.netloc)
    conn.request('HEAD', p.path)
    resp = conn.getresponse()
    return resp.status < 400

def startHTTPServer():
    global osvmDownloadDir
    global SERVER_HTTP_PORT

    null = open('/dev/null', 'w')

    p = subprocess.Popen(
        [sys.executable, '-m', 'http.server', SERVER_HTTP_PORT], 
        cwd=osvmDownloadDir,
        stdout=null,
        stderr=null,
        )
    print("Initializing HTTP Server on port %s" % SERVER_HTTP_PORT) 
    time.sleep(1)
    return p
    
def initPyChromeCast():
    global chromecasts
    global castDevice

    print('Looking for ChromeCast devices...')
    chromecasts = pychromecast.get_chromecasts(tries=2) 
    if not chromecasts:
        msg = 'No ChromeCast devices detected!'
        print(msg)
        dial = wx.MessageDialog(None, msg , 'Error', wx.OK | wx.ICON_ERROR)
        dial.ShowModal()
        return None

    print('Chromecasts Found:',chromecasts)
    for x in chromecasts:
        print(x)
        print(x.name)
        print(x.uri)
        print(x.model_name)
        print(x.device.manufacturer)
    
    dlg = ChromeCastDialog()
    ret = dlg.ShowModal()
    dlg.Destroy()
    if not castDevice:
        print('No ChromeCast devices detected!')
        return None

    print("Connecting to ChromeCast: %s." % castDevice.name)
    castDevice.wait()

    mc = castDevice.media_controller 
    return mc

def serverIpAddr():
    try:
        ipAddr = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    except OSError as e:
        msg = 'serverIpAddr(): Error %s' % ("({0}): {1}".format(e.errno, e.strerror))
        print(msg)
        ipAddr = '0;0;0;0'
    print('serverIpAddr():',ipAddr)
    return ipAddr

############# CLASSES #########################################################

#### PasswordDialog
class PasswordDialog(wx.Dialog):
    """
    Creates and displays a dialog to enter a password
    """
    def __init__(self,net):
        self.net = net

        myStyle = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
        wx.Dialog.__init__(self, None, wx.ID_ANY, 'Network Password', style=myStyle)

        self._initialize()

        self.panel1.SetSizerAndFit(self.topBoxSizer)
        self.SetClientSize(self.topBoxSizer.GetSize())
        self.Centre()

    def _initialize(self):
        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self, size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        self.wintitle = wx.StaticText(self.panel1)
        t = 'Enter Password to connect to: '
        m = "<span foreground='red'>%s</span><big><span foreground='blue'>%s</span></big>" % (t,self.net[NET_SSID])
        self.wintitle.SetLabelMarkup(m)

        self.passwdST = wx.StaticText(id=wx.ID_ANY, label='Password:', parent=self.panel1, style=0)
        self.passwdHideTC = wx.TextCtrl(id=wx.ID_ANY,
                                        parent=self.panel1, 
                                        style=wx.TE_PROCESS_ENTER | wx.TE_PASSWORD, 
                                        size=wx.Size(300, -1))
        self.passwdHideTC.SetToolTip('Enter password')
        self.passwdHideTC.SetAutoLayout(True)
        self.passwdHideTC.SetCursor(wx.STANDARD_CURSOR)
        self.passwdHideTC.Bind(wx.EVT_TEXT_ENTER, self.OnPasswdTC)
        self.passwdHideTC.SetFocus()

        self.passwdShowTC = wx.TextCtrl(id=wx.ID_ANY,
                                        parent=self.panel1, 
                                        style=wx.TE_PROCESS_ENTER,
                                        size=wx.Size(300, -1))
        self.passwdShowTC.SetToolTip('Enter password')
        self.passwdShowTC.SetAutoLayout(True)
        self.passwdShowTC.SetCursor(wx.STANDARD_CURSOR)
        self.passwdShowTC.Bind(wx.EVT_TEXT_ENTER, self.OnPasswdTC)
        self.passwdShowTC.Hide()

        self.cb1 = wx.CheckBox(self.panel1, id=wx.ID_ANY, label='Save Password')
        self.cb1.SetValue(True)

        self.cb2 = wx.CheckBox(self.panel1, id=wx.ID_ANY, label='Show Password')
        self.cb2.SetValue(False)
        self.cb2.Bind(wx.EVT_CHECKBOX, self.OnCb2)

        # widgets at the Bottom 
        # Cancel button
        self.btnCancel = wx.Button(id=wx.ID_CANCEL, parent=self.panel1, style=0)
        self.btnCancel.SetToolTip('Discard changes')
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnBtnCancel)

        # OK button
        self.btnOK = wx.Button(id=wx.ID_OK, parent=self.panel1, style=0)
        self.btnOK.SetToolTip('Save changes')
        self.btnOK.Bind(wx.EVT_BUTTON, self.OnBtnOK)

        # Connect button
        self.btnConnect = wx.Button(id=wx.ID_ANY, label='Connect', 
                                    parent=self.panel1, style=0)
        self.btnConnect.SetToolTip('Connect to this network')
        self.btnConnect.Bind(wx.EVT_BUTTON, self.OnBtnConnect)

        self._init_sizers()

    def _init_topBoxSizer_Items(self, parent):
        parent.Add(self.titleBoxSizer, 0, border=10, flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER)
        parent.Add(self.passwdBoxSizer, 1, border=10, flag=wx.EXPAND | wx.ALL)
        parent.Add(self.bottomBoxSizer, 0, border=10, flag=wx.ALL | wx.ALIGN_RIGHT)

    def _init_titleBoxSizer_Items(self, parent):
        parent.Add(0, 4, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.wintitle, 1, border=0, flag=wx.EXPAND)
        parent.Add(0, 4, 0, border=0, flag=wx.EXPAND)

    def _init_passwdBoxSizer_Items(self, parent):
        parent.Add(self.passwdSubBoxSizer1, 0, border=0, flag=wx.EXPAND | wx.ALL)
        parent.Add(0, 16, 1, border=0, flag=wx.EXPAND)
        parent.Add(self.passwdSubBoxSizer2, 0, border=0, flag=wx.EXPAND | wx.ALL)

    def _init_passwdSubBoxSizer1_Items(self, parent):
        parent.Add(self.passwdST, 0, border=0, flag=wx.EXPAND | wx.ALL)
        parent.Add(4, 4, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.passwdShowTC, 0, border=0, flag=wx.EXPAND | wx.ALL)
        parent.Add(self.passwdHideTC, 0, border=0, flag=wx.EXPAND | wx.ALL)

    def _init_passwdSubBoxSizer2_Items(self, parent):
        parent.Add(self.cb1, 0, border=0, flag=wx.EXPAND | wx.ALL)
        parent.Add(4, 4, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.cb2, 0, border=0, flag=wx.EXPAND | wx.ALL)

    def _init_bottomBoxSizer_Items(self, parent):
        parent.Add(self.btnCancel, 0, border=0, flag=wx.EXPAND)
        parent.Add(4, 4, border=0, flag=wx.EXPAND)
        parent.Add(self.btnOK, 0, border=0, flag=wx.EXPAND)
        parent.Add(4, 4, border=0, flag=wx.EXPAND)
        parent.Add(self.btnConnect, 0, border=0, flag=wx.EXPAND)

    def _init_sizers(self):
        # Create box sizers
        self.topBoxSizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.titleBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.passwdBoxSizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.passwdSubBoxSizer1 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.passwdSubBoxSizer2 = wx.BoxSizer(orient=wx.VERTICAL)
        self.bottomBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        # Initialize each sizer
        self._init_topBoxSizer_Items(self.topBoxSizer)
        self._init_titleBoxSizer_Items(self.titleBoxSizer)
        self._init_passwdBoxSizer_Items(self.passwdBoxSizer)
        self._init_passwdSubBoxSizer1_Items(self.passwdSubBoxSizer1)
        self._init_passwdSubBoxSizer2_Items(self.passwdSubBoxSizer2)
        self._init_bottomBoxSizer_Items(self.bottomBoxSizer)

    def OnCb2(self, event):
        if self.cb2.GetValue():
            self.passwdShowTC.Show(True)
            self.passwdHideTC.Show(False)
            self.passwdShowTC.SetValue(self.passwdHideTC.GetValue())
            self.passwdShowTC.SetFocus()
        else:
            self.passwdShowTC.Show(False)
            self.passwdHideTC.Show(True)
            self.passwdHideTC.SetValue(self.passwdShowTC.GetValue())
            self.passwdHideTC.SetFocus()
        self.passwdHideTC.GetParent().Layout()
        event.Skip()
            
    def OnPasswdTC(self, event):
        event.Skip()

    def OnBtnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBtnOK(self, event):
        if self.cb2.GetValue():
            passwd = self.passwdShowTC.GetValue()
        else:
            passwd = self.passwdHideTC.GetValue()
        print('OnBtnOK(): network:',self.net,'password:', passwd)
        addKnownNetwork(self.net[NET_SSID],self.net[NET_BSSID],passwd)
        self.EndModal(wx.ID_OK)
        event.Skip()

    def OnBtnConnect(self, event):
        global iface

        if self.cb2.GetValue():
            passwd = self.passwdShowTC.GetValue()
        else:
            passwd = self.passwdHideTC.GetValue()

        print('OnBtnConnect(): network:',self.net,'password:', passwd)
        success, error = iface.associateToNetwork_password_error_(self.net[NET_NET], passwd, None)
        if success:
            print('success')
            if self.cb1.GetValue(): # Must save network entry
                print('Must save Network Entry:',self.net[NET_SSID],self.net[NET_BSSID],passwd)
                addKnownNetwork(self.net[NET_SSID],self.net[NET_BSSID],passwd)
            self.EndModal(wx.ID_OK)
            event.Skip()
        else:
            print(error)

#### WifiDialog
class WifiDialog(wx.Dialog):
    """
    Creates and displays a dialog to select the WIFI network to connect
    """
    global allNetworks
    global iface

    def __init__(self,parent):
        """
        Initialize the preferences dialog box
        """
        myStyle = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
        wx.Dialog.__init__(self, None, wx.ID_ANY, 'WIFI Selector', style=myStyle)

        self.parent = parent
        self.net = None # Selected network
        self.netkey = None
        self.favoriteCbList = list()

        # Build allNetworks list
        error = scanForNetworks()
        if error:
            print(error)

        self._initialize()

        self.panel2.SetSizer(self.gsNet)
        self.panel2.SetAutoLayout(True)
        self.panel2.SetupScrolling()

        self.panel1.SetSizerAndFit(self.topBoxSizer)
        self.SetClientSize(self.topBoxSizer.GetSize())
        self.Centre()

    def _initialize(self):
        global viewMode
        global allNetworks

        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self, size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)
        self.panel2 = scrolled.ScrolledPanel(parent=self.panel1, id=wx.ID_ANY, size=(680,200), style=wx.TAB_TRAVERSAL)

        self.wintitle = wx.StaticText(self.panel1)
        if viewMode:
            m = "<big><span foreground='blue'>%s</span></big>" % 'Select a WIFI Network'
        else:
            m = "<big><span foreground='blue'>%s</span></big>" % 'Select the Camera Access Point'
        self.wintitle.SetLabelMarkup(m)

        # Sort networks by RSSI
        self.netwSorted = sorted(allNetworks, key=lambda x: x[NET_RSSI], reverse=True)

        # Store all WIFI networks information in a list
        self.netProps = list()
        self.netProps.append(('SSID', 'RSSI', 'Channel', 'BSSID', 'Security', 'Known', 'Favorite')) # Header
        for n in self.netwSorted:
            self.netProps.append((n[NET_SSID],n[NET_RSSI],n[NET_CHANNEL],n[NET_BSSID],n[NET_SECURITY],n[NET_KNOWN],n[NET_FAVORITE]))
        # Grid containing the information
        rows = len(self.netProps)
        cols = len(self.netProps[0])
        self.gsNet = wx.FlexGridSizer(rows, cols, vgap=5, hgap=10)

        # Create all individual widgets in self.fields(). Each entry contains a list
        # of fields for each network
        self.fields = list()

        # Directory. key = (SSID,BSSID) value = Radiobutton
        self.btnDir = {}

        # first line header
        self.onerowfields = list()
        for i in range(len(self.netProps[0])):
            field = wx.StaticText(self.panel2)
            field.SetLabelMarkup("<span foreground='blue'>%s</span>" % self.netProps[0][i])
            self.onerowfields.append(field)
        self.fields.append(self.onerowfields) # append to self.fields

        for i in range(1,rows):
            self.onerowfields = list()
            btn = wx.RadioButton(self.panel2, 
                                 label=self.netProps[i][0],
                                 name=self.netProps[i][0], 
                                 style=(wx.RB_GROUP if i==1 else 0)) # SSID
            btn.Bind(wx.EVT_RADIOBUTTON, self.OnRadioButton)
            self.onerowfields.append(btn)
            for j in range(1,len(self.netProps[0])-2):
                self.onerowfields.append(wx.StaticText(self.panel2, label=str(self.netProps[i][j])))
            # Known Network checkbox
            knownCb = wx.CheckBox(self.panel2, label='')
            knownCb.SetValue(self.netProps[i][len(self.netProps[0])-2])
            knownCb.Bind(wx.EVT_CHECKBOX, self.OnKnownCb)
            self.onerowfields.append(knownCb)
            # Favorite Network checkbox
            favoriteCb = wx.CheckBox(self.panel2, label='')
            favoriteCb.SetValue(self.netProps[i][len(self.netProps[0])-1])
            favoriteCb.Bind(wx.EVT_CHECKBOX, self.OnFavoriteCb)
            self.onerowfields.append(favoriteCb)
            self.favoriteCbList.append(favoriteCb)
            # Create directory entry. key=(SSID,BSSID)
            k = (self.netwSorted[i-1][NET_SSID],self.netwSorted[i-1][NET_BSSID])
            self.btnDir[k] = btn
            if iface.ssid() == btn.GetLabel() and iface.bssid() == self.netwSorted[i-1][NET_BSSID]:
                btn.SetValue(True)
                self.netkey = k
                print('WifiDialog(): Current Network:',k)
                self.panel2.ScrollChildIntoView(btn)
            self.fields.append(self.onerowfields) # append to self.fields

        # Add all widgets in the grid
        for r in range(rows):
            onerowfields = self.fields[r]
            for w in onerowfields:
                self.gsNet.Add(w, proportion=0, flag=wx.EXPAND)

        # widgets at the Bottom 
        # Scan QR Code button
        self.btnScanQR = wx.Button(id=wx.ID_ANY, label='Scan QR Code', parent=self.panel1, style=0)
        self.btnScanQR.SetToolTip('Scan QR Code from Camera')
        self.btnScanQR.Bind(wx.EVT_BUTTON, self.OnBtnScanQR)

        # Cancel button
        self.btnCancel = wx.Button(id=wx.ID_CANCEL, parent=self.panel1, style=0)
        self.btnCancel.SetToolTip('Discard changes')
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnBtnCancel)

        # OK button
        self.btnOK = wx.Button(id=wx.ID_OK, parent=self.panel1, style=0)
        self.btnOK.SetToolTip('Close this Dialog and Proceed')
        self.btnOK.Bind(wx.EVT_BUTTON, self.OnBtnOK)
        self.btnOK.SetDefault()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.timer.Start(5000)

        self._init_sizers()

    def _init_topBoxSizer_Items(self, parent):
        parent.Add(self.titleBoxSizer, 0, border=10, flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER)
        parent.Add(self.panel2, 1, border=10, flag=wx.EXPAND | wx.ALL)
        parent.Add(self.bottomBoxSizer, 0, border=10, flag=wx.ALL | wx.ALIGN_RIGHT)

    def _init_titleBoxSizer_Items(self, parent):
        parent.Add(4, 4, 1, border=0, flag=wx.EXPAND)
        parent.Add(self.wintitle, 2, border=0, flag=wx.EXPAND)
        parent.Add(4, 4, 1, border=0, flag=wx.EXPAND)

    def _init_bottomBoxSizer_Items(self, parent):
        parent.Add(self.btnScanQR, 0, border=0, flag=wx.EXPAND)
        parent.Add(16, 4, border=0, flag=wx.EXPAND)
        parent.Add(self.btnCancel, 0, border=0, flag=wx.EXPAND)
        parent.Add(4, 4, border=0, flag=wx.EXPAND)
        parent.Add(self.btnOK, 0, border=0, flag=wx.EXPAND)

    def _init_sizers(self):
        # Create box sizers
        self.topBoxSizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.titleBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.bottomBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        # Initialize each sizer
        self._init_topBoxSizer_Items(self.topBoxSizer)
        self._init_titleBoxSizer_Items(self.titleBoxSizer)
        self._init_bottomBoxSizer_Items(self.bottomBoxSizer)

    # Events
    def OnRadioButton(self, event):
        button = event.GetEventObject()
        for k,v in self.btnDir.items():
            if v == button:
                print('WifiDialog(): Selecting Network:',k)
                self.netkey = k
        event.Skip()

    def OnFavoriteCb(self, event):
        global allNetworks
        global favoriteNetwork

        cb = event.GetEventObject()
        self.timer.Stop()

        oldValue = cb.GetValue()

        # Disable all favorite checkboxes
        for w in self.favoriteCbList:
            w.SetValue(False)

        # Set this checkbox
        cb.SetValue(oldValue)

        if oldValue == False: # Clear favoriteNetwork
            favoriteNetwork = ('','')
            self.timer.Start(5000)
            event.Skip()
            return

        # Get associated network
        for onerowfields in self.fields:
            if cb in onerowfields:
                ssid = onerowfields[0].GetLabel()
                for net in allNetworks:
                    if net[NET_SSID] == ssid:
                        break
        favoriteNetwork = (net[NET_SSID],net[NET_BSSID])
        self.timer.Start(5000)
        event.Skip()

    def OnKnownCb(self, event):
        global allNetworks

        cb = event.GetEventObject()
        self.timer.Stop()

        # Get associated network
        for onerowfields in self.fields:
            if cb in onerowfields:
                ssid = onerowfields[0].GetLabel()
                for net in allNetworks:
                    if net[NET_SSID] == ssid:
                        break

        if cb.GetValue():
            # Popup a dialog to ask for this known network password
            dlg = PasswordDialog(net=net)
            ret = dlg.ShowModal()
            if ret == wx.ID_CANCEL:
                cb.SetValue(False)
            dlg.Destroy()
        else:
            # Popup a dialog to ask for removing this known network password
            # Ask confirmation
            dlg = wx.MessageDialog(None, 
                                   'Do you really want to DELETE password for Network %s ?' % ssid, 
                                   'Question', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            ret = dlg.ShowModal()
            if ret == wx.ID_YES:
                delKnownNetwork(net[NET_SSID], net[NET_BSSID])

        self.timer.Start(5000)
        event.Skip()

    def OnBtnOK(self, event):
        global knownNetworks
        global iface

        for i in range(1, len(self.fields)): # Skip header
            onerowfields = self.fields[i]
            btn = onerowfields[0]
            if btn.GetValue() and btn.GetLabel() == self.netkey[NET_SSID]:
                try:
                    self.net = self.netwSorted[i-1] # -1 for header
                except:
                    self.net = None
                else:
                    print('WifiDialog(): Using network:',self.net)
                    break
        if not self.net:
            self.EndModal(wx.ID_OK)
            return

        self.timer.Stop()

        if iface.ssid() == self.net[NET_SSID] and iface.bssid() == self.net[NET_BSSID]:
            print('WifiDialog(): Using already selected network')
            self.EndModal(wx.ID_OK)
            event.Skip()
            return

        # Check for open network
        if self.net[NET_SECURITY] == '':
            print('WifiDialog(): No password required. Connecting to %s' % self.net[NET_SSID])
            success, error = iface.associateToNetwork_password_error_(self.net[NET_NET], None, None)
            if success:
                self.EndModal(wx.ID_OK)
                event.Skip()
                return
            else:
                print(error)
                self.EndModal(ID_CONNECT_ERROR)
                event.Skip()
                return

        # Check for already known network
        for kn in knownNetworks: # kn='ssid,bssid,passwd'
            params = kn.split(',')
            if self.net[NET_SSID] == params[NET_SSID] and self.net[NET_BSSID] == params[NET_BSSID]:
                password = params[NET_PASSWD]
                print('WifiDialog(): Connecting to known network %s, bssid %s password %s' % (self.net[NET_SSID], self.net[NET_BSSID], password))
                success, error = iface.associateToNetwork_password_error_(self.net[NET_NET], password, None)
                if success:
                    self.EndModal(wx.ID_OK)
                    event.Skip()
                    return
                else:
                    print(error)
                    # Remove entry from knownNetworks
                    delKnownNetwork(params[NET_SSID], params[NET_BSSID])
                    # Known password is invalid, Ask for a new password
                    dlg = PasswordDialog(net=self.net)
                    ret = dlg.ShowModal()
                    dlg.Destroy()
                    return

        # Unknown network/password
        dlg = PasswordDialog(net=self.net)
        ret = dlg.ShowModal()
        dlg.Destroy()
        self.EndModal(wx.ID_OK)
        event.Skip()

    def OnBtnScanQR(self, event):
        global __tmpDir__

        print('Launching QR Scanner')
        dlg = simpleQRScanner.ShowCapture(self, -1, __tmpDir__)
        ret = dlg.ShowModal()
        dlg.Destroy()
        print('End of Capture Session')
#        simpleQRScanner.OISData = ['OIS1', 'TG-4-P-BHJ310474', '69074749']
#        simpleQRScanner.OISData = ['OIS1', 'HomeSweetHome_EXT', '2128819390']
        print(simpleQRScanner.OISData)
        if simpleQRScanner.OISData[0] == 'OIS1':
            scannedSSID = simpleQRScanner.OISData[1]
            scannedPasswd = simpleQRScanner.OISData[2]
            print('Looking for scanned SSID %s in detected networks' % scannedSSID)
            for onerowfields in self.fields:
                ssid = onerowfields[0].GetLabel()
                if ssid == scannedSSID:
                    break
            #print(onerowfields)
            for net in allNetworks:
                if net[NET_SSID] == scannedSSID:
                    break
            #print(net)
	    # Add scanned network to knownNetworks
            addKnownNetwork(scannedSSID,net[NET_BSSID],scannedPasswd)
            # Simulate a radiobutton press to select the scanned network
            evt = wx.PyCommandEvent(wx.EVT_RADIOBUTTON.typeId, onerowfields[0].GetId())
            evt.SetEventObject(onerowfields[0])
            wx.PostEvent(onerowfields[0], evt)
            event.Skip()

    def OnBtnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)
        event.Skip()

    def OnTimer(self, event):
        global allNetworks

        error = scanForNetworks()
        if error:
            print(error)
            return
        self.SetTitle('WIFI Selector: %d networks detected' % len(allNetworks))

        # Sort allNetworks by RSSI
        self.netwSorted = sorted(allNetworks, key=lambda x: x[NET_RSSI], reverse=True)

        # Store all WIFI networks information in a list
        self.netProps = list()
        self.netProps.append(('SSID', 'RSSI', 'Channel', 'BSSID', 'Security', 'Known', 'Favorite')) # Header
        for n in self.netwSorted:
            self.netProps.append((n[NET_SSID],n[NET_RSSI],n[NET_CHANNEL],n[NET_BSSID],n[NET_SECURITY],n[NET_KNOWN],n[NET_FAVORITE]))
        rows = len(self.netProps)
        cols = len(self.netProps[0])

        # Delete all existing widgets in the grid
        for onerowfields in self.fields: 
            for w in onerowfields:
                w.Destroy()

        # Create all individual widgets in self.fields
        self.fields = list()

        # Create a directory containing the radio buttons
        self.btnDir = {}

        # Clear existing list of favorite checkboxes
        self.favoriteCbList = list()

        # first line header
        self.onerowfields = list()
        for i in range(len(self.netProps[0])):
            field = wx.StaticText(self.panel2)
            field.SetLabelMarkup("<span foreground='blue'>%s</span>" % self.netProps[0][i])
            self.onerowfields.append(field)
        self.fields.append(self.onerowfields) # append to self.fields

        if self.net:
            print('OnTimer():',self.netkey)

        for i in range(1,rows):
            self.onerowfields = list()
            btn = wx.RadioButton(self.panel2, label=self.netProps[i][0], style=(wx.RB_GROUP if i==1 else 0)) # SSID
            btn.SetLabelMarkup("<b>%s</b>" % self.netProps[i][0])
            btn.Bind(wx.EVT_RADIOBUTTON, self.OnRadioButton)
            self.onerowfields.append(btn)
            for j in range(1,len(self.netProps[0])-2):#-1
                self.onerowfields.append(wx.StaticText(self.panel2, label=str(self.netProps[i][j])))
            knownCb = wx.CheckBox(self.panel2, label='')
            knownCb.SetValue(self.netProps[i][len(self.netProps[0])-2]) #-1
            knownCb.Bind(wx.EVT_CHECKBOX, self.OnKnownCb)
            self.onerowfields.append(knownCb)
            # Favorite Checkbox button
            favoriteCb = wx.CheckBox(self.panel2, label='')
            favoriteCb.SetValue(self.netProps[i][len(self.netProps[0])-1])
            favoriteCb.Bind(wx.EVT_CHECKBOX, self.OnFavoriteCb)
            self.favoriteCbList.append(favoriteCb)
            self.onerowfields.append(favoriteCb)

            self.fields.append(self.onerowfields) # append to self.fields

            # Create a new directory entry
            k = (self.netwSorted[i-1][NET_SSID],self.netwSorted[i-1][NET_BSSID]) # -1 for header
            self.btnDir[k] = btn 

#        self.panel2.Refresh()

        if self.netkey:
            try:
                btn = self.btnDir[self.netkey]
                btn.SetValue(True)
                self.panel2.ScrollChildIntoView(btn)
            except:
                print('OnTimer(): Network has disapeared:',self.net)
                self.net = None
        else:
            k = (iface.ssid(),iface.bssid())
            try:
                btn = self.btnDir[k]
                print('1',btn.GetLabel())
                btn.SetValue(True)
                self.panel2.ScrollChildIntoView(btn)
            except:
                pass

        # Add all widgets in the grid
        self.gsNet.SetRows(rows)
        for r in range(rows):
            onerowfields = self.fields[r]
            for w in onerowfields:
                self.gsNet.Add(w, proportion=0, flag=wx.EXPAND)

        self.panel2.SetAutoLayout(1)
        self.panel2.SetupScrolling()

####
class PkgColorLED(wx.Control):
    """
    Creates a mono color LED widget. The color is controlled by SetState()/GetState() methods
    """

    global __tmpDir__
    global fileColors

    def __init__(self, parent, id=-1, style=wx.NO_BORDER):
        size = (17, 17)
        wx.Control.__init__(self, parent, id, size, (-1,-1), style)
        self.MinSize = size
        self._state = -1
        self.SetState(0)
        self.Bind(wx.EVT_PAINT, self.OnPaint, self)
        
    def SetState(self, i):
        self._state = i

        ascii_led_header = (
            '/* XPM */\n',
            'static char * led_xpm[] = {\n',
            '"17 17 3 1",\n',
            '"0 c None", \n',
            '"* c #FFFFFF",\n')
#            '"X c #00FF00",\n',
        ascii_led_footer = (
            '"000000XXXXX000000",\n',
            '"0000XXXXXXXXX0000",\n',
            '"000XXXXXXXXXXX000",\n',
            '"00XXXXXXXXXXXXX00",\n',
            '"0XXXXXX**XXXXXXX0",\n',
            '"0XXXX***XXXXXXXX0",\n',
            '"XXXXX**XXXXXXXXXX",\n',
            '"XXXX**XXXXXXXXXXX",\n',
            '"XXXXXXXXXXXXXXXXX",\n',
            '"XXXXXXXXXXXXXXXXX",\n',
            '"XXXXXXXXXXXXXXXXX",\n',
            '"0XXXXXXXXXXXXXXX0",\n',
            '"0XXXXXXXXXXXXXXX0",\n',
            '"00XXXXXXXXXXXXX00",\n',
            '"000XXXXXXXXXXX000",\n',
            '"0000XXXXXXXXX0000",\n',
            '"000000XXXXX000000"};\n')

        colour = str(fileColors[i][0].GetAsString(flags=wx.C2S_HTML_SYNTAX))

        # Create an XPM file with desired color
        xpmFilePath = os.path.join(__tmpDir__, 'led_%s.xpm' % colour)
        if not os.path.exists(xpmFilePath):
            f = open(xpmFilePath, 'w')
            for l in ascii_led_header:
                f.write(l)
            f.write('"X c %s",\n' % colour)  # '"X c #00FF00",\n',
            for l in ascii_led_footer:
                f.write(l)
            f.close()

        self.bmp = wx.Bitmap(xpmFilePath, type=wx.BITMAP_TYPE_XPM)
        self.Refresh()
        
    def GetState(self):
        return self._state
    
    State = property(GetState, SetState)
    
    def OnPaint(self, e):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0, True)

class LED(wx.Control):
    """
    Creates a LED widget. State is controlled by SetState()/GetState() methods
    """

    global LEDS_COLOURS

    def __init__(self, parent, id=-1, style=wx.NO_BORDER):
        size = (17, 17)
        wx.Control.__init__(self, parent, id, size, (-1,-1), style)
        self.MinSize = size
        self._state = -1
        self.SetState(0)
        self.Bind(wx.EVT_PAINT, self.OnPaint, self)
        
    def SetState(self, i):
        self._state = i
        
#        ascii_led = '''
#        000000-----000000      
#        0000---------0000
#        000-----------000
#        00-----XXX----=00
#        0----XX**XXX-===0
#        0---X***XXXXX===0
#        ----X**XXXXXX====
#        ---X**XXXXXXXX===
#        ---XXXXXXXXXXX===
#        ---XXXXXXXXXXX===
#        ----XXXXXXXXX====
#        0---XXXXXXXXX===0
#        0---=XXXXXXX====0
#        00=====XXX=====00
#        000===========000
#        0000=========0000
#        000000=====000000
#        '''.strip()
#        
#        xpm = ['17 17 5 1', # width height ncolors chars_per_pixel
#               '0 c None', 
#               'X c %s' % LEDS_COLOURS[i][0],
#               '- c %s' % LEDS_COLOURS[i][1],
#               '= c %s' % LEDS_COLOURS[i][2],
#               '* c %s' % LEDS_COLOURS[i][3]]
#        
#        xpm += [s.strip() for s in ascii_led.splitlines()]
##        self.bmp = wx.BitmapFromXPMData(xpm)
#        self.bmp = wx.Bitmap('exemple.xpm', type=wx.BITMAP_TYPE_ANY)
#        self.Refresh()

        ascii_led_header = (
            '/* XPM */\n',
            'static char * led_xpm[] = {\n',
            '"17 17 3 1",\n',
            '"0 c None", \n',
            '"* c #FFFFFF",\n')
#            '"X c #00FF00",\n',
        ascii_led_footer = (
            '"000000XXXXX000000",\n',
            '"0000XXXXXXXXX0000",\n',
            '"000XXXXXXXXXXX000",\n',
            '"00XXXXXXXXXXXXX00",\n',
            '"0XXXXXX**XXXXXXX0",\n',
            '"0XXXX***XXXXXXXX0",\n',
            '"XXXXX**XXXXXXXXXX",\n',
            '"XXXX**XXXXXXXXXXX",\n',
            '"XXXXXXXXXXXXXXXXX",\n',
            '"XXXXXXXXXXXXXXXXX",\n',
            '"XXXXXXXXXXXXXXXXX",\n',
            '"0XXXXXXXXXXXXXXX0",\n',
            '"0XXXXXXXXXXXXXXX0",\n',
            '"00XXXXXXXXXXXXX00",\n',
            '"000XXXXXXXXXXX000",\n',
            '"0000XXXXXXXXX0000",\n',
            '"000000XXXXX000000"};\n')

#        colour = str(fileColors[i][0].GetAsString(flags=wx.C2S_HTML_SYNTAX))
#        colour = LEDS_COLOURS[i][0].GetAsString(flags=wx.C2S_HTML_SYNTAX)
        colour = LEDS_COLOURS[i][0]
        xpmFilePath = os.path.join(__tmpDir__, 'led_%s.xpm' % colour)
        if not os.path.exists(xpmFilePath):
        # Create an XPM file with desired color
            f = open(xpmFilePath, 'w')
            for l in ascii_led_header:
                f.write(l)
            f.write('"X c %s",\n' % colour)  # '"X c #00FF00",\n',
            for l in ascii_led_footer:
                f.write(l)
            f.close()

        self.bmp = wx.Bitmap(xpmFilePath, type=wx.BITMAP_TYPE_XPM)
        self.Refresh()
        
    def GetState(self):
        return self._state
    
    State = property(GetState, SetState)
    
    def OnPaint(self, e):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0, True)
        
#### HelpDialog
defHelpText = """<p>Sorry, the Help file cannot be found on your system. Please check your installation for file <b>help.htm</b>"""

class HtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id, size=(600,400)):
        wx.html.HtmlWindow.__init__(self, parent, id, size=size)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()

    def OnLinkClicked(self, link):
        wx.LaunchDefaultBrowser(link.GetHref())

class HelpDialog(wx.Dialog):
    global __helpPath__

    def __init__(self):
        myStyle = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
        wx.Dialog.__init__(self, None, wx.ID_ANY, "Help on %s" % (_myLongName_), style=myStyle)

        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self,
                               size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        # Create a HTML window
        self.hwin = HtmlWindow(parent=self.panel1, id=wx.ID_ANY, size=(800,600))

        # Open the file containing the HTML info
        try:
            f = open(__helpPath__, 'r', encoding="ISO-8859-1")
        except IOError as e:
            msg = "HelpDialog(): I/O error %s %s" % ("({0}): {1}".format(e.errno, e.strerror), __helpPath__)
            print (msg)
            helpText = defHelpText
        else:
            helpText = f.read()
            f.close()

        # Display the HTML page
        self.hwin.SetPage(helpText)

        # Button to close the Help dialog
        self.btnClose = wx.Button(label='Close', id=wx.ID_CLOSE, parent=self.panel1, style=0)
        self.btnClose.Bind(wx.EVT_BUTTON, self.OnBtnClose)
        
        # Everything in a BoxSizer
        self.topBoxSizer = wx.BoxSizer(orient=wx.VERTICAL) 
        self.topBoxSizer.Add(self.hwin, 0, border=0, flag=0)
        self.topBoxSizer.Add(4, 4, 0, border=0, flag=0)
        self.topBoxSizer.Add(self.btnClose, 0, border=0, flag=wx.ALL | wx.EXPAND)
        
        self.panel1.SetSizerAndFit(self.topBoxSizer)
        self.SetClientSize(self.topBoxSizer.GetSize())
        self.Centre()
        self.SetFocus()

    def OnBtnClose(self, event):
        self.Close()
        event.Skip()

####
class InstallThread(threading.Thread):

    def __init__(self, name, dialog, thrLock, queueLock, workQueue):

        threading.Thread.__init__(self)

        self._name = name
        self._pDialog = dialog
        self._thrLock = thrLock
        self._queueLock = queueLock
        self._workQueue = workQueue
        self._stopper = threading.Event()

        print('%s: Started' % self._name)

    def stopIt(self):
        print('%s: Stopping' % self._name)
        self._stopper.set()
        print('%s: isStopped(): %s' % (self._name, self.isStopped()))

    def isStopped(self):
        return self._stopper.isSet()

    def getId(self): 
        # returns id of the respective thread 
        if hasattr(self, '_thread_id'): 
            return self._thread_id 
        for id, thread in threading._active.items(): 
            if thread is self: 
                return id

    # Raise an exception to unblock a working thread
    def raiseException(self): 
        thread_id = self.getId() 
        print('%s: id=%d Raising exception' % (self._name,thread_id))
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 
                                                         ctypes.py_object(SystemExit)) 
        if res > 1: 
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0) 
            print('Exception raise failure') 

    def run(self):
        print('%s: Running' % self._name)

        while True:
            print("%s: Queue size: %d isStopped: %s" % (self._name, self._workQueue.qsize(), self.isStopped()))
            if self.isStopped():
                print('%s: Thread is stopped, Exiting' % self._name)
                return

            self._queueLock.acquire()
            if self._workQueue.empty():
                self._queueLock.release()
                print('%s: Queue is now empty, Exiting' % self._name)
                return

            op = self._workQueue.get()
            self._queueLock.release()

            self.fileName   = op[OP_FILENAME]
            self.localFile  = op[OP_FILEPATH]
            self.remoteFile = op[OP_REMURL]
            self.remSize    = op[OP_SIZE][0]
            self.remBlocks  = op[OP_SIZE][1]
            self.fileSize   = availRemoteFiles[self.fileName][F_SIZE]

            # Update subpanel to use for this operation
            wx.CallAfter(self._pDialog.nextInstallSubPanel, op)
            
            print('%s: Processing file %s: (%sB, %d bytes %d blocks)' % (self._name, self.fileName, self.fileSize, self.remSize, self.remBlocks))

            # Store thread in current operation
            op[OP_INTH] = self

            # step 0. Download file from camera
            wx.CallAfter(self._pDialog.startStep, op, 0, self._workQueue.qsize())
            (ret, msg) = downloadFile(op, self._pDialog)
            print('%s: downloadFile() ret=%d msg=%s' % (self._name, ret, msg))
            if ret < 0:
                if ret != -2:
                    wx.CallAfter(self._pDialog.installError, 1, msg, op)
                    time.sleep(1) # some time for the GUI to refresh
                op[OP_INTH] = None # Done with this op
                self._workQueue.task_done()
                continue
            # End of transfer. Update total counter
            wx.CallAfter(self._pDialog.endStep, op, 0)
            time.sleep(1) # some time for the GUI to refresh

            op[OP_INTH] = None # Done with this op
            self._workQueue.task_done()

####
class MainInstallThread(threading.Thread):
    global maxDownload
    global localFileInfos
    global osvmDownloadDir

    def __init__(self, parent, name, thrLock):
        threading.Thread.__init__(self)
        self._parent = parent
        self._name = name
        self._thrLock = thrLock

        self._threads = list()        # List of threads
        self._queueLock = threading.Lock()
        self._workQueue = queue.Queue(MAX_OPERATIONS)
        self._stopper = threading.Event()

        self._downloadDir = osvmDownloadDir

        print ('%s: Started' % self._name)

    def stopIt(self):
        print('%s: Stopping children threads' % self._name)
        for thr in self._threads:
            if thr.isAlive():
                print('%s: Stopping thread: %s' % (self._name, thr.name))
                thr.stopIt()
                thr.raiseException()
                thr.join()

#        self._stopper.set()
#        print('%s: isStopped() : %s' % (self._name, self.isStopped()))

    def isStopped(self):
        return self._stopper.isSet()

    def run(self):
        print('%s: Running, Waiting for Lock' % self._name)
        self._thrLock.acquire() # will block until the 'InstallDialog' starts
        print('%s: Lock acquired' % self._name)

        # Clear list of threads
        self._threads = list()

        # Fill the queue with pending operations
        for op in self._parent.opList:
            if op[OP_STATUS] and op[OP_TYPE] != FILE_DELETE:
                self._workQueue.put(op)

        print('%s: workQueue size: %d, maxDownload: %d' % (self._name, self._workQueue.qsize(),maxDownload))

        # Exit if nothing to do
        if not self._workQueue.qsize():
            wx.CallAfter(self._parent.finish, '')
            self._thrLock.release()
            return
            #continue

        # Create new install threads
        for i in range(maxDownload):
            tName = 'th-%d' % i
            thr = InstallThread(tName, self._parent, self._thrLock, self._queueLock, self._workQueue)
            # Start the new thread in background
            thr.setDaemon(True)
            print('%s: Starting thread %s' % (self._name, tName))
            thr.start()
            # Add the thread to the thread list
            self._threads.append(thr)

        # Wait for all threads to complete
        print('%s:' % self._name, self._threads)
        for t in self._threads:
            if t.is_alive():
                t.join()

        print('%s: All threads have finished' % self._name)

        # All Threads are exited. 
        print("%s: Updating localFileInfos" % (self._name))
        localFilesCnt = localFilesInfo(osvmDownloadDir)
        print("%s: %d files on local host" % (self._name, localFilesCnt))
 
        # Dialog cleanup if possible
        try:
            wx.CallAfter(self._parent.finish, '')
        except:
            pass

        # All Threads are exited. 
        print('%s: Exiting' % self._name)

### 
class SlideShowThread(threading.Thread):
    def __init__(self, parent, name, threadLock):
        threading.Thread.__init__(self)
        self._parent = parent
        self._name = name
        self._threadLock = threadLock

        print('%s: Started' % self._name)

    def stopIt(self):
        print('%s: Stopping' % self._name)
        self._stopper.set()
        print('%s: isStopped() : %s' % (self._name, self.isStopped()))

    def isStopped(self):
        return self._stopper.isSet()

    def run(self):
        global castMediaCtrl
        global ssDelay
        global slideShowNextIdx
        global slideShowLastIdx
        global serverAddr
        global SERVER_HTTP_PORT

        print('%s: Running. Server: %s:%s' % (self._name, serverAddr, SERVER_HTTP_PORT))

        while True:
            self._threadLock.acquire() # will block until 'Start slideshow' button is pressed 
#            self._stopper.clear() # Thread is running
            f = self._parent.mediaFileList[slideShowNextIdx % slideShowLastIdx]
            fileURL = 'http://%s:%s/%s' % (serverAddr, SERVER_HTTP_PORT, f[F_NAME])
            print('%s: idx %d/%d Loading URL: %s' % (self._name, slideShowNextIdx,slideShowLastIdx, fileURL))
            mediaFileType = { 'JPG':'image/jpg', 'MOV':'video/mov' }
            suffix = f[F_NAME].split('.')[1]
            castMediaCtrl.play_media(fileURL, mediaFileType[suffix])
            if suffix == 'MOV':
                idleCnt = 0
                while True:
                    if castMediaCtrl.status.player_state == 'IDLE':
                        idleCnt += 1
                        print('IDLE',idleCnt)
                        if idleCnt > 2:	# Assume end of video
                            break
                    time.sleep(1)
            else:
                castMediaCtrl.block_until_active()

            self._threadLock.release()
            time.sleep(int(ssDelay))
            slideShowNextIdx = (slideShowNextIdx + 1) % slideShowLastIdx


### class MediaViewer
class MediaViewer(wx.Dialog):
    def __init__(self, mediaFileListOrPath):
        global vlcVideoViewer

        wx.Dialog.__init__(self, None, wx.ID_ANY, title="Media Viewer")

        self.mediaFileListOrPath = mediaFileListOrPath
        self.singleFile = False

        if type(self.mediaFileListOrPath).__name__ == 'str':
            fileName = os.path.basename(self.mediaFileListOrPath)
            self.singleFile = True
        else:
            fileName = self.mediaFileListOrPath[0][F_NAME]
        suffix = fileName.split('.')[1]

        if suffix == 'JPG' or suffix == 'jpg':
            self.imageViewer()
        else:
            if vlcVideoViewer:
                self.videoViewer()
            else:
                self.Destroy()#???????
                return

        self.panel1.SetSizerAndFit(self.mainSizer)
        self.SetClientSize(self.mainSizer.GetSize())
        self.Centre()

        # Simulate a 'Play' event
        self._btnPlayInfo = getattr(self, "btnPlay")
        evt = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self._btnPlayInfo.GetId())
        evt.SetEventObject(self.btnPlay)
        wx.PostEvent(self.btnPlay, evt)

    ######### Image Viewer ##########
    def imageViewer(self):
        print('Launching imageViewer')
        self.imageFileListOrPath = self.mediaFileListOrPath

        width, height = wx.DisplaySize()
        self.btn = list()
        self.photoMaxSize = height - 200

        self.slideTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._imageNext, self.slideTimer)

        self.gaugeTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._gaugeTimerHandler, self.gaugeTimer)

        self.SetTitle("Image Viewer")

        self._imageInitialize()

        if type(self.imageFileListOrPath).__name__ == 'list': # List of files
            self.listToUse = self.imageFileListOrPath	# Set list to use
            self.imgDirName = osvmDownloadDir
            self.imgIdx = 0
            # Load first image manually
            self.imgFilePath = os.path.join(self.imgDirName, self.listToUse[0][F_NAME])
            self._imageLoad(self.imgFilePath)
        else: # Single file
            # Directory containing the images
            self.imgDirName = os.path.dirname(self.imageFileListOrPath)
            # Get image index in localFilesSorted
            self.imgIdx = [x[0] for x in localFilesSorted].index(os.path.basename(self.imageFileListOrPath))
            self.listToUse = [localFilesSorted[self.imgIdx]]            # Set list to use
            self._imageLoad(self.imageFileListOrPath)
        
    def _imageInitialize(self):
        """
        Layout the widgets on the panel
        """
        global ssDelay

        self.gaugeRange = int(ssDelay) * 1000 # in milli
        self.gaugeRemaining = self.gaugeRange # in milli

        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self, size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        self.mainSizer      = wx.BoxSizer(wx.VERTICAL)
        self.btnSizer       = wx.BoxSizer(wx.HORIZONTAL)
        self.bottomBtnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.quitBoxSizer   = wx.BoxSizer(wx.HORIZONTAL)

        img = wx.Image(self.photoMaxSize,self.photoMaxSize)
        self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(img))

        self.mainSizer.Add(self.imageCtrl, 0, wx.ALL|wx.CENTER, 5)

        self.btnPrev = wx.Button(label='Prev', parent=self, style=0)
        self.btnPrev.SetToolTip('Load previous Image')
        self.btnPrev.Bind(wx.EVT_BUTTON, self.imageOnBtnPrev)

        self.btnPlay = wx.Button(label='Play', parent=self, style=0)
        self.btnPlay.SetToolTip('Start the Slideshow')
        self.btnPlay.Bind(wx.EVT_BUTTON, self.imageOnBtnPlay)

        self.btnNext = wx.Button(label='Next', parent=self, style=0)
        self.btnNext.SetToolTip('Load Next Image')
        self.btnNext.Bind(wx.EVT_BUTTON, self.imageOnBtnNext)

        if self.singleFile:
            for b in [self.btnPrev,self.btnPlay,self.btnNext]:
                b.Disable()

        self.ssDelayGauge = wx.Gauge(range=self.gaugeRange, parent=self, size=(200,15))
        self.ssDelayGauge.SetValue(self.gaugeRange)

        self.btnQuit = wx.Button(id=wx.ID_EXIT, label='Quit', parent=self, style=0)
        self.btnQuit.SetToolTip('Quit Viewer')
        self.btnQuit.Bind(wx.EVT_BUTTON, self.imageOnBtnQuit)

        self.btnSizer.Add(self.btnPrev, 0, border=10, flag=wx.EXPAND| wx.ALL)
        self.btnSizer.Add(self.btnPlay, 0, border=10, flag=wx.EXPAND| wx.ALL)
        self.btnSizer.Add(self.btnNext, 0, border=10, flag=wx.EXPAND| wx.ALL)
        self.btnSizer.AddStretchSpacer(prop=1)
        self.btnSizer.Add(self.ssDelayGauge, 0, border=10, flag=wx.EXPAND| wx.ALL)

        self.quitBoxSizer.Add(self.btnQuit, 0, border=10, flag=wx.EXPAND| wx.ALL)

        self.bottomBtnSizer.AddStretchSpacer(prop=1)
        self.bottomBtnSizer.Add(self.btnSizer, 0, flag=wx.EXPAND| wx.ALL)
        self.bottomBtnSizer.AddStretchSpacer(prop=1)
        self.bottomBtnSizer.Add(self.quitBoxSizer, 0, flag=wx.ALIGN_RIGHT)

        self.mainSizer.Add(self.bottomBtnSizer, 0, flag=wx.EXPAND| wx.ALL)

    def _imageLoad(self, image):
        imageFileName = os.path.basename(image)
        wximg = wx.Image(image, wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        W = wximg.GetWidth()
        H = wximg.GetHeight()
        if W > H:
            r = W / H
#            NewW = self.photoMaxSize
#            NewH = self.photoMaxSize * H / W
            NewW = self.photoMaxSize * r
            NewH = self.photoMaxSize
        else:
            r = H / W
#            NewH = self.photoMaxSize
#            NewW = self.photoMaxSize * W / H
            NewH = self.photoMaxSize
            NewW = self.photoMaxSize * r
        wximg = wximg.Scale(NewW,NewH)

        self.imageCtrl.SetBitmap(wx.Bitmap(wximg))
        self.SetTitle(imageFileName)
        self.Refresh()
        
    def imageOnBtnNext(self, event):
        self.imgIdx = (self.imgIdx + 1) % len(self.listToUse)
        self.imgFilePath = os.path.join(self.imgDirName, self.listToUse[self.imgIdx][F_NAME])

        # Skip over non JPG files
        suffix = self.imgFilePath.rsplit('.')[-1:][0]
        while suffix != 'JPG' and suffix != 'jpg':
            print('Skipping over',self.imgFilePath)
            self.imgIdx = (self.imgIdx + 1) % len(self.listToUse)
            self.imgFilePath = os.path.join(self.imgDirName, self.listToUse[self.imgIdx][F_NAME])
            suffix = self.imgFilePath.rsplit('.')[-1:][0]

        self._imageLoad(self.imgFilePath)
        
    def imageOnBtnPrev(self, event):
        self.imgIdx = self.imgIdx - 1
        if self.imgIdx < 0:
            self.imgIdx = len(self.listToUse) - 1
        self.imgFilePath = os.path.join(self.imgDirName, self.listToUse[self.imgIdx][F_NAME])
        self._imageLoad(self.imgFilePath)
        
    def _imageNext(self, event):
        """
        Called when the slideTimer's timer event fires. Loads the next picture
        """
        self._btnNextInfo = getattr(self, 'btnNext')
        evt = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self._btnNextInfo.GetId())
        evt.SetEventObject(self.btnNext)
        wx.PostEvent(self.btnNext, evt)
        # Reset the gauge
        self.ssDelayGauge.SetValue(self.gaugeRange)
        self.gaugeRemaining = self.gaugeRange

    def _gaugeTimerHandler(self, event):
        self.gaugeRemaining -= TIMER5_FREQ # milli
        self.ssDelayGauge.SetValue(self.gaugeRemaining)
        
    def imageOnBtnPlay(self, event):
        global ssDelay

        if len(self.listToUse) == 1: # Single file, nothing to do
            return

        # Starts and stops the slideshow
        button = event.GetEventObject()
        label = button.GetLabel()
        if label == 'Play':
            self.slideTimer.Start(int(ssDelay) * 1000)
            self.gaugeTimer.Start(TIMER5_FREQ)
            button.SetLabel('Stop')
        else:
            self.slideTimer.Stop()
            self.gaugeTimer.Stop()
            button.SetLabel('Play')
       
    def imageOnBtnQuit(self, event):
        self.Destroy()
        self.EndModal(wx.ID_OK)

    ######### Video Viewer ##########
    def videoViewer(self):
        global osvmDownloadDir

        print('Launching videoViewer')
        self.videoFileListOrPath = self.mediaFileListOrPath
        self.videoDirName = osvmDownloadDir

        if type(self.videoFileListOrPath).__name__ == 'list': # List of files
            self.listToUse = self.videoFileListOrPath	# Set list to use
        else: # single file
            self.listToUse = [[self.videoFileListOrPath]] # List of list

        # create the timer, which updates the timeslider
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.videoOnTimer, self.timer)

        # VLC player controls
        self.vlcInstance = vlc.Instance()
        self.mediaIsFinished = False

        self._videoInitialize()

    def _videoSetWindow(self, player):
        # set the window id where to render VLC's video output
        handle = self.imageCtrl.GetHandle()
        if sys.platform.startswith('linux'): # for Linux using the X Server
            player.set_xwindow(handle)
        elif sys.platform == "win32": # for Windows
            player.set_hwnd(handle)
        elif sys.platform == "darwin": # for MacOS
            player.set_nsobject(handle)

    def _videoInitialize(self):
        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self, size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        self.mainSizer       = wx.BoxSizer(wx.VERTICAL)
        self.timeSliderSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btnSizer        = wx.BoxSizer(wx.HORIZONTAL)
        self.quitBoxSizer    = wx.BoxSizer(wx.HORIZONTAL)

        img = wx.Image(800,500)
        self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(img))
        self.imageCtrl.SetBackgroundColour(wx.BLACK)

        self.timeSlider = wx.Slider(self, -1, 0, 0, 1000)
        self.timeSlider.SetRange(0, 1000)
        self.Bind(wx.EVT_SLIDER, self.videoOnTimeSlider, self.timeSlider)

        self.timeElapsed = wx.StaticText(self, label='00:00:00')

        self.btnRew = wx.Button(self, label='Rew')
        self.Bind(wx.EVT_BUTTON, self.videoOnBtnRew, self.btnRew)

        self.btnPlay = wx.Button(self, label='Play')
        self.Bind(wx.EVT_BUTTON, self.videoOnBtnPlay, self.btnPlay)

        self.btnVolume = wx.Button(self, label='Mute')
        self.Bind(wx.EVT_BUTTON, self.videoOnBtnVolume, self.btnVolume)

        self.volSlider = wx.Slider(self, -1, 0, 0, 100)
        self.Bind(wx.EVT_SLIDER, self.videoOnVolSlider, self.volSlider)

        self.btnQuit = wx.Button(self, id=wx.ID_EXIT, label='Quit')
        self.btnQuit.SetToolTip('Quit Viewer')
        self.btnQuit.Bind(wx.EVT_BUTTON, self.videoOnBtnQuit)
        self.quitBoxSizer.Add(self.btnQuit, 0, border=5, flag=wx.EXPAND| wx.ALL)

        self.timeSliderSizer.AddStretchSpacer(prop=1)
        self.timeSliderSizer.Add(self.timeElapsed)
        self.timeSliderSizer.Add(8, 0)
        self.timeSliderSizer.Add(self.timeSlider, 4)
        self.timeSliderSizer.AddStretchSpacer(prop=1)

        self.btnSizer.Add(self.btnRew, 0, border=5, flag=wx.EXPAND| wx.ALL)
        self.btnSizer.Add(self.btnPlay, 0, border=5, flag=wx.EXPAND| wx.ALL)
        self.btnSizer.AddStretchSpacer(prop=1)
        self.btnSizer.Add(self.btnVolume, 0, border=5, flag=wx.EXPAND| wx.ALL)
        self.btnSizer.Add(self.volSlider, flag=wx.TOP | wx.LEFT, border=5)
        self.btnSizer.AddStretchSpacer(prop=2)
        self.btnSizer.Add(self.quitBoxSizer, 0, flag=wx.ALIGN_RIGHT)

        # Put everything together
        self.mainSizer.Add(self.imageCtrl, 0, wx.ALL|wx.CENTER, border=5)
        self.mainSizer.Add(self.timeSliderSizer, flag=wx.EXPAND, border=0)
        self.mainSizer.Add(self.btnSizer, 1, flag=wx.EXPAND)

    def videoOnBtnPlay(self, event):
        button = event.GetEventObject()

        for e in self.listToUse: # each entry is a list containing filename as first field
            v = os.path.join(self.videoDirName, e[F_NAME])
            print('videoOnBtnPlay(): Playing %s' % v)
            self.mediaIsFinished = False

            # Create a VLC Player instance
            self.vlcPlayer = self.vlcInstance.media_player_new()
            self._videoSetWindow(self.vlcPlayer)
            # Create a VLC Player Event Manager instance
            self.vlcEvents = self.vlcPlayer.event_manager()
            self.vlcEvents.event_attach(vlc.EventType.MediaPlayerEndReached, self._videoMediaFinished)
            self.vlcEvents.event_attach(vlc.EventType.MediaPlayerStopped, self._videoPlayerStopped)

            # Create a VLC Media instance
            media = self.vlcInstance.media_new(v)
            self.vlcPlayer.set_media(media)

            title = self.vlcPlayer.get_title()
            # if an error was encountred while retrieving the title, 
            # then use the filename
            if title == -1:
                title = os.path.basename(v)
            self.SetTitle(title)

            # Try to launch the media, if this fails display an error message
            if self.vlcPlayer.play() == -1:
                dlg = wx.MessageDialog(self, 'Unable to play', 'Error', wx.OK|wx.ICON_ERROR)
                dlg.ShowModal()
            else:
                self.playerIsStopped = False
                self.timer.Start(TIMER2_FREQ)
                while not self.mediaIsFinished:
                    wx.Yield() 

        print('videoOnBtnPlay(): End of list')
        self.EndModal(wx.ID_OK)
#        event.Skip()

    def videoOnBtnRew(self, event):
        """Stop the player."""
        self.vlcPlayer.stop()
        # reset the time slider
        self.timeSlider.SetValue(0)
        self.timer.Stop()

    def videoOnTimer(self, event):
        # since the self.player.get_length can change while playing,
        # re-set the timeslider to the correct range.
        self.timeSlider.SetRange(-1, self.vlcPlayer.get_length())

        if self.playerIsStopped:
            self.timer.Stop()
            return

        # update the time on the slider
        if not self.mediaIsFinished:
            self.elapsed = self.vlcPlayer.get_time()
            sec =  self.elapsed / 1000
            m, s = divmod(sec, 60)
            h, m = divmod(m, 60)
            print('%02d:%02d\r' % (m,s), end='', flush=True)
            self.timeSlider.SetValue(self.elapsed)
            self.timeElapsed.SetLabel('%02d:%02d:%02d' % (h,m,s))
        else:
            self.timer.Stop()
        event.Skip()

    def videoOnBtnVolume(self, event):
        """Mute/Unmute according to the audio button."""
        button = event.GetEventObject()

        # update the volume slider;
        # since vlc volume range is in [0, 200],
        # and our volume slider has range [0, 100], just divide by 2.
        if button.GetName() == 'btnMute':
            button.SetName('btnVolume') 
            button.SetLabel('Volume')
            self.oVolume = self.vlcPlayer.audio_get_volume()
            self.oVolSlider = self.volSlider.GetValue()
            self.vlcPlayer.audio_set_volume(0)
            self.volSlider.SetValue(0)
            print('0:',self.oVolume,self.oVolSlider)
        else:
            button.SetName('btnMute') 
            button.SetLabel('Mute')
            self.vlcPlayer.audio_set_volume(self.oVolume)
            self.volSlider.SetValue(self.oVolSlider)
            print('1:',self.oVolume,self.oVolSlider)

    def videoOnTimeSlider(self, event):
        """Set the time according to the time sider."""
        timeSliderVal = self.timeSlider.GetValue()
        len = self.vlcPlayer.get_length()
        self.timeSlider.SetValue(timeSliderVal)
        self.vlcPlayer.set_time(timeSliderVal)
        event.Skip()

    def videoOnVolSlider(self, event):
        """Set the volume according to the volume sider."""
        volume = self.volSlider.GetValue() * 2
        if self.vlcPlayer.audio_set_volume(volume) == -1:
            dlg = wx.MessageDialog(self, 'Failed to set volume', 'Error', wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
        if volume > 0:
            self.btnVolume.SetName('btnMute') 
            self.btnVolume.SetLabel('Mute')

    def videoOnBtnQuit(self, event):
        if self.vlcPlayer.is_playing():
            print('Stopping VLC')
            self.vlcPlayer.stop()
            self.vlcPlayer.release()
            self.vlcInstance.release()
            print('VLC Released')
            self.mediaIsFinished = True
        else:
            self._videoPlayerStopped(True)

    def _videoPlayerStopped(self, evt):
        print('_videoPlayerStopped(): Player stopped')
        self.playerIsStopped = True

    def _videoMediaFinished(self, evt):
        print('_videoMediaFinished(): End of Media reached')
        time.sleep(2)
        self.mediaIsFinished = True
        self.vlcPlayer.release()


#### class Preferences
class Preferences():
    
    def __init__(self, parent):
        self.parent = parent
        #self._loadPreferences()

    def _loadPreferences(self):
        newInitFile1 = self._loadInitFile()
        newInitFile2 = self._parseInitFile()
        if newInitFile1 or newInitFile2:
            dlg = PreferencesDialog(self)
            dlg.ShowModal()
            dlg.Destroy()
            printGlobals()

    def _savePreferences(self):
        self._saveInitFile()

    # Return a dictionary (if exists) for the given section in the ConfigParser object
    def _initFileSectionGet(self, config, section):
        dict1 = {}
        try:
            options = config.options(section)
        except:
                print("exception on option: %s" % options)
                return dict1
        for opt in options:
            try:
                dict1[opt] = config.get(section, opt)
                if dict1[opt] == -1:
                    print("skip: %s" % opt)
            except:
                print("_initFileSectionGet(): Got exception: %s" % opt)
                dict1[opt] = None
        return dict1

    def _loadInitFile(self):
        global __initFilePath__

        print("Loading preference file:", __initFilePath__)
        self.config = configparser.ConfigParser()
        cf = self.config.read(__initFilePath__)
        if self.config.sections() == []:
            # Create a new Init file, return TRUE
            self._createDefaultInitFile()
            cf = self.config.read([__initFilePath__])
            return True
        return False

    def _createDefaultInitFile(self):
        global DEFAULT_FILE_COLORS
        global _iniFileVersion_
        global __initFilePath__
        global _osvmDir_
        global _initFileBk_

        print("_createDefaultInitFile(): Warning: Cannot read preference file, Creating default:", __initFilePath__)

        if os.path.exists(__initFilePath__):
            initFilePathBk = os.path.join(os.path.join(expanduser("~"), _osvmDir_, _initFileBk_))
            print('Saving old/existing confile file to %s' % (initFilePathBk))
            shutil.copy2(__initFilePath__, initFilePathBk)
                                         
        # add the default settings to the file
        self.config['Version'] = {INI_VERSION: _iniFileVersion_}

        self.config['Preferences'] = {}
        self.config['Preferences'][COMPACT_MODE]           = str(DEFAULT_COMPACT_MODE)
        self.config['Preferences'][ASK_BEFORE_COMMIT]      = str(DEFAULT_ASK_BEFORE_COMMIT)
        self.config['Preferences'][ASK_BEFORE_EXIT]        = str(DEFAULT_ASK_BEFORE_EXIT)
        self.config['Preferences'][SAVE_PREFS_ON_EXIT]     = str(DEFAULT_SAVE_PREFERENCES_ON_EXIT)
        self.config['Preferences'][OVERWRITE_LOCAL_FILES]  = str(DEFAULT_OVERWRITE_LOCAL_FILES)
        self.config['Preferences'][AUTO_SWITCH_TO_CAMERA_NETWORK] = str(AUTO_SWITCH_TO_CAMERA_NETWORK)
        self.config['Preferences'][THUMB_GRID_COLUMNS]     = str(DEFAULT_THUMB_GRID_NUM_COLS)
        self.config['Preferences'][THUMB_SCALE_FACTOR]     = str(DEFAULT_THUMB_SCALE_FACTOR)
        self.config['Preferences'][OSVM_DOWNLOAD_DIR]      = DEFAULT_OSVM_DOWNLOAD_DIR
        self.config['Preferences'][SORT_ORDER]             = str(DEFAULT_SORT_ORDER)

        self.config['Sync Mode Preferences'] = {}
        self.config['Sync Mode Preferences'][REM_BASE_DIR]           = DEFAULT_OSVM_REM_BASE_DIR
        self.config['Sync Mode Preferences'][OSVM_FILES_DOWNLOAD_URL] = DEFAULT_OSVM_ROOT_URL
        self.config['Sync Mode Preferences'][MAX_DOWNLOAD]           = str(DEFAULT_MAX_DOWNLOAD)

        self.config['View Mode Preferences'] = {}
        self.config['View Mode Preferences'][SS_DELAY]     = str(DEFAULT_SLIDESHOW_DELAY)
        self.config['View Mode Preferences'][LAST_CAST_DEVICE_NAME] = ''
        self.config['View Mode Preferences'][LAST_CAST_DEVICE_UUID] = ''

        self.config['Networks'] = {}
        self.config['Networks'][FAVORITE_NETWORK] = None,None

        self.config['Colors'] = {}
        for i in range(len(DEFAULT_FILE_COLORS)):
            self.config['Colors']['color_%d' % (i)] = str(DEFAULT_FILE_COLORS[i][0].GetRGB())

        # Writing our configuration file back to initFile
        with open(__initFilePath__, 'w') as cfgFile:
            self.config.write(cfgFile)

        cfgFile.close()

    def _parseInitFile(self):
        global osvmDownloadDir
        global osvmFilesDownloadUrl
        global cameraConnected
        global compactMode
        global askBeforeCommit
        global askBeforeExit
        global overwriteLocalFiles
        global savePreferencesOnExit
        global thumbnailGridColumns
        global thumbnailScaleFactor
        global maxDownload
        global fileColors
        global remBaseDir
        global ssDelay
        global __initFilePath__
        global lastCastDeviceName
        global lastCastDeviceUuid
        global knownNetworks
        global fileSortRecentFirst
        global thumbnailGridRows
        global favoriteNetwork
        global autoSwitchToFavoriteNetwork

        try:
            self.config.read( __initFilePath__)

            # Get OSVM version section
            iniFileVersion = self.config['Version'][INI_VERSION]
            if iniFileVersion != _iniFileVersion_:
                print ('_parseInitFile(): Outdated INI file. Resetting to defaults')

            # Get preferences from Preferences
            sectionPreferences    = self.config['Preferences']
            if not compactMode: # User has not used '-c' cmdline argument
                compactMode           = str2bool(sectionPreferences[COMPACT_MODE])
            else:
                thumbnailGridRows = 5
            askBeforeCommit       = str2bool(sectionPreferences[ASK_BEFORE_COMMIT])
            askBeforeExit         = str2bool(sectionPreferences[ASK_BEFORE_EXIT])
            savePreferencesOnExit = str2bool(sectionPreferences[SAVE_PREFS_ON_EXIT])
            overwriteLocalFiles   = str2bool(sectionPreferences[OVERWRITE_LOCAL_FILES])
            autoSwitchToFavoriteNetwork = str2bool(sectionPreferences[AUTO_SWITCH_TO_CAMERA_NETWORK])
            thumbnailGridColumns  = int(sectionPreferences[THUMB_GRID_COLUMNS])
            thumbnailScaleFactor  = float(sectionPreferences[THUMB_SCALE_FACTOR])
            osvmDownloadDir       = sectionPreferences[OSVM_DOWNLOAD_DIR]
            fileSortRecentFirst       = str2bool(sectionPreferences[SORT_ORDER])

            sectionSyncModePref   = self.config['Sync Mode Preferences']
            remBaseDir		  = sectionSyncModePref[REM_BASE_DIR]
            osvmFilesDownloadUrl  = sectionSyncModePref[OSVM_FILES_DOWNLOAD_URL]
            maxDownload           = int(sectionSyncModePref[MAX_DOWNLOAD])
            if maxDownload == 0:
                maxDownload = MAX_OPERATIONS

            ssDelay            = self.config['View Mode Preferences'][SS_DELAY]
            lastCastDeviceName = self.config['View Mode Preferences'][LAST_CAST_DEVICE_NAME]
            lastCastDeviceUuid = self.config['View Mode Preferences'][LAST_CAST_DEVICE_UUID]

            sectionNetworks = self.config['Networks']
            s = sectionNetworks[FAVORITE_NETWORK]
            favoriteNetwork = (s.split(',')[0],s.split(',')[1])
            knownNetworks = list()
            knownNetworks = [value for key, value in sectionNetworks.items() if 'network_' in key]

            # Colors section
            sectionColors = self.config['Colors']
            for i in range(len(fileColors)):
                colrgb = sectionColors['color_%d' % i]
                newcol = wx.Colour()
                newcol.SetRGB(int(colrgb))
                fileColors[i][0] = newcol # update fileColors[]
            return False # Parsing OK
        except:
            print ('_parseInitFile(): Error parsing INI file')
            # Create a new Init file from builtin defaults
            del self.config
            self.config = configparser.ConfigParser()
            self._createDefaultInitFile()
            self.config.read(__initFilePath__)

            iniFileVersion = self.config['Version'][INI_VERSION]

            # Reload globals from default values
            sectionPreferences    = self.config['Preferences']
            compactMode           = str2bool(sectionPreferences[COMPACT_MODE])
            askBeforeCommit       = str2bool(sectionPreferences[ASK_BEFORE_COMMIT])
            askBeforeExit         = str2bool(sectionPreferences[ASK_BEFORE_EXIT])
            savePreferencesOnExit = str2bool(sectionPreferences[SAVE_PREFS_ON_EXIT])
            overwriteLocalFiles   = str2bool(sectionPreferences[OVERWRITE_LOCAL_FILES])
            autoSwitchToFavoriteNetwork = str2bool(sectionPreferences[AUTO_SWITCH_TO_CAMERA_NETWORK])
            thumbnailGridColumns  = int(sectionPreferences[THUMB_GRID_COLUMNS])
            thumbnailScaleFactor  = float(sectionPreferences[THUMB_SCALE_FACTOR])
            osvmDownloadDir       = sectionPreferences[OSVM_DOWNLOAD_DIR]
            fileSortRecentFirst       = str2bool(sectionPreferences[SORT_ORDER])

            sectionSyncModePref   = self.config['Sync Mode Preferences']
            remBaseDir		  = sectionSyncModePref[REM_BASE_DIR]
            osvmFilesDownloadUrl  = sectionSyncModePref[OSVM_FILES_DOWNLOAD_URL]
            maxDownload           = int(sectionSyncModePref[MAX_DOWNLOAD])
            if maxDownload == 0:
                maxDownload = MAX_OPERATIONS

            ssDelay = self.config['View Mode Preferences'][SS_DELAY]

            self.config['Networks'] = {}
            favoriteNetwork = ('None','None')

            sectionColors = self.config['Colors']
            for i in range(len(fileColors)):
                colrgb = sectionColors['color_%d' % (i)]
                newcol = wx.Colour()
                newcol.SetRGB(int(colrgb))
                fileColors[i][0] = newcol
            return True # Parsing KO, New file created

    def _saveInitFile(self):
        global osvmDownloadDir
        global osvmFilesDownloadUrl
        global cameraConnected
        global compactMode
        global askBeforeCommit
        global askBeforeExit
        global savePreferencesOnExit
        global thumbnailGridColumns
        global thumbnailScaleFactor
        global maxDownload
        global remBaseDir
        global fileColors
        global ssDelay
        global _iniFileVersion_
        global __initFilePath__
        global overwriteLocalFiles
        global castDevice
        global knownNetworks
        global favoriteNetwork
        global fileSortRecentFirst
        global autoSwitchToFavoriteNetwork

        print("Saving preference file:", __initFilePath__)

        # lets update the config file
        self.config['Version'] = {INI_VERSION: _iniFileVersion_}

        self.config['Preferences'] = {}
        self.config['Preferences'][COMPACT_MODE]           = str(compactMode)
        self.config['Preferences'][ASK_BEFORE_COMMIT]      = str(askBeforeCommit)
        self.config['Preferences'][ASK_BEFORE_EXIT]        = str(askBeforeExit)
        self.config['Preferences'][SAVE_PREFS_ON_EXIT]     = str(savePreferencesOnExit)
        self.config['Preferences'][OVERWRITE_LOCAL_FILES]  = str(overwriteLocalFiles)
        self.config['Preferences'][AUTO_SWITCH_TO_CAMERA_NETWORK] = str(autoSwitchToFavoriteNetwork)
        self.config['Preferences'][THUMB_GRID_COLUMNS]     = str(thumbnailGridColumns)
        self.config['Preferences'][THUMB_SCALE_FACTOR]     = str(thumbnailScaleFactor)
        self.config['Preferences'][OSVM_DOWNLOAD_DIR]      = osvmDownloadDir
        self.config['Preferences'][SORT_ORDER]             = str(fileSortRecentFirst)

        self.config['Sync Mode Preferences'][REM_BASE_DIR]            = remBaseDir
        self.config['Sync Mode Preferences'][OSVM_FILES_DOWNLOAD_URL] = osvmFilesDownloadUrl
        self.config['Sync Mode Preferences'][MAX_DOWNLOAD]            = str(DEFAULT_MAX_DOWNLOAD)

        self.config['View Mode Preferences'][SS_DELAY] = str(ssDelay)
        if castDevice:
            self.config['View Mode Preferences'][LAST_CAST_DEVICE_NAME] = castDevice.name
            self.config['View Mode Preferences'][LAST_CAST_DEVICE_UUID] = str(castDevice.device.uuid)
        else:
            self.config['View Mode Preferences'][LAST_CAST_DEVICE_NAME] = 'None'
            self.config['View Mode Preferences'][LAST_CAST_DEVICE_UUID] = ''

        sectionNetworks = self.config['Networks']
        # Save the favorite network
        sectionNetworks[FAVORITE_NETWORK] = ','.join(favoriteNetwork)

        # Save all knownNetworks
        for i in range(len(knownNetworks)):
            sectionNetworks['network_%d' % (i)] = knownNetworks[i]

        for i in range(len(fileColors)):
            self.config['Colors']['color_%d' % (i)] = str(fileColors[i][0].GetRGB())

        # Writing our configuration file back to initFile
        with open(__initFilePath__, 'w') as cfgFile:
            self.config.write(cfgFile)


#### Class FileOperationMenu
class FileOperationMenu(wx.Menu):
    """
    Creates and displays a file menu that allows the user to
    select an operation to perform on a given file
    """
    global localFileInfos
    global localFilesSorted
    global slideShowNextIdx
    global castMediaCtrl
    global castDevice
    global vlcVideoViewer
    global viewMode

    def __init__(self, parent, button, oplist):
        """
        Initialize the Package menu dialog box
        """
        self.parent = parent
        self.button = button
        self.opList = oplist

        super(FileOperationMenu,self).__init__()

        self.clickedPos = self.parent.panel1.ScreenToClient(wx.GetMousePosition())

        try:
            fileName = self.button.GetName()
            fileType = fileName.split('.')[1]	# File suffix
        except:
            print('FileOperationMenu(): Invalid file %s' % (fileName))
            return

        #print('FileOperationMenu():',fileName)

        # Creates a Menu containing possible operations on this file:
        self.popupMenu = wx.Menu()
        self.popupMenuTitles = []

        # Id of each menu entry. 
        if __system__ == 'Darwin':
            id = 1
        else:
            id = 0  

	# Start Slideshow from here
        if viewMode and fileType == 'JPG' or (fileType == 'MOV' and vlcVideoViewer):
            menuEntry = [fileName, FILE_SLIDESHOW, self.button]
            self.popupMenuTitles.append((id, menuEntry))
            id += 1

        # Next entry is: 'Properties'
        menuEntry = [fileName, FILE_PROPERTIES, self.button]
        self.popupMenuTitles.append((id, menuEntry))
        id += 1

        # Insert a separator
        menuEntry = [fileName, -1, self.button]
        self.popupMenuTitles.append((id, menuEntry))
        id += 1

        # Check if this file is already here
        if not fileName in list(localFileInfos.keys()):
            # file is not yet installed
            menuEntry = [fileName, FILE_DOWNLOAD, self.button, '']
            self.popupMenuTitles.append((id, menuEntry)) 
            id += 1
        else:
            filePath = localFileInfos[fileName][F_PATH]
            found = False
            for op in self.opList:
                if op[OP_STATUS] and op[OP_FILENAME] == fileName:
                    found = True
                    menuEntry = [fileName, FILE_UNSELECT, self.button, filePath]
                    self.popupMenuTitles.append((id, menuEntry))
                    id += 1
                    break
            if not found:
                if fileType == 'JPG' or (fileType == 'MOV' and vlcVideoViewer):
                    menuEntry = [fileName, FILE_SELECT, self.button, filePath]
                    self.popupMenuTitles.append((id, menuEntry)) 
                    id += 1
            if overwriteLocalFiles:
                menuEntry = [fileName, FILE_DOWNLOAD, self.button, filePath]
                self.popupMenuTitles.append((id, menuEntry)) 
                id += 1
            menuEntry = [fileName, FILE_DELETE, self.button, filePath]
            self.popupMenuTitles.append((id, menuEntry)) 
            id += 1

        # Fill-in the menu with entries
        for tmp in self.popupMenuTitles:
            id = tmp[0]
            menuEntry = tmp[1]
            if menuEntry[1] == FILE_SLIDESHOW:    # start slideshow from here
                menuItem = wx.MenuItem(self.popupMenu, id, 'Start Slideshow From Here')
                menuItem.SetBitmap(wx.Bitmap(os.path.join(__imgDir__,'play.png')))
                self.popupMenu.Append(menuItem)
                # Register Properties menu handler with EVT_MENU
                self.popupMenu.Bind(wx.EVT_MENU, self._MenuSlideShowCb, menuItem)
                continue

            if menuEntry[1] == FILE_PROPERTIES:    # Properties
                menuItem = wx.MenuItem(self.popupMenu, id, 'Properties')
                menuItem.SetBitmap(wx.Bitmap(os.path.join(__imgDir__,'properties-32.jpg')))
                self.popupMenu.Append(menuItem)
                # Register Properties menu handler with EVT_MENU
                self.popupMenu.Bind(wx.EVT_MENU, self._MenuPropertiesCb, menuItem)
                continue

            if menuEntry[1] == -1:    # Separator
                self.popupMenu.AppendSeparator()
                continue

            if menuEntry[1] == FILE_DOWNLOAD:
                title = 'Add %s to Download List' % (menuEntry[0])
                imgFile = 'plus-32.jpg'
            if menuEntry[1] == FILE_SELECT:
                title = 'Add %s to Playlist' % (menuEntry[0])
                imgFile = 'plus-32.jpg'
            if menuEntry[1] == FILE_UNSELECT:
                title = 'Remove %s from Playlist' % (menuEntry[0])
                imgFile = 'moins-32.jpg'
            elif menuEntry[1] == FILE_DELETE:
                title = 'Delete file %s' % (menuEntry[0])
                imgFile = 'moins-32.jpg'

            menuItem = wx.MenuItem(self.popupMenu, id, title)
            menuItem.SetBitmap(wx.Bitmap(os.path.join(__imgDir__, imgFile)))
            self.popupMenu.Append(menuItem)
            # Register menu handler with EVT_MENU
            self.popupMenu.Bind(wx.EVT_MENU, self._MenuSelectionCb, menuItem)

#        self.button.SetMenu(self.popupMenu)

        # Displays the menu at the current mouse position
        self.parent.panel1.PopupMenu(self.popupMenu, self.clickedPos)
        self.popupMenu.Destroy() # destroy to avoid mem leak

    def _MenuSlideShowCb(self, event):
        global localFilesSorted

        menuEntry = self.popupMenuTitles[event.GetId()][1]
        fileName = str(menuEntry[0])
        print("_MenuSlideShowCb(): Searching %s in localFilesSorted (%d files)" % (fileName, len(localFilesSorted)))
        idx = [x[0] for x in localFilesSorted].index(fileName)
        fileType = fileName.split('.')[1]	# File suffix
        filesSelected = self.parent.selectFilesByPosition(fileType, idx)

        # Simulate a button 'Play' press
        self._btnPlayInfo = getattr(self.parent, "btnPlay")
        evt = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self._btnPlayInfo.GetId())
        evt.SetEventObject(self.parent.btnPlay)
        wx.PostEvent(self.parent.btnPlay, evt)

        event.Skip()

    def _MenuPropertiesCb(self, event):
        menuEntry = self.popupMenuTitles[event.GetId()][1]
        fileName = str(menuEntry[0])
        dlg = PropertiesDialog(fileName)
        ret = dlg.ShowModal()
        dlg.Destroy()
        event.Skip()

    def _MenuSelectionCb(self, event):
        if __system__ == 'Darwin':
            id = event.GetId() - 1
        else:
            id = event.GetId()

        menuEntry = self.popupMenuTitles[id][1]
        fileName  = menuEntry[0]
        what      = menuEntry[1]

        if what == FILE_PROPERTIES:
            self._MenuPropertiesCb(event)
            return

        if what == FILE_UNSELECT:
            op = [x for x in self.opList if x[OP_FILENAME] == fileName][0]
            self.parent.resetOneButton(fileName)
            self.parent.resetOneRequest(op)

            pendingOpsCnt = self.parent.pendingOperationsCount()
            msg = 'Request successfully cleared. %d request(s) in the queue' % (pendingOpsCnt)
            wx.CallAfter(self.parent.updateStatusBar, msg)
            return
            
        # Check if one operation is already pending for this file
        # and re-use it
        for op in self.opList:
            if op[OP_FILENAME] == fileName:
                self._scheduleOperation(op, menuEntry)
                return

        # Loop thru opList[] looking for a free slot, schedule an operation
        for op in self.opList:
            if op[OP_STATUS] == 0:
                self._scheduleOperation(op, menuEntry)
                break
        else:
            msg = 'Max requests reached (%d).' % (MAX_OPERATIONS)
            print (msg)

     # Clear/Reset a button
    def _resetButton(self, button):
        # button is: [widget, pkgnum, fgcol, bgcol]
        button[0].SetForegroundColour(button[2])
        button[0].SetBackgroundColour(button[3])

    # A valid operation slot has been found. Schedule the operation
    def _scheduleOperation(self, op, menuEntry):
        fileName  = menuEntry[0]
        operation = menuEntry[1]
        button    = menuEntry[2]
        filePath  = menuEntry[3]

        if operation == FILE_DELETE:
            # Ask confirmation
            dial = wx.MessageDialog(None, 
                                    'Do you really want to DELETE file %s ?'% (fileName), 
                                    'Question', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            ret = dial.ShowModal()
            if ret == wx.ID_NO:
                return

        op[OP_STATUS]   = 1          # Busy
        op[OP_FILENAME] = fileName
        op[OP_FILETYPE] = fileName.split('.')[1]	# File suffix
        op[OP_TYPE]     = operation
        op[OP_FILEPATH] = filePath

#        print('Setting colours')
#        button.SetBackgroundColour(fileColors[FILE_OP_PENDING][0])
#        button.SetForegroundColour(fileColors[FILE_OP_PENDING][1])

        print("Operation scheduled:",op)

#### Class PropertiesDialog
class PropertiesDialog(wx.Dialog):
    """
    Creates and displays a Package Properties dialog.
    """
    global localFileInfos
    global fileColors

    def __init__(self, fileName):
        """
        Initialize the Properties dialog box
        """
        self.fileName = fileName
        self.fields = []

        myStyle = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
        wx.Dialog.__init__(self, None, wx.ID_ANY, 'File Properties: %s' % (self.fileName), style=myStyle)
        self._initialize()

        self.panel1.SetSizerAndFit(self.topBoxSizer)
        self.SetClientSize(self.topBoxSizer.GetSize())
        self.Centre()

    """
    Create and layout the widgets in the dialog
    """
    def _initialize(self):
        global viewMode

        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self, size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)
        # Close button
        self.btnClose = wx.Button(id=wx.ID_CLOSE, parent=self.panel1, style=0)
        self.btnClose.SetToolTip('Close this Dialog')
        self.btnClose.Bind(wx.EVT_BUTTON, self.OnBtnClose)

        # Retrieve information to display from the globals
        try:
            pkginfo1 = availRemoteFiles[self.fileName]
        except:
            pkginfo1 = ["",-1,-1,-1,-1,-1,""]
        try:
            pkginfo2 = localFileInfos[self.fileName]
        except:
            pkginfo2 = ["","","",""]

        # Local file attrs
        if pkginfo2[F_NAME]:
            ldate = time.strftime('%d-%b-%Y %H:%M', time.localtime(pkginfo2[F_DATE]))
            if pkginfo2[F_SIZE] < ONEMEGA:
                localFileSizeString1 = '%.1f KB' % (pkginfo2[F_SIZE] / ONEKILO)
            else:
                localFileSizeString1 = '%.1f MB' % (pkginfo2[F_SIZE] / ONEMEGA)
            localFileSizeString2 = '(%s bytes)' % str(pkginfo2[F_SIZE])
        else:
            ldate = ''
            localFileSizeString1 = ''
            localFileSizeString2 = ''


        if viewMode:
            props = [ ('File Name',	        str(self.fileName)),       # Must be first
                      ('Local File Date', 	ldate),
                      ('Local File Size', 	'%s %s' % (localFileSizeString1, localFileSizeString2)) ]
        else:
            # Remote file attrs
            rdate = time.strftime('%d-%b-%Y %H:%M', time.localtime(int(pkginfo1[F_DATEINSECS])))
            if pkginfo1[F_SIZE] < ONEMEGA:
                remFileSizeString = '%.1f KB' % (pkginfo1[F_SIZE] / ONEKILO)
            else:
                remFileSizeString = '%.1f MB' % (pkginfo1[F_SIZE] / ONEMEGA)

            props = [ ('File Name',	        str(self.fileName)),       # Must be first
                      ('Remote File Date', 	rdate),
                      ('Remote File Size',	'%s (%s bytes)' % (remFileSizeString, str(pkginfo1[F_SIZE]))),
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
        parent.Add(0, 4, border=0, flag=wx.EXPAND)
        parent.Add(self.btnClose, 0, border=0, flag=wx.ALIGN_RIGHT)

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
    def OnBtnClose(self, event):
        self.Close()

#### ColorPickerDialog
class ColorPickerDialog(wx.Dialog):
    """
    Creates and displays a dialog that allows the user to
    change the color settings for package status
    """
    global fileColors
    global FILE_COLORS_STATUS

    def __init__(self, parent):
        """
        Initialize the dialog box
        """
        self.parent = parent
        myStyle = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
        wx.Dialog.__init__(self, None, wx.ID_ANY, '%s - Choose your colors' % _myName_, style=myStyle)

        self._initialize()

        self.panel1.SetSizerAndFit(self.topBoxSizer)
        self.SetClientSize(self.topBoxSizer.GetSize())
        self.Centre()

    def _initialize(self):
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
        self.btnOK.Bind(wx.EVT_BUTTON, self.OnBtnOK)
        self.btnOK.Disable()

        self._cols = []
        # For each color/status: 
        #    create a sizer containing:
        #        - the type/name of color to tweak (text widget)
        #        - a ColorPicker
        for i in range(len(fileColors)):
            # A Static Text in a box sizer used to center vertically...
            sts = wx.BoxSizer(orient=wx.VERTICAL)
            st = wx.StaticText(id=wx.ID_ANY, label=FILE_COLORS_STATUS[i],
                               name=FILE_COLORS_STATUS[i], parent=self.panel1, style=0)

            sts.Add(4, 4, 1, border=0, flag=wx.EXPAND)
            sts.Add(st, 0, border=0, flag=wx.EXPAND)
            sts.Add(4, 4, 1, border=0, flag=wx.EXPAND)

            sb = wx.StaticBox(id=wx.ID_ANY, label='', parent=self.panel1, style=0)
            defcol = fileColors[i][0]
            cp = wx.ColourPickerCtrl(parent=self.panel1, id=wx.ID_ANY, colour=defcol, 
                                     style=wx.CLRP_DEFAULT_STYLE | wx.CLRP_SHOW_LABEL)
            cp.Bind( wx.EVT_COLOURPICKER_CHANGED, self.OnColourChanged)

            sbs = wx.StaticBoxSizer(box=sb, orient=wx.HORIZONTAL)
            sbs.Add(sts, 0, border=5, flag=wx.EXPAND | wx.ALL)    # Static Text
            sbs.Add(4, 4, 1, border=0, flag=wx.EXPAND)
            sbs.Add(cp, 0, border=5, flag=wx.EXPAND)    # Color Picker
            # Store [sizer, colorpicker] for this color
            self._cols.append([sbs, cp])

        self._init_sizers()

    def _init_sizers(self):
        self.topBoxSizer = wx.BoxSizer(orient=wx.VERTICAL)

        # GridSizer containing all the possible colors to tweak
        gsNumCols = 3
        gsNumRows = math.ceil(len(fileColors) / gsNumCols) # round up
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

    def OnBtnOK(self, event):
        i = 0
        for e in self._cols:
            color = e[1].GetColour()
            fileColors[i][0] = color    # update fileColors[]
            i += 1
        self.EndModal(wx.ID_OK)
        event.Skip()

### class dateDialog
class dateDialog(wx.Dialog):
    """
    Creates and displays a dialog to select a date
    """
    def __init__(self, fromdate, todate):
        myStyle = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
        wx.Dialog.__init__(self, None, wx.ID_ANY, 'Date Selector', style=myStyle)

        self.fromdate = fromdate
        self.todate = todate

        self._initialize()

        self.panel1.SetSizerAndFit(self.topBoxSizer)
        self.SetClientSize(self.topBoxSizer.GetSize())
        self.Centre()

    def _initialize(self):
        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self, size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        self.wintitle = wx.StaticText(self.panel1)
        t = 'Select a Date in the Calendar: '
        m = "<big><span foreground='blue'>%s</span></big>" % t
        self.wintitle.SetLabelMarkup(m)

        self.dpc = wx.adv.GenericCalendarCtrl(self.panel1, style = wx.adv.DP_DEFAULT | wx.adv.DP_SHOWCENTURY | wx.adv.DP_ALLOWNONE)
        self.dpc.EnableMonthChange(True)
        d1 = wx.DateTime.FromDMY(int(self.fromdate.split('/')[1]),
                                 int(self.fromdate.split('/')[0]) - 1,	# Month starts from 0
                                 int(self.fromdate.split('/')[2]))
        d2 = wx.DateTime.FromDMY(int(self.todate.split('/')[1]),
                                 int(self.todate.split('/')[0]) - 1,	# Month starts from 0
                                 int(self.todate.split('/')[2]))
        self.dpc.SetDateRange(lowerdate=d1, upperdate=d2)
        self.dpc.Bind(wx.adv.EVT_CALENDAR, self.OnCalendarChanged)

        # widgets at the Bottom 
        # Cancel button
        self.btnCancel = wx.Button(id=wx.ID_CANCEL, parent=self.panel1, style=0)
        self.btnCancel.SetToolTip('Discard changes')
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnBtnCancel)

        # Close button
        self.btnClose = wx.Button(id=wx.ID_CLOSE, parent=self.panel1, style=0)
        self.btnClose.SetToolTip('Close this network')
        self.btnClose.Bind(wx.EVT_BUTTON, self.OnBtnClose)

        self._init_sizers()

    def _init_topBoxSizer_Items(self, parent):
        parent.Add(self.titleBoxSizer, 0, border=10, flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER)
        parent.Add(self.mainBoxSizer, 1, border=10, flag=wx.EXPAND | wx.ALL)
        parent.Add(self.bottomBoxSizer, 0, border=10, flag=wx.ALL | wx.ALIGN_RIGHT)

    def _init_titleBoxSizer_Items(self, parent):
        parent.Add(0, 4, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.wintitle, 1, border=0, flag=wx.EXPAND)
        parent.Add(0, 4, 0, border=0, flag=wx.EXPAND)

    def _init_mainBoxSizer_Items(self, parent):
        parent.Add(self.dpc, 0, border=0, flag=wx.EXPAND | wx.ALL)

    def _init_bottomBoxSizer_Items(self, parent):
        parent.Add(self.btnCancel, 0, border=0, flag=wx.EXPAND)
        parent.Add(4, 4, border=0, flag=wx.EXPAND)
        parent.Add(self.btnClose, 0, border=0, flag=wx.EXPAND)

    def _init_sizers(self):
        # Create box sizers
        self.topBoxSizer    = wx.BoxSizer(orient=wx.VERTICAL)
        self.titleBoxSizer  = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.mainBoxSizer   = wx.BoxSizer(orient=wx.VERTICAL)
        self.bottomBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        # Initialize each sizer
        self._init_topBoxSizer_Items(self.topBoxSizer)
        self._init_titleBoxSizer_Items(self.titleBoxSizer)
        self._init_mainBoxSizer_Items(self.mainBoxSizer)
        self._init_bottomBoxSizer_Items(self.bottomBoxSizer)

    def OnCalendarChanged(self, event):
        print('OnCalendarChanged:',self.dpc.GetDate())

    def OnBtnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBtnClose(self, event):
        print('OnBtnClose:',self.dpc.GetDate())
        self.EndModal(wx.ID_OK)

#### ChromeCastDialog
class ChromeCastDialog(wx.Dialog):
    """
    Creates and displays a dialog to select the Chromecast to use.
    """
    def __init__(self):
        """
        Initialize the preferences dialog box
        """
        myStyle = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
        wx.Dialog.__init__(self, None, wx.ID_ANY, '%s - ChromeCast Selector' % _myLongName_, style=myStyle)

        self._initialize()

        self.panel1.SetSizerAndFit(self.topBoxSizer)
        self.SetClientSize(self.topBoxSizer.GetSize())
        self.Centre()

    def _initialize(self):
        global chromecasts
        global castDevice
        global lastCastDeviceName
        global lastCastDeviceUuid

        self.cc = chromecasts

        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self, size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        # Store all Chromecast information in a list
        self.ccProps = list()
        self.ccProps.append(('Device Name', 'Device URI', 'Device Model', 'Device Manufacturer'))

        dev = 1
        found = 0
        for cc in self.cc:
            self.ccProps.append((cc.name,cc.uri,cc.model_name,cc.device.manufacturer))
            print(cc.name,cc.device.uuid,lastCastDeviceName,lastCastDeviceUuid)
            if lastCastDeviceName == cc.name and lastCastDeviceUuid == str(cc.device.uuid):
                print('Found previous cast device %s' % cc.name)
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
            if (castDevice and self.ccProps[i][0] == castDevice.name) or (found and found == i) :
                btn.SetValue(True)

            btn.Bind(wx.EVT_RADIOBUTTON, self.OnRadioButton)
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
        self.btnClose.Bind(wx.EVT_BUTTON, self.OnBtnClose)
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
        self.staticBox1 = wx.StaticBox(id=wx.ID_ANY, label=' Select a ChromeCast to use ', 
                                       parent=self.panel1, style=0)
        self.propsBoxSizer = wx.StaticBoxSizer(box=self.staticBox1, orient=wx.HORIZONTAL)
        self.bottomBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        # Initialize each sizer
        self._init_topBoxSizer_Items(self.topBoxSizer)
        self._init_propsBoxSizer_Items(self.propsBoxSizer)
        self._init_bottomBoxSizer_Items(self.bottomBoxSizer)

    ## Events
    def OnRadioButton(self, event):
        global castDevice
        global chromecasts

        button = event.GetEventObject()
#        print('Casting to: %s' % button.GetLabel())
        castDevice = None
        for i in range(1,len(self.ccProps)):
            if self.ccProps[i][0] == button.GetLabel():
                if self.ccProps[i][0] == 'None':
                    castDevice = None
                else:
                    castDevice = chromecasts[i-1] # -1 for header
                print('Using Cast Device:',castDevice)
        event.Skip()

    def OnBtnClose(self, event):
        global castDevice
        global chromecasts

        for i in range(4,len(self.fields)-1,4):
            btn = self.fields[i]
            if btn.GetValue() == True:
                try:
                    castDevice = chromecasts[(i-4)%3]
                except:
                    castDevice = None
                print('Using Cast Device:',castDevice)
                break

        self.EndModal(wx.ID_OK)

    def OnBtnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)
        event.Skip()


#### PreferencesDialog
class PreferencesDialog(wx.Dialog):
    """
    Creates and displays a preferences dialog that allows the user to
    change some settings.
    """

    # tmp variables  will contain user input text in the preference dialog
    # they are discarded/copied back into global variables upon button press
    tmpOsvmDownloadDir = ''
    tmpOsvmPkgFtpUrl = ''
    
    def __init__(self, parent):
        """
        Initialize the preferences dialog box
        """
        self.parent = parent
        self.needRescan = False

        myStyle = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
        wx.Dialog.__init__(self, None, wx.ID_ANY, '%s - Preferences' % _myLongName_, style=myStyle)
        self._initialize()

        self.panel1.SetSizerAndFit(self.topBoxSizer)
        self.SetClientSize(self.topBoxSizer.GetSize())
        self.Centre()

    # top box sizer
    def _init_topBoxSizer_Items(self, parent):
        parent.Add(self.globPrefsBoxSizer, 0, border=10, flag=wx.EXPAND | wx.ALL)
        parent.Add(4, 4, border=0, flag=0)
        parent.Add(self.viewModeBoxSizer, 0, border=10, flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT)
        parent.Add(4, 4, border=0, flag=0)
        parent.Add(self.localConfigBoxSizer, 0, border=10, flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT)
        parent.Add(4, 4, border=0, flag=0)
        parent.Add(self.remConfigBoxSizer, 0, border=10, flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT)
        parent.Add(4, 4, border=0, flag=0)
        parent.Add(self.bottomBoxSizer, 0, border=10, flag= wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_RIGHT)

    # Preferences items
    def _init_globPrefsBoxSizer_Items(self, parent):
        parent.Add(self.prefsGridSizer1, 0, border=5, flag= wx.EXPAND)

    def _init_prefsGridSizer1_Items(self, parent):
        parent.Add(self.cb1, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.cb2, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.cb3, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.cb5, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.cb6, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.cb7, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.maxDownloadSizer, 0, border=0, flag= wx.EXPAND)
        parent.Add(self.fileSortSizer, 0, border=0, flag= wx.EXPAND)
        parent.Add(self.colorPickerSizer, 0, border=0, flag= wx.EXPAND)

    def _init_colorPickerSizer_Items(self, parent):
        parent.Add(self.colorPickerBtn, 0, border=0, flag=wx.ALL)
        parent.Add(4, 4, 1, border=0, flag=0)

    def _init_maxDownloadSizer_Items(self, parent):
        parent.Add(self.staticText7, 0, border=5,
                   flag=wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM | wx.LEFT | wx.TOP)
        parent.Add(4, 8, border=0, flag=0)
        parent.Add(self.maxDownloadChoice, 0, border=5, flag=wx.ALL)

    def _init_fileSortSizer_Items(self, parent):
        parent.Add(self.fileSortTxt, 0, border=5,
                   flag=wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM | wx.LEFT | wx.TOP)
        parent.Add(4, 8, border=0, flag=0)
        parent.Add(self.fileSortChoice, 0, border=5, flag=wx.ALL)

    def _init_viewModeBoxSizer_Items(self, parent):
        parent.Add(self.staticText8, 0, border=5,
                   flag=wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM | wx.LEFT | wx.TOP)
        parent.Add(4, 8, border=0, flag=0)
        parent.Add(self.ssDelayChoice, 0, border=5, flag=wx.ALL)

    # local/config items

    def _init_localConfigBoxSizer_Items(self, parent):
        parent.Add(self.configBoxSizer1, 0, border=0, flag= wx.ALL)
        parent.Add(self.configBoxSizer6, 0, border=0, flag= wx.ALL)

    def _init_remConfigBoxSizer_Items(self, parent):
        parent.Add(self.configBoxSizer3, 0, border=0, flag= wx.ALL)
        parent.Add(self.configBoxSizer4, 0, border=0, flag= wx.ALL)
        parent.Add(self.configBoxSizer5, 0, border=0, flag= wx.ALL)

    def _init_configBoxSizer1_Items(self, parent):
        pass

    def _init_configBoxSizer6_Items(self, parent):
        parent.Add(self.btnSelectDownLoc, 0, border=5,
                         flag=wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM | wx.LEFT | wx.TOP)
        parent.Add(4, 8, border=0, flag=0)
        parent.Add(self.downLocTextCtrl, 0, border=5, flag=wx.EXPAND | wx.ALL)

    def _init_configBoxSizer3_Items(self, parent):
        parent.Add(self.staticText4, 0, border=5,
                         flag=wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM | wx.LEFT | wx.TOP)
        parent.Add(4, 8, border=0, flag=0)
        parent.Add(self.cameraUrlTextCtrl, 0, border=5, flag=wx.EXPAND | wx.ALL)

    def _init_configBoxSizer4_Items(self, parent):
        parent.Add(self.staticText5, 0, border=5,
                         flag=wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM | wx.LEFT | wx.TOP)
        parent.Add(4, 8, border=0, flag=0)
        parent.Add(self.remBaseDirTextCtrl, 0, border=5, flag=wx.EXPAND | wx.ALL)

    def _init_configBoxSizer5_Items(self, parent):
        parent.Add(self.favoriteNetwork, 0, border=5,
                   flag=wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM | wx.LEFT | wx.TOP)
        parent.Add(self.staticText6, 0, border=5,
                   flag=wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM | wx.LEFT | wx.TOP)

    # Bottom items
    def _init_bottomBoxSizer_Items(self, parent):
        parent.Add(self.bottomBoxSizer2, 1, border=0,
                        flag= wx.EXPAND | wx.ALL)
        parent.Add(8, 4, 2, border=0, flag=wx.EXPAND)
        parent.Add(self.bottomBoxSizer1, 0, border=0,
                        flag= wx.EXPAND | wx.ALL)

    def _init_bottomBoxSizer1_Items(self, parent):
        parent.Add(self.bottomBoxSizer3, 0, border=0,
                        flag= wx.ALL | wx.ALIGN_RIGHT)

    def _init_bottomBoxSizer2_Items(self, parent):
        parent.Add(self.bottomBoxSizer4, 0, border=0,
                        flag= wx.ALL | wx.ALIGN_LEFT)
        parent.Add(40, 4, 1, border=0, flag=wx.EXPAND)

    def _init_bottomBoxSizer3_Items(self, parent):
        parent.Add(self.btnCancel, 0, border=0, flag=wx.ALL)
        parent.Add(4, 4, border=0, flag=wx.EXPAND)
        parent.Add(self.btnApply, 0, border=0, flag=wx.ALL)

    def _init_bottomBoxSizer4_Items(self, parent):
        parent.Add(self.btnReset, 0, border=0, flag=wx.ALL)

    def _init_sizers(self):
        self.topBoxSizer = wx.BoxSizer(orient=wx.VERTICAL)
        # Preferences staticBoxSizer
        self.globPrefsBoxSizer = wx.StaticBoxSizer(box=self.staticBox2, orient=wx.VERTICAL)
        gsNumCols = 3
        gsNumRows = 3
        self.prefsGridSizer1 = wx.GridSizer(cols=gsNumCols, hgap=0, rows=gsNumRows, vgap=2)

        # Max Download boxSizer
        self.maxDownloadSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        # File Sort boxSizer
        self.fileSortSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        # Color Picker boxSizer
        self.colorPickerSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        # viewMode Download boxSizer
        self.viewModeBoxSizer = wx.StaticBoxSizer(box=self.staticBox4,
                                                   orient=wx.HORIZONTAL)

        # Local Config staticBoxSizer
        self.localConfigBoxSizer = wx.StaticBoxSizer(box=self.staticBox1,
                                                     orient=wx.VERTICAL)
        self.configBoxSizer1 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.configBoxSizer6 = wx.BoxSizer(orient=wx.HORIZONTAL)

        #  Remote Config staticBoxSizer
        self.remConfigBoxSizer = wx.StaticBoxSizer(box=self.staticBox3,
                                                   orient=wx.VERTICAL)
        self.configBoxSizer3 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.configBoxSizer4 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.configBoxSizer5 = wx.BoxSizer(orient=wx.HORIZONTAL)

        # Bottom button boxSizer
        self.bottomBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.bottomBoxSizer1 = wx.BoxSizer(orient=wx.VERTICAL)
        self.bottomBoxSizer2 = wx.BoxSizer(orient=wx.VERTICAL)
        self.bottomBoxSizer3 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.bottomBoxSizer4 = wx.BoxSizer(orient=wx.HORIZONTAL)

        # Initialize each sizer
        self._init_topBoxSizer_Items(self.topBoxSizer)
        self._init_globPrefsBoxSizer_Items(self.globPrefsBoxSizer)
        self._init_prefsGridSizer1_Items(self.prefsGridSizer1)
        self._init_maxDownloadSizer_Items(self.maxDownloadSizer)
        self._init_fileSortSizer_Items(self.fileSortSizer)
        self._init_colorPickerSizer_Items(self.colorPickerSizer)
        self._init_viewModeBoxSizer_Items(self.viewModeBoxSizer)
        self._init_localConfigBoxSizer_Items(self.localConfigBoxSizer)
        self._init_configBoxSizer1_Items(self.configBoxSizer1)
        self._init_configBoxSizer6_Items(self.configBoxSizer6)
        self._init_remConfigBoxSizer_Items(self.remConfigBoxSizer)
        self._init_configBoxSizer3_Items(self.configBoxSizer3)
        self._init_configBoxSizer4_Items(self.configBoxSizer4)
        self._init_configBoxSizer5_Items(self.configBoxSizer5)
        self._init_bottomBoxSizer_Items(self.bottomBoxSizer)
        self._init_bottomBoxSizer1_Items(self.bottomBoxSizer1)
        self._init_bottomBoxSizer2_Items(self.bottomBoxSizer2)
        self._init_bottomBoxSizer3_Items(self.bottomBoxSizer3)
        self._init_bottomBoxSizer4_Items(self.bottomBoxSizer4)

    """
    Create and layout the widgets in the dialog
    """
    def _initialize(self):
        global cameraConnected
        global online
        global askBeforeCommit
        global askBeforeExit
        global savePreferencesOnExit
        global overwriteLocalFiles
        global autoSwitchToFavoriteNetwork
        global osvmFilesDownloadUrl
        global fileColors
        global remBaseDir
        global fileSortRecentFirst
        global compactMode
        global favoriteNetwork

        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self,
                               size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        #### Misc Preferences
        self.staticBox2 = wx.StaticBox(id=wx.ID_ANY, label=' Global Preferences ', 
                                       parent=self.panel1, style=0)

        self.cb1 = wx.CheckBox(self.panel1, id=wx.ID_ANY, label='Use Compact Mode')
        self.cb1.SetValue(compactMode)

        self.cb2 = wx.CheckBox(self.panel1, id=wx.ID_ANY, label='Ask Before Commit')
        self.cb2.SetValue(askBeforeCommit)

        self.cb3 = wx.CheckBox(self.panel1, id=wx.ID_ANY, label='Save Preferences on Exit')
        self.cb3.SetValue(savePreferencesOnExit)

        self.cb5 = wx.CheckBox(self.panel1, id=wx.ID_ANY, label='Ask Before Exit')
        self.cb5.SetValue(askBeforeExit)

        self.cb6 = wx.CheckBox(self.panel1, id=wx.ID_ANY, label='Overwrite Local Files')
        self.cb6.SetValue(overwriteLocalFiles)

        self.cb7 = wx.CheckBox(self.panel1, id=wx.ID_ANY, label='Auto switch to Camera AP')
        self.cb7.SetValue(autoSwitchToFavoriteNetwork)
        self.cb7.SetToolTip('Automatically switch to favorite network (if set) when entering Sync Mode')

        self.staticText7 = wx.StaticText(id=wx.ID_ANY, label='Max Download:', 
                                         parent=self.panel1, style=0)

        self.maxDownloadChoice = wx.Choice(choices=[str(i) for i in range(MAX_OPERATIONS+1)], 
                                           id=wx.ID_ANY, parent=self.panel1, style=0)
        self.maxDownloadChoice.SetToolTip('Max allowed download. (0 = unlimited)')
        self.maxDownloadChoice.SetStringSelection(str(maxDownload))
        self.maxDownloadChoice.Bind(wx.EVT_CHOICE, self.OnMaxDownloadChoice, id=wx.ID_ANY)

        self.sortTypes = ['Recent First', 'Oldest First']
        self.fileSortTxt = wx.StaticText(label='Sorting Order:', parent=self.panel1, id=wx.ID_ANY)
        self.fileSortChoice = wx.Choice(choices=[v for v in self.sortTypes], 
                                        id=wx.ID_ANY, parent=self.panel1, style=0)
        self.fileSortChoice.SetToolTip('Select sort order')
        self.fileSortChoice.SetStringSelection(self.sortTypes[0] if fileSortRecentFirst else self.sortTypes[1])
        self.fileSortChoice.Bind(wx.EVT_CHOICE, self.OnFileSortChoice, id=wx.ID_ANY)

        self.colorPickerBtn = wx.Button(id=wx.ID_ANY, label='Color Chooser',
                                        parent=self.panel1, style=0)
        self.colorPickerBtn.SetToolTip('Choose colors of package status')
        self.colorPickerBtn.Bind(wx.EVT_BUTTON, self.OnColorPicker)

        # viewMode preferences in staticBox4
        self.staticBox4 = wx.StaticBox(id=wx.ID_ANY,
                                       label=' View Mode Preferences ',
                                       parent=self.panel1, style=0)

        self.staticText8 = wx.StaticText(id=wx.ID_ANY, label='Slideshow Delay:', 
                                         parent=self.panel1, style=0)

        self.ssDelayChoice = wx.Choice(choices=[str(i) for i in range(MIN_SS_DELAY, MAX_SS_DELAY)], 
                                           id=wx.ID_ANY, parent=self.panel1, style=0)
        self.ssDelayChoice.SetToolTip('Delay interval')
        self.ssDelayChoice.SetStringSelection(str(ssDelay))
        self.ssDelayChoice.Bind(wx.EVT_CHOICE, self.OnSsDelayChoice, id=wx.ID_ANY)

        # Configuration
        self.staticBox1 = wx.StaticBox(id=wx.ID_ANY,
              label=' Local Configuration ', parent=self.panel1, style=0)

        self.staticBox3 = wx.StaticBox(id=wx.ID_ANY,
              label=' Remote Configuration ', parent=self.panel1, style=0)

        self.downLocTextCtrl = wx.TextCtrl(id=wx.ID_ANY,
                                                 parent=self.panel1, 
                                                 style=wx.TE_PROCESS_ENTER, 
                                                 size=wx.Size(300, -1), 
                                                 value='foobar')
        self.downLocTextCtrl.SetValue(osvmDownloadDir)
        self.downLocTextCtrl.SetToolTip('Local Download directory')
        self.downLocTextCtrl.SetAutoLayout(True)
        self.downLocTextCtrl.SetCursor(wx.STANDARD_CURSOR)
        self.downLocTextCtrl.Bind(wx.EVT_TEXT, self.OnDownLocTextCtrlText,
                                     id=wx.ID_ANY)
        self.downLocTextCtrl.Bind(wx.EVT_TEXT_ENTER, self.OnDownLocTextCtrlText)

        self.btnSelectDownLoc = wx.Button(id=wx.ID_ANY, label='Select Download Directory',
                                          parent=self.panel1, style=0)
        self.btnSelectDownLoc.SetToolTip('Select local download directory')
        self.btnSelectDownLoc.Bind(wx.EVT_BUTTON, self.getOnClick(self.downLocTextCtrl))

        self.staticText4 = wx.StaticText(id=wx.ID_ANY, label='Camera HTTP URL:', parent=self.panel1, style=0)
        self.staticText5 = wx.StaticText(id=wx.ID_ANY, label='Camera Base Directory:', parent=self.panel1, style=0)

        self.cameraUrlTextCtrl = wx.TextCtrl(id=wx.ID_ANY,
                                             parent=self.panel1, 
                                             style=wx.TE_PROCESS_ENTER, 
                                             size=wx.Size(400, -1))
        self.cameraUrlTextCtrl.SetValue(osvmFilesDownloadUrl)
        self.cameraUrlTextCtrl.SetToolTip('Camera HTTP URL')
        self.cameraUrlTextCtrl.SetAutoLayout(True)
        self.cameraUrlTextCtrl.SetCursor(wx.STANDARD_CURSOR)
        self.cameraUrlTextCtrl.Bind(wx.EVT_TEXT, self.OnUrlTextCtrlText)

        self.remBaseDirTextCtrl = wx.TextCtrl(id=wx.ID_ANY,
                                             parent=self.panel1, 
                                             style=wx.TE_PROCESS_ENTER, 
                                             size=wx.Size(300, -1))
        self.remBaseDirTextCtrl.SetValue(remBaseDir)
        self.remBaseDirTextCtrl.SetToolTip('Base Directory on Camera')
        self.remBaseDirTextCtrl.SetAutoLayout(True)
        self.remBaseDirTextCtrl.SetCursor(wx.STANDARD_CURSOR)
        self.remBaseDirTextCtrl.Bind(wx.EVT_TEXT, self.OnRemBaseDirTextCtrl)

        self.favoriteNetwork = wx.Button(id=wx.ID_ANY, label='Select Favorite Camera AP',
                                        parent=self.panel1, style=0)
        self.favoriteNetwork.SetToolTip('Choose favorite camera access point')
        self.favoriteNetwork.Bind(wx.EVT_BUTTON, self.OnFavoriteCamera)
        self.staticText6 = wx.StaticText(id=wx.ID_ANY, label=favoriteNetwork[NET_SSID], parent=self.panel1, style=0)
        #### Bottom buttons
        self.btnCancel = wx.Button(id=wx.ID_CANCEL, label='Cancel', parent=self.panel1, style=0)
        self.btnCancel.SetToolTip('Discard changes')
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnBtnCancel)

        self.btnReset = wx.Button(id=wx.ID_DEFAULT, label='Default', parent=self.panel1, style=0)
        self.btnReset.SetToolTip('Reset to factory defaults')
        self.btnReset.Bind(wx.EVT_BUTTON, self.OnBtnReset)

        self.btnApply = wx.Button(id=wx.ID_APPLY, label='Apply', parent=self.panel1, style=0)
        self.btnApply.SetToolTip('Apply changes to current session')
        self.btnApply.SetDefault()
        self.btnApply.Bind(wx.EVT_BUTTON, self.OnBtnApply)

        url = str(self.cameraUrlTextCtrl.GetValue())
        if not url.startswith('http'):
            self.btnApply.Disable()

        # Initialize temporary dicts
        self.tmpOsvmDownloadDir = osvmDownloadDir
        self.tmpOsvmPkgFtpUrl   = osvmFilesDownloadUrl

        # Copy pkg colors (backup)
        self._tmpPkgColors = deepcopy(fileColors)

        self._init_sizers()

    def isRescanRequired(self):
        return self.needRescan

    # Reset Preference Dialog to Default values
    def _GUIReset(self):
        self.cb1.SetValue(DEFAULT_COMPACT_MODE)
        self.cb2.SetValue(DEFAULT_ASK_BEFORE_COMMIT)
        self.cb3.SetValue(DEFAULT_SAVE_PREFERENCES_ON_EXIT)
        self.cb5.SetValue(DEFAULT_ASK_BEFORE_EXIT)
        self.cb6.SetValue(DEFAULT_OVERWRITE_LOCAL_FILES)
        self.cb7.SetValue(DEFAULT_AUTO_SWITCH_TO_CAMERA_NETWORK)
        self.maxDownloadChoice.SetStringSelection(str(DEFAULT_MAX_DOWNLOAD))
        self.fileSortChoice.SetStringSelection(self.sortTypes[0])
        self.ssDelayChoice.SetStringSelection(str(DEFAULT_SLIDESHOW_DELAY))
        self.downLocTextCtrl.SetValue(DEFAULT_OSVM_DOWNLOAD_DIR)
        self.cameraUrlTextCtrl.SetValue(DEFAULT_OSVM_ROOT_URL)
        self.remBaseDirTextCtrl.SetValue(DEFAULT_OSVM_REM_BASE_DIR)

        self.tmpOsvmDownloadDir = DEFAULT_OSVM_DOWNLOAD_DIR
        self.tmpOsvmPkgFtpUrl   = DEFAULT_OSVM_ROOT_URL

    def _updateGlobalsFromGUI(self):
        global cameraConnected
        global compactMode
        global askBeforeCommit
        global askBeforeExit
        global savePreferencesOnExit
        global maxDownload
        global overwriteLocalFiles
        global autoSwitchToFavoriteNetwork
        global osvmDownloadDir
        global osvmFilesDownloadUrl
        global fileColors
        global remBaseDir
        global ssDelay
        global fileSortRecentFirst

        compactMode           = self.cb1.GetValue()
        askBeforeCommit       = self.cb2.GetValue()
        savePreferencesOnExit = self.cb3.GetValue()
        askBeforeExit         = self.cb5.GetValue()
        overwriteLocalFiles   = self.cb6.GetValue()
        autoSwitchToFavoriteNetwork = self.cb7.GetValue()
        maxDownload           = int(self.maxDownloadChoice.GetSelection())
        remBaseDir            = self.remBaseDirTextCtrl.GetValue()
        ssDelay               = int(self.ssDelayChoice.GetSelection()) + MIN_SS_DELAY
        fileSortRecentFirst   = not (int(self.fileSortChoice.GetSelection()))

        # Update from temporary variables
        osvmDownloadDir      = self.tmpOsvmDownloadDir
        osvmFilesDownloadUrl = self.tmpOsvmPkgFtpUrl

        #printGlobals()

    #### Events ####
    # Event Handler generator for the "Select Location" buttons
    # The <w> parameter is the text widget to update
    def getOnClick(self, w):
        def OnClick(event):
            """
            Show the DirDialog and update the text control accordingly
            """
            dlg = wx.DirDialog(self, "Choose a directory:",
                               style=wx.DD_DEFAULT_STYLE
                               #| wx.DD_DIR_MUST_EXIST
                               #| wx.DD_CHANGE_DIR
                               )
            if dlg.ShowModal() == wx.ID_OK:
                w.SetValue(dlg.GetPath())
                self.needRescan = True
            dlg.Destroy()
        return OnClick

    def OnFavoriteCamera(self, event):
        global favoriteNetwork

        dlg = WifiDialog(self)
        ret = dlg.ShowModal()
        dlg.Destroy()
        self.staticText6.SetLabel(favoriteNetwork[NET_SSID])
        event.Skip()

    def OnColorPicker(self, event):
        dlg = ColorPickerDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.needRescan = True
        dlg.Destroy()

    def OnBtnReset(self, event):
        self._GUIReset()
        self.btnApply.SetDefault()
        event.Skip()

    def OnBtnCancel(self, event):
        global fileColors

        # Restore initial colors
        fileColors = deepcopy(self._tmpPkgColors)
        self.EndModal(wx.ID_CANCEL)
        self.needRescan = False
        event.Skip()

    def OnBtnApply(self, event):
        global osvmDownloadDir
        global __thumbDir__

        self._updateGlobalsFromGUI()
        self.parent._savePreferences()

#        if not os.path.isdir(osvmDownloadDir):
#            print('Creating:', osvmDownloadDir)
#            try:
#                os.mkdir(osvmDownloadDir)
#            except OSError as e:
#                msg = "Cannot create %s: %s" % (osvmDownloadDir, "{0}".format(e.strerror))
#                dlg = wx.MessageDialog(None, msg, 'ERROR', wx.OK | wx.ICON_ERROR)
#                dlg.ShowModal()
#                self.needRescan = False
#                self.EndModal(wx.ID_CANCEL)
#                return

#        __thumbDir__ = os.path.join(osvmDownloadDir, '.thumbnails')
#        if not os.path.isdir(__thumbDir__):
#            print('Creating:', __thumbDir__)
#            try:
#                os.mkdir(__thumbDir__)
#            except OSError as e:
#                msg = "Cannot create %s: %s" % (__thumbDir__, "{0}".format(e.strerror))
#                dlg = wx.MessageDialog(None, msg, 'ERROR', wx.OK | wx.ICON_ERROR)
#                dlg.ShowModal()
#                self.needRescan = False
#                self.EndModal(wx.ID_CANCEL)
#                return

        __thumbDir__ = os.path.join(osvmDownloadDir, '.thumbnails')
        if not os.path.isdir(__thumbDir__):
            print('Creating:', __thumbDir__)
            try:
                os.makedirs(__thumbDir__, exist_ok=True)
            except OSError as e:
                msg = "Cannot create %s: %s" % (__thumbDir__, "{0}".format(e.strerror))
                dlg = wx.MessageDialog(None, msg, 'ERROR', wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                self.needRescan = False
                self.EndModal(wx.ID_CANCEL)
                return

        self.EndModal(wx.ID_APPLY)
        event.Skip()

    def SavePrefsOnExit(self, event):
        event.Skip()

    def AskBeforeCommit(self, event):
        event.Skip()

    def AskBeforeExit(self, event):
        event.Skip()

    def OnMaxDownloadChoice(self, event):
        global maxDownload
        maxDownload = int(self.maxDownloadChoice.GetSelection())
        event.Skip()

    def OnFileSortChoice(self, event):
        self.needRescan = True
        event.Skip()

    def OnSsDelayChoice(self, event):
        global ssDelay
        ssDelay = int(self.ssDelayChoice.GetSelection()) + MIN_SS_DELAY
        event.Skip()

    def OnDownLocTextCtrlText(self, event):
        self.tmpOsvmDownloadDir = self.downLocTextCtrl.GetValue()
        event.Skip()

    def OnUrlTextCtrlText(self, event):
        #print traceback.print_stack()
        url = str(self.cameraUrlTextCtrl.GetValue())
        if url.startswith('http://') or url.startswith('https://'):
            self.needRescan = True
            self.btnApply.Enable()
        else:
            self.btnApply.Disable()
        self.tmpOsvmPkgFtpUrl = url
        event.Skip()

    def OnRemBaseDirTextCtrl(self, event):
        remBaseDir = str(self.remBaseDirTextCtrl.GetValue())
        if remBaseDir.startswith('/'):
            self.needRescan = True
            self.btnApply.Enable()
        else:
            self.btnApply.Disable()
        event.Skip()

####
class OSVMConfigThread(threading.Thread):
    def __init__(self, pDialog, name):
        threading.Thread.__init__(self)
        self._pDialog = pDialog
        self._name = name
        self._stopper = threading.Event()

    def stopIt(self):
        print('%s: Stopping' % self._name)
        self._stopper.set()
        print('%s: isStopped() : %s' % (self._name, self.isStopped()))

    def isStopped(self):
        return self._stopper.isSet()

    def run(self):
        global localFilesCnt
        global availRemoteFilesCnt
        global autoViewMode
        global autoSyncMode
        global __thumbDir__
        global osvmDownloadDir

        print("%s Starting." % (self._name))

        wx.CallAfter(self._pDialog.setBusyCursor, 1)

#        if not os.path.isdir(osvmDownloadDir):
#            print('%s: Creating: %s' % (self._name, osvmDownloadDir))
#            try:
#                os.mkdir(osvmDownloadDir)
#            except OSError as e:
#                msg = "Cannot create %s: %s" % (osvmDownloadDir, "{0}".format(e.strerror))
#                dlg = wx.MessageDialog(None, msg, 'ERROR', wx.OK | wx.ICON_ERROR)
#                dlg.ShowModal()

#        __thumbDir__ = os.path.join(osvmDownloadDir, '.thumbnails')
#        if not os.path.isdir(__thumbDir__):
#            print('%s: Creating: %s' % (self._name, __thumbDir__))
#            try:
#                os.mkdir(__thumbDir__)
#            except OSError as e:
#                msg = "Cannot create %s: %s" % (__thumbDir__, "{0}".format(e.strerror))
#                dlg = wx.MessageDialog(None, msg, 'ERROR', wx.OK | wx.ICON_ERROR)
#                dlg.ShowModal()

        __thumbDir__ = os.path.join(osvmDownloadDir, '.thumbnails')
        if not os.path.isdir(__thumbDir__):
            print('%s: Creating: %s' % (self._name, __thumbDir__))
            try:
                os.makedirs(__thumbDir__, exist_ok=True)
            except OSError as e:
                msg = "Cannot create %s: %s" % (__thumbDir__, "{0}".format(e.strerror))
                dlg = wx.MessageDialog(None, msg, 'ERROR', wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()

        # Update dictionaries using current config parameters
        localFilesCnt,availRemoteFilesCnt = updateFileDicts()

        msg = '%d local files, %d remote files' % (localFilesCnt,
                                                   availRemoteFilesCnt)
        wx.CallAfter(self._pDialog.setTitleStaticText2, msg)
        wx.CallAfter(self._pDialog.setBusyCursor, 0)
        self._pDialog.timer.Stop()

        msg1 = 'Configuration is READY'
        wx.CallAfter(self._pDialog.setTitleStaticText1, msg1)
        wx.CallAfter(self._pDialog.enableEnter)

        # Notify user about any disabled module
        wx.CallAfter(self._pDialog.notifyDisabledModules)

        # Simulate a 'Enter View Mode' event if requested
        if autoViewMode:
            self._btnEnterViewMode = getattr(self._pDialog, 'btnEnterViewMode')
            evt = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self._btnEnterViewMode.GetId())
            evt.SetEventObject(self._pDialog.btnEnterViewMode)
            wx.PostEvent(self._pDialog.btnEnterViewMode, evt)
        elif autoSyncMode:
            self._btnEnterSyncMode = getattr(self._pDialog, 'btnEnterSyncMode')
            evt = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self._btnEnterSyncMode.GetId())
            evt.SetEventObject(self._pDialog.btnEnterSyncMode)
            wx.PostEvent(self._pDialog.btnEnterSyncMode, evt)

        print("%s Exiting." % (self._name))


####
class OSVMConfig(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)
        self.parent = parent
        self.timerCnt = 0

        self._initialize()

    def _initialize(self):
        global serverAddr
        global httpServer

        self.prefs = Preferences(self.parent)
        self.prefs._loadPreferences()

#        dlg = PreferencesDialog(self.prefs)
#        ret = dlg.ShowModal()
#        dlg.Destroy()

        printGlobals()

        self._initGUI()

        self.Center()
        self.panel1.Layout()
        self.panel1.Show(True)

        # Create and start a new thread to load the config
        self.MainConfigThread = OSVMConfigThread(self, "OSVMConfigThread")
        self.MainConfigThread.setDaemon(True)
        self.MainConfigThread.start()

        serverAddr = serverIpAddr()
        httpServer = startHTTPServer()

    def _displayOSVMBitmap(self, event=None):
        global __imgDir__

        # load the image
        imgPath = os.path.join(__imgDir__, 'OSVM3.png')
        img = wx.Image(imgPath, wx.BITMAP_TYPE_PNG)

        # convert it to a wx.Bitmap, and put it on the wx.StaticBitmap
        self.staticBitmap1.SetBitmap(wx.Bitmap(img))

    #### GUI
    def _init_topBoxSizer1_Items(self, parent):
        parent.Add(self.titleBoxSizer1, 0, border=5, flag=wx.EXPAND | wx.ALL)
        parent.Add(4,0)
        parent.Add(self.bottomBoxSizer, 0, border=5, flag=wx.EXPAND | wx.ALL | wx.ALIGN_BOTTOM)

    def _init_titleBoxSizer1_Items(self, parent):
        parent.Add(self.staticBitmap1, 0, border=0, flag=wx.ALL | wx.ALIGN_CENTER)
        parent.Add(4,0)
        parent.Add(self.titleStaticText1, 0, border=0, flag=wx.ALL | wx.ALIGN_CENTER)

    def _init_bottomBoxSizer_Items(self, parent):
        parent.Add(self.titleStaticText2, 0, border=0, flag=0)
        parent.Add(4, 4, proportion=1, border=0, flag=0)
        parent.Add(self.bottomBoxSizer1, 0, border=0, flag=wx.EXPAND)

    def _init_bottomBoxSizer1_Items(self, parent):
        parent.Add(self.pltfInfo, 0, border=0, flag=wx.ALIGN_BOTTOM | wx.ALIGN_LEFT)
        parent.AddStretchSpacer(prop=1)
        bottomButtonBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        bottomButtonBoxSizer.Add(self.btnExit, 0, border=0, flag=wx.ALIGN_LEFT)
        bottomButtonBoxSizer.Add(8, 4, proportion=1, border=0, flag=0)
        bottomButtonBoxSizer.Add(self.btnEnterViewMode, 0, border=0, flag=wx.ALIGN_RIGHT)
        bottomButtonBoxSizer.Add(4, 4, proportion=1, border=0, flag=0)
        bottomButtonBoxSizer.Add(self.btnEnterSyncMode, 0, border=0, flag=wx.ALIGN_RIGHT)
        parent.Add(bottomButtonBoxSizer, 0, border=0, flag=wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT)

    # Create controls & Sizers
    def _initGUI(self):
        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self,
                               size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        self.staticBitmap1 = wx.StaticBitmap(bitmap=wx.NullBitmap,
                                             id=wx.ID_ANY, 
                                             parent=self.panel1, style=0)

        self.titleStaticText1 = wx.StaticText(id=wx.ID_ANY,
                                              label='Initializing Configuration. Please wait...', 
                                              parent=self.panel1,
                                              style=0)
        self.titleStaticText1.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL,
                                              wx.NORMAL, False, 'Ubuntu'))

        self.titleStaticText2 = wx.StaticText(id=wx.ID_ANY,
                                              label='                    ', 
                                              parent=self.panel1,
                                              style=wx.RAISED_BORDER)
        self.titleStaticText2.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL,
                                              wx.NORMAL, False, 'Ubuntu'))
        if __system__ == 'Windows':
            # Get win32api version
            fixed_file_info = win32api.GetFileVersionInfo(win32api.__file__, '\\')
            pywin32Version = fixed_file_info['FileVersionLS'] >> 16
            print("pywin32Version:", pywin32Version)
            label= '%s: Version: %s\n%s\nPython (%dbits): %s wxpython: %s pywin32: %s' % (_myName_, _myVersion_,  (platform.platform()), __pythonBits__, __pythonVersion__, wx.version(), pywin32Version)
        else:
            label= '%s: %s\n%s\nPython (%dbits): %s wxpython: %s' % (_myName_, _myVersion_,  (platform.platform()), __pythonBits__, __pythonVersion__, wx.version())            

        self.pltfInfo = wx.StaticText(label=label,
                                      id=wx.ID_ANY,
                                      parent=self.panel1)
        self.pltfInfo.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Ubuntu'))
        
#        self.btnDebug = wx.Button(id=wx.ID_EXIT, label=u'Debug',
#                                  name=u'btnDebug', parent=self.panel1, style=0)
#        self.btnDebug.SetToolTip(u'Use local files for debug')
#        self.btnDebug.Bind(wx.EVT_BUTTON, self.OnBtnDebug)

        self.btnExit = wx.Button(id=wx.ID_EXIT, label='Quit', parent=self.panel1, style=0)
        self.btnExit.SetToolTip('No, Thanks. I want to escape')
        self.btnExit.Bind(wx.EVT_BUTTON, self.OnBtnExit)

        self.btnEnterViewMode = wx.Button(id=wx.ID_ANY, 
                                          label='Enter View Mode', 
                                          parent=self.panel1, style=0)
        self.btnEnterViewMode.SetToolTip('Enter Viewing Mode to browse local pictures and videos')
        self.btnEnterViewMode.Bind(wx.EVT_BUTTON, self.OnBtnEnterViewMode)
        # Disable button. Will be enabled once configuration is loaded
        self.btnEnterViewMode.Disable()

        self.btnEnterSyncMode = wx.Button(id=wx.ID_ANY, 
                                          label='Enter Sync Mode',
                                          parent=self.panel1, style=0)
        self.btnEnterSyncMode.SetToolTip('Enter Sync Mode to sync media files between your camera and this computer')
        self.btnEnterSyncMode.Bind(wx.EVT_BUTTON, self.OnBtnEnterSyncMode)
        # Disable button. Will be enabled once configuration is loaded
        self.btnEnterSyncMode.Disable()
        
        self._displayOSVMBitmap()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnUpdate, self.timer)
        self.timer.Start(TIMER2_FREQ)

        # TOP Level BoxSizer
        self.topBoxSizer1 = wx.BoxSizer(orient=wx.VERTICAL)
        # Title BoxSizer
        self.titleBoxSizer1 = wx.BoxSizer(orient=wx.VERTICAL)
        # Bottom BoxSizer
        self.bottomBoxSizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.bottomBoxSizer1 = wx.BoxSizer(orient=wx.HORIZONTAL)

        # Initialize each boxSizer
        self._init_topBoxSizer1_Items(self.topBoxSizer1)
        self._init_titleBoxSizer1_Items(self.titleBoxSizer1)
        self._init_bottomBoxSizer_Items(self.bottomBoxSizer)
        self._init_bottomBoxSizer1_Items(self.bottomBoxSizer1)

        self.panel1.SetSizerAndFit(self.topBoxSizer1)
        self.SetClientSize(self.topBoxSizer1.GetSize())
        self.Centre()

    def OnUpdate(self, event):
        text = 'Initializing Configuration. Please wait...'

        self.timerCnt += 1

        if '2.' in __pythonVersion__:
            msg = '{0:>{width}}'.format(text[0:self.timerCnt],width=(len(text)))
        else:
            msg = '{:>{width}}'.format(text[0:self.timerCnt],width=(len(text)))
        self.titleStaticText1.SetLabel(msg)
        #print(self.timerCnt,msg)

    def OnBtnEnterViewMode(self, event):
        global viewMode

        viewMode = True

        if self.MainConfigThread.is_alive():
            self.MainConfigThread.join() # Block until thread has finished

        self.setBusyCursor(True)
        frame = OSVM(self, -1, "%s" % (_myLongName_))
        self.setBusyCursor(False)
        self.panel1.Enable(False)
        frame.Show()
        self.panel1.Enable(True)
        for b in [self.btnEnterViewMode, self.btnEnterSyncMode]:
            b.Disable()

    def OnBtnEnterSyncMode(self, event):
        global viewMode
        global cameraConnected
        global availRemoteFilesCnt

        viewMode = False

        if self.MainConfigThread.is_alive():
            self.MainConfigThread.join() # Block until thread has finished

        switchToFavoriteNetwork()

        print('OnBtnEnterSyncMode(): cameraConnected =', cameraConnected)

        # Check for any error while updating dictionaries
        if availRemoteFilesCnt == 0:
            msg = 'No remote file available. Check your Preferences'
            dlg = wx.MessageDialog(None, msg, 'Error', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
        else:
            # System is ready.
            if cameraConnected:
                msg = '%s READY!' % (_myLongName_)
            else:
                msg = '%s READY. You are OFFLINE' % (_myLongName_)
                availRemoteFilesCnt = 0

        self.setBusyCursor(True)
        frame = OSVM(self, -1, "%s" % (_myLongName_))
        self.setBusyCursor(False)
        self.panel1.Enable(False)
#        frame.ShowModal()
        frame.Show()
        self.panel1.Enable(True)
        for b in [self.btnEnterViewMode, self.btnEnterSyncMode]:
            b.Disable()
        self.timer.Stop()
#        self.Destroy()

    def OnBtnExit(self, event):
        self.Destroy()

    #def resizeEvent(self):
        #self.SendSizeEvent() # to recalculate position

    # Notify user about any disabled module
    def notifyDisabledModules(self):
        global disabledModules

        for mod in disabledModules:
            dlg = wx.MessageDialog(None, mod[1], 'Warning', wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()

    # Enable Enter button (from thread)
    def enableEnter(self):
        self.btnEnterViewMode.Enable()
        self.btnEnterViewMode.SetDefault()
        self.btnEnterViewMode.SetFocus()
        self.btnEnterSyncMode.Enable()

    # Update titleStaticText1 (from thread)
    def setTitleStaticText1(self, msg):
        self.timer.Stop()
        self.titleStaticText1.SetLabel(msg)
        self.SendSizeEvent() # to center the text

    # Update titleStaticText2 (from thread)
    def setTitleStaticText2(self, msg):
        self.titleStaticText2.SetLabel(msg)

    # Set/unset busy cursor (from thread)
    def setBusyCursor(self, state):
        if state:
            wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)
        else:
            wx.EndBusyCursor()

####
class InstallDialog(wx.Dialog):
    global osvmFilesDownloadUrl

    def __init__(self, parent, download, oplist, title):
        wx.Dialog.__init__(self, None, wx.ID_ANY, title, size=(500,500))
        self.parent = parent
        self.downloadDir = download
        self.opList = oplist
        self.keepGoing = True
        self.installCanceled = False
        self.totalSecs = 0
        self.timerTicks = 0
        self.numOps = 0
        self.totalBlocks = 0
        self.totalCount = 0
        self.errorCnt = 0
        self.tmpOpList = []
        self.installSubPanelIdx = 0
        self.installSubPanels = []

        # Create the main thread
        self.mainInstallThrLock = threading.Lock()
        self.mainInstallThrLock.acquire() # Acquire the lock to prevent the thread from running
        self.mainInstallThr = MainInstallThread(self, "MainInstallThread", self.mainInstallThrLock)
        self.mainInstallThr.setDaemon(True)
        self.mainInstallThr.start()

        self._initialize()
        self._runThread()

    def _initialize(self):
        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self,
                                   size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        # Create Top Level BoxSizer
        self.topBoxSizer = wx.BoxSizer(orient=wx.VERTICAL)

        # Loop thru all operations and fill details
        for i in range(len(self.opList)):
            op = self.opList[i]
            opStatus = op[OP_STATUS]
            # If this operation is not used, skip it
            if not opStatus:
                continue

            operation = op[OP_TYPE] # FILE_DOWNLOAD = 1  FILE_DELETE = 2
            if operation == FILE_DELETE:
                continue
            fileName = op[OP_FILENAME]
            self.numOps += 1

            dirName  = availRemoteFiles[fileName][F_DIRNAME]
            fileSize = availRemoteFiles[fileName][F_SIZE]

            # Save full pathname of local file
            op[OP_FILEPATH] = os.path.join(self.downloadDir, fileName)

            nBlocks = fileSize / URLLIB_READ_BLKSIZE
            op[OP_SIZE] = (fileSize, nBlocks)
            fileUrl = '%s%s/%s' % (osvmFilesDownloadUrl, dirName, fileName)
            op[OP_REMURL] = fileUrl

            self.totalBlocks += math.ceil(nBlocks)

        print('%d operations configured' % self.numOps)

        self._createInstallSubPanels()
        self._createOtherControls()

        # Set a timer to count the elapsed time
        self.timer = wx.Timer(self, wx.ID_ANY)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

        self.panel1.SetSizerAndFit(self.topBoxSizer)
        self.SetClientSize(self.topBoxSizer.GetSize())
        self.Centre()

    def _createInstallSubPanels(self):
        global installSubPanelsCount

        # sub-panel to contain 5 pending operations
        h = min(installSubPanelsCount,self.numOps) * 60 + 40
        self.panel2 = wx.Panel(parent=self.panel1, id=wx.ID_ANY, 
                               size=(500,h), style=wx.TAB_TRAVERSAL)

        # Create a BoxSizer (managed by panel2) for all the pending operations
        self.operationsGridSizer = wx.GridSizer(cols=1, vgap=5, hgap=5)

        for i in range(min(installSubPanelsCount,self.numOps)):
            print('Creating subpanel #%d' % i)
            # List of all widgets related to this operation
            opWidgets = []

            # widget0. Progress gauge. Range is rounded up
            w = wx.Gauge(range=10, parent=self.panel2, id=wx.ID_ANY, size=(200, 15)) 
            opWidgets.append(w)

            # widget1
            w = wx.StaticText(label='Time elapsed:', parent=self.panel2, id=wx.ID_ANY)
            opWidgets.append(w)

            # widget2. contains time elapsed counter
            w = wx.StaticText(label='00:00:00', parent=self.panel2, id=wx.ID_ANY)
            opWidgets.append(w)

            # widget3
            w = wx.StaticText(label='Time remaining:', parent=self.panel2, id=wx.ID_ANY)
            opWidgets.append(w)

            # widget4. contains time remainining counter
            w = wx.StaticText(label='00:00:00', parent=self.panel2, id=wx.ID_ANY)
            opWidgets.append(w)

            # widget5. file name and size
            w = wx.StaticBox(label='', id=wx.ID_ANY, parent=self.panel2, style=0)
            opWidgets.append(w)

            # widget6. global box sizer for 1 operation
            w = wx.StaticBoxSizer(box=opWidgets[INST_STBOX], orient=wx.HORIZONTAL)
            opWidgets.append(w)

            # widget7. To contain time related widgets (INST_GRDSZ)
            w = wx.FlexGridSizer(2, 2, vgap=5, hgap=5)
            opWidgets.append(w)

            # Add all time related widgets to its sizer
            w.Add(opWidgets[INST_ELAPTXT], 0, border=5, flag=wx.EXPAND)
            w.Add(opWidgets[INST_ELAPCNT], 0, border=5, flag=wx.EXPAND)
            w.Add(opWidgets[INST_REMTXT], 0, border=5, flag=wx.EXPAND)
            w.Add(opWidgets[INST_REMCNT], 0, border=5, flag=wx.EXPAND)

            # widget8 (INST_LEDBOXSZ). Add 3 LEDs per operation: download, extract, install
            ledBoxSz = wx.BoxSizer(orient=wx.VERTICAL)
            opWidgets.append(ledBoxSz)
            ledList = [0,0,0]    # List of 3 LEDs

            # Meaning of each LED. Used by SetToolTip()
            ledMeans = [ 'File Download', 'File Extraction', 'File Installation' ]

            # Only 1 LED is enough
            ledList[0] = w = LED(self.panel2)
            w.SetState(LED_GREY)
            w.SetToolTip(ledMeans[0])
            # Add this LED in the sizer 
            ledBoxSz.Add(w, 0, border=0, flag=wx.EXPAND)

            # Add ledList (INST_LEDLIST) to the list of widgets for this op
            opWidgets.append(ledList)

            # Put the Gauge widgets in a sizer (INST_GKBOXSZ)
            gkBoxSz = wx.BoxSizer(orient=wx.VERTICAL)
            opWidgets.append(gkBoxSz)

            gkBoxSz.AddStretchSpacer(prop=1)
            gkBoxSz.Add(opWidgets[INST_GAUGE], 0, border=0, flag=wx.EXPAND)
            gkBoxSz.AddStretchSpacer(prop=1)

            # Add widgets related to this op in its sizer
            opWidgets[INST_OPBOXSZ].Add(opWidgets[INST_GKBOXSZ], 0, border=5, 
                                        flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
            opWidgets[INST_OPBOXSZ].Add(8, 0, 1, border=0, flag=wx.EXPAND)
            opWidgets[INST_OPBOXSZ].Add(opWidgets[INST_LEDBOXSZ], 0, border=5, 
                                        flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
            opWidgets[INST_OPBOXSZ].Add(8, 0, 1, border=0, flag=wx.EXPAND)
            opWidgets[INST_OPBOXSZ].Add(opWidgets[INST_GRDSZ], 0, border=5, 
                                        flag= wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)

            # Finally add this operation in the operations grid sizer
            self.operationsGridSizer.Add(opWidgets[INST_OPBOXSZ], 0, border=0, 
                                         flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND)

            # Store all widgets in this subpanel in the installSubPanels list
            self.installSubPanels.append(opWidgets)

        # Add the panel in the topBoxSizer
        self.topBoxSizer.Add(self.panel2, 0, border=10, flag=wx.ALL | wx.EXPAND)

        self.panel2.SetSizer(self.operationsGridSizer)
        self.panel2.SetAutoLayout(True)

    def _createOtherControls(self):
        # TextCtrl to display installation output messages
        self.statusBar = wx.TextCtrl(parent=self.panel1, size=(300, 100), id=wx.ID_ANY, style=wx.TE_MULTILINE)

        # Add a Gauge at the bottom for the overall installation process. 
        # the range is rounded up to meet wxwidget 3.0.
        self.ggAll = wx.Gauge(range=math.ceil(self.totalBlocks), parent=self.panel1, 
                              id=wx.ID_ANY, size=(-1, 20))
        print('InstallDialog(): totalBlocks=%f range=%d' % (self.totalBlocks, 
                                                            math.ceil(self.totalBlocks)))
        
        # Add a Total elapsed time counter and gauge
        self.totalElapTxt = wx.StaticText(label='Total Time:', 
                                          parent=self.panel1, id=wx.ID_ANY)
        self.totalElapCnt = wx.StaticText(label='00:00:00', parent=self.panel1, id=wx.ID_ANY)
        self.totalElapSz  = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.totalElapSz.Add(self.ggAll, 1, border=10, flag=wx.TOP | wx.EXPAND)
        self.totalElapSz.Add(8, 4, 0, border=0, flag=wx.EXPAND)
        self.totalElapSz.Add(self.totalElapTxt, 0, border=10, flag=wx.TOP | wx.EXPAND)
        self.totalElapSz.Add(4, 4, 0, border=0, flag=0)
        self.totalElapSz.Add(self.totalElapCnt, 0, border=10, flag=wx.TOP | wx.EXPAND)

        # Finally add bottom buttons in a sizer
        # Add various counters at the bottom in a sizer
        self.fileQueueLabel = wx.StaticText(label='Files:', parent=self.panel1, id=wx.ID_ANY)
        # Format the fileQueueCnt initial label
        try:
            n = int(math.log10(self.numOps))+1
        except:
            n = 0
        lbl = '{s:0{width}}/{s:0{width}}'.format(s=0,width=n)
        self.fileQueueCnt   = wx.StaticText(label=lbl, parent=self.panel1, id=wx.ID_ANY)

        self.sizeQueueLabel = wx.StaticText(label='Size:', parent=self.panel1, id=wx.ID_ANY)
        # Format the sizeQueueCnt initial label
        try:
            n = int(math.log10(self.totalBlocks))+1
        except:
            n = 0
        lbl = '{s:0{width}}/{s:0{width}}'.format(s=0,width=n)
        self.sizeQueueCnt = wx.StaticText(label=lbl, parent=self.panel1, id=wx.ID_ANY)

        self.avSpeedTxt = wx.StaticText(label='Average Speed:', 
                                             parent=self.panel1, id=wx.ID_ANY)
        self.avSpeedCnt = wx.StaticText(label='000 KB/s', parent=self.panel1, id=wx.ID_ANY)

        self.ETATxt = wx.StaticText(label='ETA:', parent=self.panel1, id=wx.ID_ANY)
        self.ETACnt = wx.StaticText(label='00:00:00', parent=self.panel1, id=wx.ID_ANY)

        self.btnCancel = wx.Button(id=wx.ID_CANCEL, label='Cancel All',
                                   parent=self.panel1, style=0)
        self.btnCancel.SetToolTip('Cancel all pending operations')
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnBtnCancel)

        self.btnDone = wx.Button(id=wx.ID_ANY, label='Done', parent=self.panel1, style=0)
        self.btnDone.SetToolTip('Exit Installation Dialog')
        self.btnDone.Bind(wx.EVT_BUTTON, self.OnBtnDone)
        self.btnDone.Disable()

        self.opBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.opBoxSizer.Add(self.fileQueueLabel, 0, border=0, flag=wx.ALIGN_CENTER_VERTICAL)
        self.opBoxSizer.AddStretchSpacer(prop=0)
        self.opBoxSizer.Add(self.fileQueueCnt, 0, border=0, flag=wx.ALIGN_CENTER_VERTICAL)
        self.opBoxSizer.AddStretchSpacer(prop=3)

        self.opBoxSizer.Add(self.sizeQueueLabel, 0, border=0, flag=wx.ALIGN_CENTER_VERTICAL)
        self.opBoxSizer.AddStretchSpacer(prop=0)
        self.opBoxSizer.Add(self.sizeQueueCnt, 0, border=0, flag=wx.ALIGN_CENTER_VERTICAL)
        self.opBoxSizer.AddStretchSpacer(prop=3)

        self.opBoxSizer.Add(self.avSpeedTxt, 0, border=0, flag=wx.ALIGN_CENTER_VERTICAL)
        self.opBoxSizer.AddStretchSpacer(prop=0)
        self.opBoxSizer.Add(self.avSpeedCnt, 0, border=0, flag=wx.ALIGN_CENTER_VERTICAL)
        self.opBoxSizer.AddStretchSpacer(prop=3)

        self.opBoxSizer.Add(self.ETATxt, 0, border=0, flag=wx.ALIGN_CENTER_VERTICAL)
        self.opBoxSizer.AddStretchSpacer(prop=0)
        self.opBoxSizer.Add(self.ETACnt, 0, border=0, flag=wx.ALIGN_CENTER_VERTICAL)
        self.opBoxSizer.AddStretchSpacer(prop=3)

        self.opBoxSizer.Add(self.btnCancel, 0, border=0, flag=0)
        self.opBoxSizer.AddStretchSpacer(prop=3)
        self.opBoxSizer.Add(self.btnDone, 0, border=0, flag=0)
        
        # Add button box sizer in top box sizer
        self.topBoxSizer.Add(self.statusBar, 0, border=10, flag=wx.ALL | wx.EXPAND)
        self.topBoxSizer.Add(self.totalElapSz, 0, border=10, flag=wx.ALL | wx.EXPAND)
        self.topBoxSizer.Add(4, 4, 0, border=0, flag=wx.EXPAND)
        self.topBoxSizer.Add(self.opBoxSizer, 0, border=10, 
                                  flag=wx.ALL | wx.EXPAND | wx.ALIGN_RIGHT)

    #### Events ####

    def OnBtnCancel(self, event):
        self.timer.Stop()
        self.installCanceled = True
        # Stop the install threads
        self.mainInstallThr.stopIt()
        while self.mainInstallThr.isAlive():
            time.sleep(1)

    def OnBtnDone(self, event):
        self.timer.Stop()
        self.EndModal(wx.ID_CLOSE)
        self.Close()
        event.Skip()

    def OnTimer(self, event):
        if self.numOps:   # Only if some package install/update
            for op in self.opList:
                if not op[OP_STATUS] or op[OP_TYPE] == FILE_DELETE:
                    continue
                # Update Counters/LEDs/Labels if transfer is active
                if op[OP_INTH] and op[OP_INTH].isAlive():
                    self.updateCounter(op)
                    self._updateLeds(op)
                    self._updateLabel(op)

        self.timerTicks += TIMER1_FREQ
        self.totalSecs = self.timerTicks / 1000
        self._updateTotalCounter()

    # Local methods
    def _runThread(self):
        # Process all DELETE operations first
        deleteLocalFiles(self, self.opList)

        #dumpOperationList("Global Operation List", self.opList)

        # Process all pending INSTALL/UPDATE operations
        # Start the main thread which will create all the sub-threads 
        # to do the actual transfer
        print('Releasing IntallThreadLock')
        self.mainInstallThrLock.release()	#Let the install threads run
        self.timer.Start(TIMER1_FREQ)

    # Check if a package URL is valid
    def _checkRemoteFile(self, dirName, fileName):
        global osvmFilesDownloadUrl

        fileUrl = '%s%s/%s' % (osvmFilesDownloadUrl, dirName, fileName)
        try:
            u = urllib.request.urlopen(fileUrl)
        except urllib.error.URLError as e:
            print(e.reason)
            return (-1, e.reason)

        totalSize = int(u.info()["Content-Length"])
        print('Remote File: %s size: %s bytes...' % (fileUrl,totalSize))
        return (totalSize, fileUrl)

    def _updateLabel(self, op):
        stBox = self.subPanel[INST_STBOX]

        statinfo = os.stat(op[OP_FILEPATH])
        if statinfo.st_size < (2 * ONEMEGA):
            label = '%s  %dKB / %dKB' % (os.path.basename(op[OP_FILEPATH]), 
                                         statinfo.st_size/1024, 
                                         op[OP_SIZE][0]/1024)
        else:
            label = '%s  %.1fMB / %.1fMB' % (os.path.basename(op[OP_FILEPATH]), 
                                             statinfo.st_size/ONEMEGA, 
                                             op[OP_SIZE][0]/ONEMEGA)
        stBox.SetLabel(label)

    def _updateLeds(self, op):
        ledList = self.subPanel[INST_LEDLIST]

        led = ledList[op[OP_INSTEP]]      # LED to update
        state = op[OP_INLEDSTATE]         # ON/BLINK/OFF
        color = op[OP_INLEDCOL]           # YELLOW/GREEN/RED

        if state == LED_BLINK:
            if self.totalSecs % 2:
                led.SetState(color)
            else:
                led.SetState(LED_GREY)
        else:
            led.SetState(color)

    def _updateTotalCounter(self):
        self.totalCount = 0
        # How much has been done so far?
        for op in self.opList:
            if not op[OP_STATUS] or op[OP_TYPE] == FILE_DELETE:
                continue
            self.totalCount += op[OP_INCOUNT]

        # update overall gauge
        try:
            self.ggAll.SetValue(self.totalCount)
        except:
            print('_updateTotalCounter(): Exception in SetValue(). count=%d' % (self.totalCount))

        elapsed = time.strftime('%H:%M:%S', time.gmtime(self.totalSecs))
        self.totalElapCnt.SetLabel(elapsed)

        if self.totalSecs:
            bandWidth = ((self.totalCount) * URLLIB_READ_BLKSIZE) / (self.totalSecs * 1024)
            self.avSpeedCnt.SetLabel('%d KB/s' % bandWidth)
            # compute total remaining time (ETA)
            KBytesRemaining = ((self.totalBlocks - self.totalCount) * URLLIB_READ_BLKSIZE) / 1024
            SecondsRemaining = int(KBytesRemaining / (bandWidth+1)) # Avoid div by 0
            self.ETACnt.SetLabel('%s' % (str(datetime.timedelta(seconds=SecondsRemaining))))

    # External callable methods

    # Set the subpanel to use. Update some widgets (filename, size,...)
    def nextInstallSubPanel(self, op):
        global installSubPanelsCount

        print('nextInstallSubPanel(): Using subpanel %d' % self.installSubPanelIdx)
        self.subPanel = self.installSubPanels[self.installSubPanelIdx]

        self.subPanel[INST_GAUGE].SetRange(range=math.ceil(op[OP_SIZE][1]))
        wlabel = '%s  %.1f KB' % (op[OP_FILENAME], op[OP_SIZE][0]/ONEKILO)
        self.subPanel[INST_STBOX].SetLabel(wlabel)
        self.installSubPanelIdx = (self.installSubPanelIdx + 1) % installSubPanelsCount

    # Update the Install Dialog window containing the gauges
    # Called by the timer handler and by the worker thread
    def updateCounter(self, op, reason=0):

        # reason = 1 means final update for this download
        if reason:
            count = op[OP_SIZE][1]
            print('final update:',count)
        else:
            count = op[OP_INCOUNT]

        # update gauge for this operation
        self.subPanel[INST_GAUGE].SetValue(count)

        # Update Elapsed time widget
        op[OP_INTICKS] += 1
        elapsed = time.strftime('%H:%M:%S', time.gmtime(op[OP_INTICKS]/TICK_PER_SEC))

        # Update Remaining time widget
        approxTime =  (op[OP_INTICKS] * op[OP_SIZE][1]) / max(count, 1)
        remaining = time.strftime('%H:%M:%S', time.gmtime(abs((approxTime - op[OP_INTICKS])/TICK_PER_SEC)))

        # Update Elapsed time widget
        self.subPanel[INST_ELAPCNT].SetLabel(elapsed)

        #  Update Remaining time widget
        self.subPanel[INST_REMCNT].SetLabel(remaining)

        # Update the block transferred counter
        n = int(math.log10(self.totalBlocks))+1
        self.sizeQueueCnt.SetLabel('{s}/{t}'.format(s=self.totalCount,t=self.totalBlocks))

        # Any click on the Cancel button
        if self.installCanceled:
            self.keepGoing = False

        #print count,nBlocks,self.keepGoing,elapsed,approxTime,remaining

    def finish(self, msg):
        print('finish(): All transfers finished (%d/%d)' % (self.totalCount, self.totalBlocks))
        self.btnDone.Enable()
        self.btnCancel.Disable()
        self.timer.Stop()
        oMsg = self.statusBar.GetValue()
        self.statusBar.SetValue(oMsg + '\n' + msg + '\n' + 'End Of Transfer. %d error(s)' % self.errorCnt)
        # Notify parent to stop any animation
        wx.CallAfter(self.parent.finish)


    def installError(self, err, msg, op=None):
        #print ('InstallError():', msg)
        self.errorCnt += err
        oldMsg = self.statusBar.GetValue()
        self.statusBar.SetValue(oldMsg + str(msg))
        if op:
            op[OP_INLEDSTATE] = LED_ON
            op[OP_INLEDCOL] = LED_RED
            try:
                self._updateLeds(op)
            except:
                pass

    # Called at beginning of a given step: download/0, extract/1 or install/2
    def startStep(self, op, step, qSize):
        op[OP_INSTEP] = step    # LED number
        op[OP_INLEDSTATE] = LED_BLINK
        op[OP_INLEDCOL] = LED_ORANGE
        # Get # digits in numOps
        numDigits = int(math.log10(self.numOps))+1
        # Format the fileQueueCnt label
        self.fileQueueCnt.SetLabel('{s:0{width}}/{t:0{width}}'.format(s=qSize,width=numDigits,t=self.numOps))

    # Called at end of a given install step: download/0, extract/1 or install/2
    def endStep(self, op, step):
        op[OP_INSTEP] = step    # LED number
        op[OP_INLEDSTATE] = LED_ON
        op[OP_INLEDCOL] = LED_GREEN
        self._updateLeds(op)
        if step == 2:
            #  Clear Remaining time widget
            self.subPanel[INST_REMCNT].SetLabel('00:00:00')

####
class CleanDownloadDirDialog(wx.Dialog):
    """
    Creates and displays a dialog that allows the user to
    selectively clean the download directory
    """
    global CLEAN_FILETYPES

    def __init__(self, parent, download):
        self.parent = parent
        self.downloadDir = download

        print('CleanDownloadDirDialog:',self.downloadDir)

        myStyle = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
        wx.Dialog.__init__(self, None, wx.ID_ANY, 'Select Files To Clean', style=myStyle)

        # Initialize the Dialog
        self._initialize()

        self.panel1.SetSizerAndFit(self.topBoxSizer)
        self.SetClientSize(self.topBoxSizer.GetSize())
        self.Centre()

    def _initialize(self):
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
        i = 0
        for k in CLEAN_FILETYPES.keys():
            w0 = wx.CheckBox(self.panel1, label=k)
            w0.SetValue(False)
            w0.Bind(wx.EVT_CHECKBOX, self.OnFileType)

            CLEAN_FILETYPES[k] = 0 # Clear file counter
            s = folderSize(self.downloadDir, k)
            if s < ONEMEGA:
                size = '%d KB  ' % (s/ONEKILO)
            else:
                size = '%d MB  ' % (s/ONEMEGA)

            w1 = wx.StaticText(self.panel1) # counter
            w1.SetFont(wx.Font(12, wx.SWISS, wx.ITALIC, wx.NORMAL, False))
            lbl = "<span foreground='grey'>%s</span>" % str(CLEAN_FILETYPES[k])
            w1.SetLabelMarkup(lbl)

            w2 = wx.StaticText(self.panel1) # size
            w2.SetFont(wx.Font(12, wx.SWISS, wx.ITALIC, wx.NORMAL, False))
            lbl = "<span foreground='grey'>%s</span>" % size
            w2.SetLabelMarkup(lbl)

            self.gbs.Add(w0, pos=(i,0), border=0, flag=wx.EXPAND)
            self.gbs.Add(w1, pos=(i,1), border=0, flag=wx.ALIGN_RIGHT)
            self.gbs.Add(w2, pos=(i,2), border=0, flag=wx.ALIGN_RIGHT)
            
            self.itemList.append((w0,w1,w2,s,size,CLEAN_FILETYPES[k]))
            i += 1

        # Row for total
        w0 = wx.StaticText(self.panel1)
        lbl = "<span foreground='blue'>Total space to free</span>"
        w0.SetLabelMarkup(lbl)
        self.gbs.Add(w0, pos=(3,0), border=0, flag=wx.ALL)

        w1 = wx.StaticText(self.panel1) # total counter
        lbl = "<span foreground='grey'>%s</span>" % ''
        w1.SetLabelMarkup(lbl)
        self.gbs.Add(w1, pos=(3,1), border=0, flag=wx.ALIGN_CENTER)

        w2 = wx.StaticText(self.panel1) # total size
        lbl = "<span foreground='blue'>%s</span>" % '         '
        w2.SetLabelMarkup(lbl)
        self.gbs.Add(w2, pos=(3,2), border=0, flag=wx.ALIGN_RIGHT)
        
        self.itemList.append((w0,w1,w2))

        # Buttons at bottom
        self.btnCancel = wx.Button(id=wx.ID_CANCEL, parent=self.panel1, style=0)
        self.btnCancel.SetToolTip('Cancel')
        self.btnCancel.SetDefault()
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnBtnCancel)

        self.btnApply = wx.Button(id=wx.ID_APPLY, parent=self.panel1, style=0)
        self.btnApply.SetToolTip('Apply changes')
        self.btnApply.Bind(wx.EVT_BUTTON, self.OnBtnApply)

        # Put all buttons in a BoxSizer
        self.bottombs = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.bottombs.Add(self.btnCancel, 0, border=0, flag=0)
        self.bottombs.Add(8, 4, 0, border=0, flag=0)
        self.bottombs.Add(self.btnApply, 0, border=0, flag=0)
        
        # Add all sizers in the top box sizer
        self.topBoxSizer.Add(self.gbs, 0, border=10, flag=wx.ALL | wx.EXPAND)
        self.topBoxSizer.Add(4, 4, 1, border=0, flag=wx.EXPAND)
        self.topBoxSizer.Add(self.bottombs, 0, border=10, flag=wx.ALL | wx.ALIGN_RIGHT)

    def OnFileType(self, event):
        w0 = event.GetEventObject() # Checkbox widget
        item = [x for x in self.itemList if x[0] == w0]
        w1   = item[0][1]    # StaticText widget
        w2   = item[0][2]    # StaticText widget
        s    = item[0][3]  # Size as int
        size = item[0][4]  # Size as str
        nb   = item[0][5]  # Nb files as int
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

        # Update Total row
        sizeTotal = nbTotal = i = 0
        for k in CLEAN_FILETYPES.keys():
            w0 = self.itemList[i][0] # wx.Checkbox
            s  = self.itemList[i][3]  # Size as int
            n  = self.itemList[i][5]  # Nbfiles as int
            if w0.GetValue():
                sizeTotal += s
                nbTotal += n
            i += 1

        if nbTotal == 0: nbTotal = '       '
        w1 = self.itemList[-1][1] # StaticText widget for total counter
        w1.SetFont(wx.Font(13, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        lbl = "<span foreground='blue'>%s</span>" % nbTotal
        w1.SetLabelMarkup(lbl)

        w2 = self.itemList[-1][2] # StaticText widget for total size
        if sizeTotal == 0:
            sizeTotal = '      '
        elif sizeTotal < ONEMEGA:
            sizeTotal = '%d KB ' % (sizeTotal/ONEKILO)
        else:
            sizeTotal = '%d MB ' % (sizeTotal/ONEMEGA)
        w2.SetFont(wx.Font(13, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        lbl = "<span foreground='blue'>%s</span>" % sizeTotal
        w2.SetLabelMarkup(lbl)

    def OnBtnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)
        event.Skip()

    def OnBtnApply(self, event):
        i = 0
        for k in CLEAN_FILETYPES.keys():
            if self.itemList[i][0].GetValue():  # wx.Checkbox
                print('Cleaning %s files' % k)
                for f in [y for x in os.walk(self.downloadDir) for y in glob.glob(os.path.join(x[0], '*.%s' % k))]:
                    print('Removing:',f)
            i += 1
        self.EndModal(wx.ID_APPLY)
        event.Skip()

####
class ThumbnailDialog(wx.Dialog):
    """
    Creates and displays a dialog to show a thumbnail
    """
    def __init__(self, parent, thumbnail):
        """
        Initialize the dialog box
        """
        self.parent = parent
        self.thumbFilePath = thumbnail
        self.PhotoMaxSize = 240
 
        myStyle = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
        wx.Dialog.__init__(self, None, wx.ID_ANY, 'Thumbnail Viewer', style=myStyle)

        self._initialize()

        self.panel1.SetSizerAndFit(self.topBoxSizer)
        self.SetClientSize(self.topBoxSizer.GetSize())
        self.Centre()

    def _initialize(self):
        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self,
                               size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        img = wx.Image(240,240)
        self.imageCtrl = wx.StaticBitmap(self.panel1, wx.ID_ANY, wx.Bitmap(img))
        #  bottom buttons
        self.btnClose = wx.Button(id=wx.ID_ANY, label='Close', parent=self.panel1, style=0)
        self.btnClose.SetToolTip('Exit this Dialog')
        self.btnClose.Bind(wx.EVT_BUTTON, self.OnBtnClose)

        self._init_sizers()
        self._view_thumbnail()

    def _init_sizers(self):
        self.topBoxSizer = wx.BoxSizer(orient=wx.VERTICAL)

        self.mainSizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.mainSizer.Add(wx.StaticLine(self.panel1, wx.ID_ANY), 0, wx.ALL|wx.EXPAND, 5)
        self.mainSizer.Add(self.imageCtrl, 0, wx.ALL, 5)
        self.mainSizer.Add(wx.StaticLine(self.panel1, wx.ID_ANY), 0, wx.ALL|wx.EXPAND, 5)

        # Sizer containing the bottom buttons
        self.bottomBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.bottomBoxSizer.Add(4, 4, 1, border=0, flag=wx.EXPAND)
        self.bottomBoxSizer.Add(self.btnClose, 0, border=0, flag=0)

        self.topBoxSizer.Add(self.mainSizer, 0, border=5, flag=wx.EXPAND | wx.ALL)
        self.topBoxSizer.Add(self.bottomBoxSizer, 0, border=5, flag=wx.EXPAND | wx.ALL)

    def _view_thumbnail(self):
        filepath = self.thumbFilePath
        img = wx.Image(filepath, wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        W = img.GetWidth()
        H = img.GetHeight()
        if W > H:
            NewW = self.PhotoMaxSize
            NewH = self.PhotoMaxSize * H / W
        else:
            NewH = self.PhotoMaxSize
            NewW = self.PhotoMaxSize * W / H
        img = img.Scale(NewW, NewH)
 
        self.imageCtrl.SetBitmap(wx.Bitmap(img))
        self.panel1.Refresh()
 
    def OnBtnClose(self, event):
        self.EndModal(wx.ID_OK)
        event.Skip()


####
# From A. Gavana FlatNoteBook Demo
class LogoPanel(wx.Panel):
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.CLIP_CHILDREN):

        global _myName_, _myVersion_

        wx.Panel.__init__(self, parent, id, pos, size, style)

        self.SetBackgroundColour(wx.WHITE)
        imgpath = os.path.join(__thumbDir__, __imgDir__, 'sad-smiley.png')
        self.bmp = wx.Bitmap(wx.Image(imgpath, wx.BITMAP_TYPE_PNG))

        self.bigfont = wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD, False)
        self.normalfont = wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD, True)
        self.smallfont = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD, False)

        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.topTitle = 'No File Detected'
        self.midTitle = 'D. Poirot'
        self.bottomTitle = '%s %s' % (_myName_, _myVersion_)

    def setLogoPanelTopTitle(self, title):
        self.topTitle = title

    def setLogoPanelMidTitle(self, title):
        self.midTitle = title

    def setLogoPanelBottomTitle(self, title):
        self.bottomTitle = title

    def OnSize(self, event):
        event.Skip()
        self.Refresh()
        
    def OnPaint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        self.DoDrawing(dc)    

    def DoDrawing(self, dc):
        dc.SetBackground(wx.WHITE_BRUSH)
        dc.Clear()
        
        w, h = self.GetClientSize()
        bmpW, bmpH = self.bmp.GetWidth(), self.bmp.GetHeight()
        xpos, ypos = int((w - bmpW)/2), int((h - bmpH)/2)
        
        dc.DrawBitmap(self.bmp, xpos, ypos, True)

        dc.SetFont(self.bigfont)
        dc.SetTextForeground(wx.BLUE)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.SetPen(wx.Pen(wx.BLUE, 2))
        
        tw, th = dc.GetTextExtent(self.topTitle)
        xpos = int((w - tw)/2)
        ypos = int(h/3)

        dc.DrawRoundedRectangle(xpos-5, ypos-3, tw+10, th+6, 3)
        dc.DrawText(self.topTitle, xpos, ypos)
        
        dc.SetFont(self.normalfont)
        dc.SetTextForeground(wx.RED)
        tw, th = dc.GetTextExtent(self.midTitle)
        xpos = int((w - tw)/2)
        ypos = int(2*h/3)
        dc.DrawText(self.midTitle, xpos, ypos)

        dc.SetFont(self.smallfont)
        tw, th = dc.GetTextExtent(self.bottomTitle)
        xpos = int((w - tw)/2)
        ypos = int(2*h/3 + 4*th/2)
        dc.DrawText(self.bottomTitle, xpos, ypos)
        

####
class OSVM(wx.Frame):
    global fileColors
    global slideShowNextIdx

    colorGrid = []
    downloadDir = ''
    timerCnt = 0
    ssThr = 0

    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)
        self.parent = parent

        self.installDlg = None

        # Slideshow thread
        self.ssThrLock = threading.Lock()
        self.ssThrLock.acquire()	# Acquire the lock to prevent the thread from running
        self.ssThr = SlideShowThread(self, "SlideShowThread", self.ssThrLock)
        self.ssThr.setDaemon(True)
        self.ssThr.start()

        self._initialize()

    def _MakeModal(self, modal=True):
        if modal and not hasattr(self, '_disabler'):
            self._disabler = wx.WindowDisabler(self)
        if not modal and hasattr(self, '_disabler'):
            del self._disabler

    def ShowModal(self):
        self._MakeModal(True)
        self.Show()
        # now to stop execution start an event loop 
        self.eventLoop = wx.GUIEventLoop()
        self.eventLoop.Run()
 
    def _updateGlobalsFromGUI(self):
        pass

    def _checkLocalDir(self, localDir):
        # Test if localDir exist or not
        print('_checkLocalDir: localDir=', localDir)
        if not os.path.isdir(localDir):
            try:
                os.makedirs(localDir)
            except OSError as e:
                #accessModes = oct(os.stat(os.path.dirname(localDir)).st_mode & 0777)
                print('_checkLocalDir(): Error: Cannot create %s (%s)' % (localDir, e.strerror))
                return (-1, 'Cannot create %s (%s)' % (localDir, e.strerror))

        # Test if we can touch a file in localDir
        testFile = os.path.join(localDir, '.foo')
        try:
            touch(testFile)
        except:
            print('_checkLocalDir(): Error: Cannot touch %s' % testFile)
            return (-1, 'Cannot write in %s' % localDir)
        os.remove(testFile)
        return (0, '')

    def _updateGUIFromGlobals(self):
        pass

    def _updateStaticBox3Label(self, reason=''):
        olbl = self.staticBox3.GetLabel()
        prefix = olbl[:olbl.index('Page:')]
        self._pageCount = self.noteBook.GetPageCount()
        nlbl = '%sPage: %d/%d' % (prefix, self.noteBook.GetSelection()+1,self._pageCount)
        self.staticBox3.SetLabel(nlbl)

    def _createThumbnailTab(self, parent, listOfThumbnail, idx):
        global thumbnailGridColumns
        global thumbnailGridRows
        global viewMode
        global vlcVideoViewer

        tab = wx.Panel(id=wx.ID_ANY, name='tab%d'%idx, parent=parent)
        sizer = wx.GridSizer(rows=thumbnailGridRows, cols=thumbnailGridColumns, vgap=5, hgap=5)

        lastIdx = min(idx + (thumbnailGridRows * thumbnailGridColumns), len(listOfThumbnail))
        print('%s [%d : %d]\r' % (tab.GetName(), idx, lastIdx), end='', flush=True)
#        print('%02d:%02d\r' % (m,s), end='', flush=True)
        for f in listOfThumbnail[idx:lastIdx]:
            remFileName = f[1][F_NAME]
            remFileSize = f[1][F_SIZE]
            remFileDate = f[1][F_DATE]

            # Add 1 button for each available image
            button = wx.Button(parent=tab, 
                               id=wx.ID_ANY,
                               name=remFileName,
                               style=0)
            if viewMode:
                if vlcVideoViewer:
                    button.Bind(wx.EVT_BUTTON, self.LaunchViewer)
                button.Bind(wx.EVT_RIGHT_DOWN, self.OnThumbButtonRightDown)
            else:
                if remFileName in list(localFileInfos.keys()) and vlcVideoViewer:
                    button.Bind(wx.EVT_BUTTON, self.LaunchViewer)
                else:
                    button.Bind(wx.EVT_BUTTON, self.OnThumbButton)
            button.Bind(wx.EVT_RIGHT_DOWN, self.OnThumbButtonRightDown)

            if float(remFileSize) < ONEMEGA:
                remFileSizeString = '%.1f KB' % (remFileSize / ONEKILO)
            else:
                remFileSizeString = '%.1f MB' % (remFileSize / ONEMEGA)

            # Display thumbnail (with scaling)
            thumbnailPath = os.path.join(__thumbDir__, remFileName)
            self._displayThumbnail(button, thumbnailPath, wx.BITMAP_TYPE_JPEG)

            # Set tooltip
            if viewMode:
                toolTipString = 'File: %s\nSize: %s\nDate: %s' % (remFileName,remFileSizeString,secondsTodmY(remFileDate))
            else:
                toolTipString = 'File: %s\nSize: %s\nDate: %s' % (remFileName,remFileSizeString,getHumanDate(remFileDate))
            button.SetToolTip(toolTipString)

            # Colorize button if file is available locally
            color = fileColor(remFileName)
            button.SetBackgroundColour(color[0])
            button.SetForegroundColour(color[1])

            sizer.Add(button, proportion=1, border=0, flag=wx.EXPAND)

            # each entry in thumbButtons[] is of form: [button, filename, fgcol, bgcol]
            bgcol = button.GetBackgroundColour()
            fgcol = button.GetForegroundColour()

            newEntry = [button, remFileName, fgcol, bgcol]
            self.thumbButtons.append(newEntry)
            self.numPkgButtons += 1

        if viewMode:
            firstRemFileDate = '%s' % (secondsTodmy(listOfThumbnail[idx][1][F_DATE]))
            lastRemFileDate  = '%s' % (secondsTodmy(listOfThumbnail[lastIdx-1][1][F_DATE]))
        else:
            firstRemFileDate = '%s' % (getHumanDate(listOfThumbnail[idx][1][F_DATE]))
            lastRemFileDate  = '%s' % (getHumanDate(listOfThumbnail[lastIdx-1][1][F_DATE]))

        tab.SetSizer(sizer)
        return tab,firstRemFileDate,lastRemFileDate

    def _createThumbnailPanel(self):
        global availRemoteFilesSorted
        global localFilesSorted
        global viewMode
        global thumbnailGridRows
        global thumbnailGridColumns
        global fileSortRecentFirst

        setBusyCursor(True)

        agwStyle=fnb.FNB_VC8|fnb.FNB_COLOURFUL_TABS | fnb.FNB_NO_X_BUTTON
#        agwStyle=fnb.FNB_VC8 | fnb.FNB_COLOURFUL_TABS | fnb.FNB_NO_X_BUTTON |fnb.FNB_DROPDOWN_TABS_LIST
        self.noteBook = fnb.FlatNotebook(parent=self.panel1, id=wx.ID_ANY,agwStyle=agwStyle) 

        # Create a custom panel to use when the notebook is empty, e.g. no file is detected
        self.customPanel = LogoPanel(self.noteBook, -1)
        self.noteBook.SetCustomPage(self.customPanel)

        self._pageCount = self.noteBook.GetPageCount()
        print('_createThumbnailPanel(): # pages:', self._pageCount)

        self.numPkgButtons = 0

        if viewMode:
            fileListToUse = localFilesSorted
            self.customPanel.setLogoPanelTopTitle('No Local File Detected')
        else:
            fileListToUse = availRemoteFilesSorted
            self.customPanel.setLogoPanelTopTitle('No Remote File Detected')
            self.customPanel.setLogoPanelMidTitle('Connect to the Camera and Refresh')

        numTabs = len(fileListToUse) / (thumbnailGridRows * thumbnailGridColumns)
#        self.tabs = list()

        firstIdx = 0

        for t in range(int(math.ceil(numTabs))): # round up
            tab, firstRemFileDate,lastRemFileDate = self._createThumbnailTab(self.noteBook, fileListToUse, firstIdx)
            if fileSortRecentFirst:
                self.noteBook.AddPage(tab, '%s  -  %s' % (lastRemFileDate,firstRemFileDate))
            else:
                self.noteBook.AddPage(tab, '%s  -  %s' % (firstRemFileDate,lastRemFileDate))

#            self.tabs.append(tab)
            firstIdx += thumbnailGridRows * thumbnailGridColumns

        self._pageCount = self.noteBook.GetPageCount()
        print('_createThumbnailPanel(): %d pages created' % self._pageCount)

        # update box title
        self._updateStaticBox3Label('_createThumbnailPanel')

        self.noteBook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CHANGED,self._OnFlatNoteBookPageChanged)
        self.noteBook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSED,self._OnFlatNoteBookPageClosed)
#        self.noteBook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CHANGING,self.ev2)

        setBusyCursor(False)

    #
    # This function will rescan the installation according to user preferences
    #
    def _updateThumbnailPanel(self):
        global availRemoteFilesSorted
        global localFilesSorted
        global viewMode
        global thumbnailGridRows
        global thumbnailGridColumns
        global fileSortRecentFirst

        setBusyCursor(True)

        # Update customPanel titles *before* deleting the pages
        if viewMode:
            self.customPanel.setLogoPanelTopTitle('No Local File Detected')
        else:
            self.customPanel.setLogoPanelTopTitle('No Remote File Detected')
            self.customPanel.setLogoPanelMidTitle('Connect to the Camera and Refresh')

        # Delete all pages, one by one, starting from the last
        for p in range(self.noteBook.GetPageCount()-1, -1, -1):
            self.noteBook.DeletePage(p)

        # Clear existing button list
        self.thumbButtons = list()
        self.numPkgButtons = 0

        if viewMode:
            fileListToUse = localFilesSorted
        else:
            fileListToUse = availRemoteFilesSorted

        numTabs = len(fileListToUse) / (thumbnailGridRows * thumbnailGridColumns)
        firstIdx = 0

        for t in range(int(math.ceil(numTabs))): # round up
            tab, firstRemFileDate,lastRemFileDate = self._createThumbnailTab(self.noteBook, fileListToUse, firstIdx)
            if fileSortRecentFirst:
                self.noteBook.AddPage(tab, '%s  -  %s' % (lastRemFileDate,firstRemFileDate))
            else:
                self.noteBook.AddPage(tab, '%s  -  %s' % (firstRemFileDate,lastRemFileDate))

            firstIdx += thumbnailGridRows * thumbnailGridColumns

        self._pageCount = self.noteBook.GetPageCount()
        print('_updateThumbnailPanel(): %d pages created' % self._pageCount)

        # update box title with new page count
        self._updateStaticBox3Label('_updateThumbnailPanel')

        self.Layout()
        self.Show(True)

        setBusyCursor(False)

    #
    # A valid request slot has been found. Schedule the operation
    #
    def _scheduleOperation(self, op, menuEntry):
        fileButton = menuEntry[0]
        button     = fileButton[0]
        fileName   = menuEntry[1]
        operation  = menuEntry[2]
        fileSize   = menuEntry[3]
        fileDate   = menuEntry[4]

        if operation == FILE_DELETE:
            # Ask confirmation
            dial = wx.MessageDialog(None, 'Do you really want to DELETE file %s ?'% (fileName), 
                                    'Question', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            ret = dial.ShowModal()
            if ret == wx.ID_NO:
                return

        op[OP_STATUS]   = 1          			# Busy
        op[OP_FILENAME] = fileName
        op[OP_FILETYPE] = fileName.split('.')[1]	# File suffix
        op[OP_TYPE]     = operation
        nBlocks = fileSize / URLLIB_READ_BLKSIZE
        op[OP_SIZE]     = (fileSize, nBlocks)
        op[OP_FILEDATE] = fileDate

        pendingOpsCnt = self.pendingOperationsCount()
        statusBarMsg = 'Request successfully scheduled. %d request(s) in the queue' % (pendingOpsCnt)
        self.updateStatusBar(statusBarMsg)
        self.btnCommit.Enable()
        self.btnCancel.Enable()

        # Sanity check
        # Each entry in thumbButtons[] is of form: [widget, fileName, fgcol, bgcol]
        for b in self.thumbButtons:
            if b[1] == fileName:
                if b[0] != button:
                    print ("ERROR: File list corrupted!")
                else:
                    # Update button color
                    button.SetBackgroundColour(fileColors[FILE_OP_PENDING][0])
                    button.SetForegroundColour(fileColors[FILE_OP_PENDING][1])
                    self.Refresh()

    winDisabler = None

    # Set mode to Enable/Disable. Prevent user using not uptodate information
    def _setMode(self, mode, reason):
        global cameraConnected

        print('_setMode(): mode %s' % mode)
        #print traceback.print_stack()

        # Restore focus to panel
        # DP: 02/06/2016. Keep the focus on the current widget 
        # self.panel1.SetFocusIgnoringChildren()

        # Menu items to disable when mode == MODE_DISABLED
        menuItems = [('File', 'Preferences'),
                     ('File', 'Clean Download Directory...'),
                     ('File', 'Quit')]

        if mode == MODE_ENABLED:
            self.updateStatusBar(reason)

            # handle events which may have been queued up
            wx.Yield() 

            #del self.winDisabler

            # Allow user action
            for item in menuItems:
                id = self.menuBar.FindMenuItem(item[0],item[1])
                self.menuBar.Enable(id, True)

            # Disable some menu items if no camera
            if not cameraConnected:
                self._setOfflineMode()

            self.btnRescan.Enable()
            if cameraConnected:
                self.btnCommit.Enable()

            # Enable all pkg buttons
            self.noteBook.Enable()
        else:
            self.updateStatusBar(reason, fgcolor=wx.WHITE, bgcolor=wx.RED)

            for item in menuItems:
                id = self.menuBar.FindMenuItem(item[0],item[1])
                self.menuBar.Enable(id, False)

            # Disable all buttons
            self.noteBook.Disable()
            self.btnRescan.Enable()
#            self.btnRescan.SetDefault()

            #self.winDisabler = wx.WindowDisabler()

    # Clear/Reset a pending operation
    def resetOneRequest(self, op):
        op[OP_STATUS]     = 0
        op[OP_FILENAME]   = ''
        op[OP_FILETYPE]   = ''
        op[OP_TYPE]       = 0
        op[OP_FILEPATH]   = ''
        op[OP_SIZE]       = (0,0)
        op[OP_REMURL]     = ''
        op[OP_INWGT]      = []
        op[OP_INCOUNT]    = 0
        op[OP_INSTEP]     = 0
        op[OP_INLEDCOL]   = LED_GREY
        op[OP_INLEDSTATE] = LED_OFF
        op[OP_INTH]       = None
        op[OP_INTICKS]    = 0

    def pendingOperationsCount(self):
        cnt = 0
        for i in range(len(self.opList)):
            if self.opList[i][OP_STATUS]:
                cnt += 1
        return cnt

    def _clearAllRequests(self):
        # Loop thru opList[]: Clear all slots
        for i in range(len(self.opList)):
            opStatus = self.opList[i][OP_STATUS]
            # If this operation is in used, reset associated button
            if opStatus:
                fileName = self.opList[i][OP_FILENAME]
                self.resetOneButton(fileName)
            self.resetOneRequest(self.opList[i])

    # Reset a package button associated with pkgnum
    def resetOneButton(self, fileName):
        # Each entry in thumbButtons[] is: [widget, pkgnum, fgcol, bgcol]
        for entry in self.thumbButtons:
            if entry[1] == fileName:
                # Restore colors
                entry[0].SetForegroundColour(entry[2])
                entry[0].SetBackgroundColour(entry[3])
                #entry[0].SetValue(False)

    def updateStatusBar(self, msg=None, bgcolor=wx.NullColour, fgcolor=wx.BLACK):
        global localFilesCnt
        global availRemoteFilesCnt
        global cameraConnected

        self.statusBar1.SetForegroundColour(fgcolor)
        self.statusBar1.SetBackgroundColour(bgcolor)

        if not msg:
            if not cameraConnected:
                msg = '%d local files' % (localFilesCnt)
            else:
                msg = '%d local files, %d files available on camera' % (localFilesCnt, availRemoteFilesCnt)

        self.statusBar1.SetStatusText(msg, 2)

    def _displayBitmap(self, widget, image, type):
        global __imgDir__

        # load the image
        imgPath = os.path.join(__imgDir__, image)
        Img = wx.Image(imgPath, type)
         # convert it to a wx.Bitmap, and put it on the wx.StaticBitmap
        widget.SetBitmap(wx.Bitmap(Img))

    # Overlay the thumbnail image with a fixed 'Play' image. Return the new image pathname
    def _overlayThumbnail(self, image, type):
        global __imgDir__

        imgSuffix = {
            wx.BITMAP_TYPE_JPEG: 'JPG',
            wx.BITMAP_TYPE_PNG: 'PNG',
            }
        d=os.path.dirname(image)
        f=os.path.basename(image)
        suffix = image.rsplit('.')[-1:][0]
        nf='%s-Play.%s.%s' % (f.rsplit('.',1)[0], suffix, imgSuffix[type])
        newThumbnailPathname = os.path.join(d,nf)

        if os.path.exists(newThumbnailPathname):
#            print('_overlayThumbnail(): Using existing file %s' % newThumbnailPathname)
            return newThumbnailPathname

        print('_overlayThumbnail(): Overlaying %s' % image)
        overlay = Image.open(image)
        background = Image.open(os.path.join(__imgDir__, "play2-160x120.png"))
        background = background.convert("RGB")
        overlay = overlay.convert("RGB")

        newThumbnail = Image.blend(background, overlay, 0.7) #0.8)
        newThumbnail.save(newThumbnailPathname)
        return newThumbnailPathname

    def _displayThumbnail(self, widget, image, type):
        global __thumbDir_
        global __imgDir__
        global thumbnailScaleFactor

        suffix = image.rsplit('.')[-1:][0]
        if suffix == 'MOV':
            newThumbnailPathname = self._overlayThumbnail(image, type)
            Img = wx.Image(newThumbnailPathname, type)
        else:
            Img = wx.Image(image, type)

        # get original size of the image
        try:
            (w,h) = Img.GetSize().Get()
        except:
#            print('Invalid thumbnail file %s' % (image))
            imgPath = os.path.join(__thumbDir__, __imgDir__, 'sad-smiley.png')
            Img = wx.Image(imgPath, wx.BITMAP_TYPE_PNG)
            (w,h) = Img.GetSize().Get()
        
        # convert it to a wx.Bitmap, and put it on the wx.StaticBitmap
        widget.SetBitmap(wx.Bitmap(Img.Scale(w*thumbnailScaleFactor, h*thumbnailScaleFactor)))

    def _init_topBoxSizer_Items(self, parent):
        global compactMode

        if compactMode:
            parent.Add(self.controlBoxSizer, 0, border=5, flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT)
        else:
            parent.Add(self.titleBoxSizer, 0, border=5, flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT)
            parent.Add(self.btnGridBagBoxSizer, 0, border=5, flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT)
        parent.Add(self.thumbBoxSizer, 1, border=5, flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT)
        parent.Add(self.bottomBoxSizer, 0, border=5, flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT)

    def _init_titleBoxSizer_Items(self, parent):
        parent.AddStretchSpacer(prop=1)
        parent.Add(self.staticBitmap1, 0, border=0, flag=wx.ALL | wx.ALIGN_CENTER)
        parent.AddStretchSpacer(prop=1)
        parent.Add(self.staticBitmap2, 0, border=0, flag=wx.ALL | wx.ALIGN_CENTER)

    def _init_btnGridBagBoxSizer_Items(self, parent):
        parent.Add(self.btnGridBagSizer, 0, border=5, flag=wx.ALL | wx.CENTER)

    def _init_btnGridBagSizer_Items(self, parent):
        sts1 = wx.BoxSizer(orient=wx.VERTICAL)
        sts1.Add(self.fileTypesTxt, 0, border=0, flag=wx.EXPAND)
        sts1.AddStretchSpacer(prop=1)
        sts1.Add(self.fileTypesChoice, 0, border=0, flag=wx.EXPAND)
        parent.Add(sts1, pos=(0, 0), flag=wx.ALL | wx.EXPAND, border=0)

        sts3 = wx.BoxSizer(orient=wx.VERTICAL)
#        sts3.AddStretchSpacer(prop=1)
        sts3.Add(self.fromCb, 0, border=0, flag=wx.EXPAND)
        sts3.AddStretchSpacer(prop=1)
        sts3.Add(self.dpc1, 0, border=0, flag=wx.EXPAND)
#        sts3.AddStretchSpacer(prop=1)
        parent.Add(sts3, pos=(0, 1), flag=wx.ALL| wx.EXPAND, border=0)

        sts4 = wx.BoxSizer(orient=wx.VERTICAL)
#        sts4.AddStretchSpacer(prop=1)
        sts4.Add(self.toCb, 0, border=0, flag=wx.EXPAND)
        sts4.AddStretchSpacer(prop=1)
        sts4.Add(self.dpc2, 0, border=0, flag=wx.EXPAND)
        parent.Add(sts4, pos=(0, 2), flag=wx.ALL, border=0)

        sts2 = wx.BoxSizer(orient=wx.VERTICAL)
        sts2.Add(self.fileSortTxt, 0, border=0, flag=wx.EXPAND)
        sts2.AddStretchSpacer(prop=1)
        sts2.Add(self.fileSortChoice, 0, border=0, flag=wx.EXPAND)
        parent.Add(sts2, pos=(0, 3), flag=wx.ALL | wx.EXPAND, border=0)

        parent.Add(20,0, pos=(0, 4)) # Some space before Cast button

        sts5 = wx.BoxSizer(orient=wx.VERTICAL)
        sts5.AddStretchSpacer(prop=1)
        sts5.Add(self.btnCast, 0, border=0, flag=wx.EXPAND)
#        sts5.AddStretchSpacer(prop=1)
        parent.Add(sts5, pos=(0, 5), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=0)
        parent.Add(self.castDeviceName, pos=(1, 5), flag=wx.ALL| wx.ALIGN_CENTER, border=0)

        parent.Add(10,0, pos=(0, 6)) # Some space after Cast button

        sts6 = wx.BoxSizer(orient=wx.VERTICAL)
        sts6.AddStretchSpacer(prop=1)
        sts6.Add(self.btnRew, 0, border=0, flag=wx.EXPAND)
#        sts6.AddStretchSpacer(prop=1)
        parent.Add(sts6, pos=(0, 7), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=0)

        sts7 = wx.BoxSizer(orient=wx.VERTICAL)
        sts7.AddStretchSpacer(prop=1)
        sts7.Add(self.btnPlay, 0, border=0, flag=wx.EXPAND)
#        sts7.AddStretchSpacer(prop=1)
        parent.Add(sts7, pos=(0, 8), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=0)

        sts8 = wx.BoxSizer(orient=wx.VERTICAL)
        sts8.AddStretchSpacer(prop=1)
        sts8.Add(self.btnStop, 0, border=0, flag=wx.EXPAND)
#        sts8.AddStretchSpacer(prop=1)
        parent.Add(sts8, pos=(0, 9), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=0)

        parent.Add(10,0, pos=(0, 10)) # Some space after Stop button

        parent.Add(self.btnCancel, pos=(0, 11), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=0)
        parent.Add(self.btnCommit, pos=(0, 12), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=0)

        parent.Add(10,0, pos=(0, 13))

        parent.Add(self.btnRescan, pos=(0, 14), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=0)

    # Used in compactMode only
    def _init_trafficBoxSizer_Items(self, parent):
        parent.AddStretchSpacer(prop=1)
        parent.Add(self.staticBitmap2, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=0)
        parent.AddStretchSpacer(prop=1)
    
    # Used in compactMode only
    def _init_controlBoxSizer_Items(self, parent):
        parent.Add(self.btnGridBagBoxSizer, 0, border=0, flag=wx.EXPAND | wx.TOP | wx.LEFT)
        parent.AddStretchSpacer(prop=1)
        parent.Add(self.trafficBoxSizer, 0, border=0, flag=wx.EXPAND | wx.TOP | wx.LEFT)

    def _init_thumbBoxSizer_Items(self, parent):
        # Thumbnail window
        parent.Add(self.noteBook, 1, border=0, flag=wx.EXPAND)
        parent.Add(0, 8, border=0, flag=0)
        # Button colors meaning
        parent.Add(self.thumbGridSizer2, 0, border=0, flag=wx.EXPAND)

    def _init_thumbGridSizer2_Items(self, parent):
        for entry in self.colorGrid:
            parent.Add(entry, 0, border=0, flag=wx.ALL)

    def _init_bottomBoxSizer1_Items(self, parent):
        parent.Add(self.btnHelp, 0, border=0, flag=0)
        parent.Add(8, 4, border=0, flag=0)
        parent.Add(self.btnQuit, 0, border=0, flag=0)

    def _init_bottomBoxSizer2_Items(self, parent):
        parent.Add(self.pltfInfo, 0, border=0, flag=wx.ALL | wx.ALIGN_LEFT)
        parent.AddStretchSpacer(prop=1)
        parent.Add(self.bottomBoxSizer3, 0, border=0, flag=wx.ALL | wx.ALIGN_CENTER)##
        parent.AddStretchSpacer(prop=1)
        parent.Add(self.bottomBoxSizer1, 0, border=0, flag=wx.ALL | wx.ALIGN_RIGHT)

    def _init_bottomBoxSizer3_Items(self, parent):
        parent.Add(self.btnSwitchMode, 0, border=0, flag=wx.ALL | wx.EXPAND)
        parent.Add(4, 0, border=0, flag=0)
        parent.Add(self.btnSwitchNetwork, 0, border=0, flag=wx.ALL | wx.EXPAND)

    def _init_bottomBoxSizer_Items(self, parent):
        parent.Add(self.statusBar1, 0, border=5, flag=wx.EXPAND | wx.ALL)
        parent.Add(0, 4, border=0, flag=0)
        parent.Add(self.bottomBoxSizer2, 0, border=5, flag=wx.ALL | wx.EXPAND)

    def _init_menuBar_Menus(self, parent):
        parent.Append(self.menuFile, '&File')
        parent.Append(self.menuHelp, '&Help')

    def _init_menuFile_Items(self, parent):
        menuItem = wx.MenuItem(parent, 100, '&Preferences\tCtrl+P')#wx.ID_PREFERENCES
        parent.Append(menuItem)
        self.Bind(wx.EVT_MENU, self.OnBtnPreferences, menuItem)
        parent.Enable(menuItem.Id,True)

        menuItem = wx.MenuItem(parent, 101, '&Clean Download Directory...')#wx.ID_CLEAR
        parent.Append(menuItem)
        self.Bind(wx.EVT_MENU, self.OnBtnCleanDownloadDir, menuItem)
        parent.Enable(menuItem.Id,True)

        menuItem = wx.MenuItem(parent, 102, '&Quit\tCtrl+Q')#wx.ID_EXIT
        parent.Append(menuItem)
        self.Bind(wx.EVT_MENU, self.OnBtnQuit, menuItem)
        parent.Enable(menuItem.Id,True)

    def _init_menuHelp_Items(self, parent):
        menuItem = wx.MenuItem(parent, 103, '&About')#wx.ID_ABOUT
        parent.Append(menuItem)
        self.Bind(wx.EVT_MENU, self.OnBtnAbout, menuItem)
        parent.Enable(menuItem.Id,True)

    def _init_utils(self):
        self.menuBar = wx.MenuBar()
        self.menuFile = wx.Menu()
        self.menuHelp = wx.Menu()

        self._init_menuFile_Items(self.menuFile)
        self._init_menuHelp_Items(self.menuHelp)
        self._init_menuBar_Menus(self.menuBar)

        self.SetMenuBar(self.menuBar)

        self.menuBar.Enable(100, True)
        self.menuBar.Enable(101, True)
        self.menuBar.Enable(102, True)
        self.menuBar.Enable(103, True)

    def _init_sizers(self):
        global compactMode

        # Top Level BoxSizer
        self.topBoxSizer = wx.BoxSizer(orient=wx.VERTICAL)

        # Title BoxSizer
        if not compactMode:
            self.titleBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        # File selection grid sizer in staticBoxSizer
        self.btnGridBagBoxSizer = wx.StaticBoxSizer(box=self.staticBox4, orient=wx.HORIZONTAL)
        self.btnGridBagSizer = wx.GridBagSizer(hgap=15,vgap=0)

        if compactMode:
            self.controlBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
            self.trafficBoxSizer = wx.BoxSizer(orient=wx.VERTICAL)

        # Thumbnails Box sizer in staticBoxSizer
        self.thumbBoxSizer = wx.StaticBoxSizer(box=self.staticBox3, orient=wx.VERTICAL)

        # Grid Sizer to contain LEDs for color labels
        self.thumbGridSizer2 = wx.FlexGridSizer(cols=10, hgap=8, rows=1, vgap=0)

        # Bottom button boxSizer
        self.bottomBoxSizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.bottomBoxSizer1 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.bottomBoxSizer2 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.bottomBoxSizer3 = wx.BoxSizer(orient=wx.HORIZONTAL)

        # Initialize each boxSizer
        self._init_topBoxSizer_Items(self.topBoxSizer)

        if not compactMode:
            self._init_titleBoxSizer_Items(self.titleBoxSizer)

        self._init_btnGridBagBoxSizer_Items(self.btnGridBagBoxSizer)
        self._init_btnGridBagSizer_Items(self.btnGridBagSizer)

        if compactMode:
            self._init_trafficBoxSizer_Items(self.trafficBoxSizer)
            self._init_controlBoxSizer_Items(self.controlBoxSizer)

        self._init_thumbBoxSizer_Items(self.thumbBoxSizer)
        self._init_thumbGridSizer2_Items(self.thumbGridSizer2)

        self._init_bottomBoxSizer_Items(self.bottomBoxSizer)
        self._init_bottomBoxSizer1_Items(self.bottomBoxSizer1)
        self._init_bottomBoxSizer2_Items(self.bottomBoxSizer2)
        self._init_bottomBoxSizer3_Items(self.bottomBoxSizer3)

        self.panel1.SetSizerAndFit(self.topBoxSizer)

    def _initialize(self):
        global __imgDir__
        global localFilesCnt
        global availRemoteFilesSorted
        global availRemoteFilesCnt
        global cameraConnected
        global osvmDownloadDir
        global FILE_COLORS_STATUS
        global remOldestDate
        global remNewestDate
        global viewMode
        global localFilesSorted
        global viewMode
        global pycc
        global networkSelector
        global vlcVideoViewer
        global fileSortRecentFirst

        # Package buttons list
        self.thumbButtons = list() #[]

        # List of scheduled operations on files. Format:
        # op[OP_STATUS|0]      = status (busy=1/off=0)
        # op[OP_FILENAME|1]    = base file name
        # op[OP_TYPE|2]        = operation #FILE_DOWNLOAD FILE_DELETE = 2
        # op[OP_FILEPATH|4]    = full pathname of local file for download
        # op[OP_SIZE|5]        = (size in bytes, block count)
        # op[OP_REMURL|6]      = full remote url to download
        # op[OP_INWGT|7]       = list of all assoc. widgets in InstallDialog frame
        # op[OP_INCOUNT|8]     = current block xfer counter for this op
        # op[OP_INSTEP|9]      = Installation step
        # op[OP_INLEDCOL|10]   = Installation LED color
        # op[OP_INLEDSTATE|11] = Installation LED state: ON/BLINK/OFF
        # op[OP_INTH|12]       = Installation thread
        # op[OP_INTICKS|13]    = Installation elapsed time

        self.opList = [[0] * OP_LASTIDX for i in range(MAX_OPERATIONS)]

        # Load Preferences
        self.prefs = Preferences(self)
        self.prefs._loadPreferences()

        self._init_utils()

        self.SetClientSize(wx.Size(1200, 680))
        self.Center()

        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self,
                               size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)
#        self.panel1.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

        self.panel1.Bind(wx.EVT_KEY_DOWN, self._onKeyPress)
        self.panel1.SetFocusIgnoringChildren()
        self.panel1.Bind(wx.EVT_LEFT_UP, self._setFocus)

        self.fileTypesTxt = wx.StaticText(label='File Type', parent=self.panel1, id=wx.ID_ANY)
        if not vlcVideoViewer:
            self.fileTypesChoice = wx.Choice(choices=[v for v in FILETYPES_NOVLC], 
                                             id=wx.ID_ANY, parent=self.panel1, style=0)
        else:
            self.fileTypesChoice = wx.Choice(choices=[v for v in FILETYPES], 
                                             id=wx.ID_ANY, parent=self.panel1, style=0)

        self.fileTypesChoice.SetToolTip('Select type of files to show/sync')
        self.fileTypesChoice.SetStringSelection(FILETYPES[0])
        self.fileTypesChoice.Bind(wx.EVT_CHOICE, self.OnFileTypesChoice, id=wx.ID_ANY)

        self.fromCb = wx.CheckBox(self.panel1, id=wx.ID_ANY, label='From Date')
        self.fromCb.SetValue(False)
        self.fromCb.Bind(wx.EVT_CHECKBOX, self.OnFromDate, id=wx.ID_ANY)

        self.dpc1 = wx.adv.DatePickerCtrl(self.panel1,
                                          style = wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY | wx.adv.DP_ALLOWNONE)

        self.toCb = wx.CheckBox(self.panel1, id=wx.ID_ANY, label='To Date')
        self.toCb.SetValue(False)
        self.toCb.Bind(wx.EVT_CHECKBOX, self.OnToDate, id=wx.ID_ANY)

        self.dpc2 = wx.adv.DatePickerCtrl(self.panel1,
                                          style = wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY | wx.adv.DP_ALLOWNONE)

        self._setDatePickerCtrl()

        self.castDeviceName = wx.StaticText(id=wx.ID_ANY,
                                            parent=self.panel1,
                                            size=(60,16),
                                            style=wx.ST_ELLIPSIZE_MIDDLE)
        self.castDeviceName.SetLabelMarkup("<span foreground='red'><small>%s</small></span>" % '            ')

        self.sortTypes = ['Recent First', 'Oldest First']
        self.fileSortTxt = wx.StaticText(label='Sorting Order', parent=self.panel1, id=wx.ID_ANY)
        self.fileSortChoice = wx.Choice(choices=[v for v in self.sortTypes], 
                                        id=wx.ID_ANY, parent=self.panel1, style=0)
        self.fileSortChoice.SetToolTip('Select sort order')
        self.fileSortChoice.SetStringSelection(self.sortTypes[0] if fileSortRecentFirst else self.sortTypes[1])
        self.fileSortChoice.Bind(wx.EVT_CHOICE, self.OnFileSortChoice, id=wx.ID_ANY)

        self.btnCast = wx.Button(label="Cast", size=wx.Size(32,32), parent=self.panel1, style=wx.NO_BORDER)
        self._displayBitmap(self.btnCast, 'cast-32.jpg', wx.BITMAP_TYPE_JPEG)
        self.btnCast.SetToolTip('Cast images to a GoogleCast')
        self.btnCast.Bind(wx.EVT_BUTTON, self.OnBtnCast)
        if not pycc:
            self.btnCast.Disable()

        self.btnRew = wx.Button(size=wx.Size(32,32), parent=self.panel1, style=wx.NO_BORDER)
        self._displayBitmap(self.btnRew, 'rew.png', wx.BITMAP_TYPE_PNG)
        self.btnRew.SetToolTip('Restart the Slideshow from beginning')
        self.btnRew.Bind(wx.EVT_BUTTON, self.OnBtnRew)

        self.btnPlay = wx.Button(name='btnPlay', size=wx.Size(32,32), parent=self.panel1, style=wx.NO_BORDER)
        self._displayBitmap(self.btnPlay, 'play.png', wx.BITMAP_TYPE_PNG)
        self.btnPlay.SetToolTip('Start the Slideshow')
        self.btnPlay.Bind(wx.EVT_BUTTON, self.OnBtnPlay)

        self.btnStop = wx.Button(size=wx.Size(32,32), parent=self.panel1, style=wx.NO_BORDER)
        self._displayBitmap(self.btnStop, 'stop.png', wx.BITMAP_TYPE_PNG)
        self.btnStop.SetToolTip('Stop the Slideshow')
        self.btnStop.Bind(wx.EVT_BUTTON, self.OnBtnStop)

        for dpc in [self.dpc1,self.dpc2]:
            dpc.Disable()

        self.btnRescan = wx.Button(id=wx.ID_REFRESH, label='Refresh',
                                   name='btnRescan', parent=self.panel1, style=0)
        self.btnRescan.SetToolTip('Rescan configuration')
        self.btnRescan.Bind(wx.EVT_BUTTON, self.OnBtnRescan)

        # Create the LEDS and Static Texts to show colors meaning
        for i in range(len(FILE_COLORS_STATUS)):
            led = PkgColorLED(self.panel1)
            led.SetState(i)
            self.colorGrid.append(led)
            self.colorGrid.append(wx.StaticText(self.panel1, label=FILE_COLORS_STATUS[i]))

        self.btnCancel = wx.Button(id=wx.ID_CANCEL, label='Cancel All',
                                   parent=self.panel1, style=0)
        self.btnCancel.SetToolTip('Cancel all pending requests')
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnBtnCancel)

        self.btnCommit = wx.Button(id=wx.ID_OK, label='Commit',
                                   parent=self.panel1, style=0)
        self.btnCommit.SetToolTip('Commit all pending requests')
        self.btnCommit.Bind(wx.EVT_BUTTON, self.OnBtnCommit)
        if not cameraConnected:
            self.btnCancel.Disable()
            self.btnCommit.Disable()

        # The staticBox3 label MUST end with the string 'Page:' (will be updated automagically)
        if viewMode:
            lbl = ' Available Local Files: %d.  Page:' % localFilesCnt
        else:
            lbl = ' Available Remote Files (on camera).  Page:'

        self.staticBox3 = wx.StaticBox(id=wx.ID_ANY, label=lbl, parent=self.panel1, 
                                       pos=wx.Point(10, 199), size=wx.Size(1192, 100), style=0)
        if viewMode:
            lbl = ' File Viewer Control '
        else:
            lbl = ' Select Files to Sync... '
        self.staticBox4 = wx.StaticBox(id=wx.ID_ANY, label=lbl, parent=self.panel1, 
                                       pos=wx.Point(10, 64), style=0)

        self._createThumbnailPanel()

        self.statusBar1 = wx.StatusBar(id=wx.ID_ANY,parent=self.panel1, style=0)
        self.statusBar1.SetToolTip('Status')
        self.statusBar1.SetFont(wx.Font(11, wx.SWISS, wx.ITALIC, wx.NORMAL, False, 'foo'))

        # Configure the status bar with 2 fields
        self.statusBar1.SetFieldsCount(3)
        self.statusBar1.SetStatusText(_myName_, 0)
        self.statusBar1.SetStatusText('View Mode' if viewMode else 'Sync Mode', 1)

        if not cameraConnected or viewMode:
            msg = '%d local file(s)' % (localFilesCnt)
            self._setOfflineMode()
        else:
            msg = '%d local file(s), %d file(s) available on camera' % (localFilesCnt, availRemoteFilesCnt)

        self.updateStatusBar(msg)

        if __system__ == 'Windows':
            # Get win32api version
            fvi = win32api.GetFileVersionInfo(win32api.__file__, '\\')
            pywin32Version = fvi['FileVersionLS'] >> 16
            print("pywin32Version:", pywin32Version)
            label= '%s: Version: %s\n%s\nPython (%dbits): %s wxpython: %s pywin32: %s' % (_myName_, _myVersion_, (platform.platform()), __pythonBits__, __pythonVersion__, wx.version(), pywin32Version)
        else:
            label= '%s: %s\n%s\nPython (%dbits): %s wxpython: %s' % (_myName_, _myVersion_,  (platform.platform()), __pythonBits__, __pythonVersion__, wx.version())            

        self.pltfInfo = wx.StaticText(label=label, id=wx.ID_ANY, parent=self.panel1)
        self.pltfInfo.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Ubuntu'))

        self.btnSwitchMode = wx.Button(id=wx.ID_ANY, parent=self.panel1, style=0)
        self.btnSwitchMode.SetLabel('Switch to Sync Mode' if viewMode else 'Switch to View Mode')
        self.btnSwitchMode.Bind(wx.EVT_BUTTON, self.OnBtnSwitchMode)

        self.btnSwitchNetwork = wx.Button(id=wx.ID_ANY, label='Select Camera', 
                                          parent=self.panel1, style=0)
        self.btnSwitchNetwork.Bind(wx.EVT_BUTTON, self.OnBtnSwitchNetwork)
        if __system__ != 'Darwin' or not networkSelector:
            self.btnSwitchNetwork.Disable()

        self.btnHelp = wx.Button(id=wx.ID_HELP, label='Help', parent=self.panel1, style=0)
        self.btnHelp.Bind(wx.EVT_BUTTON, self.OnBtnHelp)

        self.btnQuit = wx.Button(id=wx.ID_EXIT, label='Quit', parent=self.panel1, style=0)
        self.btnQuit.SetToolTip('Quit Application')
        self.btnQuit.Bind(wx.EVT_BUTTON, self.OnBtnQuit)

        if not compactMode:
            self.staticBitmap1 = wx.StaticBitmap(bitmap=wx.NullBitmap, id=wx.ID_ANY, parent=self.panel1, style=0)
            self._displayBitmap(self.staticBitmap1, "OSVM5.png", wx.BITMAP_TYPE_PNG)

        self.staticBitmap2 = wx.StaticBitmap(bitmap=wx.NullBitmap,
                                             id=wx.ID_ANY, parent=self.panel1, style=0)
        self.staticBitmap2.SetToolTip('Network Status:\nRED: No Network\nGREEN:Camera OK')

        # Update connection status indicator
        self._updateConnectionStatus()

        self._init_sizers()

        self.SendSizeEvent()

        # Initialize statusBar1
        self._initStatusBar1()

        w0,h0 = self.panel1.GetSize()
        w1,h1 = self.statusBar1.GetSize()

    def _setDatePickerCtrl(self):
        global viewMode
        global remOldestDate
        global remNewestDate

        if viewMode:
            if not localFilesCnt:	# No local file available
                today = datetime.date.today()
                remNewestDate = today.strftime("%m/%d/%Y")
                remOldestDate = '01/01/1970'
                print('remOldestDate:',remOldestDate)
                print('remNewestDate:',remNewestDate)
            else:
                remNewestDate = secondsTomdY(localFilesSorted[0][1][F_DATE])
                remOldestDate = secondsTomdY(localFilesSorted[-1][1][F_DATE])
                print('remOldestDate:',remOldestDate,localFilesSorted[0][1][F_DATE])
                print('remNewestDate:',remNewestDate,localFilesSorted[-1][1][F_DATE])
        else:
            if not availRemoteFilesCnt:	# No remote file available
                today = datetime.date.today()
                remNewestDate = today.strftime("%m/%d/%Y")
                remOldestDate = '01/01/1970'
                print('remOldestDate:',remOldestDate)
                print('remNewestDate:',remNewestDate)
            else:
                remNewestDate = getHumanDate(availRemoteFilesSorted[0][1][F_DATE])
                remOldestDate = getHumanDate(availRemoteFilesSorted[-1][1][F_DATE])
                print('remOldestDate:',remOldestDate,availRemoteFilesSorted[0][1][F_DATE])
                print('remNewestDate:',remNewestDate,availRemoteFilesSorted[-1][1][F_DATE])

        self._dpcSetValue(remOldestDate, self.dpc1, remNewestDate, self.dpc2)

    def _dpcSetValue(self, date1, w1, date2, w2):
        if date1:
            d1 = wx.DateTime.FromDMY(int(date1.split('/')[1]),
                                     int(date1.split('/')[0]) - 1,	# Month starts from 0
                                     int(date1.split('/')[2]))
            w1.SetValue(d1)

        if date2:
            d2 = wx.DateTime.FromDMY(int(date2.split('/')[1]),
                                     int(date2.split('/')[0]) - 1,	# Month starts from 0
                                     int(date2.split('/')[2]))
            w2.SetValue(d2)

    def _wxdate2pydate(self, date):
        assert isinstance(date, wx.DateTime)
        if date.IsValid():
            ymd = list(map(int, date.FormatISODate().split('-')))
            return ymd
        else:
            return None

    def _setOfflineMode(self):
        # Disable some menus
        disableMenuItems = []
        for item in disableMenuItems:
            id = self.menuBar.FindMenuItem(item[0],item[1])
            self.menuBar.Enable(id, False)

    def _setFocus(self, event):
        print ("focus given to panel")
        self.panel1.SetFocusIgnoringChildren()
 
    # KeyEvent handler
    def _onKeyPress(self, event):
        keycode   = event.GetKeyCode()
        cmddown   = event.CmdDown()
        modifiers = event.GetModifiers()
        event.Skip()

    def _initStatusBar1(self):
        global viewMode

        text = 'Processing pending operations...'
        self.textlen = len(text)

        f = self.statusBar1.GetFont()
        dc = wx.WindowDC(self.statusBar1)
        dc.SetFont(f)

        # Compute length of 1st field of the status bar (to contain _myName_)
        textWidth,dummy = dc.GetTextExtent(_myName_)
        modeWidth,dummy = dc.GetTextExtent('View Mode' if viewMode else 'Sync Mode')
        self.statusBar1.SetStatusWidths([textWidth + 20, modeWidth + 20, -1])
        #print ('FieldRect:',(self.statusBar1.GetFieldRect(0)))
        #print ('FieldRect:',(self.statusBar1.GetFieldRect(1)))

        # Size of the text to display (pixel)
        textWidth,dummy = dc.GetTextExtent(text)
        # Size of a space (pixel)
        spaceWidth,dummy = dc.GetTextExtent(" ")
        # Size of the status bar (pixel)
        sbWidth,dummy = self.statusBar1.GetSize()
        # How many space characters can fit ?
        nbspaces = int( ((sbWidth - textWidth) / spaceWidth) )
        # Total # of characters in the statusbar
        self.displen = self.textlen + nbspaces
        self.display = [' '] * self.displen    # Fill the display with spaces

        print("_initStatusBar1():",textWidth,sbWidth,spaceWidth,nbspaces,self.displen)

    # stop statusBar1 animation
    def finish(self):
        if self.timer.IsRunning():
            print ('finish(): Stopping animation')
            self.timer.Stop()

        msg = 'All scheduled operations finished/Cancelled'
        self.updateStatusBar(msg)

    def _updateLEDs(self):
        for i in range(int(len(self.colorGrid) / 2)):
            self.colorGrid[i*2].SetState(i)

    #### Events ####
    def OnEraseBackground(self, evt):
        """ Add a picture to the background """
        dc = evt.GetDC()

        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        bmp = wx.Bitmap("images/maeva-1250x938.jpg")
        dc.DrawBitmap(bmp, 0, 0)

    def OnSize(self, event):
        sbWidth,dummy = self.statusBar1.GetSize()
        print("OnSize(): Resize event",sbWidth)

    def OnThumbButtonRightDown(self, event):
        button = event.GetEventObject()

        # Retrieve the button in self.thumbButtons
        # Each entry in thumbButtons[] is of form: [widget, file, fgcol, bgcol]
        found = False
        for entry in self.thumbButtons:
            if entry[0] == button:
                found = True
                break
        if not found:
            print('OnThumbButtonRightDown(): Button not found')
            FileOperationMenu(self, button, self.opList)
            return

        FileOperationMenu(self, button, self.opList)

        # Check if an operation is scheduled for this button and colorize the
        # button accordingly
        for op in self.opList:
            if op[OP_STATUS] and op[OP_FILENAME] == entry[1]:
                entry[0].SetBackgroundColour(fileColors[FILE_OP_PENDING][0])
                entry[0].SetForegroundColour(fileColors[FILE_OP_PENDING][1])
                pendingOpsCnt = self.pendingOperationsCount()
                statusBarMsg = 'Request successfully scheduled. %d request(s) in the queue' % (pendingOpsCnt)
                self.updateStatusBar(statusBarMsg)
                self.btnCommit.Enable()
                self.btnCancel.Enable()
                break

        self.panel1.Refresh()

    # Left Click on a File button, zoom in the thumbnail
    def OnThumbButton(self, event):
        global __thumbDir__

        button = event.GetEventObject()

        found = False
        # Retrieve associated button.
        # Each entry in thumbButtons[] is: [widget, filename, fgcol, bgcol]
        for entry in self.thumbButtons:
            if entry[0] == button:
                found = True
                break
        if not found:
            return

        thumbFilePath = os.path.join(__thumbDir__, entry[1])
        dlg = ThumbnailDialog(self, thumbnail=thumbFilePath)
        ret = dlg.ShowModal()
        dlg.Destroy()
        event.Skip()

    def _OnFlatNoteBookPageChanged(self, event):
        self._updateStaticBox3Label('_OnFlatNoteBookPageChanged')
        event.Skip()

    def _OnFlatNoteBookPageClosed(self, event):
        event.Skip()

    def OpenExternalViewer(self, event):
        global osvmDownloadDir

        externalViewer = {
            'JPG':'/Applications/Preview.app',
            'MOV':'/Applications/QuickTime Player.app',
            # What about ORF and MPO files ??? XXX
            }

        button = event.GetEventObject()

        found = False
        # Retrieve associated button entry in thumbButtons[].
        # Each entry in thumbButtons[] is: [widget, filename, fgcol, bgcol]
        for entry in self.thumbButtons:
            if entry[0] == button:
                found = True
                break
        if not found:
            event.Skip()
            return

        suffix = entry[1].split('.')[1]
        filePath = os.path.join(osvmDownloadDir, entry[1])
        subprocess.call(
            ["/usr/bin/open", "-W", "-n", "-a", externalViewer[suffix], filePath]
            )
        event.Skip()

    def LaunchViewer(self, event):
        global osvmDownloadDir
        global useExternalViewer
        global castMediaCtrl
        global castDevice
        global serverAddr

        button = event.GetEventObject()
        id = event.GetId()

        found = False
        # Retrieve associated button entry in thumbButtons[].
        # Each entry in thumbButtons[] is: [widget, filename, fgcol, bgcol]
        for entry in self.thumbButtons:
            if entry[0] == button:
                found = True
                break
        if not found:
            event.Skip()
            return

        fname = entry[1]
        suffix = fname.split('.')[1]

        if castMediaCtrl:
            # Suspend the slideshow if active
            if self.ssThrLock.acquire(blocking=False) == False:	# Block the thread if active
                print('Lock is already set, should have blocked, so... Slideshow is paused')
            self._displayBitmap(self.btnPlay, 'play.png', wx.BITMAP_TYPE_PNG)
            self.btnPlay.SetName('btnPlay')

            fileURL = 'http://%s:%s/%s' % (serverAddr, SERVER_HTTP_PORT, fname)
            print('Loading URL: %s' % fileURL)

            # Update status message
            msg = 'Casting %s to %s' % (fname,castDevice.name)
            self.updateStatusBar(msg)

            mediaFileType = { 'JPG':'image/jpg', 'MOV':'video/mov' }
            castMediaCtrl.play_media(fileURL, mediaFileType[suffix])
            if suffix == 'MOV':
                while castMediaCtrl.status.player_state == 'PLAYING':
                    time.sleep(1)
            else:
                castMediaCtrl.block_until_active()
            event.Skip()
            return

        filePath = os.path.join(osvmDownloadDir, fname)

        if useExternalViewer:
            suffix = entry[1].split('.')[1]
            externalViewer = {
                'JPG':'/Applications/Preview.app',
                'MOV':'/Applications/QuickTime Player.app',
                # What about ORF and MPO files ??? XXX
                }
            subprocess.call(
                ["/usr/bin/open", "-W", "-n", "-a", externalViewer[suffix], filePath]
                )
            event.Skip()
            return

        # Use internal viewer
        # Update status message
        msg = 'Launching internal viewer...'
        self.updateStatusBar(msg)

        print('Launching MediaViewer')
        dlg = MediaViewer(filePath)
        ret = dlg.ShowModal()
        dlg.Destroy()
        print('Exit of MediaViewer. ret:%d' % ret)

    def OnBtnSwitchMode(self, event):
        global viewMode
        global autoSwitchToFavoriteNetwork
        global favoriteNetwork

        button = event.GetEventObject()
        print('OnBtnSwitchMode(): Switching to: %s Mode' % ('Sync' if viewMode else 'View'))
        viewMode = not viewMode
        if viewMode:
            button.SetLabel('Switch to Sync Mode')
        else:
            button.SetLabel('Switch to View Mode')
            # Switch to favorite network
            if autoSwitchToFavoriteNetwork and favoriteNetwork != ('None','None'):
                if switchToFavoriteNetwork():
                    msg = 'Switch to favorite network has failed'
                    self.updateStatusBar(msg)
                    print(msg)
                    self.panel1.Refresh()

        # Simulate a 'Rescan' event
        evt = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self.btnRescan.GetId())
        evt.SetEventObject(self.btnRescan)
        wx.PostEvent(self.btnRescan, evt)

    def OnBtnSwitchNetwork(self, event):
        # Switch the network
        dlg = WifiDialog(self)
        ret = dlg.ShowModal()
        dlg.Destroy()
        if ret != wx.ID_CANCEL:
            # Simulate a 'Rescan' event
            evt = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self.btnRescan.GetId())
            evt.SetEventObject(self.btnRescan)
            wx.PostEvent(self.btnRescan, evt)
        event.Skip()

    def OnBtnHelp(self, event):
        dlg = HelpDialog()
        dlg.ShowModal()
        dlg.Destroy()
        event.Skip()

    def OnBtnPreferences(self, event):
        dlg = PreferencesDialog(self.prefs)
        ret = dlg.ShowModal()
        # Check if a Rescan is required
        self.needRescan = dlg.isRescanRequired()
        dlg.Destroy()
        if ret == wx.ID_APPLY and self.needRescan:
            # Simulate a 'Rescan' event
            evt = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self.btnRescan.GetId())
            evt.SetEventObject(self.btnRescan)
            wx.PostEvent(self.btnRescan, evt)

    def OnBtnCleanDownloadDir(self, event):
        global osvmDownloadDir

        downloadDir = osvmDownloadDir
        dlg = CleanDownloadDirDialog(self, download=downloadDir)
        dlg.ShowModal()
        dlg.Destroy()
        event.Skip()

    def OnBtnQuit(self, event):
        global httpServer

        if askBeforeExit:
            dlg = wx.MessageDialog(None, 'Do you really want to quit?', 'Question',
                                   wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            ret = dlg.ShowModal()
            if ret == wx.ID_YES:
                if savePreferencesOnExit:
                    self.prefs._savePreferences()
                if httpServer:
                    httpServer.kill()
                self.Destroy()    # Bye Bye
        else:
            if savePreferencesOnExit:
                self.prefs._savePreferences()

#        self._MakeModal(False) # Re-enables parent window
#        if self.eventLoop:
#            self.eventLoop.Exit()
#        self.Destroy()    # Bye Bye
        self.parent.Destroy()

    def OnClose(self, event):
        event.Skip()
        self.Destroy()

    def OnBtnAbout(self, event):
        global __imgDir__

        description = """Olympus Sync & View Manager (aka OSVM) is a powerful tool
..... to manage files between a Olympus camera and your laptop....
"""
        license = """OSVM License Info HERE"""

        info = wx.adv.AboutDialogInfo()

        imgPath = os.path.join(__imgDir__, 'butterfly-48x48x32.png')
        info.SetIcon(wx.Icon(imgPath, wx.BITMAP_TYPE_PNG))
        info.SetName(_myLongName_)
        info.SetVersion('%s' % _myVersion_)
        info.SetDescription(description)
        info.SetCopyright('(C) 2018 Didier Poirot')
        info.SetWebSite('https://github.com/hercule115/OSVM')
        info.SetLicense(license)
        info.AddDeveloper('Didier Poirot')
        info.AddDocWriter('Didier Poirot')
        #info.AddArtist('Didier Poirot')
        #info.AddTranslator('Didier Poirot')

        wx.adv.AboutBox(info)

    def _selectFiles(self, fileType):
        if viewMode:
            cnt = self._selectFilesByDate(fileType)
        else:
            cnt = self._syncFiles(fileType)
        pendingOpsCnt = self.pendingOperationsCount()
        msg = '%d requests successfully scheduled, %d in the queue' % (cnt, pendingOpsCnt)
        self.updateStatusBar(msg)
        self.panel1.Refresh()

    def OnFileTypesChoice(self, event):
        idx = self.fileTypesChoice.GetSelection()
        self.fileType = FILETYPES[idx]
        if self.fileType == 'JPG' or self.fileType == 'MOV':
            self.OnBtnCancel(1)
            self._selectFiles(self.fileType)
        elif self.fileType == 'ALL':
            self._selectFiles('JPG')
            self._selectFiles('MOV')
        else:
            # Clear all pending requests
            self.OnBtnCancel(1)

        event.Skip()

    def OnSyncImages(self, event):
        global viewMode

        button = event.GetEventObject()

        if self.cb3.GetValue():	# If Sync All button is set, nothing to do.
            event.Skip()
            return

        # If True, must browse the availRemoteFiles[] and schedule an operation for all available pictures
        if button.GetValue():
            print ('Must schedule a request for selected/all images')
            if viewMode:
                cnt = self._selectFilesByDate('JPG')
            else:
                cnt = self._syncFiles('JPG')
            pendingOpsCnt = self.pendingOperationsCount()
            msg = '%d requests successfully scheduled, %d in the queue' % (cnt, pendingOpsCnt)
        else:
            print ('Must un-schedule all pending requests for images')
            if viewMode:
                cnt = self._unSelectFiles('JPG')
            else:
                cnt = self._unSyncFiles('JPG')
            pendingOpsCnt = self.pendingOperationsCount()
            msg = '%d requests successfully cleared, %d in the queue' % (cnt, pendingOpsCnt)
        self.updateStatusBar(msg)
        self.panel1.Refresh()
        event.Skip()

    def OnSyncVideos(self, event):
        global viewMode

        button = event.GetEventObject()

        if self.cb3.GetValue():	# If Sync All button is set, nothing to do.
            event.Skip()
            return

        if button.GetValue():
            print ('Must schedule a request for selected/all videos')
            if viewMode:
                cnt = self._selectFilesByDate('MOV')
            else:
                cnt = self._syncFiles('MOV')
            pendingOpsCnt = self.pendingOperationsCount()
            msg = '%d requests successfully scheduled, %d in the queue' % (cnt, pendingOpsCnt)
        else:
            print ('Must un-schedule all pending requests for videos')
            if viewMode:
                cnt = self._unSelectFiles('MOV')
            else:
                cnt = self._unSyncFiles('MOV')
            pendingOpsCnt = self.pendingOperationsCount()
            msg = '%d requests successfully cleared, %d in the queue' % (cnt, pendingOpsCnt)
        self.updateStatusBar(msg)
        self.panel1.Refresh()
        event.Skip()

    def OnSyncAll(self, event):
        button = event.GetEventObject()

        if button.GetValue():
            # Clear pending request list
            self._clearAllRequests()
            cnt1 = self._syncFiles('JPG')
            cnt2 = self._syncFiles('MOV')
            pendingOpsCnt = self.pendingOperationsCount()
            msg = '%d requests successfully scheduled, %d in the queue' % (cnt1+cnt2, pendingOpsCnt)
        else:
            cnt1 = self._unSyncFiles('JPG')
            cnt2 = self._unSyncFiles('MOV')

            if self.cb1.GetValue():
                cnt1 = self._syncFiles('JPG')
            if self.cb2.GetValue():
                cnt2 = self._syncFiles('MOV')
            pendingOpsCnt = self.pendingOperationsCount()
            msg = '%d requests successfully cleared, %d in the queue' % (cnt1+cnt2, pendingOpsCnt)
        self.updateStatusBar(msg)
        self.panel1.Refresh()
        event.Skip()

    def OnFromDate(self, event):
        global remOldestDate
        global remNewestDate

        button = event.GetEventObject()

        if button.GetValue():	# Take FROM date into account
            dlg = dateDialog(remOldestDate, remNewestDate)
            ret = dlg.ShowModal()
            if ret == wx.ID_OK:
                fd = dlg.dpc.GetDate()
                self.fromDate = '%d/%d/%d' % (fd.month+1,fd.day,fd.year) # month, day, year
            else:
                self.fromDate = remOldestDate
                button.SetValue(False)
            dlg.Destroy()
        else:
            self.fromDate = remOldestDate

        self._dpcSetValue(self.fromDate, self.dpc1, None, self.dpc2)

        print ('OnFromDate(): fromDate: %s. Clearing pending list' % self.fromDate)
        self._clearAllRequests()

        if self.fileType == 'JPG':
            print ('Must schedule a request for available images matching interval')
            if viewMode:
                cnt = self._selectFilesByDate('JPG')
            else:
                cnt = self._syncFiles('JPG')
            pendingOpsCnt = self.pendingOperationsCount()
            msg = '%d requests successfully scheduled, %d in the queue' % (cnt, pendingOpsCnt)
            self.updateStatusBar(msg)
            self.panel1.Refresh()

        if self.fileType == 'MOV':
            print ('Must schedule a request for available video matching interval')
            if viewMode:
                cnt = self._selectFilesByDate('MOV')
            else:
                cnt = self._syncFiles('MOV')
            pendingOpsCnt = self.pendingOperationsCount()
            msg = '%d requests successfully scheduled, %d in the queue' % (cnt, pendingOpsCnt)
            self.updateStatusBar(msg)
            self.panel1.Refresh()

        if self.fileType == 'ALL':
            print ('Must schedule a request for available image/video matching interval')
            if viewMode:
                cnt1 = self._selectFilesByDate('JPG')
                cnt2 = self._selectFilesByDate('MOV')
            else:
                cnt1 = self._syncFiles('JPG')
                cnt2 = self._syncFiles('MOV')
            pendingOpsCnt = self.pendingOperationsCount()
            msg = '%d requests successfully scheduled, %d in the queue' % (cnt1+cnt2, pendingOpsCnt)
            self.updateStatusBar(msg)
            self.panel1.Refresh()

        #dumpOperationList("Pending Request List", self.opList)
        event.Skip()

    def OnToDate(self, event):
        global remOldestDate
        global remNewestDate

        button = event.GetEventObject()

        if button.GetValue():	# Take TO date into account
            dlg = dateDialog(remOldestDate, remNewestDate)
            if dlg.ShowModal() == wx.ID_OK:
                td = dlg.dpc.GetDate()
                self.toDate = '%d/%d/%d' % (td.month+1,td.day,td.year)
            else:
                self.toDate = remNewestDate
                button.SetValue(False)
            dlg.Destroy()
        else:
            self.toDate = remNewestDate

        self._dpcSetValue(None, self.dpc1, self.toDate, self.dpc2)

        print ('OnToDate(): Clearing pending list')
        self._clearAllRequests()

        if self.fileType == 'JPG':
            print ('Must schedule a request for available images matching inteval')
            if viewMode:
                cnt = self._selectFilesByDate('JPG')
            else:
                cnt = self._syncFiles('JPG')
            pendingOpsCnt = self.pendingOperationsCount()
            msg = '%d requests successfully scheduled, %d in the queue' % (cnt, pendingOpsCnt)
            self.updateStatusBar(msg)
            self.panel1.Refresh()

        if self.fileType == 'MOV':
            print ('Must schedule a request for available video matching inteval')
            if viewMode:
                cnt = self._selectFilesByDate('MOV')
            else:
                cnt = self._syncFiles('MOV')
            pendingOpsCnt = self.pendingOperationsCount()
            msg = '%d requests successfully scheduled, %d in the queue' % (cnt, pendingOpsCnt)
            self.updateStatusBar(msg)
            self.panel1.Refresh()

        if self.fileType == 'ALL':
            print ('Must schedule a request for available image/video matching interval')
            if viewMode:
                cnt1 = self._selectFilesByDate('JPG')
                cnt2 = self._selectFilesByDate('MOV')
            else:
                cnt1 = self._syncFiles('JPG')
                cnt2 = self._syncFiles('MOV')
            pendingOpsCnt = self.pendingOperationsCount()
            msg = '%d requests successfully scheduled, %d in the queue' % (cnt1+cnt2, pendingOpsCnt)
            self.updateStatusBar(msg)
            self.panel1.Refresh()

        #dumpOperationList("Pending Request List", self.opList)
        event.Skip()

    def OnDateChanged(self, event):
        global remOldestDate
        global remNewestDate

        fd = self.dpc1.GetValue()
        td = self.dpc2.GetValue()

        self.fromDate = remOldestDate
        if self.fromCb.GetValue():	# Check if From Date cb is set
            self.fromDate = self._wxdate2pydate(fd)
            print('From Date:',self.fromDate)

        self.toDate = remNewestDate
        if self.toCb.GetValue():	# Check if To Date cb is set
            self.toDate = self._wxdate2pydate(td)
            print('To Date:',self.toDate)

        #print ('Date interval: From: %s To: %s' % (self.fromDate, self.toDate))
        print ('Clearing pending list')
        self._clearAllRequests()

        if self.fileType == 'JPG':
            print('Must schedule a request for available images matching interval')
            cnt = self._syncFiles('JPG')
            pendingOpsCnt = self.pendingOperationsCount()
            msg = '%d requests successfully scheduled, %d in the queue' % (cnt, pendingOpsCnt)
            self.updateStatusBar(msg)
            self.panel1.Refresh()

        if self.fileType == 'MOV':
            print ('Must schedule a request for available video matching interval')
            cnt = self._syncFiles('MOV')
            pendingOpsCnt = self.pendingOperationsCount()
            msg = '%d requests successfully scheduled, %d in the queue' % (cnt, pendingOpsCnt)
            self.updateStatusBar(msg)
            self.panel1.Refresh()

        if self.fileType == 'ALL':
            print ('Must schedule a request for available image/video matching interval')
            cnt1 = self._syncFiles('JPG')
            cnt2 = self._syncFiles('MOV')
            pendingOpsCnt = self.pendingOperationsCount()
            msg = '%d requests successfully scheduled, %d in the queue' % (cnt1+cnt2, pendingOpsCnt)
            self.updateStatusBar(msg)
            self.panel1.Refresh()

        #dumpOperationList("Pending Request List", self.opList)
        event.Skip()

    def OnFileSortChoice(self, event):
        global fileSortRecentFirst

        idx = self.fileSortChoice.GetSelection()
        if (fileSortRecentFirst and not idx) or (not fileSortRecentFirst and idx):
            print('OnFileSortChoice(): Nothing to do')
        else:
            fileSortRecentFirst = (idx == 0)
        # Simulate a 'Rescan' event
#        self._btnRescan = getattr(self, "btnRescan")
#        evt = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self._btnRescan.GetId())
        evt = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self.btnRescan.GetId())
        evt.SetEventObject(self.btnRescan)
        wx.PostEvent(self.btnRescan, evt)
        event.Skip()

    def OnBtnCast(self, event):
        global castMediaCtrl
        global castDevice

        button = event.GetEventObject()

        castMediaCtrl = initPyChromeCast()
        if not castMediaCtrl:
            print('No ChromeCast detected :(')
            button.SetWindowStyleFlag(wx.NO_BORDER)
            self.castDeviceName.SetLabelMarkup("<span foreground='red'><small>%s</small></span>" % '            ')
        else:
            button.SetWindowStyleFlag(wx.BORDER_RAISED)
            self.castDeviceName.SetLabelMarkup("<span foreground='red'><small>%s</small></span>" % castDevice.name)

        button.Refresh()
        event.Skip()

    def OnBtnRew(self, event):
        global slideShowNextIdx

        slideShowNextIdx = 0
        print('Restarting Slideshow from beg.')
        event.Skip()

    def OnBtnPlay(self, event):
        global viewMode
        global castDevice
        global localFilesSorted
        global slideShowNextIdx
        global slideShowLastIdx

        button = event.GetEventObject()
        print('OnBtnPlay triggered: %s' % button.GetName())

        if not castMediaCtrl:	# Cast device not initialized
            print('No Cast Device, Starting Local Slideshow')

        if button.GetName() == 'btnPlay':
            print('Slideshow is starting')

            # Build a list of selected files
            self.mediaFileList = list()
            for i in range(len(self.opList)):
                if self.opList[i][OP_STATUS] and self.opList[i][OP_TYPE] == FILE_SELECT:
                    fileName = self.opList[i][OP_FILENAME]
                    self.mediaFileList.append([fileName]) # a tuple
            print('%d files selected' % len(self.mediaFileList))

            if not castMediaCtrl:
                msg = 'Starting Local Slideshow'
                self.updateStatusBar(msg)

                button.Disable()
                # If no image is selected, browse thru all the images
                if self.mediaFileList:
                    dlg = MediaViewer(self.mediaFileList)
                else:
                    dlg = MediaViewer(localFilesSorted)
                ret = dlg.ShowModal()
                dlg.Destroy()
                # Clear opList
                if viewMode:
                    cnt = self._unSelectFiles('JPG')
                    cnt += self._unSelectFiles('MOV')
                else:
                    cnt = self._unSyncFiles('JPG')
                    cnt += self._unSyncFiles('MOV')
                print('%d selected files have been cleared' % (cnt))
                self.Refresh()
                button.Enable()
            else:
                msg = 'Starting Slideshow on %s' % (castDevice.name)
                self.updateStatusBar(msg)

                if not self.mediaFileList:
                    self.mediaFileList = localFilesSorted
                slideShowLastIdx = len(self.mediaFileList)
                self.ssThrLock.release()
                self._displayBitmap(button, 'pause.png', wx.BITMAP_TYPE_PNG)
                button.SetName('btnPause')
                button.SetToolTip('Pause the Slideshow')
        else:
            # Must pause the Slideshow
            msg = 'Pausing the Slideshow'
            self.updateStatusBar(msg)
            self.ssThrLock.acquire()	# Block the thread
            print('Slideshow is paused')
            msg = ''
            self.updateStatusBar(msg)
            self._displayBitmap(button, 'play.png', wx.BITMAP_TYPE_PNG)
            button.SetName('btnPlay')
            button.SetToolTip('Start the Slideshow')
        event.Skip()

    def OnBtnStop(self, event):
        global slideShowNextIdx

        msg = 'Stopping the Slideshow'
        self.updateStatusBar(msg)
        if self.ssThrLock.acquire(blocking=False) == False:	# Block the thread if active
            print('Lock is already set, should have blocked, so... Slideshow is paused')
        print('Slideshow is stopped')
        msg = ''
        self.updateStatusBar(msg)
        self._displayBitmap(self.btnPlay, 'play.png', wx.BITMAP_TYPE_PNG)
        self.btnPlay.SetName('btnPlay')
        self.btnPlay.SetToolTip('Start the Slideshow')
        slideShowNextIdx = 0 # Reset image index
        event.Skip()

    def OnBtnRescan(self, event):
        global localFileInfos
        global slideShowLastIdx
        global fileSortRecentFirst
        global localFilesCnt
        global availRemoteFilesCnt

        found = False
        # Is there any pending operation? Warn user if needed
        try:
            op = [x for x in self.opList if x[OP_STATUS]][0] # Search for busy slot
        except IndexError:
            pass
        else:
            msg = 'All pending request(s) will be lost'
            dlg = wx.MessageDialog(None, msg , 'Warning',
                                   wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
        # Update status bar
        msg = 'Rescanning configuration. Please wait...'
        # Disable User input
        self._setMode(MODE_DISABLED, msg)
        wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)
        # Read in new parameters
        self._updateGlobalsFromGUI()
        # Set file sort choice
        self.fileSortChoice.SetStringSelection(self.sortTypes[0] if fileSortRecentFirst else self.sortTypes[1])
        # Reset File type selector
        self.fileTypesChoice.SetStringSelection(FILETYPES[0])
        # Update file information
        localFilesCnt,availRemoteFilesCnt = updateFileDicts()
        slideShowLastIdx = localFilesCnt
        # Update datePickerCtrls
        self._setDatePickerCtrl()
        # Update LEDs colors
        self._updateLEDs()
        # Cancel all pending operations
        self.OnBtnCancel(1)
        # Update connection status indicator
        self._updateConnectionStatus()
        # Rescan is finished
        wx.EndBusyCursor()
        # Update status message
        msg = '%d local files' % (localFilesCnt)
        if cameraConnected:
            msg += ', %d remote files(s)' % (availRemoteFilesCnt)
        else:
            self._setOfflineMode()
            if not viewMode:
                msg += ',No remote file(s) detected'
        print(msg)

        if viewMode:
            lbl = ' Available Local Files: %d.  Page:' % localFilesCnt
#            self.staticBox3.SetLabel(' Available Local Files Page:')
            self.staticBox3.SetLabel(lbl)
            self._updateStaticBox3Label('OnBtnRescan')
            self.staticBox4.SetLabel(' File Viewer Control ')
            self.statusBar1.SetStatusText('View Mode', 1)
        else:
            self.staticBox3.SetLabel(' Available Remote Files (on camera) Page:')
            self._updateStaticBox3Label('OnBtnRescan')
            self.staticBox4.SetLabel(' Select Files to Sync... ')
            self.statusBar1.SetStatusText('Sync Mode', 1)

        # Update list of files on the GUI
        self._updateThumbnailPanel()

        self._setMode(MODE_ENABLED, msg)
#        event.Skip()

    def _unSyncFiles(self, fileType=''): # Clear all requests associated to a given file type (JPG, MOV)
        print('Must clear all requests for %s' % (fileType))
        i = 0
        for op in self.opList:
            if op[OP_STATUS] and op[OP_FILETYPE] == fileType:
                i += 1
                self.resetOneButton(op[OP_FILENAME])
                self.resetOneRequest(op)
        return i

    def _syncFiles(self, fileType=''):	# fileType could be : JPG, MOV
        global localFileInfos
        global availRemoteFiles

        print('Syncing %s files' % (fileType))
        i = 0
        # Browse the list of buttons (remote files) and schedule a request if file matches fileType and date (if requested)
        if self.fromCb.GetValue():	# Check if From date cb is set
            m = int(self.fromDate.split('/')[0])
            d = int(self.fromDate.split('/')[1])
            y = int(self.fromDate.split('/')[2])
            tf1 = datetime.datetime(y,m,d, 0, 0)    # year, month, day
            tf2 = time.mktime(tf1.timetuple())

        if self.toCb.GetValue():	# Check if To date cb is set
            m = int(self.toDate.split('/')[0])
            d = int(self.toDate.split('/')[1])
            y = int(self.toDate.split('/')[2])
            tt1 = datetime.datetime(y,m,d, 23, 59)    # year, month, day
            tt2 = time.mktime(tt1.timetuple())

        for button in self.thumbButtons:
            remFileName = button[1]
            if remFileName.split('.')[1] != fileType:
                continue

            # Check if already available locally
            if remFileName in localFileInfos.keys():
                continue

            rf = availRemoteFiles[remFileName]
            remFileDateInSecs = rf[F_DATEINSECS]
            remFileDate = rf[F_DATE]
            remFileSize = rf[F_SIZE]

            if self.fromCb.GetValue():	# Check if From date cb is set
                if remFileDateInSecs >= tf2:
                    pass
                else:
                    continue

            if self.toCb.GetValue():	# Check if To date cb is set
                if remFileDateInSecs <= tt2:
                    pass
                else:
                    continue

            e = [button, remFileName, FILE_DOWNLOAD, remFileSize, remFileDate]
            # Loop thru opList[] looking for a free slot, schedule an operation
            for op in self.opList:
                if op[OP_STATUS] == 0:
                    self._scheduleOperation(op, e)
                    i += 1
                    break
            else:
                msg = 'Max requests reached (%d).' % (MAX_OPERATIONS)
                print (msg)
                self.updateStatusBar(msg, fgcolor=wx.WHITE, bgcolor=wx.RED)
                # Clear all pending requests
                self.OnBtnCancel(1)
                return 0
        return i

    def OnBtnSyncAll(self, event):
        global localFileInfos
        global availRemoteFiles

        i = 0
        # Browse the list of buttons (remote files) and schedule a request
        for button in self.thumbButtons:
            #e = [button, button[1], FILE_DOWNLOAD]

            remFileName = button[1]

            # Check if already available locally
            if remFileName in localFileInfos.keys():
                continue

            rf = availRemoteFiles[remFileName]
            remFileDate = rf[F_DATE]
            remFileSize = rf[F_SIZE]
            e = [button, remFileName, FILE_DOWNLOAD, remFileSize, remFileDate]

            # Loop thru opList[] looking for a free slot, schedule an operation
            for op in self.opList:
                if op[OP_STATUS] == 0:
                    self._scheduleOperation(op, e)
                    i += 1
                    break
            else:
                msg = 'Max requests reached (%d).' % (MAX_OPERATIONS)
                print (msg)
                self.updateStatusBar(msg, fgcolor=wx.WHITE, bgcolor=wx.RED)
                # Clear all pending requests
                self.OnBtnCancel(1)
                return

        msg = '%d requests successfully scheduled' % (i)
        self.updateStatusBar(msg)

    def _unSelectFiles(self, fileType=''): # Clear all requests for a given file type (JPG, MOV)
        print('Must clear all requests for %s' % (fileType))
        i = 0
        for op in self.opList:
            if op[OP_STATUS] and op[OP_FILETYPE] == fileType:
                i += 1
                self.resetOneButton(op[OP_FILENAME])
                self.resetOneRequest(op)
        return i

    def _selectFilesByDate(self, fileType=''):	# fileType could be : JPG, MOV
        global localFileInfos

        print('Selecting %s files' % (fileType))
        i = 0
        # Browse the list of buttons ( files) and schedule a request if file matches fileType and date (if requested)
        if self.fromCb.GetValue():	# Check if From date cb is set
            m = int(self.fromDate.split('/')[0])
            d = int(self.fromDate.split('/')[1])
            y = int(self.fromDate.split('/')[2])
            tf1 = datetime.datetime(y,m,d, 0, 0)    # year, month, day
            tf2 = time.mktime(tf1.timetuple())
        else:
            tf2 = remOldestDate

        if self.toCb.GetValue():	# Check if To date cb is set
            m = int(self.toDate.split('/')[0])
            d = int(self.toDate.split('/')[1])
            y = int(self.toDate.split('/')[2])
            tt1 = datetime.datetime(y,m,d, 23, 59)    # year, month, day
            tt2 = time.mktime(tt1.timetuple())
        else:
            tt2 = remNewestDate

        # Each entry in thumbButtons[] is: [widget, filename, fgcol, bgcol]
        for button in self.thumbButtons:
            fileName = button[1]
            fileDate = localFileInfos[fileName][F_DATE]

            if fileName.split('.')[1] != fileType:
                continue

            if self.fromCb.GetValue():	# Check if From date cb is set
                if fileDate >= tf2:
                    pass
                else:
                    continue

            if self.toCb.GetValue():	# Check if To date cb is set
                if fileDate <= tt2:
                    pass
                else:
                    continue

            e = [button, fileName, FILE_SELECT, -1, -1]
            op = [x for x in self.opList if not x[OP_STATUS]][0] # First free slot
            self._scheduleOperation(op, e)
            i += 1
        return i

    def selectFilesByPosition(self, fileType='', position=0):	# fileType could be : JPG, MOV
        global localFilesSorted

        # Loop thru opList[]: Clear all slots marked as SELECTED
        for op in self.opList:
            if op[OP_STATUS] and op[OP_TYPE] == FILE_SELECT:
                fileName = op[OP_FILENAME]
                self.resetOneButton(fileName)
                self.resetOneRequest(op)

        i = 0
        for f in localFilesSorted[position:]:
            fileName = f[F_NAME]
            if fileName.split('.')[1] != fileType:
                continue

            button = [x[0] for x in self.thumbButtons if x[1] == fileName]
            e = [button, fileName, FILE_SELECT, -1, -1]
            try:
                op = [x for x in self.opList if not x[OP_STATUS]][0] # First free slot
            except:
                msg = 'Maximum selection (%d) reached' % MAX_OPERATIONS
                self.updateStatusBar(msg, fgcolor=wx.WHITE, bgcolor=wx.RED)
                break
            self._scheduleOperation(op, e)
            i += 1
        return i

    def OnBtnCommit(self, event):
        global osvmDownloadDir
        global askBeforeCommit
        global localFilesCnt

        pendingOpsCnt = self.pendingOperationsCount()
        if pendingOpsCnt == 0:
            return

        # Prevent user action
        msg = 'Processing pending operations...'
        self._setMode(MODE_DISABLED, msg)

        if askBeforeCommit:
            msg = 'Do you really want to proceed with pending request(s) ?'
            dial = wx.MessageDialog(None, msg, 'Commit Operations',
                                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            ret = dial.ShowModal()
            if ret == wx.ID_NO:
                # Allow user action
                msg = ''
                self._setMode(MODE_ENABLED, msg)
                return

        # Local directory where download should happen
        localDir = osvmDownloadDir

        (ret1, ret2) = self._checkLocalDir(localDir)
        if ret1 == -1:
            print('ERROR:', ret2)
            msg = '%s.\n\nPlease check your settings.' % (ret2)
            dlg = wx.MessageDialog(None, msg , 'Error', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            # Allow user action
            msg = ''
            self._setMode(MODE_ENABLED, msg)
            return
        self.downloadDir = localDir

        # Create a timer for animation...
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnStatusBar1Update, self.timer)
        self.timerCnt = 0
        self.timer.Start(TIMER3_FREQ)

        self.installDlg = InstallDialog(self, download=self.downloadDir, oplist=self.opList, title='Downloading Files')
        self.installDlg.ShowModal()
        self.installDlg.Destroy()
        self.installDlg = None

        if self.timer.IsRunning():
            self.timer.Stop()

        wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)
        # Clear all pending operations
        self.OnBtnCancel(1)

        # If some files have been installed, rescan/update list
        # Detect local files on the host
        localFilesCnt = localFilesInfo(osvmDownloadDir)
        print('OnBtnCommit(): %d local files on this host' % localFilesCnt)

        # Update list of files on the GUI
        self._updateThumbnailPanel()
        wx.EndBusyCursor()

        # Allow user action
        msg = '%d local files, %d files available on camera' % (localFilesCnt, availRemoteFilesCnt)
        self._setMode(MODE_ENABLED, msg)
        event.Skip()

    def OnBtnCancel(self, event):
        pendingOpsCnt = self.pendingOperationsCount()
        if pendingOpsCnt == 0:
            return

        # Prevent user action
        msg = 'Cancelling pending requests...'
        self._setMode(MODE_DISABLED, msg)

        if event != 1:
            msg = 'Do you really want to Cancel all pending request(s) ?'
            dial = wx.MessageDialog(None, msg, 'Cancel Operations',
                                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            ret = dial.ShowModal()
            if ret == wx.ID_NO:
                return

        # Loop thru opList[]: Clear all slots
        for i in range(len(self.opList)):
            opStatus = self.opList[i][OP_STATUS]
            # If this operation is in used, reset associated button
            if opStatus:
                fileName = self.opList[i][OP_FILENAME]
                self.resetOneButton(fileName)
            self.resetOneRequest(self.opList[i])
        
        # Prevent user action
        msg = 'All requests have been cancelled'
        self._setMode(MODE_ENABLED, msg)

        # Reset file selection check boxes
        for cb in [self.fromCb,self.toCb]:
            cb.SetValue(False)

    def OnCbOperation(self, event):
        id = event.GetId()
        # Setting an operation by a mouse click is forbidden
        if self.opList[id][OP_CBWGT].GetValue():
            self.opList[id][OP_CBWGT].SetValue(False)
            msg = 'Use Package Buttons to schedule an operation'
            self.updateStatusBar(msg, fgcolor=wx.WHITE, bgcolor=wx.RED)
        else:
            # Clear entry. Mark it as available
            pkgNum = self.opList[id][OP_FILENAME]
            # Count all pending operations on this package
            pendingOps = 0
            for i in range(len(self.opList)):
                if self.opList[i][OP_FILENAME] == pkgNum:
                    pendingOps += 1
            if pendingOps == 1:
                self.resetOneButton(pkgNum)
            self.resetOneRequest(self.opList[id])
            msg = 'Operation %d has been cleared' % (id)
            self.updateStatusBar(msg)

    def OnStatusBar1Update(self, event):
        if 0:
            with Timer() as t:
                self.updateStatusBar1()
            print('Request took %.03f sec.' % t.interval)
        else:
            self.updateStatusBar1()

    def updateStatusBar1(self):
        text = 'Processing pending operations...'
        textlen = len(text)

        #w1,h1 = self.statusBar1.GetSize()
        #print w1,h1

        # skip over spaces at beg. of display
        i = self.displen - len(''.join(self.display).lstrip())

        #print ("0:",self.timerCnt,i#,self.display)
        if i == self.displen:    # empty display
            i -= 1 

        k = 0    # count of shifted chars
        # Shift characters to the left by 1 position
        while i < self.displen:
            self.display[i-1] = self.display[i]
            k += 1
            i += 1

        # Insert char at end of display
        if k >= textlen:
            self.display[-1] = ' '
        else:
            self.display[-1] = text[self.timerCnt % textlen]

        self.timerCnt += 1
        self.updateStatusBar(''.join(self.display))

    def _updateConnectionStatus(self):
        global cameraConnected
        global viewMode

        if cameraConnected or viewMode:
            self._displayBitmap(self.staticBitmap2, "traffic-light-green-65-nobg.png", wx.BITMAP_TYPE_PNG)
        else:
            self._displayBitmap(self.staticBitmap2, "traffic-light-red-65-nobg.png", wx.BITMAP_TYPE_PNG)

# Arguments parser
def parse_argv():
    desc = 'Graphical UI to manage files (pictures, video) on a OLYMPUS camera over WIFI''Also a File viewer over GoogleCast'

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("-d", "--debug",
                        action="store_true", dest="debug", default=False,
                        help="print debug messages (to stdout)")
    parser.add_argument('-f', '--file',
                        dest='logfile',
                        const=_logFile_,
                        default=None,
                        action='store',
                        nargs='?',
                        metavar = 'FILE',
                        help="write debug messages to FILE (default to %s)" % (_logFile_))
    parser.add_argument("-i", "--info",
                        action="store_true", dest="version", default=False,
                        help="print version and exit")
    parser.add_argument("-c", "--compact",
                        action="store_true", dest="compactmode", default=False,
                        help="Use Compact Layout")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--view", action="store_true", dest="viewmode", default=False,
                       help="Enter View/Cast Mode")
    group.add_argument("-s", "--sync", action="store_true", dest="syncmode", default=False,
                       help="Enter Synchronization Mode")
    args = parser.parse_args()
    return args

def printToolsVersion():
    global __system__
    global __pythonVersion__

    if __system__ == 'Windows':
        # Get win32api version
        fixed_file_info = win32api.GetFileVersionInfo(win32api.__file__, '\\')
        pywin32Version = fixed_file_info['FileVersionLS'] >> 16
        label = 'Platform: %s\nPython: %s\nWxPython: %s pywin32: %s' % ((platform.platform()), __pythonVersion__, wx.version(), pywin32Version)
    else:
        label = 'Platform: %s\nPython: %s\nWxPython: %s' % ((platform.platform()),  __pythonVersion__, wx.version())
    print (label)

def main():
    global __modPath__
    global __system__
    global __imgDir__
    global __tmpDir__
    global __hostarch__
    global __initFilePath__
    global __logFilePath__
    global __helpPath__
    global __pythonBits__
    global __pythonVersion__
    global _myVersion_
    global _initFile_
    global _osvmDir_
    global _logFile_
    global DEFAULT_FILE_COLORS
    global fileColors
    global htmlRootFile
    global htmlDirFile
    global autoViewMode
    global autoSyncMode
    global iface
    global networkSelector
    global compactMode
    global thumbnailGridRows

    args = parse_argv()

    osvmdirpath = os.path.join(os.path.join(expanduser("~"), _osvmDir_))
    if os.path.exists(osvmdirpath):
        if not os.path.isdir(osvmdirpath):
            print("%s must be a directory. Exit!" % (osvmdirpath))
            exit()
    else:
        try:
            os.mkdir(osvmdirpath)
        except OSError as e:
            msg = "Cannot create %s: %s" % (osvmdirpath, "{0}".format(e.strerror))
            return

    __tmpDir__ = os.path.join(osvmdirpath, '.tmp')
    if not os.path.isdir(__tmpDir__):
        print('Creating:', __tmpDir__)
        try:
            os.mkdir(__tmpDir__)
        except OSError as e:
            msg = "Cannot create %s: %s" % (__tmpDir__, "{0}".format(e.strerror))
            return

    __modPath__         = module_path(main)
    __imgDir__          = os.path.join(os.path.dirname(__modPath__), 'images')
    __initFilePath__    = os.path.join(osvmdirpath, _initFile_)
    __logFilePath__     = None
    __helpPath__        = os.path.join(os.path.dirname(__modPath__), 'help.htm')

    htmlRootFile = os.path.join(osvmdirpath, htmlRootFile)
    htmlDirFile  = os.path.join(osvmdirpath, htmlDirFile)

    # Python version
    __pythonVersion__ = (sys.version).split()[0]

    # Get python executable size (32 or 64)
    __pythonBits__ = (8 * struct.calcsize("P"))

    # Get SVN Revision through svn:keywords
#    rev = "$Revision: 1 $" # DONT TOUCH THIS LINE!!!
#    _myVersion_ = "%s.%s" % (_myVersion_, rev[rev.find(' ')+1:rev.rfind(' ')])

    if args.version:
        print('%s: Version: %s' % (_myName_, _myVersion_))
        printToolsVersion()
        print('PyChromeCast:',module_path(pychromecast))
        print('Vlc:',module_path(vlc))
        if networkSelector:
            print('Objc:',module_path(objc))
        sys.exit(0)

    if args.viewmode:
        print('Main(): Auto Entering View/Cast Mode')
        autoViewMode = True
    elif args.syncmode:
        print('Main(): Auto Entering Sync Mode')
        autoSyncMode = True

    if args.compactmode:
        print('Main(): Using Compact Mode')
        compactMode = True

    if args.debug == False:     # no debug
        app = wx.App(0)
        actualstdout = sys.stdout
        sys.stdout = io.StringIO()
    else:                       # debug
        if args.logfile == None:    # no output file, use stdio
            app = wx.App(redirect=False)
        else:             # use default/specified output file
            if not os.path.isabs(args.logfile):
                __logFilePath__ = os.path.join(osvmdirpath, args.logfile)
            else:
                __logFilePath__ = args.logfile
            # Remove existing log file
            if os.path.isfile(__logFilePath__): 
                os.remove(__logFilePath__)
            # Set redirect to True to log to the logfile
            app = wx.App(redirect=True, filename=__logFilePath__)

    print('%s: Version: %s. Running at: %s' % (_myName_, _myVersion_, time.strftime('%m/%d/%y %H:%M:%S', time.localtime())))
    print('System:', __system__ )
    printToolsVersion()
    print('Host Archictecture:', __hostarch__)
    print('Path:', __modPath__)
    print('Image Dir:', __imgDir__)
    print('Help Path:', __helpPath__)
    print('Init File:', __initFilePath__)
    if args.logfile:
        print('Log File: %s' %  (__logFilePath__))
    print('Python Executable: %dbits' % (__pythonBits__))
                                    
    # adds more named colours to wx.TheColourDatabase
    wb.updateColourDB()  
    wx.ORANGE = wx.Colour("orange")
    wx.GREY = wx.Colour("lightgrey")
    wx.STEELBLUE = wx.Colour(30, 100, 180)
    # Update package button colors
    DEFAULT_FILE_COLORS = [(wx.GREY,wx.WHITE),(wx.GREEN,wx.WHITE),(wx.ORANGE,wx.WHITE)]
    fileColors = [[wx.GREY,wx.WHITE],[wx.GREEN,wx.WHITE],[wx.ORANGE,wx.WHITE]]

    # Init network (Mac only!!!)
    if __system__ == 'Darwin' and networkSelector:
        objc.loadBundle('CoreWLAN',
                        bundle_path='/System/Library/Frameworks/CoreWLAN.framework',
                        module_globals=globals())

        for iname in CWInterface.interfaceNames():
            interface = CWInterface.interfaceWithName_(iname)

        print("""Interface:      %s
SSID:           %s
BSSID:          %s
Transmit Rate:  %s
Transmit Power: %s
RSSI:           %s""" % (iname, interface.ssid(), interface.bssid(),interface.transmitRate(),
                         interface.transmitPower(), interface.rssi()))

        iface = CWInterface.interface()
        if not iface:
            print('No Network Interface')

    frame = OSVMConfig(None, -1, "%s" % (_myLongName_))
    frame.Show(True)

#    app.SetTopWindow(frame)
    app.MainLoop()
    print('End of MainLoop')
    # Should never happen
    #print ("Application has been killed !")

    # Some cleanup
    cleanup()

if __name__ == "__main__":
    main()
