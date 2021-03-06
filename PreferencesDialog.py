#!/usr/bin/env python
import wx

import sys
import os
import builtins as __builtin__
import inspect
from copy import deepcopy
import platform

moduleList = {'osvmGlobals':'globs',
              'ColorPickerDialog':'ColorPickerDialog',
              'MailPreferencesDialog':'MailPreferencesDialog',
              'WifiDialog':'WifiDialog'}

for k,v in moduleList.items():
    print('Loading: %s as %s' % (k,v))
    mod = __import__(k, fromlist=[None])
    globals()[v] = globals().pop('mod')	# Rename module in globals()

####
#print(__name__)

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
        # Max delay interval for slideshow
        self.MIN_SS_DELAY = 3
        self.MAX_SS_DELAY = 11

        myStyle = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
        wx.Dialog.__init__(self, None, wx.ID_ANY, '%s - Preferences' % globs.myLongName, style=myStyle)

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
        parent.Add(self.cb4, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.cb5, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.cb6, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.cb7, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.cb8, 0, border=0, flag=wx.EXPAND)        
        #parent.Add(self.dummySizer1, 0, border=0, flag= wx.EXPAND) # Empty placeholder
        
        parent.Add(self.maxDownloadSizer, 0, border=0, flag= wx.EXPAND)
        parent.Add(self.fileSortSizer, 0, border=0, flag= wx.EXPAND)
        parent.Add(self.colorPickerSizer, 0, border=0, flag= wx.EXPAND)
        parent.Add(self.mailPrefsSizer, 0, border=0, flag= wx.EXPAND)

    def _init_dummySizer_Items(self, parent):
        pass
    
    def _init_mailPrefsSizer_Items(self, parent):
        parent.Add(self.mailPrefsBtn, 0, border=0,
                   flag=wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM | wx.LEFT | wx.TOP)

    def _init_colorPickerSizer_Items(self, parent):
        parent.Add(self.colorPickerBtn, 0, border=0,
                   flag=wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM | wx.LEFT | wx.TOP)

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
        parent.Add(4, 0, border=0, flag=0)
        parent.Add(self.ssDelayChoice, 0, border=5, flag=wx.ALL)
#        parent.AddStretchSpacer(prop=1)
        parent.Add(8, 0, border=0, flag=0)
        parent.Add(self.rotImgLabel, 0, border=5, flag= wx.ALL | wx.EXPAND)
        parent.Add(4, 0, border=0, flag=0)
        parent.Add(self.rotImgChoice, border=5, flag=wx.ALL | wx.EXPAND) #211 | wx.ALIGN_RIGHT)
        
    # local config items
    def _init_localConfigBoxSizer_Items(self, parent):
        parent.Add(self.configBoxSizer6, 0, border=0, flag= wx.ALL)

    def _init_remConfigBoxSizer_Items(self, parent):
        parent.Add(self.configBoxSizer3, 0, border=0, flag= wx.ALL)
        parent.Add(self.configBoxSizer4, 0, border=0, flag= wx.ALL)
        parent.Add(self.configBoxSizer5, 0, border=0, flag= wx.ALL)

    def _init_configBoxSizer6_Items(self, parent):
        parent.Add(self.btnSelectDownLoc, 0, border=5,
                   flag=wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM | wx.LEFT | wx.TOP)
        parent.Add(4, 0, border=0, flag=0)
        parent.Add(self.downLocTextCtrl, 0, border=5, flag=wx.EXPAND | wx.ALL)
        parent.AddStretchSpacer(prop=1)
        parent.Add(self.diskSpaceLabel, 0, border=5, flag= wx.ALL | wx.EXPAND)
        parent.Add(2, 0, border=0, flag=0)
        parent.Add(self.diskSpaceTextCtrl, proportion=1, border=5, flag=wx.ALL | wx.EXPAND)#211 | wx.ALIGN_RIGHT)

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
        parent.Add(self.bottomBoxSizer2, 1, border=0, flag= wx.EXPAND | wx.ALL)
        parent.Add(8, 4, 2, border=0, flag=wx.EXPAND)
        parent.Add(self.bottomBoxSizer1, 0, border=0, flag= wx.EXPAND | wx.ALL)

    def _init_bottomBoxSizer1_Items(self, parent):
        parent.Add(self.bottomBoxSizer3, 0, border=0, flag= wx.ALL | wx.ALIGN_RIGHT)

    def _init_bottomBoxSizer2_Items(self, parent):
        parent.Add(self.bottomBoxSizer4, 0, border=0, flag= wx.ALL | wx.ALIGN_LEFT)
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
        gsNumCols = 4
        gsNumRows = 3
        self.prefsGridSizer1 = wx.GridSizer(cols=gsNumCols, hgap=0, rows=gsNumRows, vgap=2)

        # Max Download boxSizer
        self.maxDownloadSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        # File Sort boxSizer
        self.fileSortSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        # Color Picker boxSizer
        self.colorPickerSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        # Mail Prefs boxSizer
        self.mailPrefsSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        # Dummy/Empty boxSizer
        self.dummySizer1 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.dummySizer2 = wx.BoxSizer(orient=wx.HORIZONTAL)        
        
        # viewMode Download boxSizer
        self.viewModeBoxSizer = wx.StaticBoxSizer(box=self.staticBox4, orient=wx.HORIZONTAL)

        # Local Config staticBoxSizer
        self.localConfigBoxSizer = wx.StaticBoxSizer(box=self.staticBox1, orient=wx.HORIZONTAL)
        self.configBoxSizer1 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.configBoxSizer6 = wx.BoxSizer(orient=wx.HORIZONTAL)

        #  Remote Config staticBoxSizer
        self.remConfigBoxSizer = wx.StaticBoxSizer(box=self.staticBox3, orient=wx.VERTICAL)
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
        self._init_mailPrefsSizer_Items(self.mailPrefsSizer)
        self._init_dummySizer_Items(self.dummySizer1)
        self._init_dummySizer_Items(self.dummySizer2)        
        self._init_viewModeBoxSizer_Items(self.viewModeBoxSizer)
        self._init_localConfigBoxSizer_Items(self.localConfigBoxSizer)
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
        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self,
                               size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        #### Misc Preferences
        self.staticBox2 = wx.StaticBox(id=wx.ID_ANY, label=' Global Preferences ', 
                                       parent=self.panel1, style=0)

        self.cb1 = wx.CheckBox(self.panel1, id=wx.ID_ANY, label='Use Compact Mode')
        self.cb1.SetValue(globs.compactMode)

        self.cb2 = wx.CheckBox(self.panel1, id=wx.ID_ANY, label='Ask Before Commit')
        self.cb2.SetValue(globs.askBeforeCommit)

        self.cb3 = wx.CheckBox(self.panel1, id=wx.ID_ANY, label='Save Preferences on Exit')
        self.cb3.SetValue(globs.savePreferencesOnExit)

        self.cb4Id = wx.Window.NewControlId()
        self.cb4 = wx.CheckBox(self.panel1, id=self.cb4Id, label='Keep local folder in Sync')
        self.cb4.SetValue(globs.keepLocalFolderInSync)
        self.cb4.SetToolTip('Keep download folder in Sync with camera. WARNING: This option will delete local files if the camera SD is formatted or files deleted on the camera.')
        
        self.cb5 = wx.CheckBox(self.panel1, id=wx.ID_ANY, label='Ask Before Exit')
        self.cb5.SetValue(globs.askBeforeExit)

        self.cb6 = wx.CheckBox(self.panel1, id=wx.ID_ANY, label='Overwrite Local Files')
        self.cb6.SetValue(globs.overwriteLocalFiles)

        self.cb7 = wx.CheckBox(self.panel1, id=wx.ID_ANY, label='Auto switch to Camera AP')
        self.cb7.SetValue(globs.autoSwitchToFavoriteNetwork)
        self.cb7.SetToolTip('Automatically switch to favorite network (if set) when entering Sync Mode')

        self.cb8 = wx.CheckBox(self.panel1, id=wx.ID_ANY, label='Log Window')
        self.cb8.SetValue(globs.logFrame)
        self.cb8.SetToolTip('Open Log Window at startup')
        
        for cb in [self.cb1,self.cb2,self.cb3,self.cb4,self.cb5,self.cb6,self.cb7,self.cb8]:
            cb.Bind(wx.EVT_CHECKBOX, lambda evt: self.OnCheckBox(evt))
            
        self.staticText7 = wx.StaticText(id=wx.ID_ANY, label='Max // Download:', 
                                         parent=self.panel1, style=0)

        self.maxDownloadChoice = wx.Choice(choices=[str(i) for i in range(globs.MAX_OPERATIONS+1)], 
                                           id=wx.ID_ANY, parent=self.panel1, style=0)
        self.maxDownloadChoice.SetToolTip('Max allowed download in //. (0 = unlimited)')
        self.maxDownloadChoice.SetStringSelection(str(globs.maxDownload))
        self.maxDownloadChoice.Bind(wx.EVT_CHOICE, lambda evt:  self.OnMaxDownloadChoice(evt))
        self.sortTypes = ['Recent First', 'Oldest First']
        self.fileSortTxt = wx.StaticText(label='Sorting Order:', parent=self.panel1, id=wx.ID_ANY)
        self.fileSortChoice = wx.Choice(choices=[v for v in self.sortTypes], 
                                        id=wx.ID_ANY, parent=self.panel1, style=0)
        self.fileSortChoice.SetToolTip('Select sort order')
        self.fileSortChoice.SetStringSelection(self.sortTypes[0] if globs.fileSortRecentFirst else self.sortTypes[1])
        self.fileSortChoice.Bind(wx.EVT_CHOICE, self.OnFileSortChoice, id=wx.ID_ANY)

        self.colorPickerBtn = wx.Button(id=wx.ID_ANY, label='Color Chooser',
                                        parent=self.panel1, style=0)
        self.colorPickerBtn.SetToolTip('Choose colors of package status')
        self.colorPickerBtn.Bind(wx.EVT_BUTTON, lambda evt: self.OnColorPicker(evt))

        self.mailPrefsBtn = wx.Button(id=wx.ID_ANY, label='Mail Preferences',
                                      parent=self.panel1, style=0)
        self.mailPrefsBtn.SetToolTip('Configure Mail Preferences')
        self.mailPrefsBtn.Bind(wx.EVT_BUTTON, lambda evt: self.OnMailPrefs(evt))
        
        # viewMode preferences in staticBox4
        self.staticBox4 = wx.StaticBox(id=wx.ID_ANY,
                                       label=' View Mode Preferences ',
                                       parent=self.panel1, style=0)

        self.staticText8 = wx.StaticText(id=wx.ID_ANY, label='Slideshow Delay:', 
                                         parent=self.panel1, style=0)

        self.ssDelayChoice = wx.Choice(choices=[str(i) for i in range(self.MIN_SS_DELAY, self.MAX_SS_DELAY)], 
                                       parent=self.panel1, style=0)
        self.ssDelayChoice.SetToolTip('Delay interval')
        self.ssDelayChoice.SetStringSelection(str(globs.ssDelay))
        self.ssDelayChoice.Bind(wx.EVT_CHOICE, lambda evt: self.OnSsDelayChoice(evt))

        self.rotImgLabel   = wx.StaticText(label='Rotated Images:', parent=self.panel1, style=0)
        self.rotImgChoice  = wx.Choice(choices=[v for v in globs.ROT_IMG_ENTRIES], parent=self.panel1, style=0)
        self.rotImgChoice.SetToolTip('Select if non rotated images/rotated images or both images must be shown')
        self.rotImgChoice.SetStringSelection(globs.ROT_IMG_ENTRIES[int(globs.rotImgChoice)])
        self.rotImgChoice.Bind(wx.EVT_CHOICE, self.OnRotImgChoice)
        
        # Configuration
        self.staticBox1 = wx.StaticBox(id=wx.ID_ANY,
              label=' Local Configuration ', parent=self.panel1, style=0)

        self.staticBox3 = wx.StaticBox(id=wx.ID_ANY,
              label=' Remote Configuration ', parent=self.panel1, style=0)

        self.downLocTextCtrl = wx.TextCtrl(id=wx.ID_ANY,
                                                 parent=self.panel1, 
                                                 style=wx.TE_PROCESS_ENTER, 
                                                 size=wx.Size(400, -1), 
                                                 value='foobar')
        self.downLocTextCtrl.SetValue(globs.osvmDownloadDir)
        self.downLocTextCtrl.SetToolTip('Local Download directory')
        self.downLocTextCtrl.SetAutoLayout(True)
        self.downLocTextCtrl.SetCursor(wx.STANDARD_CURSOR)
        self.downLocTextCtrl.Bind(wx.EVT_TEXT, self.OnDownLocTextCtrlText,
                                     id=wx.ID_ANY)
        self.downLocTextCtrl.Bind(wx.EVT_TEXT_ENTER, self.OnDownLocTextCtrlText)

        # Disk usage control
        self.diskSpaceLabel = wx.StaticText(label='Free:', parent=self.panel1, id=wx.ID_ANY)
        self.diskSpaceTextCtrl = wx.TextCtrl(id=wx.ID_ANY,
                                             parent=self.panel1, 
                                             style=wx.TE_READONLY|wx.TE_RIGHT,
                                             size=wx.Size(100, -1), 
                                             value='')
        if os.path.exists(globs.osvmDownloadDir):
            self.diskSpaceTextCtrl.SetValue(diskUsage(globs.osvmDownloadDir)[2])
        else:
            self.diskSpaceTextCtrl.SetValue('????')
        self.diskSpaceTextCtrl.SetToolTip('Available Free Space in Download Directory')
        self.diskSpaceTextCtrl.SetAutoLayout(True)
        
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
        self.cameraUrlTextCtrl.SetValue(globs.osvmFilesDownloadUrl)
        self.cameraUrlTextCtrl.SetToolTip('Camera HTTP URL')
        self.cameraUrlTextCtrl.SetAutoLayout(True)
        self.cameraUrlTextCtrl.SetCursor(wx.STANDARD_CURSOR)
        self.cameraUrlTextCtrl.Bind(wx.EVT_TEXT, self.OnUrlTextCtrlText)

        self.remBaseDirTextCtrl = wx.TextCtrl(id=wx.ID_ANY,
                                             parent=self.panel1, 
                                             style=wx.TE_PROCESS_ENTER, 
                                             size=wx.Size(300, -1))
        self.remBaseDirTextCtrl.SetValue(globs.remBaseDir)
        self.remBaseDirTextCtrl.SetToolTip('Base Directory on Camera')
        self.remBaseDirTextCtrl.SetAutoLayout(True)
        self.remBaseDirTextCtrl.SetCursor(wx.STANDARD_CURSOR)
        self.remBaseDirTextCtrl.Bind(wx.EVT_TEXT, self.OnRemBaseDirTextCtrl)

        self.favoriteNetwork = wx.Button(id=wx.ID_ANY, label='Select Favorite Camera AP',
                                        parent=self.panel1, style=0)
        self.favoriteNetwork.SetToolTip('Choose favorite camera access point')
        self.favoriteNetwork.Bind(wx.EVT_BUTTON, lambda evt: self.OnFavoriteCamera(evt))

        self.staticText6 = wx.StaticText(id=wx.ID_ANY, label=globs.favoriteNetwork[globs.NET_SSID], parent=self.panel1, style=0)
        #### Bottom buttons
        self.btnCancel = wx.Button(id=wx.ID_CANCEL, label='Cancel', parent=self.panel1, style=0)
        self.btnCancel.SetToolTip('Discard changes')
        self.btnCancel.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnCancel(evt))
        
        self.btnReset = wx.Button(id=wx.ID_DEFAULT, label='Default', parent=self.panel1, style=0)
        self.btnReset.SetToolTip('Reset to factory defaults')
        self.btnReset.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnReset(evt))

        self.btnApply = wx.Button(id=wx.ID_APPLY, label='Apply', parent=self.panel1, style=0)
        self.btnApply.SetToolTip('Apply changes to current session')
        self.btnApply.SetDefault()
        self.btnApply.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnApply(evt))

        url = str(self.cameraUrlTextCtrl.GetValue())
        if not url.startswith('http'):
            self.btnApply.Disable()

        # Initialize temporary dicts
        self.tmpOsvmDownloadDir = globs.osvmDownloadDir
        self.tmpOsvmPkgFtpUrl   = globs.osvmFilesDownloadUrl

        # Copy pkg colors (backup)
        self._tmpPkgColors = deepcopy(globs.fileColors)

        self._init_sizers()

    def isRescanRequired(self):
        return self.needRescan

    # Reset Preference Dialog to Default values
    def _GUIReset(self):
        self.cb1.SetValue(globs.DEFAULT_COMPACT_MODE)
        self.cb2.SetValue(globs.DEFAULT_ASK_BEFORE_COMMIT)
        self.cb3.SetValue(globs.DEFAULT_SAVE_PREFERENCES_ON_EXIT)
        self.cb4.SetValue(globs.DEFAULT_KEEP_LOCAL_FOLDER_IN_SYNC)
        self.cb5.SetValue(globs.DEFAULT_ASK_BEFORE_EXIT)
        self.cb6.SetValue(globs.DEFAULT_OVERWRITE_LOCAL_FILES)
        self.cb7.SetValue(globs.DEFAULT_AUTO_SWITCH_TO_CAMERA_NETWORK)
        self.maxDownloadChoice.SetStringSelection(str(globs.DEFAULT_MAX_DOWNLOAD))
        self.fileSortChoice.SetStringSelection(self.sortTypes[0])
        self.ssDelayChoice.SetStringSelection(str(globs.DEFAULT_SLIDESHOW_DELAY))
        self.downLocTextCtrl.SetValue(globs.DEFAULT_OSVM_DOWNLOAD_DIR)
        self.cameraUrlTextCtrl.SetValue(globs.DEFAULT_OSVM_ROOT_URL)
        self.remBaseDirTextCtrl.SetValue(globs.DEFAULT_OSVM_REM_BASE_DIR)

        self.tmpOsvmDownloadDir = globs.DEFAULT_OSVM_DOWNLOAD_DIR
        self.tmpOsvmPkgFtpUrl   = globs.DEFAULT_OSVM_ROOT_URL

    def _updateGlobalsFromGUI(self):
        globs.compactMode           = self.cb1.GetValue()
        globs.askBeforeCommit       = self.cb2.GetValue()
        globs.savePreferencesOnExit = self.cb3.GetValue()
        globs.keepLocalFolderInSync = self.cb4.GetValue()
        globs.askBeforeExit         = self.cb5.GetValue()
        globs.overwriteLocalFiles   = self.cb6.GetValue()
        globs.autoSwitchToFavoriteNetwork = self.cb7.GetValue()
        globs.logFrame              = self.cb8.GetValue()
        globs.maxDownload           = int(self.maxDownloadChoice.GetSelection())
        globs.remBaseDir            = self.remBaseDirTextCtrl.GetValue()
        globs.ssDelay               = int(self.ssDelayChoice.GetSelection()) + self.MIN_SS_DELAY
        globs.fileSortRecentFirst   = not (int(self.fileSortChoice.GetSelection()))

        # Update from temporary variables
        if globs.osvmDownloadDir != self.tmpOsvmDownloadDir:
            globs.osvmDownloadDir = self.tmpOsvmDownloadDir
            self.needRescan = True

        if globs.osvmFilesDownloadUrl != self.tmpOsvmPkgFtpUrl:
            globs.osvmFilesDownloadUrl = self.tmpOsvmPkgFtpUrl
            self.needRescan = True
            
        #globs.printGlobals()

    #### Events ####
    def OnCheckBox(self, event):
        self.btnApply.Enable()
        w = event.GetEventObject()
        if w.GetId() == self.cb4Id and w.GetValue():  # keepLocalFolderInSync
            msg = 'This option, when activated, may delete file(s) from your local download folder if files are erased from the camera (Sync Mode Only).'
            dlg = wx.MessageDialog(None, msg, 'Warning', wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
        event.Skip()

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
                self.btnApply.Enable()
            dlg.Destroy()
        return OnClick

    def OnFavoriteCamera(self, event):
        dlg = WifiDialog.WifiDialog(self)
        ret = dlg.ShowModal()
        dlg.Destroy()
        self.staticText6.SetLabel(globs.favoriteNetwork[globs.NET_SSID])
        self.btnApply.Enable()
        event.Skip()

    def OnColorPicker(self, event):
        dlg = ColorPickerDialog.ColorPickerDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.needRescan = True
            self.btnApply.Enable()
        dlg.Destroy()

    def OnMailPrefs(self, event):
        dlg = MailPreferencesDialog.MailPreferencesDialog(self)
        if dlg.ShowModal() == wx.ID_APPLY:
            self.btnApply.Enable()
            myprint('Mail Preferences have been updated')
        dlg.Destroy()
        
    def OnBtnReset(self, event):
        self._GUIReset()
        self.btnApply.Enable()
#        self.btnApply.SetDefault()
        event.Skip()

    def OnBtnCancel(self, event):
        # Restore initial colors
        globs.fileColors = deepcopy(self._tmpPkgColors)
        self.needRescan = False
        self.EndModal(wx.ID_CANCEL)
        event.Skip()

    def OnBtnApply(self, event):
        self._updateGlobalsFromGUI()
        self.parent._savePreferences()

        globs.thumbDir = os.path.join(globs.osvmDownloadDir, '.thumbnails')
        if not os.path.isdir(globs.thumbDir):
            myprint('Creating:', globs.thumbDir)
            try:
                os.makedirs(globs.thumbDir, exist_ok=True)
            except OSError as e:
                msg = "Cannot create %s: %s" % (globs.thumbDir, "{0}".format(e.strerror))
                dlg = wx.MessageDialog(None, msg, 'ERROR', wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                self.needRescan = False
                self.EndModal(wx.ID_CANCEL)
                return

        self.EndModal(wx.ID_APPLY)
        event.Skip()

    # def SavePrefsOnExit(self, event):
    #     self.btnApply.Enable()
    #     event.Skip()

    # def AskBeforeCommit(self, event):
    #     self.btnApply.Enable()
    #     event.Skip()

    # def AskBeforeExit(self, event):
    #     self.btnApply.Enable()
    #     event.Skip()

    def OnMaxDownloadChoice(self, event):
        globs.maxDownload = int(self.maxDownloadChoice.GetSelection())
        self.btnApply.Enable()
        event.Skip()

    def OnFileSortChoice(self, event):
        self.needRescan = True
        self.btnApply.Enable()
        event.Skip()

    def OnSsDelayChoice(self, event):
        globs.ssDelay = int(self.ssDelayChoice.GetSelection()) + self.MIN_SS_DELAY
        self.btnApply.Enable()
        event.Skip()

    def OnRotImgChoice(self, event):
        globs.rotImgChoice = int(self.rotImgChoice.GetSelection())
        self.needRescan = True
        self.btnApply.Enable()
        event.Skip()
    
    def OnDownLocTextCtrlText(self, event):
        self.tmpOsvmDownloadDir = self.downLocTextCtrl.GetValue()
        if os.path.exists(self.tmpOsvmDownloadDir):
            self.diskSpaceTextCtrl.SetValue(diskUsage(self.tmpOsvmDownloadDir)[2]) # Get Free Space
        else:
            self.diskSpaceTextCtrl.SetValue('????')
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

########################
def myprint(*args, **kwargs):
    """My custom print() function."""
    # Adding new arguments to the print function signature 
    # is probably a bad idea.
    # Instead consider testing if custom argument keywords
    # are present in kwargs
    __builtin__.print('%s():' % inspect.stack()[1][3], *args, **kwargs)

def humanBytes(size):
    power = float(2**10)     # 2**10 = 1024
    n = 0
    power_labels = {0 : 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size = float(size / power)
        n += 1
    return '%s %s' % (('%.2f' % size).rstrip('0').rstrip('.'), power_labels[n])

def diskUsage(path):
    st = os.statvfs(path)
    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    return (humanBytes(total), humanBytes(used), humanBytes(free))

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)
        panel = wx.Panel(self)
        dlg = PreferencesDialog(self)
        ret = dlg.ShowModal()
        dlg.Destroy()
        self.Destroy()
        
    def _savePreferences(self):	# dummy
        pass
    
def main():
    # Init Globals instance
    globs.system = platform.system()    # Linux or Windows or MacOS (Darwin)

    try:
        import objc # WifiDialog
    except ImportError:
        msg = 'Objc module not installed. Disabling Network Selector'
        print(msg)
        globs.networkSelector = False
        globs.disabledModules.append(('Objc',msg))
    else:
        globs.networkSelector = True
    
    # Init network (Mac only!!!)
    if globs.system == 'Darwin' and globs.networkSelector:
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

        globs.iface = CWInterface.interface()
        if not globs.iface:
            print('No Network Interface')

    # Create DemoFrame frame, passing globals instance as parameter
    app = wx.App(False)
    frame = MyFrame(None, -1, title="Test")
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
