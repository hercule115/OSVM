#!/usr/bin/env python
import wx

import ast
import builtins as __builtin__
import ctypes
import datetime
import inspect
import math
import os
#from PIL import Image, ImageOps  # ExifTags,
import platform
import queue
import re
import socket
import subprocess
import sys
import threading
import time
from urllib.error import URLError
from urllib.request import Request, urlopen
#import urllib.request, urllib.error    # urllib.parse, 

moduleList = {'osvmGlobals':'globs',
              'LedControl' :'LedControl',
              'ExifDialog' :'ExifDialog',
              'rotateImage':'rotateImage'}

for k,v in moduleList.items():
    print('Loading: %s as %s' % (k,v))
    mod = __import__(k, fromlist=[None])
    globals()[v] = globals().pop('mod')	# Rename module in globals()

exifFilePath = ''
exifDataDict = {}

####
def downloadFile(op, pDialog):
    global exifFilePath
    global exifDataDict

    fileName   = op[globs.OP_FILENAME]
    localFile  = op[globs.OP_FILEPATH]
    remoteFile = op[globs.OP_REMURL]
    remSize    = op[globs.OP_SIZE][0]
    remBlocks  = op[globs.OP_SIZE][1]
    thr        = op[globs.OP_INTH]

    myprint('%s: %s %s %d %d' % (thr.name, remoteFile, localFile, remSize, remBlocks))

    # Hack to use existing local file to save download time
    if not globs.overwriteLocalFiles:
        myprint('%s: Checking for local file: %s' % (thr.name, localFile))
        if os.path.isfile(localFile): 
            try: 
                f = open(localFile, 'r')
            except IOError:
                os.remove(localFile)
                myprint('%s: Cannnot use existing local file %s. Will download' % (thr.name, fileName))
            else:
                f.close()
                # Should check local file size here...
                statinfo = os.stat(localFile)
                myprint("%s: file: %s size: local: %d remote: %d" % (thr.name, fileName, statinfo.st_size, remSize))
                if statinfo.st_size != remSize:	
                    msg = "%s: Local file %s has a wrong size (%d/%d). Deleting local file" % (thr.name, fileName, statinfo.st_size, remSize)
                    myprint(msg)
                    os.remove(localFile)
                else:
                    myprint('%s: Skipping download. Using available local file: %s' % (thr.name, fileName))
                    return (0, '')

    try:
        out = open(localFile, 'wb')
    except IOError as e:
        msg = "%s: I/O error: Opening output file %s %s" % (thr.name, localFile, "({0}): {1}".format(e.errno, e.strerror))
        myprint (msg)
        return (-1, msg)

    req = Request(remoteFile)
    try:
        myprint('Opening %s' % req)
        response = urlopen(req, timeout=10)
    except socket.error as e:
        myprint('Connection Timed Out')
        return (-1, 'Connection Timed Out (%s)' % remoteFile)
    except ConnectionResetError as e:
        myprint('ConnectionResetError',e)
        return (-1, 'Connection Reset Error (%s)' % remoteFile)
    except URLError as e:
        if hasattr(e, 'reason'):
            myprint('Failed to reach the server/camera.')
            myprint('Reason: ', e.reason)
            return (-1, e.reason)
        elif hasattr(e, 'code'):
            myprint('The server/camera couldn\'t fulfill the request.')
            myprint('Error code: ', e.code)
            return (-1, e.code)
        else:
            pass            # everything is fine

    msg = "%s: Starting transfer %s" % (thr.name,remoteFile)
    myprint (msg)

    blockSize = globs.URLLIB_READ_BLKSIZE
    op[globs.OP_INCOUNT] = 0
    ret = 0
    while pDialog.keepGoing:
        try:
            #myprint('Reading chunk')
            chunk = response.read(blockSize)

            if thr.isStopped():
                myprint('%s: Thread stopped. Aborting transfer' % thr.name)
                ret = -2
                break
        except:
            myprint('%s: Error: Downloading file' % thr.name)
            ret = -1
            break
        if not chunk: 
            # End of transfer
            myprint('%s: End of transfer detected' % thr.name)
            #wx.CallAfter(pDialog.updateCounter, op, 1)
            pDialog.updateCounter(op, 1)
            break
        out.write(chunk)
        #time.sleep(1)#XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        op[globs.OP_INCOUNT] += 1
        #print ('downloadFile(): blkno=',op[globs.OP_INCOUNT],keepGoing)
    out.flush()
    out.close()

    # Sanity check:
    # Check if user has cancelled the transfer or wrong transfer size
    try:
        statinfo = os.stat(localFile)
    except:
        myprint('%s does not exist anymore' % localFile)
        return (ret, '')
    else:
        myprint('keepGoing=%s localSize=%d remoteSize=%d' % (pDialog.keepGoing,statinfo.st_size,remSize))
        if not pDialog.keepGoing or statinfo.st_size != remSize:	
            msg = "%s: Downloaded file %s has a wrong size (%d/%d). Deleting" % (thr.name, fileName, statinfo.st_size, remSize)
            os.remove(localFile)
            ret = -1
            return (ret, msg)
        elif statinfo.st_size == remSize:
            # Set modification date to date of media file
            d1 = getHumanDate(globs.availRemoteFiles[fileName][globs.F_DATE])
            t1 = getHumanTime(globs.availRemoteFiles[fileName][globs.F_TIME])
            m,d,y = d1.split('/')
            H,M,S = t1.split(':')

            dt = datetime.datetime(int(y),int(m),int(d),int(H),int(M),int(S)) # year, month, day, hour, min, sec
            modTime = time.mktime(dt.timetuple())
            os.utime(localFile, (modTime, modTime))

    # Check if file needs rotation
    try:
        myprint('Checking if %s needs rotation' % os.path.basename(localFile))
        exifDataAsStr = exifDataDict[os.path.basename(localFile)]
    except:
        myprint('No Exif data for %s' % localFile)
    else:
        rotateImage.rotateImage(localFile, ast.literal_eval(exifDataAsStr))
            
    # Update Exif data cache file and re-load cache
    myprint('Updating Exif cache')
    if not os.path.exists(exifFilePath):
        myprint('%s does not exist. Creating' % exifFilePath)
        ExifDialog.saveExifDataFromImages(exifFilePath)
    else:   # Exif cache file already exists. Must update it
        try:
            myprint('Retrieving Exif Data for %s' % localFile)
            ed = ExifDialog.getExifData(localFile)
        except:
            myprint('Unable to get Exif data from file %s' % localFile)
        else:
            # Load existing exif data from file
            exifDataDict = ExifDialog.buildDictFromFile(exifFilePath)

            # Update dictionary containing exif data for all files
            myprint('Updating Exif Data Dict. Length=%d' % len(exifDataDict))
            try:
                foo = exifDataDict[os.path.basename(localFile)]
            except:
                myprint('exifDataDict[%s] does not exist. Adding.' % os.path.basename(localFile))
                exifDataDict[os.path.basename(localFile)] = str(ed)
            else:
                myprint('exifDataDict[%s] already exists.' % os.path.basename(localFile))

            # Update exif data cache file
            ExifDialog.saveFileFromDict(exifDataDict, exifFilePath)

    myprint('Updated Exif Data File. Reloading...')                    
    # Re-Load existing data from file after update
    exifDataDict = ExifDialog.buildDictFromFile(exifFilePath)
    return (ret, '')


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
        self._id = threading.current_thread().ident
        
        myprint('%s: Inited. id=%d' % (self._name, self._id))

    def stopIt(self):
        print('%s: Stopping' % self._name)
        self._stopper.set()
        myprint('%s: isStopped(): %s' % (self._name, self.isStopped()))

    def isStopped(self):
        return self._stopper.isSet()

    def getId(self):
        return self._id
        # returns id of the respective thread 
        if hasattr(self, '_thread_id'): 
            return self._thread_id 
        for id, thread in threading._active.items(): 
            if thread is self: 
                return id

    # Raise an exception to unblock a working thread
    def raiseException(self): 
        thread_id = self.getId()
        myprint('InstallThread %s, id %d raising exception' % (self._name, thread_id))
        #thread_id = self._id
        #myprint('%s: id=%d Raising exception' % (self._name, thread_id))
        #res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 
        #                                                 ctypes.py_object(SystemExit)) 
        #if res == 0:
        #    raise ValueError("Nonexistent thread id %d %d", thread_id, threading.current_thread().ident)
        #elif res > 1:
        #    myprint('Exception raise failure')
            # """if it returns a number greater than one, you're in trouble, 
            # and you should call it again with exc=NULL to revert the effect"""
        #    ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
        #    raise SystemError("PyThreadState_SetAsyncExc failed")

    def run(self):
        myprint('%s: Running. id=%d' % (self._name,self._id))
        while True:
            try:
                myprint("%s: Queue size: %d isStopped: %s" % (self._name, self._workQueue.qsize(), self.isStopped()))
                if self.isStopped():
                    myprint('%s: Thread is stopped, Exiting' % self._name)
                    return

                self._queueLock.acquire()
                if self._workQueue.empty():
                    self._queueLock.release()
                    myprint('%s: Queue is now empty, Exiting' % self._name)
                    return

                op = self._workQueue.get()
                self._queueLock.release()

                self.fileName   = op[globs.OP_FILENAME]
                self.localFile  = op[globs.OP_FILEPATH]
                self.remoteFile = op[globs.OP_REMURL]
                self.remSize    = op[globs.OP_SIZE][0]
                self.remBlocks  = op[globs.OP_SIZE][1]
                self.fileSize   = globs.availRemoteFiles[self.fileName][globs.F_SIZE]

                # Update subpanel to use for this operation
                #wx.CallAfter(self._pDialog.nextInstallSubPanel, op)
                self._pDialog.nextInstallSubPanel(op)
            
                myprint('%s: Processing file %s: (%sB, %d bytes %d blocks)' % (self._name, self.fileName, self.fileSize, self.remSize, self.remBlocks))

                # Store thread in current operation
                op[globs.OP_INTH] = self

                # step 0. Download file from camera
                wx.CallAfter(self._pDialog.startStep, op, 0, self._workQueue.qsize())
                (ret, msg) = downloadFile(op=op, pDialog=self._pDialog)
                myprint('%s: ret=%d msg=%s' % (self._name, ret, msg))
                if ret < 0:
                    if ret != -2:
                        #wx.CallAfter(self._pDialog.installError, 1, msg, op)
                        self._pDialog.installError(1, msg, op)
                        time.sleep(1) # some time for the GUI to refresh
                    op[globs.OP_INTH] = 0 # Done with this op
                    self._workQueue.task_done()
                    continue
                # End of transfer. Update total counter
                wx.CallAfter(self._pDialog.endStep, op, 0)
                time.sleep(1) # some time for the GUI to refresh

                op[globs.OP_INTH] = 0 # Done with this op
                self._workQueue.task_done()

            except socket.error as e:
                myprint('SocketError:',e)
                
            except ConnectionResetError as e:
                myprint('ConnectionResetError',e)
                self.stopIt()
            
            # except urllib.error.HTTPError as e:
            #     print("HTTP Error:",e.code,e.reason)
            # except urllib.error.URLError as e:
            #     print ("Connection Error:",e.reason)
            # except:
            #    myprint('%s: *** Got Exception. Stopping thread ***' % self._name)
            #    self.stopIt()

class MainInstallThread(threading.Thread):
    def __init__(self, parent, name, thrLock):
        threading.Thread.__init__(self)
        self._parent = parent
        self._name = name
        self._thrLock = thrLock

        self._threads = list()        # List of threads
        self._queueLock = threading.Lock()
        self._workQueue = queue.Queue(globs.MAX_OPERATIONS)
        self._stopper = threading.Event()

        self._downloadDir = globs.osvmDownloadDir
        myprint ('Started')

    def stopIt(self):
        myprint('Stopping child threads')
        for thr in self._threads:
            if thr.isAlive():
                myprint('Stopping thread: %s' % (thr.name))
                thr.stopIt()
                #thr.raiseException()
                thr.join()
        myprint('All child threads now stopped')
        
    def isStopped(self):
        return self._stopper.isSet()

    def run(self):
        myprint('Running, Waiting for Lock')
        self._thrLock.acquire() # will block until the 'InstallDialog' starts
        myprint('Lock acquired')

        # Clear list of threads
        self._threads = list()

        # Fill the queue with pending operations
        for op in globs.opList:
            if op[globs.OP_STATUS]:
                self._workQueue.put(op)

        myprint('workQueue size: %d, globs.maxDownload: %d' % (self._workQueue.qsize(),globs.maxDownload))

        # Exit if nothing to do
        if not self._workQueue.qsize():
            wx.CallAfter(self._parent.finish, '')
            self._thrLock.release()
            return

        # Create new install threads
        for i in range(globs.maxDownload):
            tName = 'th-%d' % i
            thr = InstallThread(tName, self._parent, self._thrLock, self._queueLock, self._workQueue)
            myprint('Thread created', thr)
            # Start the new thread in background
            thr.setDaemon(True)
            myprint('Starting thread %s' % (tName))
            thr.start()
            myprint('Thread started', thr)
            # Add the thread to the thread list
            self._threads.append(thr)

        # Wait for all threads to complete
        for t in self._threads:
            if t.is_alive():
                t.join()

        myprint('All threads have finished')

        # All Threads are exited. 
        myprint('Updating globs.localFileInfos')
        globs.localFilesCnt = localFilesInfo(globs.osvmDownloadDir)
        myprint('%d files on local host' % (globs.localFilesCnt))
 
        # Dialog cleanup if possible
        try:
            wx.CallAfter(self._parent.finish, '')
        except:
            pass

        # All Threads are exited. 
        myprint('Exiting')

    # Raise an exception to all worker threads to release threads
    def raiseException(self):
        for thr in self._threads:
            if thr.is_alive():
                myprint('Main Install Thread raising exception', thr.getId())
                self.keepGoing = False
                # #thr.raiseException()
                # res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thr.getId(),
                #                                                  ctypes.py_object(SystemExit)) 
                # if res == 0:
                #     raise ValueError("Nonexistent thread id %d",thr.getId())
                # elif res > 1:
                #     myprint('Exception raise failure')
                #     # """if it returns a number greater than one, you're in trouble, 
                #     # and you should call it again with exc=NULL to revert the effect"""
                #     ctypes.pythonapi.PyThreadState_SetAsyncExc(thr.getId(), 0)
                #     raise SystemError("PyThreadState_SetAsyncExc failed")

class InstallDialog(wx.Dialog):
    def __init__(self, parent, download, title):
        wx.Dialog.__init__(self, None, wx.ID_ANY, title, size=(600,500))#was 500,500
        self.parent = parent
        self.downloadDir = download
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

        myprint('Main Install Thread stopped:', self.mainInstallThr.isStopped())
        
        self._initialize()
        self._runThread()

    def _initialize(self):
        global exifFilePath
        global exifDataDict
    
        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self,
                               size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        # Create Top Level BoxSizer
        self.topBoxSizer = wx.BoxSizer(orient=wx.VERTICAL)

        # Loop thru all operations and fill details
        for i in range(len(globs.opList)):
            op = globs.opList[i]
            opStatus = op[globs.OP_STATUS]
            # If this operation is not used, skip it
            if not opStatus:
                continue

            fileName = op[globs.OP_FILENAME]
            self.numOps += 1

            dirName  = globs.availRemoteFiles[fileName][globs.F_DIRNAME]
            fileSize = globs.availRemoteFiles[fileName][globs.F_SIZE]

            # Save full pathname of local file
            op[globs.OP_FILEPATH] = os.path.join(self.downloadDir, fileName)

            nBlocks = fileSize / globs.URLLIB_READ_BLKSIZE
            op[globs.OP_SIZE] = (fileSize, nBlocks)
            fileUrl = '%s%s/%s' % (globs.osvmFilesDownloadUrl, dirName, fileName)
            op[globs.OP_REMURL] = fileUrl

            self.totalBlocks += math.ceil(nBlocks)

        myprint('%d operations configured' % self.numOps)

        self._createInstallSubPanels()
        self._createOtherControls()

        # Set a timer to count the elapsed time
        self.timer = wx.Timer(self, wx.ID_ANY)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

        # Initialize the Exif Data dict from Exif cache
        exifFilePath = os.path.join(globs.osvmDownloadDir, globs.exifFile)
        exifDataDict = ExifDialog.buildDictFromFile(exifFilePath)

        self.panel1.SetSizerAndFit(self.topBoxSizer)
        self.SetClientSize(self.topBoxSizer.GetSize())
        self.Centre()

    def _createInstallSubPanels(self):
        # sub-panel to contain 5 pending operations
        h = min(globs.installSubPanelsCount,self.numOps) * 60 + 40
        self.panel2 = wx.Panel(parent=self.panel1, id=wx.ID_ANY, size=(500,h),
                               style=wx.TAB_TRAVERSAL)

        # Create a BoxSizer (managed by panel2) for all the pending operations
        self.operationsGridSizer = wx.GridSizer(cols=1, vgap=5, hgap=5)

        for i in range(min(globs.installSubPanelsCount,self.numOps)):
            myprint('Creating subpanel #%d' % i)
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
            w = wx.StaticBoxSizer(box=opWidgets[globs.INST_STBOX], orient=wx.HORIZONTAL)
            opWidgets.append(w)

            # widget7. To contain time related widgets (globs.INST_GRDSZ)
            w = wx.FlexGridSizer(2, 2, vgap=5, hgap=5)
            opWidgets.append(w)

            # Add all time related widgets to its sizer
            w.Add(opWidgets[globs.INST_ELAPTXT], 0, border=5, flag=wx.EXPAND)
            w.Add(opWidgets[globs.INST_ELAPCNT], 0, border=5, flag=wx.EXPAND)
            w.Add(opWidgets[globs.INST_REMTXT], 0, border=5, flag=wx.EXPAND)
            w.Add(opWidgets[globs.INST_REMCNT], 0, border=5, flag=wx.EXPAND)

            # widget8 (globs.INST_LEDBOXSZ). Add 3 LEDs per operation: download, extract, install
            ledBoxSz = wx.BoxSizer(orient=wx.VERTICAL)
            opWidgets.append(ledBoxSz)
            ledList = [0,0,0]    # List of 3 LEDs

            # Meaning of each LED. Used by SetToolTip()
            ledMeans = [ 'File Download', 'File Extraction', 'File Installation' ]

            # Only 1 LED is enough
            myprint('color=%s' % globs.LEDS_COLOURS[globs.LED_GREY][0])
            ledList[0] = w = LedControl.ColorLED(self.panel2, globs.LEDS_COLOURS[globs.LED_GREY][0])
            w.SetToolTip(ledMeans[0])
            # Add this LED in the sizer 
            ledBoxSz.Add(w, 0, border=0, flag=wx.EXPAND)

            # Add ledList (globs.INST_LEDLIST) to the list of widgets for this op
            opWidgets.append(ledList)

            # Put the Gauge widgets in a sizer (globs.INST_GKBOXSZ)
            gkBoxSz = wx.BoxSizer(orient=wx.VERTICAL)
            opWidgets.append(gkBoxSz)

            gkBoxSz.AddStretchSpacer(prop=1)
            gkBoxSz.Add(opWidgets[globs.INST_GAUGE], 0, border=0, flag=wx.EXPAND)
            gkBoxSz.AddStretchSpacer(prop=1)

            # Add widgets related to this op in its sizer
            opWidgets[globs.INST_OPBOXSZ].Add(opWidgets[globs.INST_GKBOXSZ], 0, border=5, 
                                        flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
            opWidgets[globs.INST_OPBOXSZ].Add(8, 0, 1, border=0, flag=wx.EXPAND)
            opWidgets[globs.INST_OPBOXSZ].Add(opWidgets[globs.INST_LEDBOXSZ], 0, border=5, 
                                        flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
            opWidgets[globs.INST_OPBOXSZ].Add(8, 0, 1, border=0, flag=wx.EXPAND)
            opWidgets[globs.INST_OPBOXSZ].Add(opWidgets[globs.INST_GRDSZ], 0, border=5, 
                                        flag= wx.ALIGN_CENTER_VERTICAL) #211 wx.ALIGN_RIGHT | 

            # Finally add this operation in the operations grid sizer
            self.operationsGridSizer.Add(opWidgets[globs.INST_OPBOXSZ], 0, border=0, 
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
        myprint('totalBlocks=%f range=%d' % (self.totalBlocks, 
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

        self.sizeQueueLabel = wx.StaticText(label='Blocks:', parent=self.panel1, id=wx.ID_ANY)
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
                             flag=wx.ALL | wx.EXPAND)#211  | wx.ALIGN_RIGHT)

    # Local methods

    def _ping(self, server, timeout=10):
        #myprint('Pinging %s' % (server))
        ret = subprocess.call("ping -t %d -c 1 %s" % (timeout,server),
                              shell=True,
                              stdout=open('/dev/null', 'w'),
                              stderr=subprocess.STDOUT)
        return not ret # ret == 0 means server is alive
        
    def _checkConnectivity(self):
        import urllib.request
        import socket

        uri = globs.rootUrl
        try:
            urllib.request.urlopen(uri, timeout=1)
            return True
        except urllib.request.URLError:
            myprint('URLError while opening %s' % uri)
            return False
        except socket.timeout:
            myprint('Timeout while opening %s' % uri)
            return False
        except IOError as e:
            mymsg = "I/O error: Opening URL %s %s" % (uri, "({0}): {1}".format(e.errno, e.strerror))
            print(msg)
            return False

    def _runThread(self):
        # Process all DELETE operations first
        #deleteLocalFiles(self, globs.opList, globs)

        #dumpOperationList("Global Operation List")

        # Process all pending INSTALL/UPDATE operations
        # Start the main thread which will create all the sub-threads 
        # to do the actual transfer
        myprint('Releasing IntallThreadLock')
        self.mainInstallThrLock.release()	#Let the install threads run
        self.timer.Start(globs.TIMER1_FREQ)

    # Check if a package URL is valid
    def _checkRemoteFile(self, dirName, fileName):
        fileUrl = '%s%s/%s' % (globs.osvmFilesDownloadUrl, dirName, fileName)
        try:
            u = urllib.request.urlopen(fileUrl)
        except urllib.error.URLError as e:
            print(e.reason)
            return (-1, e.reason)

        totalSize = int(u.info()["Content-Length"])
        print('Remote File: %s size: %s bytes...' % (fileUrl,totalSize))
        return (totalSize, fileUrl)

    def _updateLabel(self, op):
        stBox = self.subPanel[globs.INST_STBOX]
        try:
            statinfo = os.stat(op[globs.OP_FILEPATH])
        except:
            myprint('%s does not exist' % op[globs.OP_FILEPATH])
            return

        wlabel = '%s  %s / %s' % (os.path.basename(op[globs.OP_FILEPATH]), 
                                  humanBytes(statinfo.st_size),
                                  humanBytes(op[globs.OP_SIZE][0]))
        stBox.SetLabel(wlabel)
        
    def _updateLeds(self, op):
        ledList = self.subPanel[globs.INST_LEDLIST]

        led = ledList[op[globs.OP_INSTEP]]      # LED to update
        state = op[globs.OP_INLEDSTATE]         # ON/BLINK/OFF
        color = globs.LEDS_COLOURS[op[globs.OP_INLEDCOL]][0]

        if state == globs.LED_BLINK:
            if self.totalSecs % 2:
                led.SetState(color)
            else:
                led.SetState(globs.LEDS_COLOURS[globs.LED_GREY][0])
        else:
            led.SetState(color)

    def _updateTotalCounter(self):
        self.totalCount = 0
        # How much has been done so far?
        for op in globs.opList:
            if not op[globs.OP_STATUS]: # or op[globs.OP_TYPE] == globs.FILE_DELETE:
                continue
            self.totalCount += op[globs.OP_INCOUNT]

        # update overall gauge
        try:
            self.ggAll.SetValue(self.totalCount)
        except:
            print('_updateTotalCounter(): Exception in SetValue(). count=%d' % (self.totalCount))

        elapsed = time.strftime('%H:%M:%S', time.gmtime(self.totalSecs))
        self.totalElapCnt.SetLabel(elapsed)

        if self.totalSecs:
            bandWidth = ((self.totalCount) * globs.URLLIB_READ_BLKSIZE) / (self.totalSecs * 1024)
            self.avSpeedCnt.SetLabel('%d KB/s' % bandWidth)
            # compute total remaining time (ETA)
            KBytesRemaining = ((self.totalBlocks - self.totalCount) * globs.URLLIB_READ_BLKSIZE) / 1024
            SecondsRemaining = int(KBytesRemaining / (bandWidth+1)) # Avoid div by 0
            self.ETACnt.SetLabel('%s' % (str(datetime.timedelta(seconds=SecondsRemaining))))

    # External callable methods

    # Set the subpanel to use. Update some widgets (filename, size,...)
    def nextInstallSubPanel(self, op):
        myprint('Using subpanel %d' % self.installSubPanelIdx)
        self.subPanel = self.installSubPanels[self.installSubPanelIdx]
        self.subPanel[globs.INST_GAUGE].SetRange(range=math.ceil(op[globs.OP_SIZE][1]))
        wlabel = '%s  %s' % (op[globs.OP_FILENAME], humanBytes(op[globs.OP_SIZE][0]))
        self.subPanel[globs.INST_STBOX].SetLabel(wlabel)
        self.installSubPanelIdx = (self.installSubPanelIdx + 1) % globs.installSubPanelsCount

    # Update the Install Dialog window containing the gauges
    # Called by the timer handler and by the worker thread
    def updateCounter(self, op, reason=0):
        # reason = 1 means final update for this download
        if reason:
            count = op[globs.OP_SIZE][1]
            myprint('final update:',count)
        else:
            count = op[globs.OP_INCOUNT]

        # update gauge for this operation
        self.subPanel[globs.INST_GAUGE].SetValue(count)

        # Update Elapsed time widget
        op[globs.OP_INTICKS] += 1
        elapsed = time.strftime('%H:%M:%S', time.gmtime(op[globs.OP_INTICKS]/globs.TICK_PER_SEC))

        # Update Remaining time widget
        approxTime =  (op[globs.OP_INTICKS] * op[globs.OP_SIZE][1]) / max(count, 1)
        remaining = time.strftime('%H:%M:%S', time.gmtime(abs((approxTime - op[globs.OP_INTICKS])/globs.TICK_PER_SEC)))

        # Update Elapsed time widget
        self.subPanel[globs.INST_ELAPCNT].SetLabel(elapsed)

        #  Update Remaining time widget
        self.subPanel[globs.INST_REMCNT].SetLabel(remaining)

        # Update the block transferred counter
        n = int(math.log10(self.totalBlocks))+1
        self.sizeQueueCnt.SetLabel('{s}/{t}'.format(s=self.totalCount,t=self.totalBlocks))

        # Any click on the Cancel button
        if self.installCanceled:
            self.keepGoing = False

        #print count,nBlocks,self.keepGoing,elapsed,approxTime,remaining

    def finish(self, msg):
        myprint('All transfers finished (%d/%d)' % (self.totalCount, self.totalBlocks))
        self.btnDone.Enable()
        self.btnCancel.Disable()
        self.timer.Stop()
        oMsg = self.statusBar.GetValue()
        self.statusBar.SetValue(oMsg + '\n' + msg + '\n' + 'End Of Transfer. %d error(s)' % self.errorCnt)
        # Notify parent to stop any animation
        wx.CallAfter(self.parent.finish)

    def installError(self, err, msg, op=None):
        #myprint(msg)
        self.errorCnt += err
        oldMsg = self.statusBar.GetValue()
        self.statusBar.SetValue(oldMsg + '\n' + str(msg))
        if op:
            op[globs.OP_INLEDSTATE] = globs.LED_ON
            op[globs.OP_INLEDCOL] = globs.LED_RED
            try:
                self._updateLeds(op)
            except:
                pass

    # Called at beginning of a given step: download/0, extract/1 or install/2
    def startStep(self, op, step, qSize):
        op[globs.OP_INSTEP] = step    # LED number
        op[globs.OP_INLEDSTATE] = globs.LED_BLINK
        op[globs.OP_INLEDCOL] = globs.LED_ORANGE
        # Get # digits in numOps
        numDigits = int(math.log10(self.numOps))+1
        # Format the fileQueueCnt label
        self.fileQueueCnt.SetLabel('{s:0{width}}/{t:0{width}}'.format(s=qSize,width=numDigits,t=self.numOps))

    # Called at end of a given install step: download/0, extract/1 or install/2
    def endStep(self, op, step):
        op[globs.OP_INSTEP] = step    # LED number
        op[globs.OP_INLEDSTATE] = globs.LED_ON
        op[globs.OP_INLEDCOL] = globs.LED_GREEN
        self._updateLeds(op)
        if step == 2:
            #  Clear emaining time widget
            self.subPanel[globs.INST_REMCNT].SetLabel('00:00:00')

    def getTransferInfo(self):
        return (self.totalBlocks,self.totalCount)
    
    #### Events ####

    def OnBtnCancel(self, event):
        self.timer.Stop()
        self.installCanceled = True
        # Stop the install threads
        self.mainInstallThr.stopIt()
        while self.mainInstallThr.isAlive():
            time.sleep(1)
        myprint('All Install threads are stopped')

    def OnBtnDone(self, event):
        self.timer.Stop()
        myprint('totalBlocks=%d totalCount=%d' % (self.totalBlocks,self.totalCount))
        self.EndModal(wx.ID_CLOSE)
        self.Close()
        event.Skip()

    def OnTimer(self, event):
        server = globs.rootUrl.split('/')[2].split(':')[0] # Get IP address from URL of the camera
        if not self._ping(server, 15):
            myprint('%s: Lost connection with %s. Aborting download' % (datetime.datetime.now().time(), server))
            self.keepGoing = False
            #self.mainInstallThr.raiseException()
            # Simulate a 'Cancel' event
            #evt = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self.btnCancel.GetId())
            #evt.SetEventObject(self.btnCancel)
            #wx.PostEvent(self.btnCancel, evt)
        else:
            self.keepGoing = True

        if self.numOps:   # Only if some file install/update
            for op in globs.opList:
                if not op[globs.OP_STATUS]:
                    continue
                # Update Counters/LEDs/Labels if transfer is active
                if op[globs.OP_INTH] and op[globs.OP_INTH].isAlive():
                    self.updateCounter(op)
                    self._updateLeds(op)
                    self._updateLabel(op)

        self.timerTicks += globs.TIMER1_FREQ
        self.totalSecs = self.timerTicks / 1000
        self._updateTotalCounter()

#######            
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

def humanBytes(size):
    power = float(2**10)     # 2**10 = 1024
    n = 0
    power_labels = {0 : 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size = float(size / power)
        n += 1
    return '%s %s' % (('%.2f' % size).rstrip('0').rstrip('.'), power_labels[n])

# Browse a directory, looking for filenames ending with: JPG, MOV, ORF, MPO, MP4
def listLocalFiles(dir, hidden=False, relative=True, suffixes=('jpg', 'mov', 'orf', 'mpo', 'mp4')):
#    suffixes = ('jpg', 'mov', 'orf', 'mpo', 'mp4')
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

# 
# Browse the Download directory.
# Output is a dictionary globs.localFileInfos{} containing:
# - key: fileName#
# - value: list of info for this file
#
# Return # entry in the dictionary
def localFilesInfo(dirName):
    myprint('dirName=%s globs.cameraConnected=%s' % (dirName, globs.cameraConnected))
    globs.localFileInfos = {}
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
            myprint('Error: os.stat()')
            continue
        
        # Check if local file exists on camera. Rotated images are bypassed
        if not '-rot' in fileName:
            if not globs.viewMode and globs.cameraConnected:
                try:
                    remFileName = globs.availRemoteFiles[fileName][globs.F_NAME]
                except:
                    # Local file does not exist anymore on remote/camera. Probably deleted...
                    myprint('File %s not found on remote/camera. Deleting.' % (fileName))
                    if globs.keepLocalFolderInSync:
                        print('deleting %s' % filePath)
                        #os.remove(filePath)
                    continue

#        if not globs.viewMode:
#            try:
#                remFileSize = 0
#                remFileSize = globs.availRemoteFiles[fileName][globs.F_SIZE]
#            except:
#                # Local file does not exist anymore on remote/camera. Probably deleted...
#                print('File %s not found on remote/camera' % (fileName))
#                if not remFileSize:
#                    print('MUST DELETE EMPTY LOCAL FILE %s' % (fileName))
#		     #os.remove(filePath)
#                    continue
#            else:
#                if localFileSize != remFileSize:
#                    print('MUST DELETE INCOMPLETE LOCAL FILE %s (%d)' % (fileName,localFileSize))
#                    os.remove(filePath)
#                    continue

        fileDate = statinfo.st_mtime # in seconds
        globs.localFileInfos[fileName] = [fileName,localFileSize,fileDate,filePath]
        i += 1
    globs.localFilesSorted = filterRotatedFiles(sorted(list(globs.localFileInfos.items()), key=lambda x: int(x[1][globs.F_DATEINSECS]), reverse=globs.fileSortRecentFirst))
    return i

def filterRotatedFiles(fileList):
    myprint('Filter =',globs.ROT_IMG_ENTRIES[globs.rotImgChoice])
    if globs.rotImgChoice == 0:
        # Must show rotated images if available and original files if not
        lrotonly = [x[1][0] for x in fileList if '-rot' in x[0]]     # list with rotated img only
        l = list()
        for e in fileList:
            #print('###',e)
            fileName = e[0]
            field11  = e[1][1]
            field12  = e[1][2]
            filePath = e[1][3]

            prefix = fileName.split('.')[0]	# File prefix
            if '-rot' in prefix: # Rotated file
                continue
            n = [x for x in lrotonly if re.search('%s-rot[0-9]+.jpg' % prefix, x, re.IGNORECASE)]
            if n:
                # Build a new tuple and append to output list
                t = (n[0], [ n[0],field11,field12,os.path.join(os.path.dirname(filePath),n[0])])
                l.append(t)
            else:
                l.append(e)
        return l

    if globs.rotImgChoice == 1:
        # Must show only original files even if some files have been rotated
        l = [x for x in fileList if not '-rot' in x[0]] # only original files
        return l

    if globs.rotImgChoice == 2:	# Show both rotated/not rotated files
        # Must show both rotated and non-rotated files, e.g. all files
        return fileList

########
class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)

        globs.opList = [[0] * globs.OP_LASTIDX for i in range(5)]

        globs.availRemoteFiles['P7062936.JPG'] = ['P7062936.JPG', 1599056, 1594058304, '', '/DCIM/100OLYMP', 0, 20710, 40780, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7062936.JPG']
        globs.availRemoteFiles['P7032921.JPG'] = ['P7032921.JPG', 1522484, 1593782206, '', '/DCIM/100OLYMP', 0, 20707, 31255, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7032921.JPG']
        globs.availRemoteFiles['P6122903.JPG'] = ['P6122903.JPG', 1540707, 1591972676, '', '/DCIM/100OLYMP', 0, 20684, 33980, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P6122903.JPG']
        globs.availRemoteFiles['P1080010.MOV'] = ['P1080010.MOV', 189579999, 1515394036, '', '/DCIM/100OLYMP', 0, 19496, 15848, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P1080010.MOV']
        globs.availRemoteFiles['P2250320.MOV'] = ['P2250320.MOV', 81976590, 1519538094, '', '/DCIM/100OLYMP', 0, 19545, 14043, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P2250320.MOV']
        globs.availRemoteFiles['P2250317.MOV'] = ['P2250317.MOV', 195780743, 1519537996, '', '/DCIM/100OLYMP', 0, 19545, 13992, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P2250317.MOV']
        
        # self._scheduleOperation(globs.opList[0], 'P2250320.MOV', 81976590, 1519538094)
        # self._scheduleOperation(globs.opList[1], 'P1080010.MOV', 189579999, 1515394036)
        # self._scheduleOperation(globs.opList[2], 'P2250317.MOV', 195780743, 1519537996)
        
        self._scheduleOperation(globs.opList[0], 'P7062936.JPG', 1599056, 1594058304)
        self._scheduleOperation(globs.opList[1], 'P7032921.JPG', 1522484, 1593782206)
        self._scheduleOperation(globs.opList[2], 'P6122903.JPG', 1540707, 1591972676)

        self.installDlg = InstallDialog(self,
                                        download=globs.osvmDownloadDir,
                                        title='Downloading Files')
        self.installDlg.ShowModal()
        self.installDlg.Destroy()
        self.Destroy()

    # stop statusBar1 animation
    def finish(self):
        myprint('Stopping animation.')
        
    def _scheduleOperation(self, op, fileName, fileSize, fileDate):
        op[globs.OP_STATUS]   = 1
        op[globs.OP_FILENAME] = fileName
        op[globs.OP_FILETYPE] = fileName.split('.')[1]
        op[globs.OP_TYPE]     = globs.FILE_DOWNLOAD
        nBlocks               = fileSize / globs.URLLIB_READ_BLKSIZE
        op[globs.OP_SIZE]     = (fileSize, nBlocks)
        op[globs.OP_FILEDATE] = fileDate
        op[globs.OP_FILEPATH] = os.path.join(globs.osvmDownloadDir, fileName)

def main():
    # Init Globals instance
    globs.osvmFilesDownloadUrl = 'http://192.168.0.10:80'
    globs.osvmDownloadDir = '/tmp'
    globs.tmpDir = '/tmp'
    globs.overwriteLocalFiles= True
    
    # Create a frame
    app = wx.App(False)
    frame = MyFrame(None, -1, title="Test")
    frame.Show(True)
    app.MainLoop()
   
if __name__ == "__main__":
    main()
