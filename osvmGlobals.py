import wx
import os
import platform
from os.path import expanduser

class myGlobals():
    def __init__(self):

        self.myName     = 'OSVM'
        self.myLongName = 'Olympus Sync & View Manager'
        self.myVersion  = '2.2.2'

        self.disabledModules = list()
        self.pycc = True
        self.vlcVideoViewer = True
        self.networkSelector = True

        self.CWSecurityModes = {
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

        self.SERVER_HTTP_PORT = '8124'

        self.modPath         = None
        self.system          = None
        self.hostarch        = None
        self.imgDir          = None
        self.thumbDir        = None
        self.tmpDir          = None
        self.initFilePath    = None
        self.logFilePath     = None
        self.helpPath        = None
        self.pythonBits      = None
        self.pythonVersion   = None

        # Constants
        self.osvmDir         = '.osvm'		# In home directory
        self.initFile        = 'osvm.ini'	# In osvmDir
        self.initFileBk      = 'osvm.ini.bk'	# In osvmDir
        self.logFile         = 'osvm-log.txt'	# In osvmDir
        self.iniFileVersion  = '1'

        # Default values for 'Reset Preferences'
        self.DEFAULT_COMPACT_MODE = False
        self.DEFAULT_ASK_BEFORE_COMMIT = True
        self.DEFAULT_ASK_BEFORE_EXIT = True
        self.DEFAULT_SAVE_PREFERENCES_ON_EXIT = True
        self.DEFAULT_MAX_DOWNLOAD = 1
        self.DEFAULT_OVERWRITE_LOCAL_FILES = False
        self.DEFAULT_AUTO_SWITCH_TO_CAMERA_NETWORK = False
        self.DEFAULT_OSVM_ROOT_URL  = 'http://192.168.0.10:80'
        self.DEFAULT_OSVM_REM_BASE_DIR = '/DCIM'
        self.DEFAULT_OSVM_DOWNLOAD_DIR = os.path.join(expanduser("~"), self.osvmDir, 'download')
        self.DEFAULT_THUMB_GRID_NUM_COLS = 10
        self.DEFAULT_THUMB_SCALE_FACTOR = 0.59
        self.DEFAULT_SLIDESHOW_DELAY = 5
        self.DEFAULT_SORT_ORDER = True # Mean More recent first
        self.DEFAULT_SMTP_SERVER = ''
        self.DEFAULT_SMTP_SERVER_PROTOCOL = 'SMTP'
        self.DEFAULT_SMTP_SERVER_PORT = 25
        self.DEFAULT_SMTP_SERVER_USE_AUTH = False
        self.DEFAULT_SMTP_SERVER_USER_NAME = ''
        self.DEFAULT_SMTP_SERVER_USER_PASSWD = ''                
        
        self.DEFAULT_MAIL_ADDR = None
        
        # Preferences file option keys
        self.INI_VERSION = 'iniversion'
        self.HTML_ROOT_FILE = 'htmlrootfile'
        self.COMPACT_MODE = 'compactmode'
        self.ASK_BEFORE_COMMIT = 'askbeforecommit'
        self.ASK_BEFORE_EXIT = 'askbeforeexit'
        self.SAVE_PREFS_ON_EXIT = 'savepreferencesonexit'
        self.THUMB_GRID_COLUMNS = 'thumbnailgridcolumns'
        self.THUMB_SCALE_FACTOR = 'thumbnailscalefactor'
        self.OSVM_DOWNLOAD_DIR = 'osvmdownloaddir'
        self.OSVM_FILES_DOWNLOAD_URL = 'osvmrooturl'
        self.REM_BASE_DIR = "rembasedir"
        self.MAX_DOWNLOAD = 'maxdownload'
        self.OVERWRITE_LOCAL_FILES = 'overwritelocalfiles'
        self.AUTO_SWITCH_TO_CAMERA_NETWORK = 'autoswitchtocameranetwork'
        self.SS_DELAY = 'slideshowdelay'
        self.LAST_CAST_DEVICE_NAME = 'lastcastdevicename'
        self.LAST_CAST_DEVICE_UUID = 'lastcastdeviceuuid'
        self.SORT_ORDER = 'filesortreverse'
        self.FAVORITE_NETWORK = 'favoritenetwork'
        self.SMTP_SERVER = 'smtpserver'
        self.SMTP_SERVER_PROTOCOL = 'smtpserverprotocol'
        self.SMTP_SERVER_PORT = 'smtpserverport'
        self.SMTP_SERVER_USE_AUTH = 'smtpserveruseauth'
        self.SMTP_SERVER_USER_NAME = 'smtpserverusername'
        self.SMTP_SERVER_USER_PASSWD = 'smtpserveruserpasswd'        

        # Globals Managed by Preferences / Frame # In osvmDir
        self.htmlRootFile = 'htmlRootFile.html'
        self.htmlDirFile  = 'htmlDirFile.html'

        self.online = True
        self.askBeforeCommit = True
        self.askBeforeExit = True
        self.savePreferencesOnExit = True
        self.thumbnailGridColumns = self.DEFAULT_THUMB_GRID_NUM_COLS
        self.thumbnailGridRows = 3
        self.thumbnailScaleFactor = self.DEFAULT_THUMB_SCALE_FACTOR
        self.osvmDownloadDir = self.DEFAULT_OSVM_DOWNLOAD_DIR
        self.osvmFilesDownloadUrl = ''
        self.maxDownload = self.DEFAULT_MAX_DOWNLOAD
        self.overwriteLocalFiles = False
        self.autoSwitchToFavoriteNetwork = False
        self.rootUrl = self.DEFAULT_OSVM_ROOT_URL
        self.remBaseDir = self.DEFAULT_OSVM_REM_BASE_DIR
        self.ssDelay = self.DEFAULT_SLIDESHOW_DELAY
        self.favoriteNetwork = ('','')  # Favorite Network, e.g. Camera
        self.viewMode = False
        self.autoViewMode = False
        self.autoSyncMode = False
        self.compactMode = False
        self.noPanel = False	# Skip loading of thumbnail panels
        self.useExternalViewer = False
        self.httpServer = None
        self.castMediaCtrl = None
        self.slideShowNextIdx = 0
        self.chromecasts = list() # List of available chromecast devices
        self.castDevice = None # Selected chromecast
        self.lastCastDeviceName = None
        self.lastCastDeviceUuid = None
        self.serverAddr = '0.0.0.0'
        self.iface = None
        self.allNetWorks = list() # List of all available networks
        self.knownNetworks = list()
        self.fileSortRecentFirst = self.DEFAULT_SORT_ORDER
        self.installSubPanelsCount = 5
        self.smtpServer = ''
        self.smtpServerProtocol = ''
        self.smtpServerPort = 25
        self.smtpServerUseAuth = False
        self.smtpServerUserName = ''
        self.smtpServerUserPasswd = ''
        
        # List of root directories on the camera
        self.rootDirList = []
        self.rootDirCnt = 0

        # Oldest and newest date of remote files on the camera
        self.remOldestDate = ''
        self.remNewestDate = ''

        # Dict containing informations on the files available at remote/camera
        self.availRemoteFiles = {}

        # Common indexes to availRemoteFiles and localFileInfos.
        [self.F_NAME, # common
         self.F_SIZE, # common
         self.F_DATE, # common
         self.F_PATH,
         self.F_DIRNAME,
         self.F_ATTR,
         self.F_DATEINSECS,
         self.F_TIME,
         self.F_THUMBURL] = [i for i in range(9)]

        self.availRemoteFilesCnt =  0
        self.availRemoteFilesSorted = {}	# Sorted copy of the dict above

        # File Status
        [self.FILE_NOT_INSTALLED,
         self.FILE_INSTALLED,
         self.FILE_OP_PENDING] = [i for i in range(3)]

        # Colors to use for package buttons (bg,fg). 
        # Will be updated at run-time with other colors
        # Order must match "Package Status" e.g.:
        # - Remote File (NOT_INSTALLED)
        # - Local File  (INSTALLED)
        # - Request pending (OP_PENDING)
        self.fileColors = [[0,0],[wx.GREEN,wx.WHITE],[0,0]]
        self.FILE_COLORS_STATUS = ["Remote File", "Local File", "Request pending"]
        self.DEFAULT_FILE_COLORS = []

        # Dictionary of local files
        # key: fileName, value: [fileName, fileSize, fileDate, filePath]
        self.localFileInfos = {}
        [self.FINFO_NAME,
         self.FINFO_SIZE,
         self.FINFO_DATE,
         self.FINFO_PATH] = [i for i in range(4)]
        self.localFilesCnt = 0
        self.localFilesSorted = {}	# Sorted copy of the dict above

        # Possible operations on a file
        [self.FILE_DOWNLOAD,
         self.FILE_DELETE,
         self.FILE_SELECT,
         self.FILE_UNSELECT,
         self.FILE_SHARE,
         self.FILE_UNSHARE] = [i for i in range(6)]

        self.FILE_PROPERTIES = -3
        self.FILE_SLIDESHOW = -4
        self.OPERATION_NAMES = {self.FILE_DOWNLOAD:'DOWNLOAD', self.FILE_DELETE:'DELETE'}

        # Max # of operations to commit in a single click
        self.MAX_OPERATIONS = 2000

        # opList fields index
        [self.OP_STATUS,     # status (busy=1/free=0)
         self.OP_FILENAME,   # remote file name (camera)
         self.OP_FILETYPE,	# JPG, MOV,...
         self.OP_TYPE,       # FILE_DOWNLOAD = 1  FILE_DELETE = 2
         self.OP_FILEPATH,   # full pathname of local file for download
         self.OP_SIZE,       # (size in bytes, block count)
         self.OP_FILEDATE,	# remote file date
         self.OP_REMURL,     # full remote url to download
         self.OP_INWGT,      # list of all assoc. widgets in InstallDialog frame
         self.OP_INCOUNT,    # current block counter for this op
         self.OP_INSTEP,     # Installation step
         self.OP_INLEDCOL,   # Installation LED color
         self.OP_INLEDSTATE, # Installation LED state: ON/BLINK/OFF
         self.OP_INTH,       # Installation thread
         self.OP_INTICKS,    # Installation elapsed time
         self.OP_LASTIDX] = [i for i in range(16)]    # Last index (must be last field)

        # Execution Mode
        self.MODE_DISABLED = 0
        self.MODE_ENABLED  = 1

        # Urllib read block size
        self.URLLIB_READ_BLKSIZE = 8192

        # Install Dialog constants
        [self.INST_GAUGE,
         self.INST_ELAPTXT,
         self.INST_ELAPCNT,
         self.INST_REMTXT,
         self.INST_REMCNT,
         self.INST_STBOX,
         self.INST_OPBOXSZ,
         self.INST_GRDSZ,
         self.INST_LEDBOXSZ,
         self.INST_LEDLIST,
         self.INST_GKBOXSZ,
         self.INST_KEYTXT] = [i for i in range(12)]

        self.TIMER1_FREQ  = 1000.0 # milliseconds
        self.TICK_PER_SEC = 1000 / self.TIMER1_FREQ

        self.TIMER2_FREQ = 200 # milliseconds
        self.TIMER3_FREQ = 200 # milliseconds
        self.TIMER4_FREQ = 100 # milliseconds
        self.TIMER5_FREQ = 50 # milliseconds
        self.TIMER6_FREQ = 300 # milliseconds

        # LEDs colours
        self.LEDS_COLOURS = [['#929292', '#A8A8A8', '#9C9C9C', '#B7B7B7'], # grey
                             ['#0ADC0A', '#0CFD0C', '#0BEB0B', '#0DFF0D'], # green
                             ['#FAC800', '#FFE600', '#FFD600', '#FFFA00'], # yellow
                             ['#DC0A0A', '#FD0C0C', '#EB0B0B', '#FF0D0D'], # red
                             ['#1E64B4', '#2373CF', '#206BC1', '#267DE1']] # steel blue (30, 100, 180)

        [self.LED_GREY,
         self.LED_GREEN,
         self.LED_ORANGE,
         self.LED_RED,
         self.LED_BLUE] = [i for i in range(5)]

        [self.LED_OFF,
         self.LED_BLINK,
         self.LED_ON] = [i for i in range(3)]

        # File Types to view/sync
        self.FILETYPES = ['None', 'JPG', 'MOV', 'ALL']
        self.FILETYPES_NOVLC = ['', 'JPG']

        # File types to clean. For each type, a counter is provided (see folderSize())
        self.CLEAN_FILETYPES = { 'JPG':0, 'MOV':0 }

        # Wifi networks parameters (scanForNetworks())
        [self.NET_SSID,
         self.NET_BSSID,
         self.NET_PASSWD,
         self.NET_RSSI,
         self.NET_CHANNEL,
         self.NET_SECURITY,
         self.NET_KNOWN,
         self.NET_FAVORITE,
         self.NET_NET] = [i for i in range(9)]

        self.cameraConnected = False

        self.ID_CONNECT_ERROR = 400

    def printGlobals(self):
        print('globs.compactMode: %s' % self.compactMode)
        print('globs.askBeforeCommit: %s' % self.askBeforeCommit)
        print('globs.askBeforeExit: %s' % self.askBeforeExit)
        print('globs.overwriteLocalFiles: %s' % self.overwriteLocalFiles)
        print('globs.autoSwitchToFavoriteNetwork: %s' % self.autoSwitchToFavoriteNetwork)
        print('globs.cameraConnected: %s' % self.cameraConnected)
        print('globs.maxDownload: %s' % self.maxDownload)
        print('globs.localFilesCnt: %s' % self.localFilesCnt)
        print('globs.availRemoteFilesCnt: %s' % self.availRemoteFilesCnt)
        print('globs.savePreferencesOnExit: %s' % self.savePreferencesOnExit)
        print('globs.osvmDownloadDir: %s' % self.osvmDownloadDir)
        print('globs.osvmFilesDownloadUrl: %s' % self.osvmFilesDownloadUrl)
        print('globs.fileColors:', self.fileColors)
        print('globs.ssDelay:', self.ssDelay)
        print('globs.knownNetworks:', self.knownNetworks)
        print('globs.favoriteNetwork:', self.favoriteNetwork)
        print('globs.fileSortRecentFirst:', self.fileSortRecentFirst)
        print('globs.smtpServer:', self.smtpServer)
        print('globs.smtpServerProtocol:', self.smtpServerProtocol)
        print('globs.smtpServerPort:', self.smtpServerPort)
        print('globs.smtpServerUseAuth:', self.smtpServerUseAuth)
        print('globs.smtpServerUserName:', self.smtpServerUserName)
        print('globs.smtpServerUserPasswd:', self.smtpServerUserPasswd)
