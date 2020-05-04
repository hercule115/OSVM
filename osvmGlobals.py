import wx
import os
import platform
from os.path import expanduser
from wx.lib.newevent import NewEvent

myName     = 'OSVM'
myLongName = 'Olympus Sync & View Manager'
myVersion  = '2.6.3'

disabledModules = list()
pycc = True
vlcVideoViewer = True
networkSelector = True

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

SERVER_HTTP_PORT = '8125'

modPath         = None
system          = None
hostarch        = None
imgDir          = None
thumbDir        = None
tmpDir          = None
initFilePath    = None
logFilePath     = None
helpPath        = None
pythonBits      = None
pythonVersion   = None

# Constants
osvmDir         = '.osvm'		# In home directory
initFile        = 'osvm.ini'		# In osvmDir
initFileBk      = 'osvm.ini.bk'		# In osvmDir
logFile         = 'osvm-log.txt'	# In osvmDir
logConsoleFile  = 'osvm-console.txt'	# In osvmDir
exifFile        = '.exif-cache.txt'	# In osvmDownloadDir
iniFileVersion  = '1'

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
DEFAULT_OSVM_DOWNLOAD_DIR = os.path.join(expanduser("~"), osvmDir, 'download')
DEFAULT_THUMB_GRID_NUM_COLS = 10
DEFAULT_THUMB_SCALE_FACTOR = 0.59
DEFAULT_SLIDESHOW_DELAY = 5
DEFAULT_ROT_IMG_CHOICE = 0 	# Show rotated image only
DEFAULT_SORT_ORDER = True 	# Mean More recent first
DEFAULT_SMTP_SERVER = ''
DEFAULT_SMTP_SERVER_PROTOCOL = 'SMTP'
DEFAULT_SMTP_SERVER_PORT = 25
DEFAULT_SMTP_SERVER_USE_AUTH = False
DEFAULT_SMTP_SERVER_USER_NAME = ''
DEFAULT_SMTP_SERVER_USER_PASSWD = ''                
DEFAULT_SMTP_FROM_USER = ''
DEFAULT_SMTP_RECIPIENTS_LIST = ''
SMTP_RECIPIENTS_LIST_LEN = 5	# Keep only 5 entries

# Preferences file option keys in ini file
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
ROT_IMG_CHOICE = 'rotimgchoice'
LAST_CAST_DEVICE_NAME = 'lastcastdevicename'
LAST_CAST_DEVICE_UUID = 'lastcastdeviceuuid'
SORT_ORDER = 'filesortreverse'
FAVORITE_NETWORK = 'favoritenetwork'
SMTP_SERVER = 'smtpserver'
SMTP_SERVER_PROTOCOL = 'smtpserverprotocol'
SMTP_SERVER_PORT = 'smtpserverport'
SMTP_SERVER_USE_AUTH = 'smtpserveruseauth'
SMTP_SERVER_USER_NAME = 'smtpserverusername'
SMTP_SERVER_USER_PASSWD = 'smtpserveruserpasswd'        
SMTP_FROM_USER = 'smtpfromuser'
SMTP_RECIPIENTS_LIST = 'smtprecipientslist'

# Globals Managed by Preferences / Frame # In osvmDir
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
rotImgChoice = DEFAULT_ROT_IMG_CHOICE
favoriteNetwork = ('','')  # Favorite Network, e.g. Camera
viewMode = False
autoViewMode = False
autoSyncMode = False
compactMode = False
noPanel = False	# Skip loading of thumbnail panels
useExternalViewer = False
httpServer = None
castMediaCtrl = None
slideShowNextIdx = 0
slideShowLastIdx = 0
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
smtpServer = ''
smtpServerProtocol = ''
smtpServerPort = 25
smtpServerUseAuth = False
smtpServerUserName = ''
smtpServerUserPasswd = ''
smtpFromUser = ''
smtpRecipientsList = list()
imagePathCmdLineArg = None

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
 FILE_MARK,
 FILE_UNMARK] = [i for i in range(3)]

FILE_PROPERTIES = -3
FILE_SLIDESHOW  = -4

# Max # of operations to commit in a single click
MAX_OPERATIONS = 5000

# opList fields index
[OP_STATUS,	# status (busy=1/free=0)
 OP_FILENAME,	# remote file name (camera)
 OP_FILETYPE,	# JPG, MOV,...
 OP_TYPE,	# FILE_DOWNLOAD = 0  FILE_MARK = 1,...
 OP_FILEPATH,	# full pathname of local file for download
 OP_SIZE,	# (size in bytes, block count)
 OP_FILEDATE,	# remote file date
 OP_REMURL,	# full remote url to download
 OP_INWGT,	# list of all assoc. widgets in InstallDialog frame
 OP_INCOUNT,	# current block counter for this op
 OP_INSTEP,	# Installation step
 OP_INLEDCOL,	# Installation LED color
 OP_INLEDSTATE,	# Installation LED state: ON/BLINK/OFF
 OP_INTH,	# Installation thread
 OP_INTICKS,	# Installation elapsed time
 OP_LASTIDX] = [i for i in range(16)]    # LASTIDX must be last field

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
TIMER5_FREQ =  50 # milliseconds
TIMER6_FREQ = 300 # milliseconds

# File Types Choice entries. 'None' MUST BE FIRST
FILE_IMAGES = 'PICT'
FILE_MOVIES = 'VIDEO'
FILE_TYPES = ['None', FILE_IMAGES, FILE_MOVIES, 'ALL']
FILE_TYPES_NOVLC = ['', FILE_IMAGES] # If No VLC detected
# File suffixes supported for images and videos
FILE_SUFFIXES = { FILE_IMAGES:('JPG','jpg','JPEG', 'jpeg'),
                  FILE_MOVIES:('MOV', 'mov','mp4', 'MP4') }

ROT_IMG_ENTRIES = ['Show Rotated Only', 'Show Original Only', 'Show Both']

# LEDs colours
LEDS_COLOURS = [['#929292', '#A8A8A8', '#9C9C9C', '#B7B7B7'], # grey
                     ['#0ADC0A', '#0CFD0C', '#0BEB0B', '#0DFF0D'], # green
                     ['#FAC800', '#FFE600', '#FFD600', '#FFFA00'], # yellow
                     ['#DC0A0A', '#FD0C0C', '#EB0B0B', '#FF0D0D'], # red
                     ['#1E64B4', '#2373CF', '#206BC1', '#267DE1']] # steel blue (30, 100, 180)

[LED_GREY,
 LED_GREEN,
 LED_ORANGE,
 LED_RED,
 LED_BLUE] = [i for i in range(5)]

[LED_OFF,
 LED_BLINK,
 LED_ON] = [i for i in range(3)]

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

cameraConnected = False

ID_CONNECT_ERROR = 400

wxLogFrameClose, EVT_LOG_FRAME_CLOSE = NewEvent()
wxOsvmFrameClose, EVT_OSVM_FRAME_CLOSE = NewEvent()
    
def printGlobals():
    print('globs.compactMode: %s' % compactMode)
    print('globs.askBeforeCommit: %s' % askBeforeCommit)
    print('globs.askBeforeExit: %s' % askBeforeExit)
    print('globs.overwriteLocalFiles: %s' % overwriteLocalFiles)
    print('globs.autoSwitchToFavoriteNetwork: %s' % autoSwitchToFavoriteNetwork)
    print('globs.cameraConnected: %s' % cameraConnected)
    print('globs.maxDownload: %s' % maxDownload)
    print('globs.localFilesCnt: %s' % localFilesCnt)
    print('globs.availRemoteFilesCnt: %s' % availRemoteFilesCnt)
    print('globs.savePreferencesOnExit: %s' % savePreferencesOnExit)
    print('globs.osvmDownloadDir: %s' % osvmDownloadDir)
    print('globs.osvmFilesDownloadUrl: %s' % osvmFilesDownloadUrl)
    print('globs.fileColors:', fileColors)
    print('globs.ssDelay:', ssDelay)
    print('globs.rotImgChoice:', rotImgChoice)    
    print('globs.knownNetworks:', knownNetworks)
    print('globs.favoriteNetwork:', favoriteNetwork)
    print('globs.fileSortRecentFirst:', fileSortRecentFirst)
    print('globs.smtpServer:', smtpServer)
    print('globs.smtpServerProtocol:', smtpServerProtocol)
    print('globs.smtpServerPort:', smtpServerPort)
    print('globs.smtpServerUseAuth:', smtpServerUseAuth)
    print('globs.smtpServerUserName:', smtpServerUserName)
    print('globs.smtpServerUserPasswd:', smtpServerUserPasswd)
    print('globs.smtpRecipientsList:', smtpRecipientsList)
