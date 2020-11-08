#!/usr/bin/env python
import wx
import wx.grid
import wx.html
import wx.lib.colourdb as wb
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin, ColumnSorterMixin, ListRowHighlighter

import sys
import os
import builtins as __builtin__
import inspect
import time
import csv

from wx.lib.newevent import NewEvent

# Custom events generated when an item is selected/deselected
itemChecked, EVT_LIST_ITEM_CHECKED = NewEvent()
itemUnChecked, EVT_LIST_ITEM_UNCHECKED = NewEvent()
fileListFrameCustomEvent, EVT_FLF_CUSTOM = NewEvent()

FLF_ITEMS = [FLF_CHECKBOX,
             FLF_TYPE,
             FLF_IDX,
             FLF_FILENAME,
             FLF_SIZEINMB,
             FLF_DATE,
             FLF_TIME,
             FLF_SIZERAW,
             FLF_DATERAW,
             FLF_SIZETOTAL,
             FLF_MARKED] = [i for i in range(11)]

moduleList = {'osvmGlobals':'globs',
              'InstallDialog':'InstallDialog'}

for k,v in moduleList.items():
    print('Loading: %s as %s' % (k,v))
    mod = __import__(k, fromlist=[None])
    globals()[v] = globals().pop('mod')	# Rename module in globals()

####
#print(__name__)

def buildFileListAndDict(fList, sortField, sortDir):
    myprint('Sorting criteria: Field: %d. Direction: %s' % (sortField, sortDir))
    if sortField != globs.F_NAME:
        fileList = sorted(fList, key=lambda x: int(x[1][sortField]), reverse=sortDir)
    else:
        fileList = sorted(fList, key=lambda x: x[0], reverse=sortDir)

    d = dict()
    l = list()

    idx= 0
    totalSize = 0
    for v in fileList:
        d1 = secondsTodby(v[1][globs.F_DATEINSECS])
        t1 = secondsTohms(v[1][globs.F_DATEINSECS])

        totalSize += v[1][globs.F_SIZE]

        d[v[1][globs.F_NAME]] = ('',				# FLF_CHECKBOX
                                 '',				# FLF_TYPE
                                 str(idx),			# FLF_IDX
                                 v[1][globs.F_NAME],		# FLF_FILENAME
                                 humanBytes(v[1][globs.F_SIZE]),# FLF_SIZEINMB
                                 d1,				# FLF_DATE
                                 t1,				# FLF_TIME
                                 v[1][globs.F_SIZE],		# FLF_SIZERAW
                                 v[1][globs.F_DATEINSECS],	# FLF_DATERAW
                                 humanBytes(totalSize),		# FLF_SIZETOTAL
                                 0)				# FLF_MARKED

        l.append(('',
                  '',
                  idx,
                  v[1][globs.F_NAME],
                  humanBytes(v[1][globs.F_SIZE]),
                  d1,
                  t1,
                  v[1][globs.F_SIZE],
                  v[1][globs.F_DATEINSECS],
                  humanBytes(totalSize),
                  0))
        idx += 1
    #print(d,l)
    return(d,l)

def buildDiff2Dict():
    # Build a list of local files. Format:(filename, size)
    localFilesList = [(x[1][0],x[1][1]) for x in list(globs.localFileInfos.items())]
    # Build a list of remote files. Format:(filename, size)
    remoteFilesList = [(x[1][0],x[1][1]) for x in globs.availRemoteFiles.items()]
    # Get missing files list
    tmp = listDiff2(remoteFilesList, localFilesList)
    # Build a dictionary from list above
    dictDiff = dict()
    for e in tmp:
        dictDiff[e[0]] = globs.availRemoteFiles[e[0]]
    return dictDiff

def buildDiff3Dict():
    # Build a list of local files. Format:(filename, size)
    localFilesList = [(x[1][0],x[1][1]) for x in list(globs.localFileInfos.items())]
    # Build a list of remote files. Format:(filename, size)
    remoteFilesList = [(x[1][0],x[1][1]) for x in globs.availRemoteFiles.items()]
    # Get common files list
    tmp = listDiff3(remoteFilesList, localFilesList)
    # Build a dictionary from list above
    dictDiff = dict()
    for e in tmp:
        dictDiff[e[0]] = globs.availRemoteFiles[e[0]]
    return dictDiff

# A valid operation slot has been found. Schedule the operation
def _scheduleOperation(op, e):
    fileName  = e[0]
    fileSize  = e[1]
    fileDate  = e[2]
    operation = e[3]

    op[globs.OP_STATUS]   = 1          			# Busy
    op[globs.OP_FILENAME] = fileName
    op[globs.OP_FILETYPE] = fileName.split('.')[1]	# File suffix
    op[globs.OP_TYPE]     = operation
    nBlocks = fileSize / globs.URLLIB_READ_BLKSIZE
    op[globs.OP_SIZE]     = (fileSize, nBlocks)
    op[globs.OP_FILEDATE] = fileDate
    op[globs.OP_FILEPATH] = os.path.join(globs.osvmDownloadDir, fileName)
    #myprint(op)

# Clear/Reset an operation
def _clearAllOperations():
    globs.opList = [[0] * globs.OP_LASTIDX for i in range(globs.MAX_OPERATIONS)]
    
class FileListFrameEventTracker(wx.EvtHandler):

    def __init__(self, processingCodeFunctionHandle):
        wx.EvtHandler.__init__(self)
        self.processingCodeFunctionHandle = processingCodeFunctionHandle
        self.Bind(EVT_FLF_CUSTOM, self.FLFEventHandler)
        
    def FLFEventHandler(self, event):
        myprint(event.resultOfFrame)
        self.processingCodeFunctionHandle(event.resultOfFrame)
        event.Skip()

class MyListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):

    def __init__(self, parent, hdrLabels, dataDict):

        wx.ListCtrl.__init__( self, parent, wx.ID_ANY, style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_HRULES|wx.LC_VRULES)
        ListCtrlAutoWidthMixin.__init__(self)

        self.parent = parent

        self.EnableAlternateRowColours(enable=True)
        self.EnableCheckBoxes(enable=True)
        
        # Adding some attributes (colourful background for each item rows)
        self.attrs = dict()
        attr0 = wx.ItemAttr()
        attr0.SetBackgroundColour("white")
        self.attrs[0] = attr0

        attr1 = wx.ItemAttr()
        attr1.SetBackgroundColour("light blue")
        self.attrs[1] = attr1

        # Add images
        self.il = wx.ImageList(16, 16)
        self.idx0 = self.il.Add(wx.Bitmap(os.path.join(globs.imgDir,'blue_camera.png')))
        self.idx1 = self.il.Add(wx.Bitmap(os.path.join(globs.imgDir,'video.png')))
        #self.idx2 = self.il.Add(self.makeBlank())
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        # Building the columns. Each entry is: (Column Name, Column Width)
        idx = 0
        for c in hdrLabels:
            self.InsertColumn(idx, c[0])
            self.SetColumnWidth(idx, c[1])
            idx += 1

        self.UpdateDataMap(dataDict)
        
        # Events
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._OnItemActivated)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._OnItemDeselected)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._OnItemSelected)
        self.Bind(wx.EVT_LIST_ITEM_CHECKED, self._OnItemChecked)
        self.Bind(wx.EVT_LIST_ITEM_UNCHECKED, self._OnItemChecked)
        #self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColumnClick)

    def makeBlank(self):
        empty = wx.Bitmap(16,16,32)
        dc = wx.MemoryDC(empty)
        dc.SetBackground(wx.Brush((0,0,0,0)))
        dc.Clear()
        del dc
        empty.SetMaskColour((0,0,0))
        return empty
    
    def UpdateDataMap(self, dataDict):
        self.itemDataMap = dataDict
        self.itemIndexMap = dataDict.keys()
        self.SetItemCount(len(dataDict))
        
    # These methods are callbacks for implementing the
    # "virtualness" of the list...
    def OnGetItemText(self, item, col):
        k = list(self.itemIndexMap)[item]
        s = self.itemDataMap[k][col]
        return str(s)

    def OnGetItemImage(self, item):
        k = list(self.itemIndexMap)[item]
        suffix = k.split('.')[1].lower()
        if suffix == 'jpg':
            return self.idx0
        else:
            return self.idx1
        #return -1

    def OnGetItemColumnImage(self, item, column):
        if column != 1:
            return -1
        k = list(self.itemIndexMap)[item]
        suffix = k.split('.')[1].lower()
        if suffix == 'jpg':
            return self.idx0
        else:
            return self.idx1

        
    def OnGetItemIsChecked(self, item):
        k = list(self.itemIndexMap)[item]
        v = self.itemDataMap[k][FLF_ITEMS[FLF_MARKED]]		# Get mark
        #myprint(item,k,v)
        return(v)
    
    def OnGetItemAttr(self, item):
        k = list(self.itemIndexMap)[item]
        idx = int(self.itemDataMap[k][FLF_ITEMS[FLF_IDX]])	# Line index
        #myprint(k,idx)
        return self.attrs[idx%2]
    
    def GetListCtrl(self):
        return self

    # def OnCheckItem(self, idx, flag):
    #     myprint(idx,flag)
    #     if flag: # item checked
    #         evt = itemChecked()
    #     else:
    #         evt = itemUnChecked()
    #     wx.PostEvent(self, evt)
        
    # def OnColumnClick(self,event):
    #     print('OnColumnClick')
    #     self.RefreshRows()
    #     event.Skip()

    def _OnItemChecked(self, event):
        index = event.Index
        fname = self._getColumnText(index, FLF_ITEMS[FLF_FILENAME])
        # Convert tuple to list to update mark
        l = list(self.itemDataMap[fname])
        l[FLF_ITEMS[FLF_MARKED]] = not(l[FLF_ITEMS[FLF_MARKED]])		# Update Mark
        # Convert back to tuple
        self.itemDataMap[fname] = tuple(l)
        #myprint(index,fname,self.itemDataMap[fname])

        # Notify parent
        if l[FLF_ITEMS[FLF_MARKED]]:
            evt = itemChecked()
        else:
            evt = itemUnChecked()
        wx.PostEvent(self, evt)
        event.Skip()

    def _getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()
        
    def _OnItemSelected(self, event):
        self.currentItem = event.Index
        myprint('%d, %s, %s, %s, %s, %s' %
                (self.currentItem,
                 self.GetItemText(self.currentItem),		# Mark
                 self._getColumnText(self.currentItem, 1),	# Idx
                 self._getColumnText(self.currentItem, 2),	# Name
                 self._getColumnText(self.currentItem, 3),	# Size
                 self._getColumnText(self.currentItem, 4)))	# Date
        event.Skip()
        
    def _OnItemDeselected(self, event):
        myprint('')
        event.Skip()
        
    def _OnItemActivated(self, event):
        self.currentItem = event.Index
        myprint(self.currentItem)
        event.Skip()

    def MarkItem(self, index, state):
        fname = self._getColumnText(index, FLF_ITEMS[FLF_FILENAME])
        # Convert tuple to list to update mark
        l = list(self.itemDataMap[fname])
        l[FLF_ITEMS[FLF_MARKED]] = state		# Update Mark
        # Convert back to tuple
        self.itemDataMap[fname] = tuple(l)
        #myprint(index,fname,self.itemDataMap[fname])

    def IsMarked(self, fname):
        v = self.itemDataMap[fname][FLF_ITEMS[FLF_MARKED]]		# Get mark
        #myprint(fname,v)
        return(v)

        
class FileListFrame(wx.Frame):
    """
    Creates and displays a window to list files
    """
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent=parent, title=title)
        self.parent = parent
        self.blocksToTransfer = 0
        self.blocksTransfered = 0
        
        self.Bind(wx.EVT_CLOSE, self._OnClose)
        
        self.HDR_IDX = [self.HDR_CHECKBOX,
                        self.HDR_FILETYPE,
                        self.HDR_FILEIDX,
                        self.HDR_FILENAME,
                        self.HDR_FILESIZE,
                        self.HDR_FILEDATE,
                        self.HDR_FILETIME] = [i for i in range(7)]

        # Each column header entry of type: (label,width)
        self.HDR_LABELS = [('MARK', 40),
                           ('TYPE', 40),
                           ('IDX',  60),
                           ('FILENAME', 180),
                           ('SIZE', 100),
                           ('DATE', 100),
                           ('TIME', 100)]

        # Headers used when saving in CSV file
        self.CSV_COL_HDRS = ["Checkbox",
                             "Type",
                             "Index",
                             "Filename",
                             "Size",
                             "Raw Size",
                             "Date",
                             "Raw Date",
                             "Time",
                             "Total Size",
                             "Marked"]
        
        [self.FT_REMOTE,
         self.FT_LOCAL,
         self.FT_NOTSYNCED,
         self.FT_SYNCED,
         self.FT_MARKED] = [i for i in range(5)]
        
        self.FILE_TYPES = [('Remote Files Not Synced', self.FT_NOTSYNCED),
                           ('Files Synced', self.FT_SYNCED),
                           ('Local Files', self.FT_LOCAL),
                           ('Remote Files', self.FT_REMOTE),
                           ('Marked Files', self.FT_MARKED)]
        
        self.FILE_SORT_FIELD = [('Filename', globs.F_NAME),
                                ('Date',     globs.F_DATEINSECS),
                                ('Size',     globs.F_SIZE)]
        
        self.FILE_SORT_ORDER = ['Ascending',
                                'Descending']

        [self.MARK_NONE,
         self.MARK_JPG,
         self.MARK_MOV,
         self.MARK_ALL] = [i for i in range(4)]
        
        self.FILE_MARKER_CHOICE = ['Clear Marks',
                                   'Mark JPG',
                                   'Mark MOV',
                                   'Mark All']
                                   
        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self,
                               size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        # Build a list of not synced files
        dictDiff = buildDiff2Dict()
        self.fileDict, self.fileList = buildFileListAndDict(list(dictDiff.items()), globs.F_DATEINSECS, False)

        # Box Sizer to contain all buttons
        self.btnBS = wx.BoxSizer(orient=wx.HORIZONTAL)

        # File Selector to select the list of files to show: All files/Missing remote files
        self.sb1 = wx.StaticBox(label='Files to list...', parent=self.panel1, style=0)
        self.fileTypesBS = wx.StaticBoxSizer(box=self.sb1, orient=wx.HORIZONTAL)

        self.fileTypesChoice = wx.Choice(choices=[v[0] for v in self.FILE_TYPES],
                                         parent=self.panel1, style=0)
        self.fileTypesChoice.SetToolTip('Select type of files to show')
        self.fileTypesChoice.SetStringSelection(self.FILE_TYPES[0][0])
        self.fileTypesChoice.Bind(wx.EVT_CHOICE, lambda evt: self._OnParamsSelector(evt))
        self.fileTypesBS.Add(self.fileTypesChoice, 0, border=0, flag=wx.EXPAND)
        
        # Sorting Selector
        self.sb2 = wx.StaticBox(label='Sorting Parameters...', parent=self.panel1, style=0)
        self.sortBS = wx.StaticBoxSizer(box=self.sb2, orient=wx.VERTICAL)

        self.sortFieldChoice = wx.Choice(choices=[v[0] for v in self.FILE_SORT_FIELD],
                                         parent=self.panel1, style=0)
        self.sortFieldChoice.SetToolTip('Select sort field')
        self.sortFieldChoice.SetStringSelection(self.FILE_SORT_FIELD[1][0]) # By Date
        self.sortFieldChoice.Bind(wx.EVT_CHOICE, lambda evt: self._OnParamsSelector(evt))
        self.sortBS.Add(self.sortFieldChoice, 0, border=0, flag=wx.EXPAND)

        self.sortBS.Add(0, 8, 0, border=0, flag=wx.EXPAND)

        # Sorting Order Selector
        self.sortOrderChoice = wx.Choice(choices=[v for v in self.FILE_SORT_ORDER],
                                         parent=self.panel1, style=0)
        self.sortOrderChoice.SetToolTip('Select sort order')
        self.sortOrderChoice.SetStringSelection(self.FILE_SORT_ORDER[0])
        self.sortOrderChoice.Bind(wx.EVT_CHOICE, lambda evt: self._OnParamsSelector(evt))
        self.sortBS.Add(self.sortOrderChoice, 0, border=0, flag=wx.EXPAND)

        # Markers buttons
        self.sb3 = wx.StaticBox(label='Sync Parameters...', parent=self.panel1, style=0)
        self.markerBS = wx.StaticBoxSizer(box=self.sb3, orient=wx.VERTICAL)

        self.markerChoice = wx.Choice(choices=[v for v in self.FILE_MARKER_CHOICE],
                                      parent=self.panel1, style=0)
        self.markerChoice.SetToolTip('Select files to mark')
        self.markerChoice.SetStringSelection(self.FILE_MARKER_CHOICE[0])
        self.markerChoice.Bind(wx.EVT_CHOICE, lambda evt: self._OnParamsSelector(evt))
        self.markerBS.Add(self.markerChoice, 0, border=0, flag=wx.EXPAND)

        self.markerBS.Add(0, 8, border=0, flag=wx.EXPAND)
        
        self.btnDownload = wx.Button(label='Download...', parent=self.panel1, style=0)
        self.btnDownload.Bind(wx.EVT_BUTTON, self._OnBtnDownload)
        self.btnDownload.Enable(False)
        self.markerBS.Add(self.btnDownload, 0, border=0, flag=wx.EXPAND)
        
        # Button to save the list
        self.sb4 = wx.StaticBox(label='...', parent=self.panel1, style=0)
        self.rightBS = wx.StaticBoxSizer(box=self.sb4, orient=wx.VERTICAL)

        self.btnSave = wx.Button(label='Save List', parent=self.panel1, style=0)
        self.btnSave.Bind(wx.EVT_BUTTON, self._OnBtnSave)
        self.rightBS.Add(self.btnSave, 0, border=0, flag=wx.EXPAND)

        self.rightBS.Add(0, 8, 0, border=0, flag=wx.EXPAND)
        
        # Button to close the frame
        self.btnClose = wx.Button(label='Close', id=wx.ID_CLOSE, parent=self.panel1, style=0)
        self.btnClose.Bind(wx.EVT_BUTTON, self._OnBtnClose)
        self.rightBS.Add(self.btnClose, 0, border=0, flag=wx.EXPAND)

        # Add all button boxes to btnBS
        self.btnBS.Add(self.fileTypesBS, 0, border=0, flag=wx.EXPAND)
        self.btnBS.Add(self.sortBS, 0, border=0, flag=wx.EXPAND)
        self.btnBS.Add(self.markerBS, 0, border=0, flag=wx.EXPAND)
        self.btnBS.Add(8, 0, 0, border=0, flag=wx.EXPAND)
        self.btnBS.Add(self.rightBS, 0, border=0, flag=wx.EXPAND)
        
        # Buttons boxsizer in the topBoxSizer
        self.topBS = wx.BoxSizer(orient=wx.VERTICAL)
        self.topBS.Add(self.btnBS, 0, border=5, flag=wx.EXPAND|wx.ALL)
        self.topBS.Add(0, 4, 0, border=0, flag=0)

        # ListCtrl to contain file list
        self.fileListCtrl = MyListCtrl(self.panel1, self.HDR_LABELS, self.fileDict)

        #self.fileListCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self._OnItemSelected)
        self.fileListCtrl.Bind(EVT_LIST_ITEM_CHECKED, self._OnListCheckUpdate)
        self.fileListCtrl.Bind(EVT_LIST_ITEM_UNCHECKED, self._OnListCheckUpdate)
        #self.fileListCtrl.Bind(wx.EVT_LIST_COL_CLICK, self.OnColumnClick)

        self.topBS.Add(self.fileListCtrl, 4, border=0, flag=wx.EXPAND|wx.ALL) #flag=0)
        self.topBS.Add(0, 8, 0, border=0, flag=wx.EXPAND)

        # Log TextCtrl to contain list of marked files in a boxsizer
        self.sb4 = wx.StaticBox(label='Marked Files...', parent=self.panel1, style=0)
        self.logBS = wx.StaticBoxSizer(box=self.sb4, orient=wx.VERTICAL)

        self.logTC = wx.TextCtrl(self.panel1, style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.logBS.Add(self.logTC, 4, border=0, flag=wx.EXPAND|wx.ALL)
        self.topBS.Add(self.logBS, 3, border=0, flag=wx.EXPAND|wx.ALL)
        self.topBS.Add(0, 8, 0, border=0, flag=wx.EXPAND)
        
        # Status bar at the bottom
        self.infoSB = wx.StatusBar(parent=self.panel1, style=0)
        self.infoSB.SetToolTip('Status')
        self.infoSB.SetFont(wx.Font(11, wx.SWISS, wx.ITALIC, wx.NORMAL, False, 'foo'))
        
        self.infoSBFieldsCount = 9
        
        [self.SB_FILEHDR,	# Total file counter
         self.SB_FILECNT,	
         self.SB_FILESIZEHDR,	# Total file size
         self.SB_FILESIZECNT,
         self.SB_MARKHDR,	# Marked file counter
         self.SB_MARKCNT,
         self.SB_MARKSIZEHDR,	# Markedfile size
         self.SB_MARKSIZECNT,
         self.SB_SPARE0] = [i for i in range(self.infoSBFieldsCount)]

        self.infoSB.SetFieldsCount(self.infoSBFieldsCount)
        self.infoSB.SetStatusWidths([80,40,100,80,80,60,100,80,-1])

        self.infoSB.SetStatusText('Files #:', self.SB_FILEHDR)
        self.infoSB.SetStatusText('0', self.SB_FILECNT)

        self.infoSB.SetStatusText('Total Files Size:', self.SB_FILESIZEHDR)
        self.infoSB.SetStatusText('0', self.SB_FILESIZECNT)
        
        self.infoSB.SetStatusText('Files Marked:', self.SB_MARKHDR)
        self.infoSB.SetStatusText('0', self.SB_MARKCNT)

        self.infoSB.SetStatusText('Marked Files Size:', self.SB_MARKSIZEHDR)
        self.infoSB.SetStatusText('0', self.SB_MARKSIZECNT)
        self.infoSB.SetStatusText('', self.SB_SPARE0)
        self.topBS.Add(self.infoSB, 0, border=0, flag=wx.EXPAND)

        self.checkedItems = set()
        # Update statusbar
        if not self.fileList:
            self._update1StatusBar(0, 0)
        else:
            humanTotalSize = self.fileList[-1][FLF_ITEMS[FLF_SIZETOTAL]]
            self._update1StatusBar(len(self.fileDict), humanTotalSize)
        
        self.panel1.SetSizerAndFit(self.topBS)
        self.SetClientSize(self.topBS.GetSize())
        self.Centre()
        self.SetFocus()

    # Events
    
    def _OnListCheckUpdate(self, event):
        # Update the logTC
        self.logTC.Clear()

        # Update the status bar
        self.infoSB.SetStatusText('0', self.SB_MARKCNT)
        self.infoSB.SetStatusText('0', self.SB_MARKSIZECNT)

        num = self.fileListCtrl.GetItemCount()
        cnt = size = 0
        for i in range(num):
            filename = self.fileListCtrl.GetItem(i,self.HDR_FILENAME).GetText()
            if self.fileListCtrl.IsMarked(filename):
                self.logTC.AppendText(filename + '\n')
                cnt  += 1
                size += self.fileDict[filename][FLF_ITEMS[FLF_SIZERAW]]
                self.checkedItems.add(filename)
            else:
                self.checkedItems.discard(filename)

        sel = self.fileTypesChoice.GetSelection()
        if cnt and (self.FILE_TYPES[sel][1] == self.FT_NOTSYNCED or self.FILE_TYPES[sel][1] == self.FT_MARKED):
            self.btnDownload.Enable(True)
        else:
            self.btnDownload.Enable(False)
        # Update the status bar
        self.infoSB.SetStatusText(str(cnt), self.SB_MARKCNT)
        self.infoSB.SetStatusText(humanBytes(size), self.SB_MARKSIZECNT)
        myprint(self.checkedItems)

    def _OnItemSelected(self, event):
        item = event.GetItem()
        #myprint(item.GetId(), item.GetText(),item.GetData(),item.GetColumn())
        event.Skip()

    def _OnMarkAll(self, event):
        num = self.fileListCtrl.GetItemCount()
        for i in range(num):
            self.fileListCtrl.MarkItem(i, True)
        self.btnDownload.Enable(True)

    def _OnUnMarkAll(self, event):
        num = self.fileListCtrl.GetItemCount()
        for i in range(num):
            self.fileListCtrl.MarkItem(i, False)
        self.btnDownload.Enable(False)
        # Update the status bar
        self.infoSB.SetStatusText('0', self.SB_MARKCNT)
        self.infoSB.SetStatusText('0', self.SB_MARKSIZECNT)
        
    def _OnBtnDownload(self, event):
        myprint('Items checked:',self.checkedItems)
        # Loop thru the list of files, searching for marked files
        num = self.fileListCtrl.GetItemCount()
        for i in range(num):
            fileName = self.fileListCtrl.GetItem(i,self.HDR_FILENAME).GetText()
            if fileName in self.checkedItems:
                # myprint(self.fileDict[fileName][FLF_ITEMS[FLF_FILENAME]],
                #         self.fileDict[fileName][FLF_ITEMS[FLF_SIZERAW]],
                #         self.fileDict[fileName][FLF_ITEMS[FLF_DATERAW]] )
                fileSize = globs.availRemoteFiles[fileName][globs.F_SIZE]
                fileDate = globs.availRemoteFiles[fileName][globs.F_DATEINSECS]

                e = [fileName, fileSize, fileDate, globs.FILE_MARK]
                myprint('Adding to download list:',e)
                # Loop thru opList[] looking for a free slot, schedule an operation
                for op in globs.opList:
                    if op[globs.OP_STATUS] == 0:	# Free slot
                        _scheduleOperation(op, e)
                        break
                else:
                    msg = 'Max requests reached (%d).' % (globs.MAX_OPERATIONS)
                    myprint(msg)
                    return

        self.installDlg = InstallDialog.InstallDialog(self,
                                        download=globs.osvmDownloadDir,
                                        title='Downloading Files')
        self.installDlg.ShowModal()
        self.blocksToTransfer, self.blocksTransfered = self.installDlg.getTransferInfo()
        myprint('blocksToTransfer=%d blocksTransfered=%d' % (self.blocksToTransfer, self.blocksTransfered))
        self.installDlg.Destroy()

        # Clear Operations list
        _clearAllOperations()

        # If some blocks have been transfered, need to update the marked file list
        if self.blocksTransfered:
            # Update checkedItems set
            self._updateMarkedFileList()
            self._OnParamsSelector(0)	# To rebuild the displayed list
        event.Skip()

    def _OnParamsSelector(self, event):
        self.logTC.Clear()
        self.btnDownload.Enable(False)
        self.markerChoice.Enable(False)
        self.fileListCtrl.EnableCheckBoxes(enable=False)
        
        c0,c1,c2,c3 = self._getSortingParams()
        
        if c0 == self.FT_REMOTE: #'All Remote Files':
            self.fileDict, self.fileList = buildFileListAndDict(list(globs.availRemoteFiles.items()), c1, c2)
        elif c0 == self.FT_LOCAL: #'All Local Files':
            self.fileDict, self.fileList = buildFileListAndDict(list(globs.localFileInfos.items()), c1, c2)
        elif c0 == self.FT_NOTSYNCED:
            # Build a list of not synced files
            dictDiff = buildDiff2Dict()
            self.fileDict, self.fileList = buildFileListAndDict(list(dictDiff.items()), c1, c2)
            self.markerChoice.Enable(True)
            self.fileListCtrl.EnableCheckBoxes(enable=True)
            if len(self.checkedItems):
                self.btnDownload.Enable(True)
        elif c0 == self.FT_SYNCED:	# Common files
            # Build a list of synced files (files in common)
            dictDiff = buildDiff3Dict()
            self.fileDict, self.fileList = buildFileListAndDict(list(dictDiff.items()), c1, c2)
            if len(self.checkedItems):
                self.btnDownload.Enable(True)
        else: # Marked Files
            checkedItemsDict = dict()
            for f in self.checkedItems:
                checkedItemsDict[f] = globs.availRemoteFiles[f]
                #myprint(checkedItemsDict)
            self.fileDict, self.fileList = buildFileListAndDict(list(checkedItemsDict.items()), c1, c2)
            # Update fileDict to reflect mark/unmark
            for k,v in self.fileDict.items():
                # Convert tuple to list to update mark
                l = list(v)
                l[FLF_ITEMS[FLF_MARKED]] = 1
                # Convert back to tuple
                self.fileDict[k] = tuple(l)
        #print('D',self.fileDict)
        #print('L',self.fileList)
        
        # Update ListCtrl data
        self.fileListCtrl.UpdateDataMap(self.fileDict)

        if self.markerChoice.IsEnabled():
            # Handle Marker selection
            if c3 == self.MARK_NONE:
                self._OnUnMarkAll(0)
            elif c3 == self.MARK_JPG:
                self._markFilesBySuffix('jpg')
            elif c3 == self.MARK_MOV:
                self._markFilesBySuffix('mov')
            else:
                self._OnMarkAll(0)

        # Update status bar
        if not self.fileList:	# If list is empty...
            self._update1StatusBar(0, 0)
        else:
            humanTotalSize = self.fileList[-1][FLF_ITEMS[FLF_SIZETOTAL]]
            self._update1StatusBar(len(self.fileDict), humanTotalSize)

        self._OnListCheckUpdate(0)
        
        if event:
            event.Skip()

    def _OnBtnClose(self, event):
        dlg = wx.MessageDialog(self, "Do you really want to close this frame?", "Confirm Exit", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_CANCEL:
            event = fileListFrameCustomEvent(resultOfFrame = 'CANCEL')
            self.GetEventHandler().ProcessEvent(event)
        else: # result == wx.ID_OK
            event = fileListFrameCustomEvent(resultOfFrame = '%d-%d' % (wx.ID_OK,self.blocksTransfered))
            myprint('Generating and processing event:', event.resultOfFrame)
            self.GetEventHandler().ProcessEvent(event)
            self.Close()

    def _OnBtnSave(self, event):
        listType = self.FILE_TYPES[self.fileTypesChoice.GetSelection()][0]
        currentDate = time.strftime('%m%d%y', time.localtime())
        filePath = '%s-%s.csv' % (listType,currentDate)

        myprint('Saving list: %s to %s' % (listType, filePath))
        #myprint(self.fileList)
        with open(filePath, 'w') as f:
            wr = csv.writer(f, quoting=csv.QUOTE_ALL)
            wr.writerow(self.CSV_COL_HDRS)
            wr.writerows(self.fileList)
        dlg = wx.MessageDialog(self, "List saved to file %s" % (filePath), 'Information', wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
        event.Skip()
        
    def _OnClose(self, event):
        myprint("Closing")
        self.PopEventHandler(True)
        event.Skip()

    def _update1StatusBar(self, fileCnt, sizeTotal):
        self.infoSB.SetStatusText(str(fileCnt), self.SB_FILECNT)	# Total File count
        self.infoSB.SetStatusText(str(sizeTotal), self.SB_FILESIZECNT)	# Total File size

    def _updateMarkedFileList(self):
        # Rebuild the list of 'not synced' files
        notSyncedDict = buildDiff2Dict()

        # Iterate on a copy to allow set modification in the loop
        size = 0
        for f in self.checkedItems.copy():
            if f in notSyncedDict.keys():
                myprint('%s still in notSynced list. Keeping mark' % f)
                size += notSyncedDict[f][globs.F_SIZE]
            else:
                myprint('%s nomore in notSynced list. Removing mark' % f)
                self.checkedItems.discard(f)
        # Update the status bar
        self.infoSB.SetStatusText(str(len(self.checkedItems)), self.SB_MARKCNT)
        self.infoSB.SetStatusText(humanBytes(size), self.SB_MARKSIZECNT)
                
    def _getSortingParams(self):
        idx = self.fileTypesChoice.GetSelection()
        c0 = self.FILE_TYPES[idx][1]

        idx = self.sortFieldChoice.GetSelection()
        c1 = self.FILE_SORT_FIELD[idx][1]

        c2 = self.sortOrderChoice.GetSelection()

        c3 = self.markerChoice.GetSelection()
        myprint('Criteria: Type: %s Field: %d Order: %d Marker: %d' % (c0,c1,c2,c3))

        return(c0,c1,c2,c3)

    def _markFilesBySuffix(self, suffix):
        self._OnUnMarkAll(0)
        for i in range(self.fileListCtrl.GetItemCount()):
            filename = self.fileListCtrl.GetItem(i,self.HDR_FILENAME).GetText()
            if filename.lower().endswith(suffix):
                #myprint('Marking',filename)
                self.fileListCtrl.MarkItem(i, True)

    # Called by InstallDialog()
    def finish(self):
        myprint('has been run.')

            
########################
def module_path(local_function):
    ''' returns the module path without the use of __file__.  
    Requires a function defined locally in the module.
    from http://stackoverflow.com/questions/729583/getting-file-path-of-imported-module'''
    return os.path.abspath(inspect.getsourcefile(local_function))

def myprint(*args, **kwargs):
    """My custom print() function."""
    # Adding new arguments to the print function signature 
    # is probably a bad idea.
    # Instead consider testing if custom argument keywords
    # are present in kwargs
    __builtin__.print('%s():' % inspect.stack()[1][3], *args, **kwargs)

def unbufprint(text):
    sys.__stdout__.write(text)
    sys.__stdout__.flush()
    
def secondsTohms(t):
    d = time.strftime('%H:%M:%S', time.localtime(t))
    return d

def secondsTodmy(t):
    d = time.strftime('%d/%m/%y', time.localtime(t))
    return d

def secondsTodby(t):
    d = time.strftime('%d %b %y', time.localtime(t))
    return d

def humanBytes(size):
    power = float(2**10)     # 2**10 = 1024
    n = 0
    power_labels = {0 : 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size = float(size / power)
        n += 1
    return '%s %s' % (('%.2f' % size).rstrip('0').rstrip('.'), power_labels[n])

# Build a list containing elements NOT in common to parameters
def listDiff1(li1, li2): 
    l = [i for i in li1 + li2 if i not in li1 or i not in li2] 
    return l

# Build a list containing elements of list1 NOT in list2
def listDiff2(li1, li2): 
    l = [i for i in li1 if i not in li2] 
    return l

# Build a list containing elements of list1 AND in list2
def listDiff3(li1, li2): 
    l = [i for i in li1 if i in li2] 
    return l

class MyApp(wx.App):
    def OnInit(self):

        eventTrackerHandle = FileListFrameEventTracker(self.OnResults)
        self.frame = FileListFrame(None, -1, 'List of Files')
        self.frame.PushEventHandler(eventTrackerHandle)

        self.frame.Show(True)
        self.frame.Center()
        return True

    def OnResults(self, resultData):
        myprint("Result data gathered: %s" % resultData)
        a,b = (int(x) for x in resultData.split('-'))
        retCode, needRefresh = resultData.split('-')
        if retCode == wx.ID_OK and needRefresh:
            myprint('needRefresh=%d retCode=%d' % (needRefresh,retCode))

def main():
    # Init Globals instance
    
    globs.availRemoteFiles['P6122903.JPG'] = ['P6122903.JPG', 1540707, 1591972676, '', '/DCIM/100OLYMP', 0, 20684, 33980, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P6122903.JPG']
    globs.availRemoteFiles['P8232966.JPG'] = ['P8232966.JPG', 1538041, 1598171028, '', '/DCIM/100OLYMP', 0, 20759, 21240, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P8232966.JPG']
    globs.availRemoteFiles['P7032921.JPG'] = ['P7032921.JPG', 1522484, 1593782206, '', '/DCIM/100OLYMP', 0, 20707, 31255, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7032921.JPG']
    globs.availRemoteFiles['P7062936.JPG'] = ['P7062936.JPG', 1599056, 1594058304, '', '/DCIM/100OLYMP', 0, 20710, 40780, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P7062936.JPG']
    globs.availRemoteFiles['P4062936.JPG'] = ['P4062936.JPG', 1509056, 1504058304, '', '/DCIM/100OLYMP', 0, 20710, 46780, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P4062936.JPG']
    globs.availRemoteFiles['P1234567.MOV'] = ['P1234567.MOV', 5508000, 1504000000, '', '/DCIM/100OLYMP', 0, 20600, 12345, 'http://192.168.0.10:80/get_thumbnail.cgi?DIR=/DCIM/100OLYMP/P1234567.MOV']

#    globs.availRemoteFiles = dict()
    
    globs.localFileInfos['P8232966.JPG'] = ['P8232966.JPG',1538041,1598171028,'foo']
    globs.localFileInfos['P7032921.JPG'] = ['P7032921.JPG',1522484,1593782206,'bar']

    globs.osvmFilesDownloadUrl = 'http://192.168.0.10:80'
    globs.osvmDownloadDir = '/tmp'
    globs.tmpDir = '/tmp'
    globs.overwriteLocalFiles = True
    globs.modPath = module_path(main)
    globs.imgDir  = os.path.join(os.path.dirname(globs.modPath), 'images')

    app = MyApp(0)
    app.MainLoop()

# Entry point    
if __name__ == "__main__":
    main()
