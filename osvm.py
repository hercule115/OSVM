#!/usr/bin/env python

# Create Globals instance
import osvmGlobals as globs

#import wx.lib.platebtn as platebtn

import sys
import platform

# Python version
globs.pythonVersion = (sys.version).split()[0]	# 2.x or 3.x ?
globs.system = platform.system()		# Linux or Windows or MacOS (Darwin)
globs.hostarch = platform.architecture()[0]	# 64bit or 32bit

if '2.' in globs.pythonVersion:
    try:
        # for Python2
        from Tkinter import *   ## notice capitalized T in Tkinter 
    except ImportError:
        # for Python3
        from tkinter import *   ## notice lowercase 't' in tkinter here

    root = Tk()
    root.title("ERROR!")
    label = Label(root, text="\nERROR: %s requires Python 3.x to run.\n\n" % (globs.myName))
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
        label = Label(root, text="\nERROR: %s requires wxPython widgets to run.\n\n" % (globs.myName) +
                      "wxPython is available at http://www.wxpython.org/\n\n" +
                      "%s has been developped and tested with python 3.6 and wxPython 4.0.1 (Cocoa)\n" % (globs.myName))
        label.pack()
        root.mainloop()
        exit()
        #raise ImportError,"The wxPython module is required to run this program."
    except:
        print("ERROR: %s requires wxPython widgets to run.\n\n" % (globs.myName)),\
        ("wxPython is available at http://www.wxpython.org/\n\n",) \
        ("%s has been developped and tested with python 3.6 and wxPython 4.0.1 (Cocoa)\n" % (globs.myName))
        exit()

import ast
import argparse
import builtins as __builtin__
import configparser
import ctypes
import datetime
import http.client
import inspect
import io
import math
import os
from os.path import expanduser
from PIL import Image, ImageOps  # ExifTags,
import queue
import re
from urllib.request import Request, urlopen
from urllib.error import URLError
import urllib.request, urllib.error    # urllib.parse, 
import shutil
import socket
import struct
import subprocess
import threading
import tempfile
import time
import wx.adv
import wx.lib.colourdb as wb
import wx.lib.inspection
from wx.lib.newevent import NewEvent
import wx.lib.agw.flatnotebook as fnb

#from copy import deepcopy
#import wx.lib.scrolledpanel as scrolled
#import glob
#import traceback
#from urllib.parse import urlparse

# Local modules
moduleList = (
    'ChromecastDialog',
    'CleanDownloadDirDialog',
    'DateDialog',
    'ExifDialog',
    'FileListFrame',
    'HelpDialog',
    'InstallDialog',
    'LedControl', 
    'LogFrame', 
    'LogoPanel', 
    'MailDialog',
    'MediaViewerDialog', 
    'PreferencesDialog', 
    'PropertiesDialog', 
    'rotateImage',
    'ThumbnailDialog', 
    'WifiDialog',
    'simpleQRScanner')

for m in moduleList:
    print('Loading %s' % m)
    mod = __import__(m, fromlist=[None])
    globals()[m] = globals().pop('mod') # Rename module in globals()

try:
    import pychromecast
except ImportError:
        msg = 'PyChromeCast module not installed. Disabling Casting'
        print(msg)
        globs.pycc = False
        globs.disabledModules.append(('PyChromecast',msg))
else:
    globs.pycc = True

try:
    import vlc # MediaViewer
except ImportError:
        msg = 'Vlc module not installed. Disabling Video Viewer'
        print(msg)
        globs.vlcVideoViewer = False
        globs.disabledModules.append(('VLC',msg))
else:
    globs.vlcVideoViewer = True

try:
    import objc # WifiDialog
except ImportError:
        msg = 'Objc module not installed. Disabling Network Selector'
        print(msg)
        globs.networkSelector = False
        globs.disabledModules.append(('Objc',msg))
else:
    globs.networkSelector = True


if globs.system == 'Windows':
    try:
        #print 'Importing Windows win32 packages'
        import win32api
        import win32process
        import win32event
    except ImportError:
        from tkinter import *

        root = Tk()
        root.title("ERROR!")
        label = Label(root, text="\nERROR: %s requires win32 module to run.\n\n" % (globs.myName) +
                      "win32 is available at http://sourceforge.net/projects/pywin32/files/pywin32/\n\n" +
                      "%s has been developped and tested with python 3.6, wxPython 4.0.1 and pywin32 219\n" % (globs.myName))
        label.pack()
        root.mainloop()
        sys.exit()
        #raise ImportError,"The win32 modules are not installed."

wxRescanNeeded, EVT_RESCAN_NEEDED = NewEvent()

########################################
def myprint(*args, **kwargs):
    """My custom print() function."""
    # Adding new arguments to the print function signature 
    # is probably a bad idea.
    # Instead consider testing if custom argument keywords
    # are present in kwargs
    __builtin__.print('%s():' % inspect.stack()[1][3], *args, **kwargs)

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

#    myprint(year, month, day, hours, minutes, seconds)
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

def cleanup():
    myprint('Destroying HTTP Server pid=%d' % globs.httpServer.pid)
    try:
        outs, errs = globs.httpServer.communicate(timeout=2)
    except subprocess.TimeoutExpired:
        myprint('Killing HTTP Server')
        globs.httpServer.kill()
        outs, errs = globs.httpServer.communicate()
    
    myprint('Removing temporary files')
    if os.path.exists(globs.htmlRootFile):
        try:
            os.remove(globs.htmlRootFile)
        except:
            myprint('Failed to remove %s' % (globs.htmlRootFile))

    if os.path.exists(globs.htmlDirFile):
        try:
            os.remove(globs.htmlDirFile)
        except:
            myprint('Failed to remove %s' % (globs.htmlDirFile))

    myprint('Removing corrupted/partial files')
    for v in globs.localFileInfos.values():
        filePath = v[globs.F_PATH]
        try:
            localFileSize = os.stat(filePath).st_size
        except:
            myprint('Error: os.stat()')
            continue
        else:
            if localFileSize == 0:
                myprint('Removing empty file %s' % filePath)
                os.remove(filePath)
    
def getTmpFile():
    f = tempfile.NamedTemporaryFile(delete=False)
    return f.name

def dumpOperationList(title, oplist):
    optype = ["DOWNLOAD", "MARK", "UNMARK"]
    opstep = ["DOWNLOAD", "EXTRACT", "INSTALL"]
    i = 0
    print('**** Dump: %s ****' % title)
    for op in oplist:
#        print ('%d: STATUS: %d' % (i, op[globs.OP_STATUS]))
        if op[globs.OP_STATUS] != 0:
            print('*** %d ***' % (i))
            print('         File Name: %s' % op[globs.OP_FILENAME])
            print('         File Path: %s' % op[globs.OP_FILEPATH])
            print('         File Type: %s' % op[globs.OP_FILETYPE])
            ldate = time.strftime('%d-%b-%Y %H:%M', time.localtime(op[globs.OP_FILEDATE]))
            print('         File Date: %s' % ldate)
            print('      Request Type: %s' % optype[op[globs.OP_TYPE]])

            if op[globs.OP_TYPE] == globs.FILE_DOWNLOAD:
                print('    Local filename: %s' % op[globs.OP_FILEPATH])
                print('    Remote File URL: %s' % op[globs.OP_REMURL])
                print('    Remote File Size: %d/%d' % (op[globs.OP_SIZE][0],op[globs.OP_SIZE][1]))
                print('    Current Transfer Block Counter: %d' % op[globs.OP_INCOUNT])
                print('    Current Installation Step: %s' % opstep[op[globs.OP_INSTEP]])

            if op[globs.OP_INTH]:
                print('    Installation Thread: %s' % op[globs.OP_INTH].name)
        i += 1

#
# Remove a local file. return -1 in case of failure
#
# def removeFile(pathname):
#     try:
#         myprint('Deleting:',pathname)
#         os.remove(pathname)
#     except OSError as e:
#         msg = "Cannot remove %s: %s" % (pathname, "{0}".format(e.strerror))
#         myprint(msg)
#         return -1
#     return 0

#
# Create a symbolic link on source. return -1 in case of failure
#
def createSymLink(path, link):
    try:
        myprint('path=%s link=%s' % (path,link))
        os.symlink(path, link)
    except IOError as e:
        msg = "I/O error: %s %s" % ("({0}): {1}".format(e.errno, e.strerror),link)
        myprint(msg)
        return -1
    return 0

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
        
def downloadThumbnail(e):
    uri       = e[globs.F_THUMBURL]
    thumbFile = e[globs.F_NAME]
    thumbSize = e[globs.F_SIZE]

    thumbnailPath = os.path.join(globs.thumbDir, thumbFile)

    if os.path.isfile(thumbnailPath): 
        try: 
            f = open(thumbnailPath, 'r')
        except IOError:
            os.remove(thumbnailPath)
            myprint('%s: Cannot use existing thumbnail. Will download it' % (thumbFile))
        else:
            f.close()  # Using available local file
#            myprint('Using existing thumbnail %s' % (thumbFile))
            return 0

    if globs.cameraConnected:
        myprint("Downloading %s from camera" % (thumbFile))
        try:
            response = urllib.request.urlopen(uri)
        except IOError as e:
            msg = "I/O error: Opening URL %s %s" % (uri, "({0}): {1}".format(e.errno, e.strerror))
            myprint(msg)
            globs.cameraConnected = False

    if globs.cameraConnected:
        tmp = response.read()

        try:
            myprint("Creating %s" % (thumbnailPath))
            out = open(thumbnailPath, 'wb')
            out.write(tmp)
            out.close()
            return 0
        except IOError as e:
            msg = "I/O error: Creating %s: %s" % (thumbnailPath, "({0}): {1}".format(e.errno, e.strerror))
            myprint(msg)
            return -1

def getRootDirInfo(rootDir, uri):
    if globs.cameraConnected:
        myprint("Downloading from network: %s" % (uri))
        try:
            response = urllib.request.urlopen(uri)
        except IOError as e:
            msg = "I/O error: Opening URL %s %s" % (uri, "({0}): {1}".format(e.errno, e.strerror))
            myprint(msg)
            globs.cameraConnected = False

    if globs.cameraConnected:
        tmp = response.read()

        try:
            myprint("Opening: %s" % (globs.htmlDirFile))
            out = open(globs.htmlDirFile, 'wb')
            out.write(tmp)
            out.close()
        except IOError as e:
            msg = "I/O error: Opening %s: %s" % (globs.htmlDirFile, "({0}): {1}".format(e.errno, e.strerror))
            myprint(msg)
            return -1
    else:
        myprint("You are offline")
        return -1

    # Filter out unnecessary lines
    input = open(globs.htmlDirFile, 'r')
    tmp = input.read()
    input.close()

    filterUrl = "%s/%s" % (globs.remBaseDir,rootDir)     # e.g. /DCIM/100OLYMP   XXX
    tmp2 = [x for x in tmp.split('\n') if re.search(filterUrl, x)]

    # Example :
    # wlansd[0]="/DCIM/100OLYMP,PC020065.JPG,1482293,0,19330,31239";

    globs.availRemoteFiles = {}
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
        thumbnailUrl = "%s/get_thumbnail.cgi?DIR=%s/%s" % (globs.rootUrl,dirName,fileName) # e.g: http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/PC020065.JPG

#        globs.availRemoteFiles[fileName] = [fileName, int(fileSize), int(fileDate), '', dirName, int(fileAttr), int(dateInSeconds(int(fileDate), int(fileTime))), int(fileTime), thumbnailUrl]
        globs.availRemoteFiles[fileName] = [fileName, int(fileSize), int(dateInSeconds(int(fileDate), int(fileTime))), '', dirName, int(fileAttr), int(fileDate), int(fileTime), thumbnailUrl]

        i += 1

    myprint("%d files found" % i)
    #print(globs.availRemoteFiles)
    
    # Sort the dict by date: Latest file first
    globs.availRemoteFilesSorted = sorted(list(globs.availRemoteFiles.items()), key=lambda x: int(x[1][globs.F_DATEINSECS]), reverse=globs.fileSortRecentFirst)
    #    for e in globs.availRemoteFilesSorted:
    #        print("Found remote file: %s size %d created %s %s %d" % (e[1][globs.F_NAME],e[1][globs.F_SIZE],getHumanDate(e[1][globs.F_DATE]),getHumanTime(e[1][globs.F_TIME]),int(e[1][globs.F_DATEINSECS])))
    return i

def htmlRoot(): # XXX
    if globs.cameraConnected:
        myprint("Downloading from network: %s" % (globs.rootUrl))
        try:
            response = urllib.request.urlopen(globs.rootUrl,None,5)
        except IOError as e:
            msg = "I/O error: Opening URL %s %s" % (globs.rootUrl, "({0}): {1}".format(e.errno, e.strerror))
            myprint(msg)
            globs.cameraConnected = False

    if globs.cameraConnected:
        tmp = response.read()
        try:
            myprint("Opening: %s" % (globs.htmlRootFile))
            out = open(globs.htmlRootFile, 'wb')
            out.write(tmp)
            out.close()
        except IOError as e:
            msg = "I/O error: Opening %s: %s" % (globs.htmlRootFile, "({0}): {1}".format(e.errno, e.strerror))
            myprint(msg)
            return -1
    else:
        myprint ('You are offline')
        return -1

    # Filter out unnecessary lines
    input = open(globs.htmlRootFile, 'r')
    tmp = input.read()
    input.close()

    baseRootDirs = [x for x in tmp.split('\n') if re.search(globs.remBaseDir, x)]

    # Example :
    # wlansd[0]="/DCIM,100OLYMP,0,16,19311,45705";

    globs.rootDirList = []
    i = 0
    for line in baseRootDirs:
        fields = line.split(',')
        foo1,dirName,foo2,dirAttr,dirDate,foo3 = fields
        if not int(dirAttr) & 0x10:
            myprint("Invalid entry %s. Skipping" % (dirName))
            continue
        globs.rootDirList.append(dirName)
        i += 1

    myprint("%d root dirs found" % len(globs.rootDirList))
    for d in globs.rootDirList:
        myprint("Detected remote folder: %s" % d)
    return len(globs.rootDirList)

def clearDirectory(dir):
    myprint('Deleting:',dir)
    if not os.path.isdir(dir):
        return
    shutil.rmtree(dir)

def updateFileDicts():
    # Reset camera status. Will be updated if connection fails
    globs.cameraConnected = True

    # Download the root HTML from the camera
    #relRootUrl = '%s%s' % (globs.osvmFilesDownloadUrl, globs.remBaseDir)
    globs.rootDirCnt =  htmlRoot()
    myprint('%d root directories available for download' % (globs.rootDirCnt))
    if globs.rootDirCnt <= 0:
        globs.availRemoteFilesCnt = 0
        globs.cameraConnected = False
        globs.availRemoteFiles.clear()
        globs.availRemoteFilesSorted.clear()
    else:
        for d in globs.rootDirList:
            uri = '%s%s/%s' % (globs.osvmFilesDownloadUrl, globs.remBaseDir, d)
            myprint("1%s 2%s 3%s" % (globs.osvmFilesDownloadUrl, globs.remBaseDir, d))
            myprint("Querying URL %s..." % (uri))
            globs.availRemoteFilesCnt = getRootDirInfo(d, uri)
            myprint('%d remote files available' % globs.availRemoteFilesCnt)

            for e in sorted(globs.availRemoteFiles.values()):
                ret = downloadThumbnail(e)
                if ret:
                    myprint ("Error while downloading thumbnail.")
                    break

    # Detect local files
    globs.localFilesCnt = localFilesInfo(globs.osvmDownloadDir)
    myprint('%d local files, %d remote files' % (globs.localFilesCnt, globs.availRemoteFilesCnt))
    return globs.localFilesCnt,globs.availRemoteFilesCnt

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")

def touch(path):
    with open(path, 'a'):
        os.utime(path, None)

# Delete local files if needed
def deleteLocalFile(pDialog, filePath):
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
    
    ret = p.wait()
    print('removeCmd =',removeCmd,'ret=',ret,'msg=',msg)
    if not ret:
        msg = "File %s successfully removed\n" % (filePath)
        globs.localFilesCnt = localFilesInfo(globs.osvmDownloadDir)

    wx.CallAfter(pDialog.installError, ret, msg)
    return (ret, msg)

# Return the background and foreground colors to paint a widget associated 
# to the given file
def fileColor(fileName):
    color = globs.fileColors[globs.FILE_NOT_INSTALLED]    # Default color
    try:
        e = globs.localFileInfos[fileName]
    except:
        return color

    color = globs.fileColors[globs.FILE_INSTALLED]
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
def dumpAttrs(obj):
    for attr in dir(obj):
        print("obj.%s = %s" % (attr, getattr(obj, attr)))

def checkUrl(url):
    p = urlparse(url)
    conn = http.client.HTTPConnection(p.netloc)
    conn.request('HEAD', p.path)
    resp = conn.getresponse()
    return resp.status < 400

def startHTTPServer():
    null = open('/dev/null', 'w')

    p = subprocess.Popen(
        [sys.executable, '-m', 'http.server', globs.SERVER_HTTP_PORT],
        shell=False,
        cwd=globs.osvmDownloadDir,
        stdout=null,
        stderr=null,
        )
    myprint('Initializing HTTP Server on port %s, root=%s' % (globs.SERVER_HTTP_PORT, globs.osvmDownloadDir)) 
    time.sleep(1)
    return p

def serverIpAddr():
    try:
        ipAddr = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    except OSError as e:
        msg = 'serverIpAddr(): Error %s' % ("({0}): {1}".format(e.errno, e.strerror))
        print(msg)
        ipAddr = '0;0;0;0'
    myprint(ipAddr)
    return ipAddr

        
# Check if local images need to be rotated using Exif metadata and proceed accordingly
def rotateLocalImages(exifData):
    fileList = listLocalFiles(globs.osvmDownloadDir, hidden=False, relative=False, suffixes=('jpg'))
    for f in [x for x in fileList if not '-rot' in x]: # Skip over rotated images
        try:
            exifDataAsStr = exifData[os.path.basename(f)]
        except:
            myprint('No Exif data for %s' % f)
        else:
            rotateImage.rotateImage(f, ast.literal_eval(exifDataAsStr))

# Check if some thumbnails are missing in globs.osvmDownloadDir
def createImagesThumbnail():
    fileList = listLocalFiles(globs.osvmDownloadDir, hidden=False, relative=True, suffixes=('jpg'))
    for f in [x for x in fileList if not '-rot' in x]: # Skip over rotated images
        thumbnailFilePath = os.path.join(globs.thumbDir, f)
        if not os.path.exists(thumbnailFilePath):
            filePath = os.path.join(globs.osvmDownloadDir, f)
            myprint('Creating: %s' % (thumbnailFilePath))
            
            size = (160,120)
            thumb = ImageOps.fit(Image.open(filePath), size, Image.ANTIALIAS)
            thumb.save(thumbnailFilePath)
            
            # image = Image.open(filePath)
            # try:
            #     exif = image.info['exif'] # Read exif from info attribute
            # except:
            #     exif = b''
            # #Create thumbnail of image, keeping exif data
            # size = (160,120)
            # image.thumbnail(size, Image.ANTIALIAS)
            # image.save(thumbnailFilePath, exif=exif)
            # image.close()
            # Modify modification time
            os.utime(thumbnailFilePath, (0, os.path.getmtime(filePath)))

def unbufprint(text):
    sys.__stdout__.write(text)
    sys.__stdout__.flush()

############# CLASSES #########################################################

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
        print('%s: Running. Server: %s:%s' % (self._name, globs.serverAddr, globs.SERVER_HTTP_PORT))

        while True:
            self._threadLock.acquire() # will block until 'Start slideshow' button is pressed 
#            self._stopper.clear() # Thread is running
            f = self._parent.mediaFileList[globs.slideShowNextIdx % globs.slideShowLastIdx]
            fileURL = 'http://%s:%s/%s' % (globs.serverAddr, globs.SERVER_HTTP_PORT, f[globs.F_NAME])
            print('%s: idx %d/%d Loading URL: %s' % (self._name, globs.slideShowNextIdx,globs.slideShowLastIdx, fileURL))
            mediaFileType = { 'jpg':'image/jpg', 'mov':'video/mov', 'mp4':'video/mov' }
            suffix = f[globs.F_NAME].split('.')[1].lower()
            globs.castMediaCtrl.play_media(fileURL, mediaFileType[suffix])
            if suffix == 'mov':
                idleCnt = 0
                while True:
                    if globs.castMediaCtrl.status.player_state == 'IDLE':
                        idleCnt += 1
                        print('IDLE',idleCnt)
                        if idleCnt > 2:	# Assume end of video
                            break
                    time.sleep(1)
            else:
                globs.castMediaCtrl.block_until_active()

            self._threadLock.release()
            time.sleep(int(globs.ssDelay))
            globs.slideShowNextIdx = (globs.slideShowNextIdx + 1) % globs.slideShowLastIdx

#### class Preferences
class Preferences():
    def __init__(self):
        pass

    def _loadPreferences(self):
        newInitFile1 = self._loadInitFile()
        newInitFile2 = self._parseInitFile()
        if newInitFile1 or newInitFile2:
            dlg = PreferencesDialog.PreferencesDialog(self)
            dlg.ShowModal()
            dlg.Destroy()
            #globs.printGlobals()

    def _savePreferences(self):
        self._saveInitFile()

    # Return a dictionary (if exists) for the given section in the ConfigParser object
    def _initFileSectionGet(self, config, section):
        dict1 = {}
        try:
            options = config.options(section)
        except:
                myprint('exception on option: %s' % options)
                return dict1
        for opt in options:
            try:
                dict1[opt] = config.get(section, opt)
                if dict1[opt] == -1:
                    myprint('skipping: %s' % opt)
            except:
                myprint("Got exception: %s" % opt)
                dict1[opt] = None
        return dict1

    def _loadInitFile(self):
        myprint("Loading preference file:", globs.initFilePath)
        self.config = configparser.ConfigParser()
        cf = self.config.read(globs.initFilePath)

        if self.config.sections() == []:
            # Create a new Init file, return TRUE
            self._createDefaultInitFile()
            cf = self.config.read([globs.initFilePath])
            return True
        return False

    def _createDefaultInitFile(self):
        myprint('Warning: Cannot read preference file, Creating default: %s' % globs.initFilePath)

        if os.path.exists(globs.initFilePath):
            initFilePathBk = os.path.join(os.path.join(expanduser("~"), globs.osvmDir, globs.initFileBk))
            myprint('Saving old/existing confile file to %s' % (initFilePathBk))
            shutil.copy2(globs.initFilePath, initFilePathBk)
                                         
        # add the default settings to the file
        self.config['Version'] = {globs.INI_VERSION: globs.iniFileVersion}

        self.config['Preferences'] = {}
        self.config['Preferences'][globs.COMPACT_MODE]           = str(globs.DEFAULT_COMPACT_MODE)
        self.config['Preferences'][globs.ASK_BEFORE_COMMIT]      = str(globs.DEFAULT_ASK_BEFORE_COMMIT)
        self.config['Preferences'][globs.ASK_BEFORE_EXIT]        = str(globs.DEFAULT_ASK_BEFORE_EXIT)
        self.config['Preferences'][globs.KEEP_LOCAL_FOLDER_IN_SYNC] = str(globs.DEFAULT_KEEP_LOCAL_FOLDER_IN_SYNC)        
        self.config['Preferences'][globs.SAVE_PREFS_ON_EXIT]     = str(globs.DEFAULT_SAVE_PREFERENCES_ON_EXIT)
        self.config['Preferences'][globs.OVERWRITE_LOCAL_FILES]  = str(globs.DEFAULT_OVERWRITE_LOCAL_FILES)
        self.config['Preferences'][globs.AUTO_SWITCH_TO_CAMERA_NETWORK] = str(globs.AUTO_SWITCH_TO_CAMERA_NETWORK)
        self.config['Preferences'][globs.THUMB_GRID_COLUMNS]     = str(globs.DEFAULT_THUMB_GRID_NUM_COLS)
        self.config['Preferences'][globs.THUMB_SCALE_FACTOR]     = str(globs.DEFAULT_THUMB_SCALE_FACTOR)
        self.config['Preferences'][globs.OSVM_DOWNLOAD_DIR]      = globs.DEFAULT_OSVM_DOWNLOAD_DIR
        self.config['Preferences'][globs.SORT_ORDER]             = str(globs.DEFAULT_SORT_ORDER)
        self.config['Preferences'][globs.LOG_FRAME ]             = str(globs.DEFAULT_LOG_FRAME)

        self.config['Sync Mode Preferences'] = {}
        self.config['Sync Mode Preferences'][globs.REM_BASE_DIR] = globs.DEFAULT_OSVM_REM_BASE_DIR
        self.config['Sync Mode Preferences'][globs.OSVM_FILES_DOWNLOAD_URL] = globs.DEFAULT_OSVM_ROOT_URL
        self.config['Sync Mode Preferences'][globs.MAX_DOWNLOAD] = str(globs.DEFAULT_MAX_DOWNLOAD)

        self.config['View Mode Preferences'] = {}
        self.config['View Mode Preferences'][globs.SS_DELAY]     = str(globs.DEFAULT_SLIDESHOW_DELAY)
        self.config['View Mode Preferences'][globs.LAST_CAST_DEVICE_NAME] = ''
        self.config['View Mode Preferences'][globs.LAST_CAST_DEVICE_UUID] = ''
        self.config['View Mode Preferences'][globs.ROT_IMG_CHOICE] = str(globs.DEFAULT_ROT_IMG_CHOICE)
        self.config['Networks'] = {}
        self.config['Networks'][globs.FAVORITE_NETWORK] = ''',''' #None,None

        self.config['Colors'] = {}
        for i in range(len(globs.DEFAULT_FILE_COLORS)):
            self.config['Colors']['color_%d' % (i)] = str(globs.DEFAULT_FILE_COLORS[i][0].GetRGB())

        self.config['Mail Preferences'] = {}
        self.config['Mail Preferences'][globs.SMTP_SERVER] = globs.DEFAULT_SMTP_SERVER
        self.config['Mail Preferences'][globs.SMTP_SERVER_PROTOCOL] = globs.DEFAULT_SMTP_SERVER_PROTOCOL
        self.config['Mail Preferences'][globs.SMTP_SERVER_PORT] = str(globs.DEFAULT_SMTP_SERVER_PORT)
        self.config['Mail Preferences'][globs.SMTP_SERVER_USE_AUTH] = str(globs.DEFAULT_SMTP_SERVER_USE_AUTH)
        self.config['Mail Preferences'][globs.SMTP_SERVER_USER_NAME] = globs.DEFAULT_SMTP_SERVER_USER_NAME
        self.config['Mail Preferences'][globs.SMTP_SERVER_USER_PASSWD] = globs.DEFAULT_SMTP_SERVER_USER_PASSWD
        self.config['Mail Preferences'][globs.SMTP_FROM_USER] = globs.DEFAULT_SMTP_FROM_USER
        self.config['Mail Preferences'][globs.SMTP_RECIPIENTS_LIST] = globs.DEFAULT_SMTP_RECIPIENTS_LIST
        
        # Writing our configuration file back to initFile
        with open(globs.initFilePath, 'w') as cfgFile:
            self.config.write(cfgFile)

        cfgFile.close()

    def _parseInitFile(self):
        try:
            self.config.read( globs.initFilePath)

            # Get OSVM version section
            iniFileVersion = self.config['Version'][globs.INI_VERSION]
            if iniFileVersion != globs.iniFileVersion:
                print ('_parseInitFile(): Outdated INI file. Resetting to defaults')

            # Get preferences from Preferences
            sectionPreferences    = self.config['Preferences']
            if not globs.compactMode: # User has not used '-c' cmdline argument
                globs.compactMode       = str2bool(sectionPreferences[globs.COMPACT_MODE])
            else:
                globs.thumbnailGridRows = 5
            globs.askBeforeCommit       = str2bool(sectionPreferences[globs.ASK_BEFORE_COMMIT])
            globs.askBeforeExit         = str2bool(sectionPreferences[globs.ASK_BEFORE_EXIT])
            globs.keepLocalFolderInSync = str2bool(sectionPreferences[globs.KEEP_LOCAL_FOLDER_IN_SYNC])
            globs.savePreferencesOnExit = str2bool(sectionPreferences[globs.SAVE_PREFS_ON_EXIT])
            globs.overwriteLocalFiles   = str2bool(sectionPreferences[globs.OVERWRITE_LOCAL_FILES])
            globs.autoSwitchToFavoriteNetwork = str2bool(sectionPreferences[globs.AUTO_SWITCH_TO_CAMERA_NETWORK])
            globs.thumbnailGridColumns  = int(sectionPreferences[globs.THUMB_GRID_COLUMNS])
            globs.thumbnailScaleFactor  = float(sectionPreferences[globs.THUMB_SCALE_FACTOR])
            # If user has used the '-p' cmdline argument, override the osvmDownloadDir parameter
            if globs.imagePathCmdLineArg:
                globs.osvmDownloadDir   =  globs.imagePathCmdLineArg
            else:
                globs.osvmDownloadDir   = sectionPreferences[globs.OSVM_DOWNLOAD_DIR]
            globs.fileSortRecentFirst   = str2bool(sectionPreferences[globs.SORT_ORDER])
            globs.logFrame              = str2bool(sectionPreferences[globs.LOG_FRAME])
            
            sectionSyncModePref         = self.config['Sync Mode Preferences']
            globs.remBaseDir		= sectionSyncModePref[globs.REM_BASE_DIR]
            globs.osvmFilesDownloadUrl  = sectionSyncModePref[globs.OSVM_FILES_DOWNLOAD_URL]
            globs.maxDownload           = int(sectionSyncModePref[globs.MAX_DOWNLOAD])
            if globs.maxDownload == 0:
                globs.maxDownload = globs.MAX_OPERATIONS

            globs.ssDelay            = self.config['View Mode Preferences'][globs.SS_DELAY]
            globs.lastCastDeviceName = self.config['View Mode Preferences'][globs.LAST_CAST_DEVICE_NAME]
            globs.lastCastDeviceUuid = self.config['View Mode Preferences'][globs.LAST_CAST_DEVICE_UUID]
            globs.rotImgChoice       = int(self.config['View Mode Preferences'][globs.ROT_IMG_CHOICE])

            sectionNetworks = self.config['Networks']
            s = sectionNetworks[globs.FAVORITE_NETWORK]
            globs.favoriteNetwork = (s.split(',')[0],s.split(',')[1])
            globs.knownNetworks = list()
            globs.knownNetworks = [value for key, value in sectionNetworks.items() if 'network_' in key]

            # Colors section
            sectionColors = self.config['Colors']
            for i in range(len(globs.fileColors)):
                colrgb = sectionColors['color_%d' % i]
                newcol = wx.Colour()
                newcol.SetRGB(int(colrgb))
                globs.fileColors[i][0] = newcol # update globs.fileColors[]

            sectionMail = self.config['Mail Preferences']
            globs.smtpServer           = sectionMail[globs.SMTP_SERVER]
            globs.smtpServerProtocol   = sectionMail[globs.SMTP_SERVER_PROTOCOL]
            globs.smtpServerPort       = int(sectionMail[globs.SMTP_SERVER_PORT])
            globs.smtpServerUseAuth    = str2bool(sectionMail[globs.SMTP_SERVER_USE_AUTH])
            globs.smtpServerUserName   = sectionMail[globs.SMTP_SERVER_USER_NAME]
            globs.smtpServerUserPasswd = sectionMail[globs.SMTP_SERVER_USER_PASSWD]
            globs.smtpFromUser         = sectionMail[globs.SMTP_FROM_USER]
            globs.smtpRecipientsList   = list(filter(None, sectionMail[globs.SMTP_RECIPIENTS_LIST].split(',')))[:globs.SMTP_RECIPIENTS_LIST_LEN]
            return False # Parsing OK
        
        except:
            myprint('Error parsing INI file')
            # Create a new Init file from builtin defaults
            del self.config
            self.config = configparser.ConfigParser()
            self._createDefaultInitFile()
            self.config.read(globs.initFilePath)

            iniFileVersion = self.config['Version'][globs.INI_VERSION]

            # Reload globals from default values
            sectionPreferences    = self.config['Preferences']
            globs.compactMode           = str2bool(sectionPreferences[globs.COMPACT_MODE])
            globs.askBeforeCommit       = str2bool(sectionPreferences[globs.ASK_BEFORE_COMMIT])
            globs.askBeforeExit         = str2bool(sectionPreferences[globs.ASK_BEFORE_EXIT])
            globs.keepLocalFolderInSync = str2bool(sectionPreferences[globs.KEEP_LOCAL_FOLDER_IN_SYNC])
            globs.savePreferencesOnExit = str2bool(sectionPreferences[globs.SAVE_PREFS_ON_EXIT])
            globs.overwriteLocalFiles   = str2bool(sectionPreferences[globs.OVERWRITE_LOCAL_FILES])
            globs.autoSwitchToFavoriteNetwork = str2bool(sectionPreferences[globs.AUTO_SWITCH_TO_CAMERA_NETWORK])
            globs.thumbnailGridColumns  = int(sectionPreferences[globs.THUMB_GRID_COLUMNS])
            globs.thumbnailScaleFactor  = float(sectionPreferences[globs.THUMB_SCALE_FACTOR])
            globs.osvmDownloadDir       = sectionPreferences[globs.OSVM_DOWNLOAD_DIR]
            globs.fileSortRecentFirst   = str2bool(sectionPreferences[globs.SORT_ORDER])
            globs.logFrame              = str2bool(sectionPreferences[globs.LOG_FRAME])            

            sectionSyncModePref         = self.config['Sync Mode Preferences']
            globs.remBaseDir		= sectionSyncModePref[globs.REM_BASE_DIR]
            globs.osvmFilesDownloadUrl  = sectionSyncModePref[globs.OSVM_FILES_DOWNLOAD_URL]
            globs.maxDownload           = int(sectionSyncModePref[globs.MAX_DOWNLOAD])
            if globs.maxDownload == 0:
                globs.maxDownload = globs.MAX_OPERATIONS

            globs.ssDelay = self.config['View Mode Preferences'][globs.SS_DELAY]
            globs.rotImgChoice = int(self.config['View Mode Preferences'][globs.ROT_IMG_CHOICE])

            self.config['Networks'] = {}
            globs.favoriteNetwork = ('None','None')

            sectionColors = self.config['Colors']
            for i in range(len(globs.fileColors)):
                colrgb = sectionColors['color_%d' % (i)]
                newcol = wx.Colour()
                newcol.SetRGB(int(colrgb))
                globs.fileColors[i][0] = newcol

            sectionMail = self.config['Mail Preferences']
            globs.smtpServer           = sectionMail[globs.SMTP_SERVER]
            globs.smtpServerProtocol   = sectionMail[globs.SMTP_SERVER_PROTOCOL]
            globs.smtpServerPort       = int(sectionMail[globs.SMTP_SERVER_PORT])
            globs.smtpServerUseAuth    = str2bool(sectionMail[globs.SMTP_SERVER_USE_AUTH])
            globs.smtpServerUserName   = sectionMail[globs.SMTP_SERVER_USER_NAME]
            globs.smtpServerUserPasswd = sectionMail[globs.SMTP_SERVER_USER_PASSWD]
            globs.smtpFromUser         = sectionMail[globs.SMTP_FROM_USER]
            globs.smtpRecipientsList   = list(filter(None, sectionMail[globs.SMTP_RECIPIENTS_LIST].split(',')))[:globs.SMTP_RECIPIENTS_LIST_LEN]
            return True # Parsing KO, New file created

    def _saveInitFile(self):
        myprint("Saving preference file:%s" % globs.initFilePath)

        # lets update the config file
        self.config['Version'] = {globs.INI_VERSION: globs.iniFileVersion}

        self.config['Preferences'] = {}
        self.config['Preferences'][globs.COMPACT_MODE]           = str(globs.compactMode)
        self.config['Preferences'][globs.ASK_BEFORE_COMMIT]      = str(globs.askBeforeCommit)
        self.config['Preferences'][globs.ASK_BEFORE_EXIT]        = str(globs.askBeforeExit)
        self.config['Preferences'][globs.KEEP_LOCAL_FOLDER_IN_SYNC] = str(globs.keepLocalFolderInSync)
        self.config['Preferences'][globs.SAVE_PREFS_ON_EXIT]     = str(globs.savePreferencesOnExit)
        self.config['Preferences'][globs.OVERWRITE_LOCAL_FILES]  = str(globs.overwriteLocalFiles)
        self.config['Preferences'][globs.AUTO_SWITCH_TO_CAMERA_NETWORK] = str(globs.autoSwitchToFavoriteNetwork)
        self.config['Preferences'][globs.THUMB_GRID_COLUMNS]     = str(globs.thumbnailGridColumns)
        self.config['Preferences'][globs.THUMB_SCALE_FACTOR]     = str(globs.thumbnailScaleFactor)
        self.config['Preferences'][globs.OSVM_DOWNLOAD_DIR]      = globs.osvmDownloadDir
        self.config['Preferences'][globs.SORT_ORDER]             = str(globs.fileSortRecentFirst)
        self.config['Preferences'][globs.LOG_FRAME]              = str(globs.logFrame)

        self.config['Sync Mode Preferences'][globs.REM_BASE_DIR]            = globs.remBaseDir
        self.config['Sync Mode Preferences'][globs.OSVM_FILES_DOWNLOAD_URL] = globs.osvmFilesDownloadUrl
        self.config['Sync Mode Preferences'][globs.MAX_DOWNLOAD]            = str(globs.DEFAULT_MAX_DOWNLOAD)

        self.config['View Mode Preferences'][globs.SS_DELAY] = str(globs.ssDelay)
        self.config['View Mode Preferences'][globs.ROT_IMG_CHOICE] = str(globs.rotImgChoice)        
        if globs.castDevice:
            self.config['View Mode Preferences'][globs.LAST_CAST_DEVICE_NAME] = globs.castDevice.name
            self.config['View Mode Preferences'][globs.LAST_CAST_DEVICE_UUID] = str(globs.castDevice.device.uuid)
        else:
            self.config['View Mode Preferences'][globs.LAST_CAST_DEVICE_NAME] = 'None'
            self.config['View Mode Preferences'][globs.LAST_CAST_DEVICE_UUID] = ''

        sectionNetworks = self.config['Networks']
        # Save the favorite network
        sectionNetworks[globs.FAVORITE_NETWORK] = ','.join(globs.favoriteNetwork)

        # Save all globs.knownNetworks
        for i in range(len(globs.knownNetworks)):
            sectionNetworks['network_%d' % (i)] = globs.knownNetworks[i]

        for i in range(len(globs.fileColors)):
            self.config['Colors']['color_%d' % (i)] = str(globs.fileColors[i][0].GetRGB())

        sectionMail = self.config['Mail Preferences']
        sectionMail[globs.SMTP_SERVER]             = globs.smtpServer
        sectionMail[globs.SMTP_SERVER_PROTOCOL]    = globs.smtpServerProtocol
        sectionMail[globs.SMTP_SERVER_PORT]        = str(globs.smtpServerPort)
        sectionMail[globs.SMTP_SERVER_USE_AUTH]    = str(globs.smtpServerUseAuth)
        sectionMail[globs.SMTP_SERVER_USER_NAME]   = globs.smtpServerUserName
        sectionMail[globs.SMTP_SERVER_USER_PASSWD] = globs.smtpServerUserPasswd
        sectionMail[globs.SMTP_FROM_USER]          = globs.smtpFromUser
        sectionMail[globs.SMTP_RECIPIENTS_LIST]    = ','.join(globs.smtpRecipientsList)
        # Writing our configuration file back to initFile
        with open(globs.initFilePath, 'w') as cfgFile:
            self.config.write(cfgFile)


#### Class FileOperationMenu
class FileOperationMenu(wx.Menu):
    """
    Creates and displays a file menu that allows the user to
    select an operation to perform on a given file
    """
    def __init__(self, parent, button):
        """
        Initialize the Package menu dialog box
        """
        self.parent = parent
        self.button = button

        super(FileOperationMenu,self).__init__()

        self.clickedPos = self.parent.panel1.ScreenToClient(wx.GetMousePosition())

        try:
            fileName = self.button.GetName()
            fileType = fileName.split('.')[1].lower()	# File suffix
        except:
            print('FileOperationMenu(): Invalid file %s' % (fileName))
            return

        # Creates a Menu containing possible operations on this file:
        self.popupMenu = wx.Menu()
        self.popupMenuTitles = []

        # Id of each menu entry. 
        if globs.system == 'Darwin':
            id = 1
        else:
            id = 0  

	# Start Slideshow from here
        if globs.viewMode and fileType == 'jpg' or (fileType == 'mov' and globs.vlcVideoViewer):
            menuEntry = [fileName, globs.FILE_SLIDESHOW, self.button]
            self.popupMenuTitles.append((id, menuEntry))
            id += 1

        # Next entry is: 'Properties'
        menuEntry = [fileName, globs.FILE_PROPERTIES, self.button]
        self.popupMenuTitles.append((id, menuEntry))
        id += 1

        # Insert a separator
        menuEntry = [fileName, -1, self.button]
        self.popupMenuTitles.append((id, menuEntry))
        id += 1

        # Check if this file is already here
        if not fileName in list(globs.localFileInfos.keys()):
            # file is not yet installed
            menuEntry = [fileName, globs.FILE_DOWNLOAD, self.button, '']
            self.popupMenuTitles.append((id, menuEntry)) 
            id += 1
        else:
            filePath = globs.localFileInfos[fileName][globs.F_PATH]
            found = False
            for op in globs.opList:
                if op[globs.OP_STATUS] and op[globs.OP_FILENAME] == fileName:
                    found = True
                    menuEntry = [fileName, globs.FILE_UNMARK, self.button, filePath]
                    self.popupMenuTitles.append((id, menuEntry))
                    id += 1
                    break
            if not found:
                menuEntry = [fileName, globs.FILE_MARK, self.button, filePath]
                self.popupMenuTitles.append((id, menuEntry)) 
                id += 1
            if globs.overwriteLocalFiles:
                menuEntry = [fileName, globs.FILE_DOWNLOAD, self.button, filePath]
                self.popupMenuTitles.append((id, menuEntry)) 
                id += 1

        # Fill-in the menu with entries
        for tmp in self.popupMenuTitles:
            id = tmp[0]
            menuEntry = tmp[1]
            if menuEntry[1] == globs.FILE_SLIDESHOW:    # start slideshow from here
                menuItem = wx.MenuItem(self.popupMenu, id, 'Start Slideshow From Here')
                menuItem.SetBitmap(wx.Bitmap(os.path.join(globs.imgDir,'play.png')))
                self.popupMenu.Append(menuItem)
                # Register Properties menu handler with EVT_MENU
                self.popupMenu.Bind(wx.EVT_MENU, lambda evt: self._MenuSlideShowCb(evt), menuItem)
                continue

            if menuEntry[1] == globs.FILE_PROPERTIES:    # Properties
                menuItem = wx.MenuItem(self.popupMenu, id, 'Properties')
                menuItem.SetBitmap(wx.Bitmap(os.path.join(globs.imgDir,'properties-32.jpg')))
                self.popupMenu.Append(menuItem)
                # Register Properties menu handler with EVT_MENU
                self.popupMenu.Bind(wx.EVT_MENU, lambda evt: self._MenuPropertiesCb(evt), menuItem)
                continue

            if menuEntry[1] == -1:    # Separator
                self.popupMenu.AppendSeparator()
                continue

            if menuEntry[1] == globs.FILE_DOWNLOAD:
                title = 'Add %s to Download List' % (menuEntry[0])
                imgFile = 'plus-32.jpg'
            if menuEntry[1] == globs.FILE_MARK:
                title = 'Mark %s' % (menuEntry[0])
                imgFile = 'plus-32.jpg'
            if menuEntry[1] == globs.FILE_UNMARK:
                title = 'Unmark %s' % (menuEntry[0])
                imgFile = 'moins-32.jpg'

            menuItem = wx.MenuItem(self.popupMenu, id, title)
            menuItem.SetBitmap(wx.Bitmap(os.path.join(globs.imgDir, imgFile)))
            self.popupMenu.Append(menuItem)
            # Register menu handler with EVT_MENU
            self.popupMenu.Bind(wx.EVT_MENU, lambda evt: self._MenuSelectionCb(evt), menuItem)

        # Displays the menu at the current mouse position
        self.parent.panel1.PopupMenu(self.popupMenu, self.clickedPos)
        self.popupMenu.Destroy() # destroy to avoid mem leak

    def _MenuSlideShowCb(self, event):
        menuEntry = self.popupMenuTitles[event.GetId()][1]
        fileName = str(menuEntry[0])
        myprint("Searching %s in globs.localFilesSorted (%d files)" % (fileName, len(globs.localFilesSorted)))
        idx = [x[0] for x in globs.localFilesSorted].index(fileName)
        suffix = fileName.split('.')[1]	# File suffix

        # Get key in globs.FILE_SUFFIXES containing the suffix
        fileType = [key for (key, value) in globs.FILE_SUFFIXES.items() if suffix in value]
        if not fileType: # Key not found
            myprint('File type %s not supported' % suffix)
            return
        filesSelected = self.parent.selectFilesByPosition(fileType[0], idx)

        # Simulate a button 'Play' press
        self._btnPlayInfo = getattr(self.parent, "btnPlay")
        evt = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self._btnPlayInfo.GetId())
        evt.SetEventObject(self.parent.btnPlay)
        wx.PostEvent(self.parent.btnPlay, evt)

        event.Skip()

    def _MenuPropertiesCb(self, event):
        menuEntry = self.popupMenuTitles[event.GetId()][1]
        fileName = str(menuEntry[0])
        dlg = PropertiesDialog.PropertiesDialog(self, fileName)
        ret = dlg.ShowModal()
        dlg.Destroy()
        event.Skip()

    def _MenuSelectionCb(self, event):
        if globs.system == 'Darwin':
            id = event.GetId() - 1
        else:
            id = event.GetId()

        menuEntry = self.popupMenuTitles[id][1]
        fileName  = menuEntry[0]
        what      = menuEntry[1]

        if what == globs.FILE_PROPERTIES:
            self._MenuPropertiesCb(event)
            return

        myprint('fileName=%s what=%d' % (fileName,what))
        
        if what == globs.FILE_UNMARK:
            op = [x for x in globs.opList if x[globs.OP_FILENAME] == fileName][0]
            self.parent.resetOneButton(fileName)
            self.parent.resetOneRequest(op)

            pendingOpsCnt = self.parent.pendingOperationsCount()
            msg = 'Request successfully cleared. %d marked file(s)' % (pendingOpsCnt)
            wx.CallAfter(self.parent.updateStatusBar, msg)
            return
            
        # Check if one operation is already pending for this file and re-use it
        for op in globs.opList:
            if op[globs.OP_FILENAME] == fileName:
                self._scheduleOperation(op, menuEntry)
                return

        # Loop thru opList[] looking for a free slot, schedule an operation
        for op in globs.opList:
            if op[globs.OP_STATUS] == 0:
                self._scheduleOperation(op, menuEntry)
                break
        else:
            msg = 'Max requests reached (%d).' % (globs.MAX_OPERATIONS)
            myprint(msg)

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

        op[globs.OP_STATUS]   = 1          # Busy
        op[globs.OP_FILENAME] = fileName
        op[globs.OP_FILETYPE] = fileName.split('.')[1]	# File suffix
        op[globs.OP_TYPE]     = operation
        op[globs.OP_FILEPATH] = filePath

#        print('Setting colours')
#        button.SetBackgroundColour(globs.fileColors[globs.FILE_OP_PENDING][0])
#        button.SetForegroundColour(globs.fileColors[globs.FILE_OP_PENDING][1])

        #myprint(op)

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
        print("%s Starting." % (self._name))

        wx.CallAfter(self._pDialog.setBusyCursor, 1)

        globs.thumbDir = os.path.join(globs.osvmDownloadDir, '.thumbnails')
        if not os.path.isdir(globs.thumbDir):
            print('%s: Creating: %s' % (self._name, globs.thumbDir))
            try:
                os.makedirs(globs.thumbDir, exist_ok=True)
            except OSError as e:
                msg = "Cannot create %s: %s" % (globs.thumbDir, "{0}".format(e.strerror))
                dlg = wx.MessageDialog(None, msg, 'ERROR', wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()

        time.sleep(5) # To let the timer run for animation

        # Build Exif data cache file
        exifFilePath = os.path.join(globs.osvmDownloadDir, globs.exifFile)
        if not os.path.exists(exifFilePath):
            myprint('%s does not exist. Creating' % exifFilePath)
            ExifDialog.saveExifDataFromImages(exifFilePath)
        # Load Exif data from file
        self.exifData = ExifDialog.buildDictFromFile(exifFilePath)

        # Create thumbnail image if needed
        createImagesThumbnail()
        
        # Check if some images need rotation
        rotateLocalImages(self.exifData)

        # Update dictionaries using current config parameters
        myprint('Updating file dictionaries')
        globs.localFilesCnt,globs.availRemoteFilesCnt = updateFileDicts()

        if not globs.cameraConnected:
            msg = '%d local files' % (globs.localFilesCnt)
        else:
            msg = '%d local files, %d remote files' % (globs.localFilesCnt, globs.availRemoteFilesCnt)
        
        wx.CallAfter(self._pDialog.setTitleStaticText2, msg)
        wx.CallAfter(self._pDialog.setBusyCursor, 0)

        self._pDialog.timer.Stop()

        msg1 = 'Configuration is READY'
        wx.CallAfter(self._pDialog.setTitleStaticText1, msg1)
        wx.CallAfter(self._pDialog.enableEnter)

        # Notify user about any disabled module
        wx.CallAfter(self._pDialog.notifyDisabledModules)

        # Simulate a 'Enter View Mode' event if requested
        if globs.autoViewMode:
            self._btnEnterViewMode = getattr(self._pDialog, 'btnEnterViewMode')
            evt = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self._btnEnterViewMode.GetId())
            evt.SetEventObject(self._pDialog.btnEnterViewMode)
            wx.PostEvent(self._pDialog.btnEnterViewMode, evt)
        elif globs.autoSyncMode:
            self._btnEnterSyncMode = getattr(self._pDialog, 'btnEnterSyncMode')
            evt = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self._btnEnterSyncMode.GetId())
            evt.SetEventObject(self._pDialog.btnEnterSyncMode)
            wx.PostEvent(self._pDialog.btnEnterSyncMode, evt)

        myprint('Timer status:',self._pDialog.timer.IsRunning())

        print("%s Exiting." % (self._name))

####
class OSVMConfig(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)
        self.timerCnt = 0
        self.parent = parent
        self.osvmFrame = None
        self.logFrame = None
        
        [self.MENUITEM_FILELIST,
         self.MENUITEM_PREFERENCES,
         self.MENUITEM_CLEAN,
         self.MENUITEM_QUIT,
         self.MENUITEM_ABOUT,
         self.MENUITEM_LOG] = [i for i in range(100,106)]

        self._initialize()

    def _initialize(self):
        self.prefs = Preferences()
        self.prefs._loadPreferences()

#        dlg = PreferencesDialog(self.prefs)
#        ret = dlg.ShowModal()
#        dlg.Destroy()

        if globs.logFrame or globs.logWin:
            self._openLogFrame()

        globs.printGlobals()

        self._initGUI()
        self._init_utils()

        self.Center()
        self.panel1.Layout()
        self.panel1.Show(True)

        # Create and start a new thread to load the config
        self.MainConfigThread = OSVMConfigThread(self, "OSVMConfigThread")
        self.MainConfigThread.setDaemon(True)
        self.MainConfigThread.start()

        globs.serverAddr = serverIpAddr()
        globs.httpServer = startHTTPServer()

    def _displayOSVMBitmap(self):
        # load the image
        imgPath = os.path.join(globs.imgDir, 'OSVM3.png')
        img = wx.Image(imgPath, wx.BITMAP_TYPE_PNG)

        # convert it to a wx.Bitmap, and put it on the wx.StaticBitmap
        self.staticBitmap1.SetBitmap(wx.Bitmap(img))

    #### GUI
    def _init_topBoxSizer1_Items(self, parent):
        parent.Add(self.titleBoxSizer1, 0, border=5, flag=wx.EXPAND | wx.ALL)
        parent.Add(4,0)
        parent.Add(self.bottomBoxSizer, 0, border=5, flag=wx.EXPAND | wx.ALL)#211 | wx.ALIGN_BOTTOM)

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
        # bottomButtonBoxSizer.Add(self.btnExit, 0, border=0, flag=wx.ALIGN_LEFT)
        # bottomButtonBoxSizer.Add(8, 4, proportion=1, border=0, flag=0)
        # bottomButtonBoxSizer.Add(self.btnEnterViewMode, 0, border=0, flag=wx.ALIGN_RIGHT)
        # bottomButtonBoxSizer.Add(4, 4, proportion=1, border=0, flag=0)
        # bottomButtonBoxSizer.Add(self.btnEnterSyncMode, 0, border=0, flag=wx.ALIGN_RIGHT)
        bottomButtonBoxSizer.Add(self.btnEnterViewMode, 0, border=0)#, flag=wx.ALIGN_RIGHT)
        bottomButtonBoxSizer.Add(4, 4, proportion=1, border=0, flag=0)
        bottomButtonBoxSizer.Add(self.btnEnterSyncMode, 0, border=0)#, flag=wx.ALIGN_RIGHT)
        bottomButtonBoxSizer.Add(12, 4, proportion=2, border=0, flag=0)
        bottomButtonBoxSizer.Add(self.btnExit, 0, border=0)#, flag=wx.ALIGN_LEFT)

        parent.Add(bottomButtonBoxSizer, 0, border=0, flag=wx.ALIGN_BOTTOM)#211 | wx.ALIGN_RIGHT)

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
        if globs.system == 'Windows':
            # Get win32api version
            fixed_file_info = win32api.GetFileVersionInfo(win32api.__file__, '\\')
            pywin32Version = fixed_file_info['FileVersionLS'] >> 16
            print("pywin32Version:", pywin32Version)
            label= '%s: Version: %s\n%s\nPython (%dbits): %s wxpython: %s pywin32: %s' % (globs.myName, globs.myVersion,  (platform.platform()), globs.pythonBits, globs.pythonVersion, wx.version(), pywin32Version)
        else:
            label= '%s: %s\n%s\nPython (%dbits): %s wxpython: %s' % (globs.myName, globs.myVersion, (platform.platform()), globs.pythonBits, globs.pythonVersion, wx.version())            

        self.pltfInfo = wx.StaticText(label=label,
                                      id=wx.ID_ANY,
                                      parent=self.panel1)
        self.pltfInfo.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Ubuntu'))
        
        self.btnEnterViewMode = wx.Button(id=wx.ID_ANY, 
                                          label='Enter View Mode', 
                                          parent=self.panel1, style=0)
        self.btnEnterViewMode.SetToolTip('Enter Viewing Mode to browse local pictures and videos')
#        self.btnEnterViewMode.Bind(wx.EVT_BUTTON, self.OnBtnEnterViewMode)
        self.btnEnterViewMode.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnEnterViewMode(evt))
        # Disable button. Will be enabled once configuration is loaded
        self.btnEnterViewMode.Disable()

        self.btnEnterSyncMode = wx.Button(id=wx.ID_ANY, 
                                          label='Enter Sync Mode',
                                          parent=self.panel1, style=0)
        self.btnEnterSyncMode.SetToolTip('Enter Sync Mode to sync media files between your camera and this computer')
        self.btnEnterSyncMode.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnEnterSyncMode(evt))
        # Disable button. Will be enabled once configuration is loaded
        self.btnEnterSyncMode.Disable()

        self.btnExit = wx.Button(id=wx.ID_EXIT, parent=self.panel1, style=0)
        self.btnExit.SetToolTip('No, Thanks. I want to escape')
        self.btnExit.Bind(wx.EVT_BUTTON, self.OnBtnExit)

        self.Bind(globs.EVT_OSVM_FRAME_CLOSE, self.OnOsvmFrameClose)
        
        self._displayOSVMBitmap()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, lambda evt: self.OnUpdate(evt), self.timer)
        myprint('Starting timer')
        self.timer.Start(globs.TIMER2_FREQ)

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

    def _init_menuBar_Menus(self, parent):
        parent.Append(self.menuFile, '&File')
        parent.Append(self.menuHelp, '&Help')

    def _init_menuFile_Items(self, parent):
        menuItem0 = wx.MenuItem(parent, self.MENUITEM_FILELIST, '&File List\tCtrl+L')
        parent.Append(menuItem0)
        parent.Enable(menuItem0.Id,True)

        menuItem1 = wx.MenuItem(parent, self.MENUITEM_PREFERENCES, '&Preferences\tCtrl+P') #wx.ID_PREFERENCES
        parent.Append(menuItem1)
        parent.Enable(menuItem1.Id,True)

        menuItem2 = wx.MenuItem(parent, self.MENUITEM_CLEAN, '&Clean Download Directory...')#wx.ID_CLEAR
        parent.Append(menuItem2)
        parent.Enable(menuItem2.Id,True)

        menuItem2 = wx.MenuItem(parent, self.MENUITEM_QUIT, '&Quit\tCtrl+Q')
        parent.Append(menuItem2)
        parent.Enable(menuItem2.Id,True)

    def _init_menuHelp_Items(self, parent):
        parent.AppendCheckItem(self.MENUITEM_LOG, item='&Log Window', help='Turn ON/OFF Log Window')
        parent.Check(self.MENUITEM_LOG, self.isLogFrame()) # Set check mark

        menuItem1 = wx.MenuItem(parent, self.MENUITEM_ABOUT, '&About')
        parent.Append(menuItem1)
        parent.Enable(menuItem1.Id,True)

    def _init_utils(self):
        self.menuBar = wx.MenuBar()
        self.menuFile = wx.Menu()
        self.menuHelp = wx.Menu()

        self._init_menuFile_Items(self.menuFile)
        self._init_menuHelp_Items(self.menuHelp)
        self._init_menuBar_Menus(self.menuBar)

        self.SetMenuBar(self.menuBar)

        self.menuBar.Enable(self.MENUITEM_FILELIST, globs.autoSyncMode)
        self.menuBar.Enable(self.MENUITEM_PREFERENCES, True)
        self.menuBar.Enable(self.MENUITEM_CLEAN, True)
        self.menuBar.Enable(self.MENUITEM_QUIT, True)
        self.menuBar.Enable(self.MENUITEM_ABOUT, True)
        self.menuBar.Enable(self.MENUITEM_LOG, True)

        self.Bind(wx.EVT_MENU, lambda event: self._menuHdl(event))

    def _menuHdl(self, event):
        id = event.GetId() 

        if id == self.MENUITEM_FILELIST:
            self.OnBtnFileList(event)
        elif id == self.MENUITEM_PREFERENCES:
            self.OnBtnPreferences(event)
        elif id == self.MENUITEM_CLEAN:
            self.OnBtnCleanDownloadDir(event)
        elif id == self.MENUITEM_QUIT:
            self.OnBtnQuit(event)
        elif id == self.MENUITEM_ABOUT:
            self.OnBtnAbout(event)
        elif id == self.MENUITEM_LOG:
            self.OnBtnLog(event)

    def OnFLFResults(self, resultData):
        myprint("Result data gathered: %s" % resultData)
        #retCode, needRefresh = resultData.split('-')
        retCode, needRefresh = (int(x) for x in resultData.split('-'))
        if retCode == wx.ID_OK and needRefresh:
            if self.osvmFrame:
                # Send a 'Rescan' event
                myprint('Sending EVT_RESCAN_NEEDED Event')
                evt = wxRescanNeeded()
                wx.PostEvent(self.osvmFrame, evt)

    def OnBtnFileList(self, event):
        eventTrackerHdl = FileListFrame.FileListFrameEventTracker(self.OnFLFResults)
        self.flFrame = FileListFrame.FileListFrame(None, -1, 'List of Files')
        self.flFrame.PushEventHandler(eventTrackerHdl)
        
        self.flFrame.Show(True)
        event.Skip()
        
    def OnBtnPreferences(self, event):
        dlg = PreferencesDialog.PreferencesDialog(self.prefs)
        ret = dlg.ShowModal()
        # Check if a Rescan is required
        self.needRescan = dlg.isRescanRequired()
        dlg.Destroy()
        if ret == wx.ID_APPLY and self.needRescan:
            if self.osvmFrame:
                # Simulate a 'Rescan' event
                myprint('Sending EVT_RESCAN_NEEDED Event')
                evt = wxRescanNeeded()
                wx.PostEvent(self.osvmFrame, evt)

    def OnBtnCleanDownloadDir(self, event):
        downloadDir = globs.osvmDownloadDir
        dlg = CleanDownloadDirDialog.CleanDownloadDirDialog(self, download=downloadDir)
        dlg.ShowModal()
        dlg.Destroy()
        event.Skip()

    def _cleanAndQuit(self):
        if globs.savePreferencesOnExit:
            self.prefs._savePreferences()
        if self.logFrame:
            self._closeLogFrame()
        if globs.httpServer:
            globs.httpServer.kill()
        self.Destroy()    # Bye Bye

    def OnBtnQuit(self, event):
        if globs.askBeforeExit:
            dlg = wx.MessageDialog(None, 'Do you really want to quit?', 'Question',
                                   wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            ret = dlg.ShowModal()
            if ret == wx.ID_YES:
                self._cleanAndQuit()
        else:
            self._cleanAndQuit()

    def OnBtnAbout(self, event):
        description = """Olympus Sync & View Manager (aka OSVM) is a powerful tool
..... to manage files between a Olympus camera and your laptop....
"""
        license = """OSVM License Info HERE"""
        info = wx.adv.AboutDialogInfo()

        imgPath = os.path.join(globs.imgDir, 'butterfly-48x48x32.png')
        info.SetIcon(wx.Icon(imgPath, wx.BITMAP_TYPE_PNG))
        info.SetName(globs.myLongName)
        info.SetVersion('%s' % globs.myVersion)
        info.SetDescription(description)
        info.SetCopyright('(C) 2018 Didier Poirot')
        info.SetWebSite('https://github.com/hercule115/OSVM')
        info.SetLicense(license)
        info.AddDeveloper('Didier Poirot')
        info.AddDocWriter('Didier Poirot')
        #info.AddArtist('Didier Poirot')
        #info.AddTranslator('Didier Poirot')

        wx.adv.AboutBox(info)

    def OnBtnLog(self, event):
        if not self.logFrame:		# Open Log Window
            self._openLogFrame()
        else:
            self._closeLogFrame()	# Close Log Window
        event.Skip()

    # Called when a EVT_CLOSE is received from the Log Frame
    def OnLogFrameClosed(self, event):
        self.menuHelp.Check(self.MENUITEM_LOG, False) # Clear check mark
        sys.stdout = sys.__stdout__
        self.logFrame = None
        event.Skip()

    def restartTimer(self):
        self.timer.Stop()
        self.timer.Start(globs.TIMER2_FREQ)
        myprint('Timer restarted after exception')
                
    def OnUpdate(self, event):
        text = 'Initializing Configuration. Please wait...'

        self.timerCnt += 1

        if '2.' in globs.pythonVersion:
            msg = '{0:>{width}}'.format(text[0:self.timerCnt],width=(len(text)))
        else:
            msg = '{:>{width}}'.format(text[0:self.timerCnt],width=(len(text)))
        self.titleStaticText1.SetLabel(msg)
        #myprint(self.timerCnt,msg)

    def OnBtnEnterViewMode(self, event):
        globs.viewMode = True

        if self.MainConfigThread.is_alive():
            self.MainConfigThread.join() # Block until thread has finished

        self.setBusyCursor(True)
        myprint('Launching OSVM')
        self.osvmFrame = OSVM(parent=self, id=-1, title=globs.myLongName)
        self.setBusyCursor(False)
        self.panel1.Enable(False)
        self.osvmFrame.Show()
        self.panel1.Enable(True)
        for b in [self.btnEnterViewMode, self.btnEnterSyncMode]:
            b.Disable()
        myprint('Timer status:',self.timer.IsRunning())
        
    def OnBtnEnterSyncMode(self, event):
        globs.viewMode = False

        if self.MainConfigThread.is_alive():
            self.MainConfigThread.join() # Block until thread has finished

        WifiDialog.switchToFavoriteNetwork()

        myprint('globs.cameraConnected =', globs.cameraConnected)

        # Check for any error while updating dictionaries
        if globs.availRemoteFilesCnt == 0:
            msg = 'No remote file available. Check your Preferences'
            dlg = wx.MessageDialog(None, msg, 'Error', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
        else:
            # System is ready.
            if globs.cameraConnected:
                msg = '%s READY!' % (globs.myLongName)
            else:
                msg = '%s READY. You are OFFLINE' % (globs.myLongName)
                globs.availRemoteFilesCnt = 0

        self.setBusyCursor(True)
        self.osvmFrame = OSVM(parent=self, id=-1, title=globs.myLongName)
        self.setBusyCursor(False)
        self.panel1.Enable(False)
        self.osvmFrame.Show()
        self.panel1.Enable(True)
        for b in [self.btnEnterViewMode, self.btnEnterSyncMode]:
            b.Disable()
        myprint('Stopping timer')
        self.timer.Stop()

    def OnOsvmFrameClose(self, event):
        myprint('OSVM Frame has closed. Exiting')
        # Simulate a 'Exit' button event
        evt = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self.btnExit.GetId())
        wx.PostEvent(self.btnExit, evt)
        event.Skip()
    
    # Bye Bye
    def OnBtnExit(self, event):
        self.Destroy()

    # Notify user about any disabled module
    def notifyDisabledModules(self):
        for mod in globs.disabledModules:
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
        myprint('Stopping timer')
#        self.timer.Stop()
        self.titleStaticText1.SetLabel(msg)
        self.SendSizeEvent() # to center the text

    # Update titleStaticText2 (from thread)
    def setTitleStaticText2(self, msg):
        myprint(msg)
        self.titleStaticText2.SetLabel(msg)

    # Set/unset busy cursor (from thread)
    def setBusyCursor(self, state):
        if state:
            wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)
        else:
            wx.EndBusyCursor()

    def _openLogFrame(self):
        # Compute size of the Log Frame.
        # Size it to provide a TextCtrl with 80x20 chars
        dc = wx.WindowDC(self)
        dc.SetFont(self.GetFont())
        sz = dc.GetTextExtent('X') # Size of 'X'
        sz = wx.Size(sz.x * 80, sz.y * 20) # Size of dialog
        # Open the Log Frame
        self.logFrame = LogFrame.LogFrame(title='Log Output', parent=self, size=sz)
        # Handle CLOSE event from Log Frame
        self.Bind(globs.EVT_LOG_FRAME_CLOSE, self.OnLogFrameClose) 
        self.logFrame.Show()
        # Redirect stdout
        sys.stdout = LogFrame.SysOutListener(self)

    def OnLogFrameClose(self, event):
        myprint('Log Frame has Closed. Clearing Menu Flag (is %s)' % self.menuHelp.IsChecked(self.MENUITEM_LOG))
        self.menuHelp.Check(self.MENUITEM_LOG, False)
        
    def _closeLogFrame(self):
        if not self.logFrame:
            return
        # Send EVT_CLOSE to logFrame
        wx.PostEvent(self.logFrame, wx.PyCommandEvent(wx.EVT_CLOSE.typeId, self.GetId()))
        sys.stdout = sys.__stdout__
        self.logFrame = None

    # Is LogFrame open ?
    def isLogFrame(self):
        return self.logFrame != None

####
class OSVM(wx.Frame):
    colorGrid = []
    downloadDir = ''
    timerCnt = 0
    ssThr = 0

    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)
        self.parent = parent

        self.installDlg = None
        self.fileType = None

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
        prefix = olbl[:olbl.index(':')]
        self._pageCount = self.noteBook.GetPageCount()
        if globs.viewMode:
            fileCnt = globs.localFilesCnt
        else:
            fileCnt = globs.availRemoteFilesCnt
        nlbl = '%s: %d.  Page: %d/%d' % (prefix, fileCnt, self.noteBook.GetSelection()+1,self._pageCount)
        self.staticBox3.SetLabel(nlbl)

    def OnKeyPress(self, event):
        #obj = event.GetEventObject()
        keycode = event.GetKeyCode()
        pos = event.GetPosition()
        print(keycode,pos)
        for i in range(3):
            print(self.thumbButtons[i][0].GetScreenRect())
        #event.Skip()
        
    def _createThumbnailTab(self, parent, listOfThumbnail, idx):
        tab = wx.Panel(id=wx.ID_ANY, name='tab%d'%idx, parent=parent)

#        tab.Bind(wx.EVT_KEY_DOWN, self.OnKeyPress)
        
        sizer = wx.GridSizer(rows=globs.thumbnailGridRows, cols=globs.thumbnailGridColumns, vgap=5, hgap=5)

        lastIdx = min(idx + (globs.thumbnailGridRows * globs.thumbnailGridColumns), len(listOfThumbnail))
        unbufprint('%s [%d : %d]\r' % (tab.GetName(), idx, lastIdx)) #, end='', flush=True)
        self.updateStatusBar(field=self.SB_COUNTER, msg='%d files' % (lastIdx))

        for f in listOfThumbnail[idx:lastIdx]:
            remFileName = f[1][globs.F_NAME]
            remFileSize = f[1][globs.F_SIZE]
            remFileDate = f[1][globs.F_DATEINSECS]

            # Add 1 button for each available image
            button = wx.Button(parent=tab, name=remFileName, style=0)
            if globs.viewMode:
                if globs.vlcVideoViewer:
                    button.Bind(wx.EVT_BUTTON, self.LaunchViewer)
                button.Bind(wx.EVT_RIGHT_DOWN, self.OnThumbButtonRightDown)
            else:
                if remFileName in list(globs.localFileInfos.keys()) and globs.vlcVideoViewer:
                    button.Bind(wx.EVT_BUTTON, self.LaunchViewer)
                else:
                    button.Bind(wx.EVT_BUTTON, lambda evt: self.OnThumbButton(evt))
#            button.Bind(wx.EVT_RIGHT_DOWN, self.OnThumbButtonRightDown)
            button.Bind(wx.EVT_RIGHT_DOWN, lambda evt: self.OnThumbButtonRightDown(evt))
            button.Bind(wx.EVT_KEY_DOWN, self.OnThumbKeyDown)
        
            remFileSizeString = humanBytes(remFileSize)

            # Display thumbnail (with scaling)
            thumbnailPath = os.path.join(globs.thumbDir, remFileName)
            self._displayThumbnail(button, thumbnailPath, wx.BITMAP_TYPE_JPEG)

            # Set tooltip
            if globs.viewMode:
                toolTipString = 'File: %s\nSize: %s\nDate: %s' % (remFileName,remFileSizeString,secondsTodmY(remFileDate))
            else:
#                toolTipString = 'File: %s\nSize: %s\nDate: %s' % (remFileName,remFileSizeString,getHumanDate(remFileDate))
                toolTipString = 'File: %s\nSize: %s\nDate: %s' % (remFileName,remFileSizeString,secondsTodmY(remFileDate))
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

        if globs.viewMode:
            firstRemFileDate = '%s' % (secondsTodmy(listOfThumbnail[idx][1][globs.F_DATEINSECS]))
            lastRemFileDate  = '%s' % (secondsTodmy(listOfThumbnail[lastIdx-1][1][globs.F_DATEINSECS]))
        else:
            firstRemFileDate = '%s' % (getHumanDate(listOfThumbnail[idx][1][globs.F_DATE]))
            lastRemFileDate  = '%s' % (getHumanDate(listOfThumbnail[lastIdx-1][1][globs.F_DATE]))

        tab.SetSizer(sizer)
        return tab,firstRemFileDate,lastRemFileDate

    # Filter the file list to select files matching globs.rotImgChoice value.
    # ROT_IMG_ENTRIES = ['Show Rotated Only', 'Show Original Only', 'Show Both']
    # def _filterRotatedFiles(self, fileList):
    #     myprint('Filter =',globs.ROT_IMG_ENTRIES[globs.rotImgChoice])
    #     if globs.rotImgChoice == 0:
    #         # Must show rotated images if available and original files if not
    #         lrotonly = [x[1][0] for x in fileList if '-rot' in x[0]]     # list with rotated img only
    #         l = list()
    #         for e in fileList:
    #             print('***',e)
    #             fileName = e[0]
    #             field11  = e[1][1]
    #             field12  = e[1][2]
    #             filePath = e[1][3]
            
    #             prefix = fileName.split('.')[0]	# File prefix
    #             if '-rot' in prefix: # Rotated file
    #                 continue
    #             n = [x for x in lrotonly if re.search('%s-rot[0-9]+.jpg' % prefix, x, re.IGNORECASE)]
    #             if n:
    #                 # Build a new tuple and append to output list
    #                 t = (n[0], [ n[0],field11,field12,os.path.join(os.path.dirname(filePath),n[0])])
    #                 l.append(t)
    #             else:
    #                 l.append(e)
    #         return l
        
    #     if globs.rotImgChoice == 1:
    #         # Must show only original files even if some files have been rotated
    #         l = [x for x in fileList if not '-rot' in x[0]] # only original files
    #         return l
        
    #     if globs.rotImgChoice == 2:	# Show both rotated/not rotated files
    #         # Must show both rotated and non-rotated files, e.g. all files
    #         return fileList

    def _createThumbnailPanel(self):
        setBusyCursor(True)

        agwStyle=fnb.FNB_VC8|fnb.FNB_COLOURFUL_TABS | fnb.FNB_NO_X_BUTTON
#        agwStyle=fnb.FNB_VC8 | fnb.FNB_COLOURFUL_TABS | fnb.FNB_NO_X_BUTTON |fnb.FNB_DROPDOWN_TABS_LIST
        self.noteBook = fnb.FlatNotebook(parent=self.panel1, id=wx.ID_ANY,agwStyle=agwStyle) 

        # Create a custom panel to use when the notebook is empty, e.g. no file is detected
        self.customPanel = LogoPanel.LogoPanel(self.noteBook, -1)
        self.noteBook.SetCustomPage(self.customPanel)

        self._pageCount = self.noteBook.GetPageCount()
        myprint('%d pages' % self._pageCount)
        
        if globs.viewMode:
            fileListToUse = globs.localFilesSorted
#            fileListToUse = self._filterRotatedFiles(globs.localFilesSorted)
            self.customPanel.setLogoPanelTopTitle('No Local File Detected')
        else:
            fileListToUse = globs.availRemoteFilesSorted
            self.customPanel.setLogoPanelTopTitle('No Remote File Detected')
            self.customPanel.setLogoPanelMidTitle('Connect to the Camera and Refresh')

        if globs.noPanel:
            msg = 'Skipping loading of thumbnail panel'
            myprint(msg)
            self.updateStatusBar(msg=msg)
            numTabs = 0
        else:
            numTabs = len(fileListToUse) / (globs.thumbnailGridRows * globs.thumbnailGridColumns)

        firstIdx = 0

        for t in range(int(math.ceil(numTabs))): # round up
            tab, firstRemFileDate,lastRemFileDate = self._createThumbnailTab(self.noteBook, fileListToUse, firstIdx)
            if globs.fileSortRecentFirst:
                self.noteBook.AddPage(tab, '%s  -  %s' % (lastRemFileDate,firstRemFileDate))
            else:
                self.noteBook.AddPage(tab, '%s  -  %s' % (firstRemFileDate,lastRemFileDate))

#            self.tabs.append(tab)
            firstIdx += globs.thumbnailGridRows * globs.thumbnailGridColumns

        self._pageCount = self.noteBook.GetPageCount()
        myprint('%d pages created' % self._pageCount)

        # update box title
        self._updateStaticBox3Label('_createThumbnailPanel')

        self.noteBook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CHANGED,self._OnFlatNoteBookPageChanged)
        self.noteBook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSED,self._OnFlatNoteBookPageClosed)
#        self.noteBook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CHANGING,self.ev2)

        setBusyCursor(False)
        myprint('Timer status:',self.parent.timer.IsRunning())
        myprint('Stopping timer in OSVMConfig')
        self.parent.timer.Stop() # Stop the timer in parent class (OSVMConfig)
        myprint('Timer status:',self.parent.timer.IsRunning())
        
    #
    # This function will rescan the installation according to user preferences
    #
    def _updateThumbnailPanel(self):
        setBusyCursor(True)

        # Update customPanel titles *before* deleting the pages
        if globs.viewMode:
            self.customPanel.setLogoPanelTopTitle('No Local File Detected')
        else:
            self.customPanel.setLogoPanelTopTitle('No Remote File Detected')
            self.customPanel.setLogoPanelMidTitle('Connect to the Camera and Refresh')

        # Delete all pages, one by one, starting from the last
        for p in range(self.noteBook.GetPageCount()-1, -1, -1):
            self.noteBook.DeletePage(p)

        # Clear existing button list
        self.thumbButtons = list()

        if globs.viewMode:
            fileListToUse = globs.localFilesSorted
#            fileListToUse = self._filterRotatedFiles(globs.localFilesSorted)            
        else:
            fileListToUse = globs.availRemoteFilesSorted

        if globs.noPanel:
            msg = 'Skipping loading of thumbnail panel'
            myprint(msg)
            self.updateStatusBar(msg=msg)
            numTabs = 0
        else:
            numTabs = len(fileListToUse) / (globs.thumbnailGridRows * globs.thumbnailGridColumns)
        firstIdx = 0

        for t in range(int(math.ceil(numTabs))): # round up
            tab, firstRemFileDate,lastRemFileDate = self._createThumbnailTab(self.noteBook, fileListToUse, firstIdx)
            if globs.fileSortRecentFirst:
                self.noteBook.AddPage(tab, '%s  -  %s' % (lastRemFileDate,firstRemFileDate))
            else:
                self.noteBook.AddPage(tab, '%s  -  %s' % (firstRemFileDate,lastRemFileDate))

            firstIdx += globs.thumbnailGridRows * globs.thumbnailGridColumns

        self._pageCount = self.noteBook.GetPageCount()
        myprint('%d pages created' % self._pageCount)

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

        # if operation == globs.FILE_DELETE:
        #     # Ask confirmation
        #     dial = wx.MessageDialog(None, 'Do you really want to DELETE file %s ?'% (fileName), 
        #                             'Question', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        #     ret = dial.ShowModal()
        #     if ret == wx.ID_NO:
        #         return

        op[globs.OP_STATUS]   = 1          			# Busy
        op[globs.OP_FILENAME] = fileName
        op[globs.OP_FILETYPE] = fileName.split('.')[1]	# File suffix
        op[globs.OP_TYPE]     = operation
        nBlocks = fileSize / globs.URLLIB_READ_BLKSIZE
        op[globs.OP_SIZE]     = (fileSize, nBlocks)
        op[globs.OP_FILEDATE] = fileDate
#        op[globs.OP_FILEPATH] = globs.localFileInfos[fileName][globs.F_PATH]
        op[globs.OP_FILEPATH] = os.path.join(globs.osvmDownloadDir, fileName)
            
        pendingOpsCnt = self.pendingOperationsCount()
        statusBarMsg = 'File successfully marked. %d marked file(s)' % (pendingOpsCnt)
        self.updateStatusBar(msg=statusBarMsg)
        self._enableActionButtons()
        
        # Sanity check
        # Each entry in thumbButtons[] is of form: [widget, fileName, fgcol, bgcol]
        for b in self.thumbButtons:
            if b[1] == fileName:
                if b[0] != button:
                    print ("ERROR: File list corrupted!")
                else:
                    # Update button color
                    button.SetBackgroundColour(globs.fileColors[globs.FILE_OP_PENDING][0])
                    button.SetForegroundColour(globs.fileColors[globs.FILE_OP_PENDING][1])
                    self.Refresh()
        #myprint(op)

    winDisabler = None

    # Set mode to Enable/Disable. Prevent user using out-dated information
    def _setMode(self, mode, reason):
        myprint('Setting mode %s' % mode)
        #print traceback.print_stack()

        # Restore focus to panel
        # DP: 02/06/2016. Keep the focus on the current widget 
        # self.panel1.SetFocusIgnoringChildren()

        # Menu items to disable when mode == globs.MODE_DISABLED
        # menuItems = [('File', 'Preferences'),
        #              ('File', 'Clean Download Directory...'),
        #              ('File', 'Quit')]

        if mode == globs.MODE_ENABLED:
            self.updateStatusBar(msg=reason)

            # handle events which may have been queued up
            wx.Yield() 

            #del self.winDisabler

            # Allow user action
            # for item in menuItems:
            #     id = self.menuBar.FindMenuItem(item[0],item[1])
            #     self.menuBar.Enable(id, True)

            # Disable some menu items if no camera
            if not globs.cameraConnected:
                self._setOfflineMode()

            self.btnRescan.Enable()
            if not globs.viewMode and globs.cameraConnected:
                self.btnDownload.Enable()

            # Enable all pkg buttons
            self.noteBook.Enable()
        else:
            self.updateStatusBar(msg=reason, fgcolor=wx.WHITE, bgcolor=wx.RED)

            # for item in menuItems:
            #     id = self.menuBar.FindMenuItem(item[0],item[1])
            #     self.menuBar.Enable(id, False)

            # Disable all buttons
            self.noteBook.Disable()
            self.btnRescan.Enable()
#            self.btnRescan.SetDefault()

            #self.winDisabler = wx.WindowDisabler()

    # Clear/Reset a pending operation
    def resetOneRequest(self, op):
        op[globs.OP_STATUS]     = 0
        op[globs.OP_FILENAME]   = ''
        op[globs.OP_FILETYPE]   = ''
        op[globs.OP_TYPE]       = 0
        op[globs.OP_FILEPATH]   = ''
        op[globs.OP_SIZE]       = (0,0)
        op[globs.OP_REMURL]     = ''
        op[globs.OP_INWGT]      = []
        op[globs.OP_INCOUNT]    = 0
        op[globs.OP_INSTEP]     = 0
        op[globs.OP_INLEDCOL]   = globs.LED_GREY
        op[globs.OP_INLEDSTATE] = globs.LED_OFF
        op[globs.OP_INTH]       = None
        op[globs.OP_INTICKS]    = 0

    def pendingOperationsCount(self):
        cnt = 0
        for i in range(len(globs.opList)):
            if globs.opList[i][globs.OP_STATUS]:
                cnt += 1
        return cnt

    def _clearAllRequests(self):
        # Loop thru opList[]: Clear all slots
        for i in range(len(globs.opList)):
            opStatus = globs.opList[i][globs.OP_STATUS]
            # If this operation is in used, reset associated button
            if opStatus:
                fileName = globs.opList[i][globs.OP_FILENAME]
                self.resetOneButton(fileName)
            self.resetOneRequest(globs.opList[i])
            
    # Reset a package button associated with pkgnum
    def resetOneButton(self, fileName):
        # Each entry in thumbButtons[] is: [widget, pkgnum, fgcol, bgcol]
        for entry in self.thumbButtons:
            if entry[1] == fileName:
                # Restore colors
                entry[0].SetForegroundColour(entry[2])
                entry[0].SetBackgroundColour(entry[3])
                #entry[0].SetValue(False)

    def updateStatusBar(self, field=-1, msg=None, bgcolor=wx.NullColour, fgcolor=wx.BLACK):
        self.statusBar1.SetForegroundColour(fgcolor)
        self.statusBar1.SetBackgroundColour(bgcolor)

        if not msg:
            if not globs.cameraConnected:
                msg = '%d local files' % (globs.localFilesCnt)
            else:
                msg = '%d local files, %d files available on camera' % (globs.localFilesCnt, globs.availRemoteFilesCnt)

        if int(field) < 0:
            self.statusBar1.SetStatusText(msg, self.SB_MSG)
        else:
            self.statusBar1.SetStatusText(msg, field)

        # Check if SSID has changed
        if self.statusBar1.GetStatusText(self.SB_SSID) != globs.iface.ssid():
            myprint('SSID has changed: %s / %s' % (self.statusBar1.GetStatusText(self.SB_SSID), globs.iface.ssid()))
            if globs.iface.ssid():
                self.statusBar1.SetStatusText(globs.iface.ssid(), self.SB_SSID)
        # DP DP DP: Allow GUI to refresh the status bar. warning: Slow down !!!!
        #wx.Yield()
        
    def _displayBitmap(self, widget, image, type):
        # load the image
        imgPath = os.path.join(globs.imgDir, image)
        Img = wx.Image(imgPath, type)
         # convert it to a wx.Bitmap, and put it on the wx.StaticBitmap
        widget.SetBitmap(wx.Bitmap(Img))

    # Overlay the thumbnail image with a fixed 'Play' image. Return the new image pathname
    def _overlayThumbnail(self, image, type):
        imgSuffix = {
            wx.BITMAP_TYPE_JPEG: 'JPG',
            wx.BITMAP_TYPE_PNG: 'PNG',
            }
        # Check if original thumbnail exists
        if not os.path.exists(image):
            return ''
        
        d=os.path.dirname(image)
        f=os.path.basename(image)
        suffix = image.rsplit('.')[-1:][0]
        nf='%s-Play.%s.%s' % (f.rsplit('.',1)[0], suffix, imgSuffix[type])
        newThumbnailPathname = os.path.join(d,nf)

        if os.path.exists(newThumbnailPathname):
#            myprint('Using existing file %s' % newThumbnailPathname)
            return newThumbnailPathname

        myprint('Overlaying %s' % image)
        overlay = Image.open(image)
        background = Image.open(os.path.join(globs.imgDir, "play2-160x120.png"))
        background = background.convert("RGB")
        overlay = overlay.convert("RGB")

        newThumbnail = Image.blend(background, overlay, 0.7) #0.8)
        newThumbnail.save(newThumbnailPathname)
        return newThumbnailPathname

    def _displayThumbnail(self, widget, image, type):
        suffix = image.rsplit('.')[-1:][0]
        if suffix.lower() == 'mov':
            newThumbnailPathname = self._overlayThumbnail(image, type)
            if not newThumbnailPathname:  # If thumbnail does not exist, use sad smiley
                newThumbnailPathname = os.path.join(globs.imgDir, 'sad-smiley.png')
                type = wx.BITMAP_TYPE_PNG
            Img = wx.Image(newThumbnailPathname, type)
        else:
            Img = wx.Image(image, type)

        # get original size of the image
        try:
            (w,h) = Img.GetSize().Get()
        except:
#            myprint('Invalid thumbnail file %s' % (image))
#            imgPath = os.path.join(globs.thumbDir, globs.imgDir, 'sad-smiley.png')
            imgPath = os.path.join(globs.imgDir, 'sad-smiley.png')            
            Img = wx.Image(imgPath, wx.BITMAP_TYPE_PNG)
            (w,h) = Img.GetSize().Get()

        # convert it to a wx.Bitmap, and put it on the wx.StaticBitmap
        widget.SetBitmap(wx.Bitmap(Img.Scale(w*globs.thumbnailScaleFactor, h*globs.thumbnailScaleFactor)),dir=wx.TOP)

    def _init_topBoxSizer_Items(self, parent):
        if globs.compactMode:
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
        sts1.Add(self.fileTypesTxt, 0, border=6, flag=wx.EXPAND|wx.BOTTOM)
        sts1.AddStretchSpacer(prop=1)
        sts1.Add(self.fileTypesChoice, 0, border=0, flag=wx.EXPAND)
        parent.Add(sts1, pos=(0, 0), flag=wx.ALL, border=0)# | wx.EXPAND

        sts3 = wx.BoxSizer(orient=wx.VERTICAL)
        sts3.Add(self.fromCb, 0, border=0, flag=wx.EXPAND)
        sts3.AddStretchSpacer(prop=1)
        sts3.Add(self.dpc1, 0, border=0, flag=wx.EXPAND)
        parent.Add(sts3, pos=(0, 1), flag=wx.ALL, border=0)#| wx.EXPAND

        sts4 = wx.BoxSizer(orient=wx.VERTICAL)
        sts4.Add(self.toCb, 0, border=0, flag=wx.EXPAND)
        sts4.AddStretchSpacer(prop=1)
        sts4.Add(self.dpc2, 0, border=0, flag=wx.EXPAND)
        parent.Add(sts4, pos=(0, 2), flag=wx.ALL, border=0)

        sts2 = wx.BoxSizer(orient=wx.VERTICAL)
        sts2.Add(self.fileSortTxt, 0, border=6, flag=wx.EXPAND|wx.BOTTOM)
        sts2.AddStretchSpacer(prop=1)
        sts2.Add(self.fileSortChoice, 0, border=0, flag=wx.EXPAND)
        parent.Add(sts2, pos=(0, 3), flag=wx.ALL, border=0)# | wx.EXPAND

        parent.Add(20,0, pos=(0, 4)) # Some space before Cast button

        sts5 = wx.BoxSizer(orient=wx.VERTICAL)
        sts5.AddStretchSpacer(prop=1)
        sts5.Add(self.btnCast, 0, border=0, flag=wx.EXPAND)
        parent.Add(sts5, pos=(0, 5), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=0)
        parent.Add(self.castDeviceName, pos=(1, 5), flag=wx.ALL| wx.ALIGN_CENTER, border=0)

        parent.Add(10,0, pos=(0, 6)) # Some space after Cast button

        sts6 = wx.BoxSizer(orient=wx.VERTICAL)
        sts6.AddStretchSpacer(prop=1)
        sts6.Add(self.btnRew, 0, border=0, flag=wx.EXPAND)
        parent.Add(sts6, pos=(0, 7), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=0)

        sts7 = wx.BoxSizer(orient=wx.VERTICAL)
        sts7.AddStretchSpacer(prop=1)
        sts7.Add(self.btnPlay, 0, border=0, flag=wx.EXPAND)
        parent.Add(sts7, pos=(0, 8), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=0)

        sts8 = wx.BoxSizer(orient=wx.VERTICAL)
        sts8.AddStretchSpacer(prop=1)
        sts8.Add(self.btnStop, 0, border=0, flag=wx.EXPAND)
        parent.Add(sts8, pos=(0, 9), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=0)

        parent.Add(10,0, pos=(0, 10)) # Some space after Stop button

#        parent.Add(self.btnCancel, pos=(0, 11), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=0)
#        parent.Add(self.btnDownload, pos=(0, 12), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=0)

        sts9 = wx.BoxSizer(orient=wx.VERTICAL)
        sts9.AddStretchSpacer(prop=1)
        sts9.Add(self.btnCancel, 0, border=0, flag=wx.EXPAND)
        parent.Add(sts9, pos=(0, 11), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=0)
        
        sts10 = wx.BoxSizer(orient=wx.VERTICAL)
        sts10.AddStretchSpacer(prop=1)
        sts10.Add(self.btnDownload, 0, border=0, flag=wx.EXPAND)
        sts10.AddStretchSpacer(prop=1)
        sts10.Add(self.btnShare, 0, border=0, flag=wx.EXPAND)
        sts10.AddStretchSpacer(prop=1)
        sts10.Add(self.btnDelete, 0, border=0, flag=wx.EXPAND)
        parent.Add(sts10, pos=(0, 12), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=0)

        parent.Add(10,0, pos=(0, 13)) #13

        parent.Add(self.btnRescan, pos=(0, 14), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=0) #14

    # Used in globs.compactMode only
    def _init_trafficBoxSizer_Items(self, parent):
        parent.AddStretchSpacer(prop=1)
        #parent.Add(self.staticBitmap2, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=0)
        parent.Add(self.staticBitmap2, border=0, flag=wx.ALL) #211 wx.ALIGN_CENTER_VERTICAL|
        parent.AddStretchSpacer(prop=1)
    
    # Used in globs.compactMode only
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
        parent.Add(self.btnClose, 0, border=0, flag=0)

    def _init_bottomBoxSizer2_Items(self, parent):
        parent.Add(self.pltfInfo, 0, border=0, flag=wx.ALL | wx.ALIGN_LEFT)
        parent.AddStretchSpacer(prop=1)
        parent.Add(self.bottomBoxSizer3, 0, border=0, flag=wx.ALL | wx.ALIGN_CENTER)##
        parent.AddStretchSpacer(prop=1)
        parent.Add(self.bottomBoxSizer1, 0, border=0, flag=wx.ALL)#211 | wx.ALIGN_RIGHT)

    def _init_bottomBoxSizer3_Items(self, parent):
        parent.Add(self.btnSwitchMode, 0, border=0, flag=wx.ALL | wx.EXPAND)
        parent.Add(4, 0, border=0, flag=0)
        parent.Add(self.btnSwitchNetwork, 0, border=0, flag=wx.ALL | wx.EXPAND)

    def _init_bottomBoxSizer_Items(self, parent):
        parent.Add(self.statusBar1, 0, border=5, flag=wx.EXPAND | wx.ALL)
        parent.Add(0, 4, border=0, flag=0)
        parent.Add(self.bottomBoxSizer2, 0, border=5, flag=wx.ALL | wx.EXPAND)


    def _init_sizers(self):
        # Top Level BoxSizer
        self.topBoxSizer = wx.BoxSizer(orient=wx.VERTICAL)

        # Title BoxSizer
        if not globs.compactMode:
            self.titleBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        # File selection grid sizer in staticBoxSizer
        self.btnGridBagBoxSizer = wx.StaticBoxSizer(box=self.staticBox4, orient=wx.HORIZONTAL)
        self.btnGridBagSizer = wx.GridBagSizer(hgap=15,vgap=0)

        if globs.compactMode:
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

        if not globs.compactMode:
            self._init_titleBoxSizer_Items(self.titleBoxSizer)

        self._init_btnGridBagBoxSizer_Items(self.btnGridBagBoxSizer)
        self._init_btnGridBagSizer_Items(self.btnGridBagSizer)

        if globs.compactMode:
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
        # Package buttons list
        self.thumbButtons = list()

        # List of scheduled operations on files. Format:
        # op[globs.OP_STATUS|0]      = status (busy=1/off=0)
        # op[globs.OP_FILENAME|1]    = base file name
        # op[globs.OP_TYPE|2]        = operation #FILE_DOWNLOAD=0 FILE_MARK=1 FILE_UNMARK=2
        # op[globs.OP_FILEPATH|4]    = full pathname of local file for download
        # op[globs.OP_SIZE|5]        = (size in bytes, block count)
        # op[globs.OP_REMURL|6]      = full remote url to download
        # op[globs.OP_INWGT|7]       = list of all assoc. widgets in InstallDialog frame
        # op[globs.OP_INCOUNT|8]     = current block xfer counter for this op
        # op[globs.OP_INSTEP|9]      = Installation step
        # op[globs.OP_INLEDCOL|10]   = Installation LED color
        # op[globs.OP_INLEDSTATE|11] = Installation LED state: ON/BLINK/OFF
        # op[globs.OP_INTH|12]       = Installation thread
        # op[globs.OP_INTICKS|13]    = Installation elapsed time

        #self.opList = [[0] * globs.OP_LASTIDX for i in range(globs.MAX_OPERATIONS)]

        # Load Preferences
        self.prefs = Preferences()
        self.prefs._loadPreferences()

        self.SetClientSize(wx.Size(1200, 680))
        self.Center()

        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self,
                               size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)
#        self.panel1.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

#        self.panel1.Bind(wx.EVT_KEY_DOWN, self._onKeyPress)
        self.panel1.SetFocusIgnoringChildren()
        self.panel1.Bind(wx.EVT_LEFT_UP, self._setFocus)

        self.fileTypesTxt = wx.StaticText(label='File Type', parent=self.panel1, id=wx.ID_ANY)
        if not globs.vlcVideoViewer:
            self.fileTypesChoice = wx.Choice(choices=[v for v in globs.FILE_TYPES_NOVLC],
                                             id=wx.ID_ANY, parent=self.panel1, style=0)
        else:
            self.fileTypesChoice = wx.Choice(choices=[v for v in globs.FILE_TYPES],
                                             id=wx.ID_ANY, parent=self.panel1, style=0)

        self.fileTypesChoice.SetToolTip('Select type of files to show/sync')
        self.fileTypesChoice.SetStringSelection(globs.FILE_TYPES[0])
        self.fileTypesChoice.Bind(wx.EVT_CHOICE, lambda evt: self.OnFileTypesChoice(evt))

        self.fromCb = wx.CheckBox(self.panel1, id=wx.ID_ANY, label='From Date')
        self.fromCb.SetValue(False)
        self.fromCb.Bind(wx.EVT_CHECKBOX, lambda evt: self.OnFromDate(evt))
        self.fromCb.Disable()
        
        self.dpc1 = wx.adv.DatePickerCtrl(self.panel1,
                                          style = wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY | wx.adv.DP_ALLOWNONE)

        self.toCb = wx.CheckBox(self.panel1, id=wx.ID_ANY, label='To Date')
        self.toCb.SetValue(False)
        self.toCb.Bind(wx.EVT_CHECKBOX, lambda evt: self.OnToDate(evt))
        self.toCb.Disable()

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
        self.fileSortChoice.SetStringSelection(self.sortTypes[0] if globs.fileSortRecentFirst else self.sortTypes[1])
        self.fileSortChoice.Bind(wx.EVT_CHOICE, lambda evt: self.OnFileSortChoice(evt))

        self.btnCast = wx.Button(label="Cast", size=wx.Size(32,32), parent=self.panel1, style=wx.NO_BORDER)
        self._displayBitmap(self.btnCast, 'cast-32.jpg', wx.BITMAP_TYPE_JPEG)
        self.btnCast.SetToolTip('Cast images to a GoogleCast')
        self.btnCast.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnCast(evt))
        if not globs.pycc:
            self.btnCast.Disable()

        self.btnRew = wx.Button(size=wx.Size(32,32), parent=self.panel1, style=wx.NO_BORDER)
        self._displayBitmap(self.btnRew, 'rew.png', wx.BITMAP_TYPE_PNG)
        self.btnRew.SetToolTip('Restart the Slideshow from beginning')
        self.btnRew.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnRew(evt))

        self.btnPlay = wx.Button(name='btnPlay', size=wx.Size(32,32), parent=self.panel1, style=wx.NO_BORDER)
        self._displayBitmap(self.btnPlay, 'play.png', wx.BITMAP_TYPE_PNG)
        self.btnPlay.SetToolTip('Start the Slideshow')
        self.btnPlay.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnPlay(evt))

        self.btnStop = wx.Button(size=wx.Size(32,32), parent=self.panel1, style=wx.NO_BORDER)
        self._displayBitmap(self.btnStop, 'stop.png', wx.BITMAP_TYPE_PNG)
        self.btnStop.SetToolTip('Stop the Slideshow')
        self.btnStop.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnStop(evt))
        for dpc in [self.dpc1,self.dpc2]:
            dpc.Disable()

        self.btnRescan = wx.Button(id=wx.ID_REFRESH, label='Refresh',
                                   name='btnRescan', parent=self.panel1, style=0)
        self.btnRescan.SetToolTip('Rescan configuration')
        self.btnRescan.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnRescan(evt))
        # Event received from our parent (OSVMConfig) asking for a rescan
        self.Bind(EVT_RESCAN_NEEDED, self.OnBtnRescan)

        # Create the LEDS and Static Texts to show colors meaning
        for i in range(len(globs.FILE_COLORS_STATUS)):
            led = LedControl.ColorLED(self.panel1, str(globs.fileColors[i][0].GetAsString(flags=wx.C2S_HTML_SYNTAX)))
            self.colorGrid.append(led)
            self.colorGrid.append(wx.StaticText(self.panel1, label=globs.FILE_COLORS_STATUS[i]))

        self.btnCancel = wx.Button(id=wx.ID_CANCEL, label='Cancel All', parent=self.panel1, style=0)
        self.btnCancel.SetToolTip('Cancel all pending requests')
        self.btnCancel.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnCancel(evt))
        self.btnCancel.Disable()
        
        self.btnDownload = wx.Button(id=wx.ID_OK, label='Download', parent=self.panel1, style=0)
        self.btnDownload.SetToolTip('Commit all pending requests')
        self.btnDownload.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnDownload(evt))
        self.btnDownload.Disable()
        
        self.btnShare = wx.Button(id=wx.ID_OK, label='Share', parent=self.panel1, style=0)
        self.btnShare.SetToolTip('Share selected files')
        self.btnShare.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnShare(evt))
        self.btnShare.Disable()

        self.btnDelete = wx.Button(id=wx.ID_OK, label='Delete', parent=self.panel1, style=0)
        self.btnDelete.SetToolTip('Delete selected files')
        self.btnDelete.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnDelete(evt))
        self.btnDelete.Disable()

        self._disableActionButtons()

        # The staticBox3 label MUST end with the string 'Page:' (will be updated automagically)
        if globs.viewMode:
            lbl = ' Available Local Files: %d.  Page:' % globs.localFilesCnt
        else:
            lbl = ' Available Remote Files (on camera).  Page:'

        self.staticBox3 = wx.StaticBox(id=wx.ID_ANY, label=lbl, parent=self.panel1, 
                                       pos=wx.Point(10, 199), size=wx.Size(1192, 100), style=0)
        if globs.viewMode:
            lbl = ' File Viewer Control '
        else:
            lbl = ' Select Files to Sync... '
        self.staticBox4 = wx.StaticBox(id=wx.ID_ANY, label=lbl, parent=self.panel1, 
                                       pos=wx.Point(10, 64), style=0)

        self.statusBar1 = wx.StatusBar(id=wx.ID_ANY,parent=self.panel1, style=0)
        self.statusBar1.SetToolTip('Status')
        self.statusBar1.SetFont(wx.Font(11, wx.SWISS, wx.ITALIC, wx.NORMAL, False, 'foo'))

        self.statusBarFieldsCount = 5
        
        [self.SB_MODE,		# Operating mode (View/Sync)
         self.SB_SSID,		# Current SSID
         self.SB_DIR,		# Current download directory
         self.SB_COUNTER,	# Various counters
         self.SB_MSG] = [i for i in range(self.statusBarFieldsCount)] # Free field for msg

        self.statusBar1.SetFieldsCount(self.statusBarFieldsCount)
        self.statusBar1.SetStatusText('View Mode' if globs.viewMode else 'Sync Mode', self.SB_MODE)
        self.statusBar1.SetStatusText(globs.iface.ssid(), self.SB_SSID)
        self.statusBar1.SetStatusText(globs.osvmDownloadDir, self.SB_DIR)
        self.statusBar1.SetStatusText(' ', self.SB_COUNTER)

        self._createThumbnailPanel()
        
        if globs.noPanel:
            msg = 'Skipping loading of thumbnail panel'
            myprint(msg)
        elif not globs.cameraConnected or globs.viewMode:
            msg = '%d local file(s)' % (globs.localFilesCnt)
            self._setOfflineMode()
        else:
            msg = '%d local file(s), %d file(s) available on camera' % (globs.localFilesCnt, globs.availRemoteFilesCnt)

        self.updateStatusBar(msg=msg)

        if globs.system == 'Windows':
            # Get win32api version
            fvi = win32api.GetFileVersionInfo(win32api.__file__, '\\')
            pywin32Version = fvi['FileVersionLS'] >> 16
            print("pywin32Version:", pywin32Version)
            label= '%s: Version: %s\n%s\nPython (%dbits): %s wxpython: %s pywin32: %s' % (globs.myName, globs.myVersion, (platform.platform()), globs.pythonBits, globs.pythonVersion, wx.version(), pywin32Version)
        else:
            label= '%s: %s\n%s\nPython (%dbits): %s wxpython: %s' % (globs.myName, globs.myVersion,  (platform.platform()), globs.pythonBits, globs.pythonVersion, wx.version())            

        self.pltfInfo = wx.StaticText(label=label, id=wx.ID_ANY, parent=self.panel1)
        self.pltfInfo.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Ubuntu'))

        self.btnSwitchMode = wx.Button(id=wx.ID_ANY, parent=self.panel1, style=0)
        self.btnSwitchMode.SetLabel('Switch to Sync Mode' if globs.viewMode else 'Switch to View Mode')
        #        self.btnSwitchMode.Bind(wx.EVT_BUTTON, self.OnBtnSwitchMode)
        self.btnSwitchMode.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnSwitchMode(evt))

        self.btnSwitchNetwork = wx.Button(id=wx.ID_ANY, label='Select Camera', parent=self.panel1, style=0)
        #        self.btnSwitchNetwork.Bind(wx.EVT_BUTTON, self.OnBtnSwitchNetwork)
        self.btnSwitchNetwork.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnSwitchNetwork(evt))
        if globs.system != 'Darwin' or not globs.networkSelector:
            self.btnSwitchNetwork.Disable()

        self.btnHelp = wx.Button(id=wx.ID_HELP, label='Help', parent=self.panel1, style=0)
        self.btnHelp.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnHelp(evt))

        self.btnClose = wx.Button(id=wx.ID_CLOSE, parent=self.panel1, style=0)
        self.btnClose.SetToolTip('Quit Application')
        self.btnClose.Bind(wx.EVT_BUTTON, self.OnBtnClose)
        
        if not globs.compactMode:
            self.staticBitmap1 = wx.StaticBitmap(bitmap=wx.NullBitmap, id=wx.ID_ANY, parent=self.panel1, style=0)
            self._displayBitmap(self.staticBitmap1, "OSVM5.png", wx.BITMAP_TYPE_PNG)

        self.staticBitmap2 = wx.StaticBitmap(bitmap=wx.NullBitmap,
                                             id=wx.ID_ANY, parent=self.panel1, style=0)
        self.staticBitmap2.SetToolTip('Network Status:\nRED: No Network\nGREEN:Camera OK')

        # Detect CLOSE event from Log Window (if any)
        #self.Bind(LogFrame.EVT_LOG_WINDOW_CLOSED, self.OnLogFrameClosed)
        
        # Update connection status indicator
        self._updateConnectionStatus()

        self._init_sizers()

        self.SendSizeEvent()

        # Initialize statusBar1
        self._initStatusBar1()

        w0,h0 = self.panel1.GetSize()
        w1,h1 = self.statusBar1.GetSize()

    def _setDatePickerCtrl(self):
        if globs.viewMode:
            if not globs.localFilesCnt:	# No local file available
                today = datetime.date.today()
                globs.remNewestDate = today.strftime("%m/%d/%Y")
                globs.remOldestDate = '01/01/1970'
                myprint('globs.remOldestDate:',globs.remOldestDate)
                myprint('globs.remNewestDate:',globs.remNewestDate)
            else:
                globs.remNewestDate = secondsTomdY(globs.localFilesSorted[0][1][globs.F_DATEINSECS])
                globs.remOldestDate = secondsTomdY(globs.localFilesSorted[-1][1][globs.F_DATEINSECS])
                myprint('globs.remOldestDate:',globs.remOldestDate,globs.localFilesSorted[0][1][globs.F_DATEINSECS])
                myprint('globs.remNewestDate:',globs.remNewestDate,globs.localFilesSorted[-1][1][globs.F_DATEINSECS])
        else:
            if not globs.availRemoteFilesCnt:	# No remote file available
                today = datetime.date.today()
                globs.remNewestDate = today.strftime("%m/%d/%Y")
                globs.remOldestDate = '01/01/1970'
                myprint('globs.remOldestDate:',globs.remOldestDate)
                myprint('globs.remNewestDate:',globs.remNewestDate)
            else:
                globs.remNewestDate = getHumanDate(globs.availRemoteFilesSorted[0][1][globs.F_DATE])
                globs.remOldestDate = getHumanDate(globs.availRemoteFilesSorted[-1][1][globs.F_DATE])
                myprint('globs.remOldestDate:',globs.remOldestDate,globs.availRemoteFilesSorted[0][1][globs.F_DATE])
                myprint('globs.remNewestDate:',globs.remNewestDate,globs.availRemoteFilesSorted[-1][1][globs.F_DATE])

        self._dpcSetValue(globs.remOldestDate, self.dpc1, globs.remNewestDate, self.dpc2)

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
        # disableMenuItems = []
        # for item in disableMenuItems:
        #     id = self.menuBar.FindMenuItem(item[0],item[1])
        #     self.menuBar.Enable(id, False)
        pass
    
    def _setFocus(self, event):
        print ("focus given to panel")
        self.panel1.SetFocusIgnoringChildren()
 
    # KeyEvent handler
    def _onKeyPress(self, event):
        keycode   = event.GetKeyCode()
        cmddown   = event.CmdDown()
        modifiers = event.GetModifiers()
        pos       = event.GetPosition()
        panel_pos = self.panel1.ScreenToClient(wx.GetMousePosition())
        print('***',keycode,wx.GetMousePosition()) #self.noteBook.GetScreenRect(),pos,panel_pos,
        for i in range(3):
            print(self.thumbButtons[i][0].GetScreenRect())
        #event.Skip()

    def _initStatusBar1(self):
        text = 'Processing pending requests...'
        self.textlen = len(text)

        f = self.statusBar1.GetFont()
        dc = wx.WindowDC(self.statusBar1)
        dc.SetFont(f)

        # Compute length of 1st field of the status bar (View Mode or Sync Mode)
        modeWidth,dummy = dc.GetTextExtent('View Mode' if globs.viewMode else 'Sync Mode')
        # Current SSID
        ssidWidth,dummy = dc.GetTextExtent(str(globs.iface.ssid()))
        # Current download dir
        ddirWidth,dummy = dc.GetTextExtent(str(globs.osvmDownloadDir))
        # Counters
        counterWidth,dummy = dc.GetTextExtent('00000000')
        self.statusBar1.SetStatusWidths([modeWidth + 20, ssidWidth + 20, ddirWidth + 10, counterWidth + 10, -1])
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

        myprint(textWidth,sbWidth,spaceWidth,nbspaces,self.displen)

    # stop statusBar1 animation
    def finish(self):
        if self.timer.IsRunning():
            myprint('Stopping animation')
            self.timer.Stop()

        msg = 'All scheduled operations finished/Cancelled'
        self.updateStatusBar(msg=msg)

    def _updateLEDs(self):
        for i in range(int(len(self.colorGrid) / 2)):
            color = str(globs.fileColors[i][0].GetAsString(flags=wx.C2S_HTML_SYNTAX))
            self.colorGrid[i*2].SetState(color)

    def _disableActionButtons(self):
        for b in [self.btnCancel, self.btnDownload, self.btnShare, self.btnDelete]:
            b.Disable()

    def _enableActionButtons(self):
        for b in [self.btnCancel, self.btnDownload, self.btnShare, self.btnDelete]:
            b.Enable()
        if globs.viewMode:
            self.btnDownload.Disable()
            
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

    # Left Click on a File button, zoom in the thumbnail
    def OnThumbButton(self, event):
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

        thumbFilePath = os.path.join(globs.thumbDir, entry[1])
        dlg = ThumbnailDialog.ThumbnailDialog(self, thumbnail=thumbFilePath)
        ret = dlg.ShowModal()
        dlg.Destroy()
        event.Skip()
        
    def OnThumbButtonRightDown(self, event):
        button = event.GetEventObject()

        # Retrieve the button in self.thumbButtons
        # Each entry in thumbButtons[] is of form: [widget, file, fgcol, bgcol]
        # found = False
        # for entry in self.thumbButtons:
        #     if entry[0] == button:
        #         found = True
        #         break
        # if not found:
        #     myprint('Button not found')
        #     FileOperationMenu(self, button)
        #     return

        try:
            e = [x for x in self.thumbButtons if x[0] == button]
        except:
            myprint('Button not found')
            return
        else:
            entry = e[0] # Use first element

        FileOperationMenu(self, button)

        # Check if an operation is scheduled for this button and colorize the
        # button accordingly
        for op in globs.opList:
            if op[globs.OP_STATUS] and op[globs.OP_FILENAME] == entry[1]:
                entry[0].SetBackgroundColour(globs.fileColors[globs.FILE_OP_PENDING][0])
                entry[0].SetForegroundColour(globs.fileColors[globs.FILE_OP_PENDING][1])
                pendingOpsCnt = self.pendingOperationsCount()
                statusBarMsg = 'File successfully marked. %d file(s) marked' % (pendingOpsCnt)
                self.updateStatusBar(msg=statusBarMsg)
                self._enableActionButtons()
                break

        self.panel1.Refresh()

    def OnThumbKeyDown(self, event):
        button = event.GetEventObject()
        try:
            e = [x for x in self.thumbButtons if x[0] == button]
        except:
            myprint('Button not found')
            event.Skip()
            return
        else:
            entry = e[0] # Use first element
        keycode = event.GetKeyCode()
        myprint('keycode=%d' % keycode)
        event.Skip()
            
    def _OnFlatNoteBookPageChanged(self, event):
        self._updateStaticBox3Label('_OnFlatNoteBookPageChanged')
        event.Skip()

    def _OnFlatNoteBookPageClosed(self, event):
        event.Skip()

    # def OpenExternalViewer(self, event):
    #     externalViewer = {
    #         'jpg':'/Applications/Preview.app',
    #         'mov':'/Applications/QuickTime Player.app',
    #         'mp4':'/Applications/QuickTime Player.app',
    #         # What about ORF and MPO files ??? XXX
    #         }

    #     button = event.GetEventObject()

    #     found = False
    #     # Retrieve associated button entry in thumbButtons[].
    #     # Each entry in thumbButtons[] is: [widget, filename, fgcol, bgcol]
    #     for entry in self.thumbButtons:
    #         if entry[0] == button:
    #             found = True
    #             break
    #     if not found:
    #         event.Skip()
    #         return

    #     suffix = entry[1].split('.')[1].lower()
    #     filePath = os.path.join(globs.osvmDownloadDir, entry[1])
    #     subprocess.call(
    #         ["/usr/bin/open", "-W", "-n", "-a", externalViewer[suffix], filePath]
    #         )
    #     event.Skip()

    def LaunchViewer(self, event):
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
        suffix = fname.split('.')[1].lower()

        if globs.castMediaCtrl:
            # Suspend the slideshow if active
            if self.ssThrLock.acquire(blocking=False) == False:	# Block the thread if active
                myprint('Lock is already set, should have blocked, so... Slideshow is paused')
            self._displayBitmap(self.btnPlay, 'play.png', wx.BITMAP_TYPE_PNG)
            self.btnPlay.SetName('btnPlay')

            fileURL = 'http://%s:%s/%s' % (globs.serverAddr, globs.SERVER_HTTP_PORT, fname)
            myprint('Loading URL: %s' % fileURL)

            # Update status message
            msg = 'Casting %s to %s' % (fname,globs.castDevice.name)
            self.updateStatusBar(msg=msg)
            myprint(msg)
            
            mediaFileType = { 'jpg':'image/jpg', 'mov':'video/mov', 'mp4':'video/mov' }
            globs.castMediaCtrl.play_media(fileURL, mediaFileType[suffix])
            if suffix == 'mov' or suffix == 'mp4':
                while globs.castMediaCtrl.status.player_state == 'PLAYING':
                    time.sleep(1)
            else:
                globs.castMediaCtrl.block_until_active()
            event.Skip()
            return

        filePath = os.path.join(globs.osvmDownloadDir, fname)

        if globs.useExternalViewer:
            suffix = entry[1].split('.')[1].lower()
            externalViewer = {
                'jpg':'/Applications/Preview.app',
                'mov':'/Applications/QuickTime Player.app',
                'mp4':'/Applications/QuickTime Player.app',
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
        self.updateStatusBar(msg=msg)

        myprint('Generating file list')
        fileList = [x[0] for x in globs.localFilesSorted]
        
        myprint("Searching %s in globs.localFilesSorted (%d files)" % (fname, len(globs.localFilesSorted)))
        try:
            idx = [x[0] for x in globs.localFilesSorted].index(fname)
        except:
            myprint('Unable to retrieve %s in globs.localFilesSorted. Starting from 0' % fname)
            idx = 0
        myprint('Launching MediaViewerDialog. (idx=%d)' % (idx))
        dlg = MediaViewerDialog.MediaViewerDialog(self, fileList, idx=idx, slideShow=False) #286
        ret = dlg.ShowModal()
        dlg.Destroy()
        self.updateStatusBar(msg=None)
        #myprint('Exit of MediaViewerDialog. ret:%d' % ret)

    def OnBtnSwitchMode(self, event):
        button = event.GetEventObject()
        myprint('Switching to: %s Mode' % ('Sync' if globs.viewMode else 'View'))

        self.parent.menuBar.Enable(self.parent.MENUITEM_FILELIST, globs.viewMode)
        
        globs.viewMode = not globs.viewMode
        if globs.viewMode:
            button.SetLabel('Switch to Sync Mode')
        else:
            button.SetLabel('Switch to View Mode')
            # Switch to favorite network
            if globs.autoSwitchToFavoriteNetwork and globs.favoriteNetwork != ('None','None'):
                if WifiDialog.switchToFavoriteNetwork():
                    msg = 'Switch to favorite network has failed'
                    self.updateStatusBar(msg=msg)
                    print(msg)
                    self.panel1.Refresh()
                    
        # Simulate a 'Rescan' event
        evt = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self.btnRescan.GetId())
        evt.SetEventObject(self.btnRescan)
        wx.PostEvent(self.btnRescan, evt)

    def OnBtnSwitchNetwork(self, event):
        # Switch the network
        ossid = globs.iface.ssid()
        dlg = WifiDialog.WifiDialog(self)
        ret = dlg.ShowModal()
        dlg.Destroy()
        if ret != wx.ID_CANCEL:
            nssid = globs.iface.ssid()
            if ossid != nssid:
                myprint('SSID has changed: %s/%s' % (ossid,nssid))
                self.updateStatusBar(msg=None)
            # Simulate a 'Rescan' event
            evt = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self.btnRescan.GetId())
            evt.SetEventObject(self.btnRescan)
            wx.PostEvent(self.btnRescan, evt)
        event.Skip()

    def OnBtnHelp(self, event):
        dlg = HelpDialog.HelpDialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        event.Skip()

    def OnBtnClose(self, event):        
        self.Close()
        myprint('Closing OSVM Frame')
        # Notify our parent
        evt = globs.wxOsvmFrameClose()
        wx.PostEvent(self.parent, evt)
        event.Skip()
        
    def _selectFiles(self, fileType):
        if globs.viewMode:
            cnt = self._selectFilesByDate(fileType)
        else:
            cnt = self._syncFiles(fileType)
        pendingOpsCnt = self.pendingOperationsCount()
        msg = '%d requests successfully marked, %d in the queue' % (cnt, pendingOpsCnt)
        self.updateStatusBar(msg=msg)
        self.panel1.Refresh()
        return cnt

    def OnFileTypesChoice(self, event):
        idx = self.fileTypesChoice.GetSelection()
        self.fileType = globs.FILE_TYPES[idx]
        print(idx,self.fileType)
        if self.fileType in globs.FILE_SUFFIXES.keys():
            self.OnBtnCancel(1)
            self._selectFiles(self.fileType)
            self.fromCb.Enable()
            self.toCb.Enable()
        elif self.fileType == 'ALL':
            self.OnBtnCancel(1)
            cnt = 0
            for suffix in globs.FILE_SUFFIXES.keys():
                cnt += self._selectFiles(suffix)
            msg = '%d requests successfully marked' % (cnt)
            self.updateStatusBar(msg=msg)
            self.fromCb.Enable()
            self.toCb.Enable()
        else:
            # Clear all pending requests
            self.OnBtnCancel(1)
            self.fromCb.Disable()
            self.toCb.Disable()

        event.Skip()

    def OnFromDate(self, event):
        button = event.GetEventObject()

        if button.GetValue():	# Take FROM date into account
            dlg = DateDialog.DateDialog(self, globs.remOldestDate, globs.remNewestDate)
            ret = dlg.ShowModal()
            if ret == wx.ID_OK:
                fd = dlg.dpc.GetDate()
                self.fromDate = '%d/%d/%d' % (fd.month+1,fd.day,fd.year) # month, day, year
            else:
                self.fromDate = globs.remOldestDate
                button.SetValue(False)
            dlg.Destroy()
        else:
            self.fromDate = globs.remOldestDate

        self._dpcSetValue(self.fromDate, self.dpc1, None, self.dpc2)

        myprint('fromDate: %s. Clearing pending list' % self.fromDate)
        self._clearAllRequests()

        if self.fileType != 'ALL':
            myprint('Must schedule a request for available file (%s) matching interval' % self.fileType)
            if globs.viewMode:
                cnt = self._selectFilesByDate(self.fileType)
            else:
                cnt = self._syncFiles(self.fileType)
#            pendingOpsCnt = self.pendingOperationsCount()
#            msg = '%d requests successfully marked, %d in the queue' % (cnt, pendingOpsCnt)
#            self.updateStatusBar(msg=msg)
#            self.panel1.Refresh()
        else:
            myprint('Must schedule a request for any available file matching interval')
            cnt = 0
            for suffix in globs.FILE_SUFFIXES.keys():
                if globs.viewMode:
                    cnt += self._selectFilesByDate(suffix)
                else:
                    cnt += self._syncFiles(suffix)
        pendingOpsCnt = self.pendingOperationsCount()
        msg = '%d requests successfully marked, %d in the queue' % (cnt, pendingOpsCnt)
        self.updateStatusBar(msg=msg)
        self.panel1.Refresh()

        #dumpOperationList("Pending Request List")
        event.Skip()

    def OnToDate(self, event):
        button = event.GetEventObject()

        if button.GetValue():	# Take TO date into account
            dlg = DateDialog.DateDialog(self, globs.remOldestDate, globs.remNewestDate)
            if dlg.ShowModal() == wx.ID_OK:
                td = dlg.dpc.GetDate()
                self.toDate = '%d/%d/%d' % (td.month+1,td.day,td.year)
            else:
                self.toDate = globs.remNewestDate
                button.SetValue(False)
            dlg.Destroy()
        else:
            self.toDate = globs.remNewestDate

        self._dpcSetValue(None, self.dpc1, self.toDate, self.dpc2)

        myprint('Clearing pending list')
        self._clearAllRequests()

        if self.fileType != 'ALL':
            myprint('Must schedule a request for available file (%s) matching interval' % self.fileType)
            if globs.viewMode:
                cnt = self._selectFilesByDate(self.fileType)
            else:
                cnt = self._syncFiles(self.fileType)
            #pendingOpsCnt = self.pendingOperationsCount()
            #msg = '%d requests successfully marked, %d in the queue' % (cnt, pendingOpsCnt)
            #self.updateStatusBar(msg=msg)
            #self.panel1.Refresh()
        else:
            myprint('Must schedule a request for any available file matching interval')
            cnt = 0
            for suffix in globs.FILE_SUFFIXES.keys():
                if globs.viewMode:
                    cnt += self._selectFilesByDate(suffix)
                else:
                    cnt += self._syncFiles(suffix)
        pendingOpsCnt = self.pendingOperationsCount()
        msg = '%d requests successfully marked, %d in the queue' % (cnt, pendingOpsCnt)
        self.updateStatusBar(msg=msg)
        self.panel1.Refresh()

        #dumpOperationList("Pending Request List")
        event.Skip()

    def OnDateChanged(self, event):
        fd = self.dpc1.GetValue()
        td = self.dpc2.GetValue()

        self.fromDate = globs.remOldestDate
        if self.fromCb.GetValue():	# Check if From Date cb is set
            self.fromDate = self._wxdate2pydate(fd)
            print('From Date:',self.fromDate)

        self.toDate = globs.remNewestDate
        if self.toCb.GetValue():	# Check if To Date cb is set
            self.toDate = self._wxdate2pydate(td)
            print('To Date:',self.toDate)

        #print ('Date interval: From: %s To: %s' % (self.fromDate, self.toDate))
        print ('Clearing pending list')
        self._clearAllRequests()

        myprint('Must schedule a request for available files (%s) matching interval' % self.fileType)
        cnt = self._syncFiles(self.fileType)
        pendingOpsCnt = self.pendingOperationsCount()
        msg = '%d requests successfully scheduled, %d in the queue' % (cnt, pendingOpsCnt)
        self.updateStatusBar(msg=msg)
        self.panel1.Refresh()

        if self.fileType == 'ALL':
            myprint('Must schedule a request for available image/video matching interval')
            cnt = 0
            for suffix in globs.FILE_SUFFIXES.keys():
                cnt += self._syncFiles(suffix)
            pendingOpsCnt = self.pendingOperationsCount()
            msg = '%d requests successfully scheduled, %d in the queue' % (cnt, pendingOpsCnt)
            self.updateStatusBar(msg=msg)
            self.panel1.Refresh()

        #dumpOperationList("Pending Request List")
        event.Skip()

    def OnFileSortChoice(self, event):
        idx = self.fileSortChoice.GetSelection()
        if (globs.fileSortRecentFirst and not idx) or (not globs.fileSortRecentFirst and idx):
            myprint('Nothing to do')
        else:
            globs.fileSortRecentFirst = (idx == 0)
        # Simulate a 'Rescan' event
        evt = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self.btnRescan.GetId())
        evt.SetEventObject(self.btnRescan)
        wx.PostEvent(self.btnRescan, evt)
        event.Skip()

    def OnBtnCast(self, event):
        button = event.GetEventObject()

        globs.castMediaCtrl = ChromecastDialog.initPyChromecast()
        if not globs.castMediaCtrl:
            myprint('No Chromecast detected :(')
            button.SetWindowStyleFlag(wx.NO_BORDER)
            self.castDeviceName.SetLabelMarkup("<span foreground='red'><small>%s</small></span>" % '            ')
        else:
            button.SetWindowStyleFlag(wx.BORDER_RAISED)
            self.castDeviceName.SetLabelMarkup("<span foreground='red'><small>%s</small></span>" % globs.castDevice.name)

        button.Refresh()
        event.Skip()

    def OnBtnRew(self, event):
        globs.slideShowNextIdx = 0
        print('Restarting Slideshow from beg.')
        event.Skip()

    def OnBtnPlay(self, event):
        button = event.GetEventObject()

        if not globs.castMediaCtrl:	# Cast device not initialized
            myprint('No Cast Device, Starting Local Slideshow')

        if button.GetName() == 'btnPlay':
            myprint('Slideshow is starting')

            # Build a list of selected files
            self.mediaFileList = list()
            for i in range(len(globs.opList)):
                if globs.opList[i][globs.OP_STATUS] and globs.opList[i][globs.OP_TYPE] == globs.FILE_MARK:
                    fileName = globs.opList[i][globs.OP_FILENAME]
                    self.mediaFileList.append(fileName) # 286
            myprint('%d files selected' % len(self.mediaFileList))

            if not globs.castMediaCtrl:
                msg = 'Starting Local Slideshow'
                self.updateStatusBar(msg=msg)

                button.Disable()
                # If no image is selected, browse thru all the images
                if self.mediaFileList:
                    dlg = MediaViewerDialog.MediaViewerDialog(self, self.mediaFileList, idx=0, slideShow=True)
                else:
                    fileList = [x[0] for x in globs.localFilesSorted]
                    dlg = MediaViewerDialog.MediaViewerDialog(self, fileList, idx=0, slideShow=True)#286                    
                ret = dlg.ShowModal()
                dlg.Destroy()
                # Clear opList
                if globs.viewMode:
                    cnt = 0
                    for suffix in globs.FILE_SUFFIXES.keys():
                        cnt += self._unSelectFiles(suffix)
                    # Re-Select files by type (if specified)
                    # e = wx.PyCommandEvent(wx.EVT_CHOICE.typeId, self.fileTypesChoice.GetId())
                    # e.SetEventObject(self.fileTypesChoice)
                    # wx.PostEvent(self.fileTypesChoice, e)

                    self.fileTypesChoice.SetStringSelection(globs.FILE_TYPES[0]) # None 
                else:
                    cnt = 0
                    for suffix in globs.FILE_SUFFIXES.keys():
                        cnt += self._unSyncFiles(suffix)
                myprint('%d selected files have been cleared' % (cnt))
                self.updateStatusBar(msg='')
                self.Refresh()
                button.Enable()
            else:
                msg = 'Starting Slideshow on %s' % (globs.castDevice.name)
                self.updateStatusBar(msg=msg)

                if not self.mediaFileList:
                    self.mediaFileList = globs.localFilesSorted
                globs.slideShowLastIdx = len(self.mediaFileList)
                self.ssThrLock.release()
                self._displayBitmap(button, 'pause.png', wx.BITMAP_TYPE_PNG)
                button.SetName('btnPause')
                button.SetToolTip('Pause the Slideshow')
        else:
            # Must pause the Slideshow
            msg = 'Pausing the Slideshow'
            self.updateStatusBar(msg=msg)
            self.ssThrLock.acquire()	# Block the thread
            print('Slideshow is paused')
            msg = ''
            self.updateStatusBar(msg=msg)
            self._displayBitmap(button, 'play.png', wx.BITMAP_TYPE_PNG)
            button.SetName('btnPlay')
            button.SetToolTip('Start the Slideshow')
        event.Skip()

    def OnBtnStop(self, event):
        msg = 'Stopping the Slideshow'
        self.updateStatusBar(msg=msg)
        if self.ssThrLock.acquire(blocking=False) == False:	# Block the thread if active
            print('Lock is already set, should have blocked, so... Slideshow is paused')
        print('Slideshow is stopped')
        msg = ''
        self.updateStatusBar(msg=msg)
        self._displayBitmap(self.btnPlay, 'play.png', wx.BITMAP_TYPE_PNG)
        self.btnPlay.SetName('btnPlay')
        self.btnPlay.SetToolTip('Start the Slideshow')
        globs.slideShowNextIdx = 0 # Reset image index
        event.Skip()

    def OnBtnRescan(self, event):
        found = False
        # Is there any pending operation? Warn user if needed
        try:
            op = [x for x in globs.opList if x[globs.OP_STATUS]][0] # Search for busy slot
        except IndexError:
            pass
        else:
            msg = 'Rescanning: All pending request(s) will be lost'
            dlg = wx.MessageDialog(None, msg , 'WARNING', wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
        # Update statusbar configuration (lengths of fields)
        self._initStatusBar1()
        # Update status bar
        msg = 'Rescanning configuration. Please wait...'
        # Disable User input
        self._setMode(globs.MODE_DISABLED, msg)
        wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)
        # Read in new parameters
        self._updateGlobalsFromGUI()
        self.updateStatusBar(field=self.SB_DIR, msg=globs.osvmDownloadDir)
        # Set file sort choice
        self.fileSortChoice.SetStringSelection(self.sortTypes[0] if globs.fileSortRecentFirst else self.sortTypes[1])
        # Reset File type selector
        self.fileTypesChoice.SetStringSelection(globs.FILE_TYPES[0])
        # Create thumbnail image if needed
        createImagesThumbnail()
        # Build Exif data cache file
        exifFilePath = os.path.join(globs.osvmDownloadDir, globs.exifFile)
        if not os.path.exists(exifFilePath):
            myprint('%s does not exist. Creating' % exifFilePath)
            ExifDialog.saveExifDataFromImages(exifFilePath)
        # Load data from file
        self.exifData = ExifDialog.buildDictFromFile(exifFilePath)
        # Check if some images need rotation
        rotateLocalImages(self.exifData)
        # Update file information
        globs.localFilesCnt,globs.availRemoteFilesCnt = updateFileDicts()
        globs.slideShowLastIdx = globs.localFilesCnt
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
        msg = '%d local files' % (globs.localFilesCnt)
        if globs.cameraConnected:
            msg += ', %d remote files(s)' % (globs.availRemoteFilesCnt)
        else:
            self._setOfflineMode()
            if not globs.viewMode:
                msg += ', No remote file detected'

        if globs.viewMode:
            lbl = ' Available Local Files: %d.  Page:' % globs.localFilesCnt
            self.staticBox3.SetLabel(lbl)
            self._updateStaticBox3Label('OnBtnRescan')
            self.staticBox4.SetLabel(' File Viewer Control ')
            self.statusBar1.SetStatusText('View Mode', self.SB_MODE)
        else:
            self.staticBox3.SetLabel(' Available Remote Files (on camera) Page:')
            self._updateStaticBox3Label('OnBtnRescan')
            self.staticBox4.SetLabel(' Select Files to Sync... ')
            self.statusBar1.SetStatusText('Sync Mode', self.SB_MODE)

        # Update list of files on the GUI
        self._updateThumbnailPanel()

        self._setMode(globs.MODE_ENABLED, msg)
#        event.Skip()

    def _unSyncFiles(self, fileType=''): # Clear all requests associated to a given file type (JPG, MOV)
        myprint('Must clear all requests for %s. Suffixes: %s' % (fileType,globs.FILE_SUFFIXES[fileType]))
        i = 0
        for op in globs.opList:
            if op[globs.OP_STATUS] and op[globs.OP_FILETYPE] in globs.FILE_SUFFIXES[fileType]:
                i += 1
                self.resetOneButton(op[globs.OP_FILENAME])
                self.resetOneRequest(op)
        return i

    def _syncFiles(self, fileType=''):	# fileType could be : JPG, MOV
        myprint('Syncing %s files. Suffixes: %s' % (fileType, globs.FILE_SUFFIXES[fileType]))
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
            if not remFileName.split('.')[1] in globs.FILE_SUFFIXES[fileType]:
                continue

            # Check if already available locally
            if remFileName in globs.localFileInfos.keys():
                continue

            rf = globs.availRemoteFiles[remFileName]
            remFileDateInSecs = rf[globs.F_DATEINSECS]
            remFileDate = rf[globs.F_DATE]
            remFileSize = rf[globs.F_SIZE]

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

            e = [button, remFileName, globs.FILE_DOWNLOAD, remFileSize, remFileDate]
            # Loop thru opList[] looking for a free slot, schedule an operation
            for op in globs.opList:
                if op[globs.OP_STATUS] == 0:
                    self._scheduleOperation(op, e)
                    i += 1
                    break
            else:
                msg = 'Max requests reached (%d).' % (globs.MAX_OPERATIONS)
                print (msg)
                self.updateStatusBar(msg=msg, fgcolor=wx.WHITE, bgcolor=wx.RED)
                # Clear all pending requests
                self.OnBtnCancel(1)
                return 0
        return i

    def _unSelectFiles(self, fileType=''): # Clear all requests for a given file type (JPG, MOV)
        myprint('Must clear all requests for %s. Suffixes: %s' % (fileType, globs.FILE_SUFFIXES[fileType]))
        i = 0
        for op in globs.opList:
            if op[globs.OP_STATUS] and op[globs.OP_FILETYPE] in globs.FILE_SUFFIXES[fileType]:
                i += 1
                self.resetOneButton(op[globs.OP_FILENAME])
                self.resetOneRequest(op)
        return i

    def _selectFilesByDate(self, fileType=''):	# fileType could be : JPG, MOV
        myprint('Selecting %s files. Suffixes: %s' % (fileType, globs.FILE_SUFFIXES[fileType]))
        i = 0
        # Browse the list of buttons and schedule a request if file matches fileType and date (if requested)
        if self.fromCb.GetValue():	# Check if From date cb is set
            m = int(self.fromDate.split('/')[0])
            d = int(self.fromDate.split('/')[1])
            y = int(self.fromDate.split('/')[2])
            tf1 = datetime.datetime(y,m,d, 0, 0)    # year, month, day
            tf2 = time.mktime(tf1.timetuple())
        else:
            tf2 = globs.remOldestDate

        if self.toCb.GetValue():	# Check if To date cb is set
            m = int(self.toDate.split('/')[0])
            d = int(self.toDate.split('/')[1])
            y = int(self.toDate.split('/')[2])
            tt1 = datetime.datetime(y,m,d, 23, 59)    # year, month, day
            tt2 = time.mktime(tt1.timetuple())
        else:
            tt2 = globs.remNewestDate

        # Each entry in thumbButtons[] is: [widget, filename, fgcol, bgcol]
        for button in self.thumbButtons:
            fileName = button[1]
            fileDate = globs.localFileInfos[fileName][globs.F_DATE]

            if not fileName.split('.')[1] in globs.FILE_SUFFIXES[fileType]:
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

            e = [button, fileName, globs.FILE_MARK, -1, fileDate]
            try:
                op = [x for x in globs.opList if not x[globs.OP_STATUS]][0] # First free slot
                self._scheduleOperation(op, e)
                i += 1
            except:
                msg = 'Maximum selection (%d) reached' % globs.MAX_OPERATIONS
                self.updateStatusBar(msg=msg, fgcolor=wx.WHITE, bgcolor=wx.RED)
                myprint(msg)
                break
        return i

    def selectFilesByPosition(self, fileType='', position=0):	# fileType could be : JPG, MOV
        myprint('Selecting %s files, position=%d. Suffixes: %s' % (fileType, position, globs.FILE_SUFFIXES[fileType]))
        # Loop thru opList[]: Clear all slots marked as MARK
        for op in globs.opList:
            if op[globs.OP_STATUS] and op[globs.OP_TYPE] == globs.FILE_MARK:
                fileName = op[globs.OP_FILENAME]
                self.resetOneButton(fileName)
                self.resetOneRequest(op)

        i = 0
        # DP Must use a filtered list !!!!!!!!!
        for f in globs.localFilesSorted[position:]:
            #print(f)
            fileName = f[1][globs.F_NAME]
            if not fileName.split('.')[1] in globs.FILE_SUFFIXES[fileType]:
                continue
            fileDate = f[1][globs.F_DATEINSECS]
            button = [x[0] for x in self.thumbButtons if x[1] == fileName]
            e = [button, fileName, globs.FILE_MARK, -1, fileDate]
            try:
                op = [x for x in globs.opList if not x[globs.OP_STATUS]][0] # First free slot
            except:
                msg = 'Maximum selection (%d) reached' % globs.MAX_OPERATIONS
                self.updateStatusBar(msg=msg, fgcolor=wx.WHITE, bgcolor=wx.RED)
                break
            self._scheduleOperation(op, e)
            i += 1
        return i

    def OnBtnShare(self, event):
        shareList = list()

        #dumpOperationList("Global Operation List")
        
        for op in globs.opList:
            if op[globs.OP_STATUS]:
                filePath = op[globs.OP_FILEPATH]
                shareList.append(filePath)

        myprint('Sharing files', shareList)
        
        mailDlg = MailDialog.MailDialog(self, attachmentlist=shareList)
        mailDlg.ShowModal()
        mailDlg.Destroy()
        # Clear all marked files
        cnt = 0
        for suffix in globs.FILE_SUFFIXES.keys():
            cnt += self._unSelectFiles(suffix)
        self.updateStatusBar(msg='')
        # Clear action buttons
        self._disableActionButtons()
        self.Refresh()
        event.Skip()

    def OnBtnDelete(self, event):
        #if globs.askBeforeCommit:
        msg = 'Do you really want to DELETE marked files(s) ?'
        dial = wx.MessageDialog(None, msg, 'Delete Files',
                                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        ret = dial.ShowModal()
        if ret == wx.ID_NO:
            # Allow user action
            msg = ''
            self._setMode(globs.MODE_ENABLED, msg)
            event.Skip()
            return

        needRefresh = False
        for op in globs.opList:
            if op[globs.OP_STATUS]:
                filePath = op[globs.OP_FILEPATH]
                try:
                    os.remove(filePath)
                except OSError as error:
                    myprint('Failed to delete %s: %s' % (filePath,error))
                else:
                    myprint('%s successfully deleted' % filePath)
                    needRefresh = True
        if needRefresh:
            globs.localFilesCnt = localFilesInfo(globs.osvmDownloadDir)
            myprint('%d local files on this host' % globs.localFilesCnt)

            # Update list of files on the GUI
            self._updateThumbnailPanel()
        self._disableActionButtons()
        event.Skip()
        
    def OnBtnDownload(self, event):
        pendingOpsCnt = self.pendingOperationsCount()
        if pendingOpsCnt == 0:
            return

        # Prevent user action
        msg = 'Processing pending operations...'
        self._setMode(globs.MODE_DISABLED, msg)

        if globs.askBeforeCommit:
            msg = 'Do you really want to proceed with pending request(s) ?'
            dial = wx.MessageDialog(None, msg, 'Download Files',
                                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            ret = dial.ShowModal()
            if ret == wx.ID_NO:
                # Allow user action
                msg = ''
                self._setMode(globs.MODE_ENABLED, msg)
                return

        # Local directory where download should happen
        localDir = globs.osvmDownloadDir

        (ret1, ret2) = self._checkLocalDir(localDir)
        if ret1 == -1:
            print('ERROR:', ret2)
            msg = '%s.\n\nPlease check your settings.' % (ret2)
            dlg = wx.MessageDialog(None, msg , 'Error', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            # Allow user action
            msg = ''
            self._setMode(globs.MODE_ENABLED, msg)
            return
        self.downloadDir = localDir

        # Create a timer for animation...
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnStatusBar1Update, self.timer)
        self.timerCnt = 0
        self.timer.Start(globs.TIMER3_FREQ)

        self.installDlg = InstallDialog.InstallDialog(self, download=self.downloadDir, title='Downloading Files')
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
        globs.localFilesCnt = localFilesInfo(globs.osvmDownloadDir)
        myprint('%d local files on this host' % globs.localFilesCnt)

        # Update list of files on the GUI
        self._updateThumbnailPanel()
        wx.EndBusyCursor()

        # Allow user action
        msg = '%d local files, %d files available on camera' % (globs.localFilesCnt, globs.availRemoteFilesCnt)
        self._setMode(globs.MODE_ENABLED, msg)
        event.Skip()

    def OnBtnCancel(self, event):
        # pendingOpsCnt = self.pendingOperationsCount()
        # if pendingOpsCnt == 0:
        #     return

        # Prevent user action
        msg = 'Cancelling pending requests...'
        self._setMode(globs.MODE_DISABLED, msg)

        if globs.askBeforeCommit:        
#        if event != 1:
            msg = 'Do you really want to Cancel all pending request(s) ?'
            dial = wx.MessageDialog(None, msg, 'Cancel Operations',
                                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            ret = dial.ShowModal()
            if ret == wx.ID_NO:
                return

        # Loop thru opList[]: Clear all busy slots
        self._clearAllRequests()            

        # Reset file choices if a 'real Cancel' request only
        if event != 1:
            self.fileTypesChoice.SetStringSelection(globs.FILE_TYPES[0]) # None

        # Prevent user action
        msg = 'All requests have been cancelled'
        self._setMode(globs.MODE_ENABLED, msg)

        # Reset file selection check boxes
        for cb in [self.fromCb,self.toCb]:
            cb.SetValue(False)

        self._disableActionButtons()

    def OnStatusBar1Update(self, event):
        if 0:
            with Timer() as t:
                self.updateStatusBar1()
            print('Request took %.03f sec.' % t.interval)
        else:
            self.updateStatusBar1()

    def updateStatusBar1(self):
        text = 'Processing pending requests...'
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
        self.updateStatusBar(msg=''.join(self.display))

    def _updateConnectionStatus(self):
        if globs.cameraConnected or globs.viewMode:
            self._displayBitmap(self.staticBitmap2, "traffic-light-green-65-nobg.png", wx.BITMAP_TYPE_PNG)
        else:
            self._displayBitmap(self.staticBitmap2, "traffic-light-red-65-nobg.png", wx.BITMAP_TYPE_PNG)

# Arguments parser
def parse_argv():
    desc = 'Graphical UI to manage files (pictures, video) on a OLYMPUS camera over WIFI''Provides a Remote File viewer over GoogleCast'

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("-c", "--compact",
                        action="store_true", dest="compactmode", default=False,
                        help="Use Compact Layout")
    parser.add_argument("-d", "--debug",
                        action="store_true", dest="debug", default=False,
                        help="print debug messages (to stdout)")
    parser.add_argument('-f', '--file',
                        dest='logfile',
                        const=globs.logFile,
                        default=None,
                        action='store',
                        nargs='?',
                        metavar = 'FILE',
                        help="write debug messages to FILE (default to %s)" % (globs.logFile))
    parser.add_argument("-i", "--info",
                        action="store_true", dest="version", default=False,
                        help="print version and exit")
    parser.add_argument("-l", "--logwin",
                        action="store_true", dest="logwin", default=False,
                        help="Open Log Window at startup")
    parser.add_argument("-n", "--nopanel",
                        action="store_true", dest="nopanel", default=False,
                        help="Skip loading of thumbnail panels (faster startup)")
    parser.add_argument('-p', '--path',
                        dest='imagedir',
                        help="use directory (default to %s)" % (globs.osvmDownloadDir))
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--view", action="store_true", dest="viewmode", default=False,
                       help="Enter View/Cast Mode")
    group.add_argument("-s", "--sync", action="store_true", dest="syncmode", default=False,
                       help="Enter Synchronization Mode")
    args = parser.parse_args()
    return args

def printToolsVersion():
    if globs.system == 'Windows':
        # Get win32api version
        fixed_file_info = win32api.GetFileVersionInfo(win32api.__file__, '\\')
        pywin32Version = fixed_file_info['FileVersionLS'] >> 16
        label = 'Platform: %s\nPython: %s\nWxPython: %s pywin32: %s' % ((platform.platform()), globs.pythonVersion, wx.version(), pywin32Version)
    else:
        label = 'Platform: %s\nPython: %s\nWxPython: %s' % ((platform.platform()),  globs.pythonVersion, wx.version())
    print(label)

def main():
    args = parse_argv()    

    osvmdirpath = os.path.join(os.path.join(expanduser("~"), globs.osvmDir))
    if os.path.exists(osvmdirpath):
        if not os.path.isdir(osvmdirpath):
            print("%s must be a directory. Exit!" % (osvmdirpath))
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
        print('Creating:', globs.tmpDir)
        try:
            os.mkdir(globs.tmpDir)
        except OSError as e:
            msg = "Cannot create %s: %s" % (globs.tmpDir, "{0}".format(e.strerror))
            print(msg)
            exit()

    globs.modPath         = module_path(main)
    globs.imgDir          = os.path.join(os.path.dirname(globs.modPath), 'images')
    globs.initFilePath    = os.path.join(osvmdirpath, globs.initFile)
    globs.logFilePath     = None
    globs.helpPath        = os.path.join(os.path.dirname(globs.modPath), 'help.htm')

    globs.htmlRootFile = os.path.join(osvmdirpath, globs.htmlRootFile)
    globs.htmlDirFile  = os.path.join(osvmdirpath, globs.htmlDirFile)

    # Get python executable size (32 or 64)
    globs.pythonBits = (8 * struct.calcsize("P"))

    # Get SVN Revision through svn:keywords
#    rev = "$Revision: 1 $" # DONT TOUCH THIS LINE!!!
#    globs.myVersion = "%s.%s" % (globs.myVersion, rev[rev.find(' ')+1:rev.rfind(' ')])

    if args.imagedir:
        myprint('Using Image Directory: %s' % args.imagedir)
        globs.imagePathCmdLineArg = args.imagedir

    if args.version:
        print('%s: Version: %s' % (globs.myName, globs.myVersion))
        printToolsVersion()
        print('PyChromeCast:',module_path(pychromecast))
        print('Vlc:',module_path(vlc))
        if globs.networkSelector:
            print('Objc:',module_path(objc))
        sys.exit(0)

    if args.viewmode:
        myprint('Auto Entering View/Cast Mode')
        globs.autoViewMode = True
    elif args.syncmode:
        myprint('Auto Entering Sync Mode')
        globs.autoSyncMode = True

    if args.compactmode:
        myprint('Using Compact Mode')
        globs.compactMode = True

    globs.logWin = args.logwin
        
    if args.nopanel:
        myprint('Skipping Panel load (faster startup)')
        globs.noPanel = True
        
    if args.debug == False:     # no debug
        app = wx.App(0)
        actualstdout = sys.stdout
        sys.stdout = io.StringIO()
    else:                       # debug
        if args.logfile == None:    # no output file, use stdio
            app = wx.App(redirect=False)
        else:             # use default/specified output file
            if not os.path.isabs(args.logfile):
                globs.logFilePath = os.path.join(osvmdirpath, args.logfile)
            else:
                globs.logFilePath = args.logfile
            # Remove existing log file
            if os.path.isfile(globs.logFilePath): 
                os.remove(globs.logFilePath)
            # Set redirect to True to log to the logfile
            app = wx.App(redirect=True, filename=globs.logFilePath)

    print('%s: Version: %s. Running at: %s' % (globs.myName, globs.myVersion, time.strftime('%m/%d/%y %H:%M:%S', time.localtime())))
    print('System:', globs.system )
    printToolsVersion()
    print('Host Archictecture:', globs.hostarch)
    print('Path:', globs.modPath)
    print('Image Dir:', globs.imgDir)
    print('Help Path:', globs.helpPath)
    print('Init File:', globs.initFilePath)
    if args.logfile:
        print('Log File: %s' %  (globs.logFilePath))
    print('Python Executable: %dbits' % (globs.pythonBits))
                                    
    # adds more named colours to wx.TheColourDatabase
    wb.updateColourDB()  
    wx.ORANGE = wx.Colour("orange")
    wx.GREY = wx.Colour("lightgrey")
    wx.STEELBLUE = wx.Colour(30, 100, 180)
    # Update package button colors
    globs.DEFAULT_FILE_COLORS = [(wx.GREY,wx.WHITE),(wx.GREEN,wx.WHITE),(wx.ORANGE,wx.WHITE)]
    globs.fileColors = [[wx.GREY,wx.WHITE],[wx.GREEN,wx.WHITE],[wx.ORANGE,wx.WHITE]]

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
            myprint('No Network Interface')

    frame = OSVMConfig(None, -1, globs.myLongName)
    frame.Show(True)

    #wx.lib.inspection.InspectionTool().Show()
    
#    app.SetTopWindow(frame)
    app.MainLoop()
    myprint('End of MainLoop')
    # Should never happen
    #print ("Application has been killed !")

    # Some cleanup
    cleanup()

if __name__ == "__main__":
    main()
