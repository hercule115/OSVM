#!/usr/bin/env python
import wx

import sys
import os
import builtins as __builtin__
import inspect
import time

testImg = False # Test image or video ?

moduleList = {'osvmGlobals':'globs',
              'ExifDialog':'ExifDialog'}

for k,v in moduleList.items():
    print('Loading: %s as %s' % (k,v))
    mod = __import__(k, fromlist=[None])
    globals()[v] = globals().pop('mod')	# Rename module in globals()

try:
    import vlc # MediaViewer
except ImportError:
    msg = 'Vlc module not installed. Disabling Video Viewer'
    print(msg)
    vlcVideoViewer = False
else:
    vlcVideoViewer = True

####
#print(__name__)

### class MediaViewer
class MediaViewerDialog(wx.Dialog):
    def __init__(self, parent, mediaFileListOrPath, idx=0, slideShow=True):
        wx.Dialog.__init__(self, None, wx.ID_ANY, title="Media Viewer")

        self.mediaFileListOrPath = mediaFileListOrPath
        self.mediaListIdx = idx
        self.mediaSlideShow = slideShow
        self.singleFile = False

        exifFilePath = os.path.join(globs.osvmDownloadDir, globs.exifFile)
        if not os.path.exists(exifFilePath):
            myprint('%s does not exist. Creating' % exifFilePath)
            ExifDialog.saveExifDataFromImages(exifFilePath)
        # Load data from file
        self.exifData = ExifDialog.buildDictFromFile(exifFilePath)

        if type(self.mediaFileListOrPath).__name__ == 'str':
            fileName = os.path.basename(self.mediaFileListOrPath)
            self.singleFile = True
        else:
            fileName = self.mediaFileListOrPath[self.mediaListIdx]#286
        suffix = fileName.split('.')[1]

        if suffix.lower() == 'jpg' or suffix.lower() == 'png':
            self.imageViewer()
        else:
            if globs.vlcVideoViewer:
                self.videoViewer()
            else:
                self.Destroy()#???????
                return

        self.panel1.SetSizerAndFit(self.mainSizer)
        self.SetClientSize(self.mainSizer.GetSize())
        self.Centre()

        if self.mediaSlideShow:
            # Simulate a 'Play' event
            self._btnPlayInfo = getattr(self, "btnPlay")
            evt = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self._btnPlayInfo.GetId())
            evt.SetEventObject(self.btnPlay)
            wx.PostEvent(self.btnPlay, evt)

    ######### Image Viewer ##########
    def imageViewer(self):
        myprint('Launching imageViewer')
        self.imageFileListOrPath = self.mediaFileListOrPath
        self.imgIdx = self.mediaListIdx

        width, height = wx.DisplaySize()
        self.btn = list()
        self.photoMaxSize = height - 200

        self.slideTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._imageNext, self.slideTimer)

        self.gaugeTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, lambda evt: self._gaugeTimerHandler(evt), self.gaugeTimer)

        self.SetTitle("Image Viewer")

        self._imageInitialize()

        if type(self.imageFileListOrPath).__name__ == 'list': # List of files
            self.listToUse = self.imageFileListOrPath	# Set list to use
            self.imgDirName = globs.osvmDownloadDir
            # Load first image manually
            self.imgFilePath = os.path.join(self.imgDirName, self.listToUse[self.imgIdx])#286
            myprint('Loading image %s (idx %d)' % (self.imgFilePath, self.imgIdx))
            self._imageLoad(self.imgFilePath)
        else: # Single file
            # Get image index in localFilesSorted
            self.imgIdx = [x[0] for x in globs.localFilesSorted].index(os.path.basename(self.imageFileListOrPath))
            self.listToUse = [globs.localFilesSorted[self.imgIdx]]  # Set list to use (single item)
            self.imgFilePath = self.imageFileListOrPath
            self._imageLoad(self.imgFilePath)
            
    def _imageInitialize(self):
        """
        Layout the widgets on the panel
        """
        self.gaugeRange = int(globs.ssDelay) * 1000 # in milli
        self.gaugeRemaining = self.gaugeRange # in milli

        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self, size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        self.mainSizer      = wx.BoxSizer(wx.VERTICAL)
        self.btnSizer       = wx.BoxSizer(wx.HORIZONTAL)
        self.bottomBtnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.quitBoxSizer   = wx.BoxSizer(wx.HORIZONTAL)

        img = wx.Image(self.photoMaxSize,self.photoMaxSize)
        self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(img))

        self.mainSizer.Add(self.imageCtrl, 0, wx.ALL|wx.CENTER, 5)

        self.btnPrev = wx.Button(label='Prev', parent=self)
        self.btnPrev.SetToolTip('Load previous Image')
        self.btnPrev.Bind(wx.EVT_BUTTON, lambda evt: self.imageOnBtnPrev(evt))

        self.btnPlay = wx.Button(label='Play', parent=self)
        self.btnPlay.SetToolTip('Start the Slideshow')
        #        self.btnPlay.Bind(wx.EVT_BUTTON, self.imageOnBtnPlay)
        self.btnPlay.Bind(wx.EVT_BUTTON, lambda evt: self.imageOnBtnPlay(evt))
            
        self.btnNext = wx.Button(label='Next', parent=self)
        self.btnNext.SetToolTip('Load Next Image')
        self.btnNext.Bind(wx.EVT_BUTTON, lambda evt: self.imageOnBtnNext(evt))

        if self.singleFile:
            for b in [self.btnPrev,self.btnPlay,self.btnNext]:
                b.Disable()

        self.ssDelayGauge = wx.Gauge(range=self.gaugeRange, parent=self, size=(200,15))
        self.ssDelayGauge.SetValue(self.gaugeRange)

        # Exif Data button
        self.btnExif = wx.Button(label='Exif Data', parent=self)
        self.btnExif.SetToolTip('Show the Exif Data')
        self.btnExif.Bind(wx.EVT_BUTTON, self.imageOnBtnExif)

        self.btnQuit = wx.Button(id=wx.ID_CLOSE, parent=self)
        self.btnQuit.SetToolTip('Quit Viewer')
        self.btnQuit.Bind(wx.EVT_BUTTON, self.imageOnBtnQuit)

        self.btnSizer.Add(self.btnPrev, 0, border=10, flag=wx.EXPAND| wx.ALL)
        self.btnSizer.Add(self.btnPlay, 0, border=10, flag=wx.EXPAND| wx.ALL)
        self.btnSizer.Add(self.btnNext, 0, border=10, flag=wx.EXPAND| wx.ALL)
        self.btnSizer.AddStretchSpacer(prop=1)
        self.btnSizer.Add(self.ssDelayGauge, 0, border=10, flag=wx.EXPAND| wx.ALL)
        self.btnSizer.AddStretchSpacer(prop=1)
        self.btnSizer.Add(self.btnExif, 0, border=10, flag=wx.EXPAND| wx.ALL)
        self.quitBoxSizer.Add(self.btnQuit, 0, border=10, flag=wx.EXPAND| wx.ALL)

        self.bottomBtnSizer.AddStretchSpacer(prop=1)
        self.bottomBtnSizer.Add(self.btnSizer, 0, flag=wx.EXPAND| wx.ALL)
        self.bottomBtnSizer.AddStretchSpacer(prop=1)
        self.bottomBtnSizer.Add(self.quitBoxSizer, 0, flag=wx.ALIGN_RIGHT)

        self.mainSizer.Add(self.bottomBtnSizer, 0, flag=wx.EXPAND| wx.ALL)

    def _imageLoad(self, imagePath):
        imageFileName = os.path.basename(imagePath)
        wximg = wx.Image(imagePath, wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        W = wximg.GetWidth()
        H = wximg.GetHeight()
        if W > H:
            r = W / H
            NewW = self.photoMaxSize * r
            NewH = self.photoMaxSize
        else:
            NewH = self.photoMaxSize
            NewW = ( NewH * W ) / H
        wximg = wximg.Scale(NewW,NewH)

        #print(wx.DisplaySize(), self.photoMaxSize)
        #print(NewW,NewH)

        self.imageCtrl.SetBitmap(wx.Bitmap(wximg))
        self.SetTitle(imageFileName)
        try:
            entry = self.exifData[imageFileName]    # Exif data don't exist for filename
            self.btnExif.Enable()
        except:
            myprint('No Exif Data for file %s' % imageFileName)
            self.btnExif.Disable()
        self.Refresh()
        
    def imageOnBtnNext(self, event):
        self.imgIdx = (self.imgIdx + 1) % len(self.listToUse)
        self.imgFilePath = os.path.join(self.imgDirName, self.listToUse[self.imgIdx])#286

        # Skip over non JPG files
        suffix = self.imgFilePath.rsplit('.')[-1:][0].upper()
        while suffix != 'JPG':
            myprint('Skipping over %s' % self.imgFilePath)
            self.imgIdx = (self.imgIdx + 1) % len(self.listToUse)
            self.imgFilePath = os.path.join(self.imgDirName, self.listToUse[self.imgIdx])#286
            suffix = self.imgFilePath.rsplit('.')[-1:][0]

        self._imageLoad(self.imgFilePath)
        
    def imageOnBtnPrev(self, event):
        self.imgIdx = self.imgIdx - 1
        if self.imgIdx < 0:
            self.imgIdx = len(self.listToUse) - 1
        self.imgFilePath = os.path.join(self.imgDirName, self.listToUse[self.imgIdx])#286
        
        # Skip over non JPG files
        suffix = self.imgFilePath.rsplit('.')[-1:][0].upper()
        while suffix != 'JPG':
            myprint('Skipping over %s' % self.imgFilePath)
            self.imgIdx = (self.imgIdx - 1)
            if self.imgIdx < 0:
                self.imgIdx = len(self.listToUse) - 1
            self.imgFilePath = os.path.join(self.imgDirName, self.listToUse[self.imgIdx])#286
            suffix = self.imgFilePath.rsplit('.')[-1:][0].upper()

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
        self.gaugeRemaining -= globs.TIMER5_FREQ # milli
        self.ssDelayGauge.SetValue(self.gaugeRemaining)
        
    def imageOnBtnPlay(self, event):
        if len(self.listToUse) == 1: # Single file, nothing to do
            return

        # Starts and stops the slideshow
        button = event.GetEventObject()
        label = button.GetLabel()
        if label == 'Play':
            self.slideTimer.Start(int(globs.ssDelay) * 1000)
            self.gaugeTimer.Start(globs.TIMER5_FREQ)
            button.SetLabel('Stop')
        else:
            self.slideTimer.Stop()
            self.gaugeTimer.Stop()
            button.SetLabel('Play')

    def imageOnBtnExif(self, event):
        fileName = os.path.basename(self.imgFilePath)
        dlg = ExifDialog.ExifDialog(self, self.imgFilePath, self.exifData[fileName])
        dlg.ShowModal()
        dlg.Destroy()
        event.Skip()
            
    def imageOnBtnQuit(self, event):
        self.Destroy()
        self.EndModal(wx.ID_OK)

    ######### Video Viewer ##########
    def videoViewer(self):
        myprint('Launching videoViewer')
        self.videoFileListOrPath = self.mediaFileListOrPath
        self.videoDirName = globs.osvmDownloadDir

        if type(self.videoFileListOrPath).__name__ == 'list': # List of files
            self.listToUse = self.videoFileListOrPath	# Set list to use
        else: # single file
            self.listToUse = [[self.videoFileListOrPath]] # List of list

        # create the timer, which updates the timeslider
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.videoOnTimer, self.timer)

        # GUI controls
        self._videoInitialize()

        # VLC player controls
        self._videoVlcInitialize()

    def _videoSetWindow(self, player):
        # set the window id where to render VLC's video output
        handle = self.imageCtrl.GetHandle()
        if sys.platform.startswith('linux'): # for Linux using the X Server
            player.set_xwindow(handle)
        elif sys.platform == "win32": # for Windows
            player.set_hwnd(handle)
        elif sys.platform == "darwin": # for MacOS
            player.set_nsobject(handle)
            pass

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

        self.btnPrev = wx.Button(self, label='Prev')
        self.Bind(wx.EVT_BUTTON, self.videoOnBtnPrev, self.btnPrev)

        self.btnPlay = wx.Button(self, label='Play')
        self.Bind(wx.EVT_BUTTON, self.videoOnBtnPlayPause, self.btnPlay)

        self.btnStop = wx.Button(self, label='Stop')
        self.Bind(wx.EVT_BUTTON, self.videoOnBtnStop, self.btnStop)

        self.btnNext = wx.Button(self, label='Next')
        self.Bind(wx.EVT_BUTTON, self.videoOnBtnNext, self.btnNext)
        
        self.btnVolume = wx.Button(self, label='Mute')
        self.Bind(wx.EVT_BUTTON, self.videoOnBtnVolume, self.btnVolume)

        self.volSlider = wx.Slider(self, -1, 0, 0, 100)
        self.Bind(wx.EVT_SLIDER, self.videoOnVolSlider, self.volSlider)

        self.btnQuit = wx.Button(self, id=wx.ID_CLOSE)
        self.btnQuit.SetToolTip('Quit Viewer')
        self.btnQuit.Bind(wx.EVT_BUTTON, self.videoOnBtnQuit)
        self.quitBoxSizer.Add(self.btnQuit, 0, border=5, flag=wx.EXPAND| wx.ALL)

        self.timeSliderSizer.AddStretchSpacer(prop=1)
        self.timeSliderSizer.Add(self.timeElapsed)
        self.timeSliderSizer.Add(8, 0)
        self.timeSliderSizer.Add(self.timeSlider, 4)
        self.timeSliderSizer.AddStretchSpacer(prop=1)

        self.btnSizer.Add(self.btnPrev, 0, border=5, flag=wx.EXPAND| wx.ALL)
        self.btnSizer.Add(self.btnPlay, 0, border=5, flag=wx.EXPAND| wx.ALL)
        self.btnSizer.Add(self.btnStop, 0, border=5, flag=wx.EXPAND| wx.ALL)
        self.btnSizer.Add(self.btnNext, 0, border=5, flag=wx.EXPAND| wx.ALL)
        self.btnSizer.AddStretchSpacer(prop=1)
        self.btnSizer.Add(self.btnVolume, 0, border=5, flag=wx.EXPAND| wx.ALL)
        self.btnSizer.Add(self.volSlider, flag=wx.TOP | wx.LEFT, border=5)
        self.btnSizer.AddStretchSpacer(prop=2)
        self.btnSizer.Add(self.quitBoxSizer, 0, flag=wx.ALIGN_RIGHT)

        # Put everything together
        self.mainSizer.Add(self.imageCtrl, 0, wx.ALL|wx.CENTER, border=5)
        self.mainSizer.Add(self.timeSliderSizer, flag=wx.EXPAND, border=0)
        self.mainSizer.Add(self.btnSizer, 1, flag=wx.EXPAND)

    def _videoVlcInitialize(self):
        # Create a VLC Instance
        self.vlcInstance = vlc.Instance()  # '--verbose 1'.split())
        # Create a VLC MediaListPlayer instance
        self.vlcMLPlayer = self.vlcInstance.media_list_player_new()
        # Create a VLC Player instance and bind it to our MediaListPlayer
        self.vlcPlayer = self.vlcInstance.media_player_new()
        self.vlcMLPlayer.set_media_player(self.vlcPlayer)
        # Create a VLC Media List Instance
        self.mediaList = self.vlcInstance.media_list_new() #ml
        for e in self.listToUse: # each entry is a list containing filename as first field
            # Skip over non MOV files
            suffix = e[globs.F_NAME].rsplit('.')[-1:][0].upper()
            if suffix != 'MOV':
                #myprint('Skipping over %s' % (e[globs.F_NAME]))
                continue
            filePath = os.path.join(self.videoDirName, e)#286
            myprint('Adding %s' % filePath)
            media = vlc.Media(filePath)
            self.mediaList.add_media(media)
        self.vlcMLPlayer.set_media_list(self.mediaList)
        # Bind the Media Player to our bitmap
        self._videoSetWindow(self.vlcPlayer)
        
        # Create VLC Player Event Manager instances
        self.vlcMLPEvent0 = self.vlcMLPlayer.event_manager()
        # self.vlcMLPEvent0.event_attach(vlc.EventType.MediaListEndReached, self._videoMediaListEndReached)

        self.vlcMLPEvent0.event_attach(vlc.EventType.MediaListPlayerNextItemSet, self._videoMediaListPlayerNextItemSet) #self._videoMediaListPlayerCallback)

        self.vlcPEventS = self.vlcPlayer.event_manager()
        self.vlcPEventS.event_attach(vlc.EventType.MediaPlayerStopped, self._videoMediaPlayerStopped)

        self.vlcPEventP = self.vlcPlayer.event_manager()
        self.vlcPEventP.event_attach(vlc.EventType.MediaPlayerPaused, self._videoMediaPlayerPaused)
        
        self.vlcPEventE = self.vlcPlayer.event_manager()
        self.vlcPEventE.event_attach(vlc.EventType.MediaPlayerEndReached, self._videoMediaPlayerFinished)
        # Tweak configuration depending on current parameters
        if self.mediaList.count() == 1:
            self.btnNext.Disable()

    def _videoReset(self):
        if self.vlcMLPlayer.is_playing():
            myprint('Stopping VLC MediaListPlayer')
            self.vlcMLPlayer.stop()
            time.sleep(1)
        # Release VLC objects
        self.vlcPlayer.release()
        self.vlcMLPlayer.release()
        self.vlcInstance.release()
        myprint('VLC Instance released')

    ## Events
    def _videoMediaListPlayerNextItemSet(self, event):
        # Set Window Title
        mediaTitle = vlc.Media(event.u.media).get_meta(vlc.Meta.Title)
        self.SetTitle(mediaTitle)
        self.btnPlay.SetLabel('Pause')
        
    def videoOnBtnPrev(self, event):
        """Rewind to previous/beginning of media."""
        myprint('Rewinding Media')
        if self.vlcMLPlayer.previous():
            myprint('No previous item')
        self.btnStop.Enable()
        event.Skip()            
        
    def videoOnBtnPlayPause(self, event):
        button = event.GetEventObject()

        if button.GetLabel() == 'Play':
            button.SetLabel('Pause')
            self._videoOnBtnPlay()
        else:
            button.SetLabel('Play')
            self._videoOnBtnPause()
        event.Skip()

    def _videoOnBtnPause(self):
        myprint('Pausing Player')
        if self.vlcMLPlayer.is_playing():
            self.vlcMLPlayer.pause()
            
    def _videoOnBtnPlay(self):            
        """ Try to launch the media. If it fails, display an error message."""
        if self.vlcMLPlayer.play() == -1:
            dlg = wx.MessageDialog(self, 'Unable to play', 'Error', wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            self._videoReset()    # Destroy VLC objects
            self.Close()
            return
        myprint('MediaListPlayer is playing...')
        self.timer.Start(globs.TIMER2_FREQ)
        self.btnStop.Enable()
        
    def videoOnBtnStop(self, event):
        """Stop the Player."""
        myprint('Stopping Player')
        self.vlcMLPlayer.stop()
        self.btnPlay.SetLabel('Play')        
        # reset the time slider
        self.timeSlider.SetValue(0)
        self.timeElapsed.SetLabel('00:00:00')
        self.SetTitle('Media Viewer')
        self.btnStop.Disable()
        event.Skip()        

    def videoOnBtnNext(self, event):
        """Skip to next item."""
        myprint('Skipping to next item in list')        
        if self.vlcMLPlayer.next():
            myprint('No next item')
        self.btnStop.Enable()
        event.Skip()
        
    def videoOnTimer(self, event):
        # since the self.player.get_length can change while playing,
        # re-set the timeslider to the correct range.
        self.timeSlider.SetRange(-1, self.vlcPlayer.get_length())

        #if self.playerIsStopped:
        if not self.vlcMLPlayer.is_playing():            
            return
        else:
            # update the time on the slider
            self.elapsed = self.vlcPlayer.get_time()
            sec =  self.elapsed / 1000
            m, s = divmod(sec, 60)
            h, m = divmod(m, 60)
            #print('%02d:%02d\r' % (m,s), end='', flush=True)
            self.timeSlider.SetValue(self.elapsed)
            self.timeElapsed.SetLabel('%02d:%02d:%02d' % (h,m,s))
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
            self.oVolume = self.vlcMLPlayer.audio_get_volume()
            self.oVolSlider = self.volSlider.GetValue()
            self.vlcMLPlayer.audio_set_volume(0)
            self.volSlider.SetValue(0)
            myprint('Muting:', 'ovolume=',self.oVolume,'pos=',self.oVolSlider)
        else:
            button.SetName('btnMute') 
            button.SetLabel('Mute')
            self.vlcMLPlayer.audio_set_volume(self.oVolume)
            self.volSlider.SetValue(self.oVolSlider)
            myprint('Unmuting:', 'ovolume=',self.oVolume,'pos=',self.oVolSlider)

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
        if self.vlcMLPlayer.audio_set_volume(volume) == -1:
            dlg = wx.MessageDialog(self, 'Failed to set volume', 'Error', wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
        if volume > 0:
            self.btnVolume.SetName('btnMute') 
            self.btnVolume.SetLabel('Mute')

    def videoOnBtnQuit(self, event):
        self._videoReset()
        # Stop the timer
        self.timer.Stop()
        self.Close()
        event.Skip()
        
    # def _videoMediaListEndReached(self, event):
    #     myprint('End of media list reached')
    
    def _videoMediaPlayerStopped(self, event):
        myprint('Player stopped')

    def _videoMediaPlayerPaused(self, event):
        myprint('Player paused')

    def _videoMediaPlayerFinished(self, event):
        myprint('Media Player finished')
        self.btnPlay.SetLabel('Play')

########################
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
        panel = wx.Panel(self)

        #filePath = os.path.join( os.getcwd(), 'images', 'plus-32.jpg')
        #filePath = '/Users/didier/SynologyDrive/Photo/TEST2/n.jpg'
        #filePath = '/Users/didier/SynologyDrive/Photo/Olympus TG4/P3302742.MOV'

        #filePath = '/Users/didier/SynologyDrive/Photo/Galaxy S3/IMG_20190605_121158.jpg'
        #dlg = MediaViewerDialog(self, filePath)

        if testImg:
            mediaList = list()
            mediaList.append('/Users/didier/SynologyDrive/Photo/Galaxy S3/IMG_20190605_121158.jpg')
            mediaList.append('/Users/didier/SynologyDrive/Photo/Galaxy S3/20170907_142805.jpg')
            mediaList.append('/Users/didier/SynologyDrive/Photo/Galaxy S3/IMG_20190526_185518.jpg')
            dlg = MediaViewerDialog(self, mediaList, idx=0, slideShow=True)
        else:
            mediaList = list()
            mediaList.append('/Users/didier/SynologyDrive/Photo/Olympus TG4/P3302741.MOV')
            mediaList.append('/Users/didier/SynologyDrive/Photo/Olympus TG4/P3302742.MOV')
            mediaList.append('/Users/didier/SynologyDrive/Photo/Olympus TG4/P3302739.MOV')
            filePath = '/Users/didier/SynologyDrive/Photo/Olympus TG4/P3302742.MOV'
            dlg = MediaViewerDialog(self, mediaList, idx=0, slideShow=True)

        ret = dlg.ShowModal()
        dlg.Destroy()

        self.Show()
        self.Destroy()

def main():
    # Init Globals instance
    globs.vlcVideoViewer = vlcVideoViewer
    if not globs.vlcVideoViewer:
        globs.disabledModules.append(('VLC',msg))

    globs.osvmDownloadDir = '/Users/didier/SynologyDrive/Photo/Galaxy S3'
        
    # Create a list of image files containing a single file
    #globs.localFileInfos['plus-32.jpg'] = ['plus-32.jpg', 0, 0, '']
    #globs.localFileInfos['n.jpg'] = ['n.jpg', 0, 0, '']
    globs.localFileInfos['IMG_20190605_121158.jpg'] = ['IMG_20190605_121158.jpg', 0, 0, '']

    #globs.localFileInfos['P3302741.MOV'] = ['P3302741.MOV', 0, 0, '']
    #globs.localFileInfos['P3302742.MOV'] = ['P3302742.MOV', 0, 0, '']
    #globs.localFileInfos['P3302739.MOV'] = ['P3302739.MOV', 0, 0, '']

    globs.localFilesSorted = sorted(list(globs.localFileInfos.items()), key=lambda x: int(x[1][globs.F_DATE]), reverse=globs.fileSortRecentFirst)
    
    # Create DemoFrame frame, passing globals instance as parameter
    app = wx.App(False)
    frame = MyFrame(None, -1, title="Test")
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
        
