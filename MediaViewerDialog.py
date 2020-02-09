#!/usr/bin/env python
import wx

import sys
import os
import builtins as __builtin__
import inspect
import time

#import osvmGlobals
moduleList = ['osvmGlobals']

for m in moduleList:
    print('Loading: %s' % m)
    mod = __import__(m, fromlist=[None])
    globals()[m] = globals().pop('mod')	# Rename module in globals()

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
    def __init__(self, parent, mediaFileListOrPath, globs):
        wx.Dialog.__init__(self, None, wx.ID_ANY, title="Media Viewer")

        self.mediaFileListOrPath = mediaFileListOrPath
        self.singleFile = False

        if type(self.mediaFileListOrPath).__name__ == 'str':
            fileName = os.path.basename(self.mediaFileListOrPath)
            self.singleFile = True
        else:
            fileName = self.mediaFileListOrPath[0][globs.F_NAME]
        suffix = fileName.split('.')[1]

        if suffix == 'JPG' or suffix == 'jpg':
            self.imageViewer(globs)
        else:
            if globs.vlcVideoViewer:
                self.videoViewer(globs)
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
    def imageViewer(self, globs):
        myprint('Launching imageViewer')
        self.imageFileListOrPath = self.mediaFileListOrPath

        width, height = wx.DisplaySize()
        self.btn = list()
        self.photoMaxSize = height - 200

        self.slideTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._imageNext, self.slideTimer)

        self.gaugeTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, lambda evt,temp=globs: self._gaugeTimerHandler(evt,temp), self.gaugeTimer)

        self.SetTitle("Image Viewer")

        self._imageInitialize(globs)

        if type(self.imageFileListOrPath).__name__ == 'list': # List of files
            self.listToUse = self.imageFileListOrPath	# Set list to use
            self.imgDirName = globs.osvmDownloadDir
            self.imgIdx = 0
            # Load first image manually
            self.imgFilePath = os.path.join(self.imgDirName, self.listToUse[0][globs.F_NAME])
            self._imageLoad(self.imgFilePath)
        else: # Single file
            # Directory containing the images
            self.imgDirName = os.path.dirname(self.imageFileListOrPath)
            # Get image index in localFilesSorted
            self.imgIdx = [x[0] for x in globs.localFilesSorted].index(os.path.basename(self.imageFileListOrPath))
            self.listToUse = [globs.localFilesSorted[self.imgIdx]]            # Set list to use
            self._imageLoad(self.imageFileListOrPath)
        
    def _imageInitialize(self, globs):
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

        self.btnPrev = wx.Button(label='Prev', parent=self, style=0)
        self.btnPrev.SetToolTip('Load previous Image')
        self.btnPrev.Bind(wx.EVT_BUTTON, lambda evt,temp=globs: self.imageOnBtnPrev(evt,temp))

        self.btnPlay = wx.Button(label='Play', parent=self, style=0)
        self.btnPlay.SetToolTip('Start the Slideshow')
        #        self.btnPlay.Bind(wx.EVT_BUTTON, self.imageOnBtnPlay)
        self.btnPlay.Bind(wx.EVT_BUTTON, lambda evt, temp=globs: self.imageOnBtnPlay(evt, temp))
            
        self.btnNext = wx.Button(label='Next', parent=self, style=0)
        self.btnNext.SetToolTip('Load Next Image')
        self.btnNext.Bind(wx.EVT_BUTTON, lambda evt, temp=globs: self.imageOnBtnNext(evt,temp))

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
        
    def imageOnBtnNext(self, event, globs):
        self.imgIdx = (self.imgIdx + 1) % len(self.listToUse)
        self.imgFilePath = os.path.join(self.imgDirName, self.listToUse[self.imgIdx][globs.F_NAME])

        # Skip over non JPG files
        suffix = self.imgFilePath.rsplit('.')[-1:][0]
        while suffix != 'JPG' and suffix != 'jpg':
            print('Skipping over',self.imgFilePath)
            self.imgIdx = (self.imgIdx + 1) % len(self.listToUse)
            self.imgFilePath = os.path.join(self.imgDirName, self.listToUse[self.imgIdx][globs.F_NAME])
            suffix = self.imgFilePath.rsplit('.')[-1:][0]

        self._imageLoad(self.imgFilePath)
        
    def imageOnBtnPrev(self, event, globs):
        self.imgIdx = self.imgIdx - 1
        if self.imgIdx < 0:
            self.imgIdx = len(self.listToUse) - 1
        self.imgFilePath = os.path.join(self.imgDirName, self.listToUse[self.imgIdx][globs.F_NAME])
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

    def _gaugeTimerHandler(self, event, globs):
        self.gaugeRemaining -= globs.TIMER5_FREQ # milli
        self.ssDelayGauge.SetValue(self.gaugeRemaining)
        
    def imageOnBtnPlay(self, event, globs):
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
       
    def imageOnBtnQuit(self, event):
        self.Destroy()
        self.EndModal(wx.ID_OK)

    ######### Video Viewer ##########
    def videoViewer(self, globs):
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

        # VLC player controls
        self.vlcInstance = vlc.Instance()
        self.mediaIsFinished = False

        self._videoInitialize(globs)

    def _videoSetWindow(self, player):
        # set the window id where to render VLC's video output
        handle = self.imageCtrl.GetHandle()
        if sys.platform.startswith('linux'): # for Linux using the X Server
            player.set_xwindow(handle)
        elif sys.platform == "win32": # for Windows
            player.set_hwnd(handle)
        elif sys.platform == "darwin": # for MacOS
            player.set_nsobject(handle)

    def _videoInitialize(self, globs):
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
        #        self.Bind(wx.EVT_BUTTON, self.videoOnBtnPlay, self.btnPlay)
        self.btnPlay.Bind(wx.EVT_BUTTON, lambda evt,temp=globs: self.videoOnBtnPlay(evt,temp))

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

    def videoOnBtnPlay(self, event, globs):
        button = event.GetEventObject()

        for e in self.listToUse: # each entry is a list containing filename as first field
            v = os.path.join(self.videoDirName, e[globs.F_NAME])
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
                self.timer.Start(globs.TIMER2_FREQ)
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


########################
def myprint(*args, **kwargs):
    """My custom print() function."""
    # Adding new arguments to the print function signature 
    # is probably a bad idea.
    # Instead consider testing if custom argument keywords
    # are present in kwargs
    __builtin__.print('%s():' % inspect.stack()[1][3], *args, **kwargs)

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title, globs):
        wx.Frame.__init__(self, parent, id, title)
        panel = wx.Panel(self)
        filePath = os.path.join( os.getcwd(), 'images', 'plus-32.jpg')
        dlg = MediaViewerDialog(self, filePath, globs)
        ret = dlg.ShowModal()
        dlg.Destroy()

        self.Show()

def main():
    # Create Globals instance
    g = osvmGlobals.myGlobals()

    g.vlcVideoViewer = vlcVideoViewer
    if not g.vlcVideoViewer:
        g.disabledModules.append(('VLC',msg))

    # Create a list of image files containing a single file
    g.localFileInfos['plus-32.jpg'] = ['plus-32.jpg', 0, 0, '']    
    g.localFilesSorted = sorted(list(g.localFileInfos.items()), key=lambda x: int(x[1][g.F_DATE]), reverse=g.fileSortRecentFirst)
    
            # Create DemoFrame frame, passing globals instance as parameter
    app = wx.App(False)
    frame = MyFrame(None, -1, title="Test", globs=g)
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
        
