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
   
moduleList = {'osvmGlobals':'globs',
              'InstallDialog':'InstallDialog'}

for k,v in moduleList.items():
    print('Loading: %s as %s' % (k,v))
    mod = __import__(k, fromlist=[None])
    globals()[v] = globals().pop('mod')	# Rename module in globals()

####
#print(__name__)

def buildFileListDict(fList, sortField, sortDir):
    myprint('Sorting criteria: Field: %d. Direction: %s' % (sortField, sortDir))
    #myprint(fList)
    print('sorting')
    if sortField != globs.F_NAME:
        fileList = sorted(fList, key=lambda x: int(x[1][sortField]), reverse=sortDir)
    else:
        fileList = sorted(fList, key=lambda x: x[0], reverse=sortDir)
    print('sorted')
    #myprint(fileList)

    d = dict()
    l = list()
    #k = 0
    idx= 0
    totalSize = 0
    for v in fileList:
        d1 = secondsTodby(v[1][globs.F_DATEINSECS])
        t1 = secondsTohms(v[1][globs.F_DATEINSECS])

        totalSize += v[1][globs.F_SIZE]

        d[v[1][globs.F_NAME]] = (str(idx),			# FL_IDX
                                 v[1][globs.F_NAME],		# FL_FILENAME
                                 humanBytes(v[1][globs.F_SIZE]),# FL_SIZEINMB
                                 v[1][globs.F_SIZE],		# FL_SIZERAW
                                 d1,				# FL_DATE
                                 v[1][globs.F_DATEINSECS],	# FL_DATERAW
                                 t1,				# FL_TIME
                                 humanBytes(totalSize))		# FL_SIZETOTAL

        l.append((idx,
                  v[1][globs.F_NAME],
                  humanBytes(v[1][globs.F_SIZE]),
                  v[1][globs.F_SIZE],
                  d1,
                  v[1][globs.F_DATEINSECS],
                  t1,
                  humanBytes(totalSize)))
        idx += 1
        #k += 1
    #print(d,l)
    #print(d)
    return(d,l)

def buildDiffDict():
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
    myprint(op)

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
    
class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):

    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, style=wx.LC_REPORT |
                wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)
    

class MyListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin, ListRowHighlighter):

    def __init__(self, parent, numCols, dataDict):

        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, style=wx.LC_REPORT)

        ListCtrlAutoWidthMixin.__init__(self)
        ListRowHighlighter.__init__(self)
        CheckListCtrlMixin.__init__(self)

        self.parent = parent
        
        self.itemDataMap = dataDict
        self.itemIndexMap = dataDict.keys()
        
        #events
        #self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._OnItemSelected)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
        #self.Bind(wx.EVT_LIST_ITEM_CHECKED, self.OnItemChecked)
        #self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColumnClick)
        
    def GetListCtrl(self):
        return self

    def OnCheckItem(self, idx, flag):
        myprint(idx,flag)
        if flag: # item checked
            evt = itemChecked()
        else:
            evt = itemUnChecked()
        wx.PostEvent(self, evt)
        
    # def OnColumnClick(self,event):
    #     print('OnColumnClick')
    #     self.RefreshRows()
    #     event.Skip()

    def OnItemChecked(self, event):
        myprint('')
        event.Skip()
        
    def _OnItemSelected(self, event):
        #item = event.GetItem()
        #print('Item Selected:',item.GetId(), item.GetText(),item.GetData(),item.GetColumn())
        #self.CheckItem(item.GetId())
        event.Skip()
        
    def OnItemDeselected(self, event):
        myprint('')
        event.Skip()
        
    def OnItemActivated(self, event):
        myprint('')
        event.Skip()

    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()

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
        
        [self.HDR_MARK,
         self.HDR_FILEIDX,
         self.HDR_FILENAME,
         self.HDR_FILESIZE,
         self.HDR_FILEDATE,
         self.HDR_FILETIME] = [i for i in range(6)]

        # Each column header entry of type: (label,width)
        self.HEADERLIST = [('MARK',60),
                           ('IDX',60),
                           ('FILENAME',180),
                           ('SIZE',100),
                           ('DATE',100),
                           ('TIME',100)]

        [self.FT_REMOTE,
         self.FT_LOCAL,
         self.FT_NOTSYNCED,
         self.FT_MARKED] = [i for i in range(4)]
        
        self.FILE_TYPES = [('Remote Files Not Synced', self.FT_NOTSYNCED),
                           ('Local Files', self.FT_LOCAL),
                           ('Remote Files', self.FT_REMOTE),
                           ('Marked Files', self.FT_MARKED)]
        
        self.FILE_SORT_FIELD = [('Filename', globs.F_NAME),
                                ('Date',     globs.F_DATEINSECS),
                                ('Size',     globs.F_SIZE)]
        
        self.FILE_SORT_ORDER = ['Ascending',
                                'Descending']

        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self,
                               size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        # Build a list of not synced files
        dictDiff = buildDiffDict()
        self.fileListDict, self.fileList = buildFileListDict(list(dictDiff.items()), globs.F_DATEINSECS, False)

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
        self.sb3 = wx.StaticBox(label='Markers...', parent=self.panel1, style=0)
        self.markerBS = wx.StaticBoxSizer(box=self.sb3, orient=wx.VERTICAL)

        self.btnClearAll = wx.Button(label='Clear All', parent=self.panel1, style=0)
        self.btnClearAll.Bind(wx.EVT_BUTTON, self._OnDeSelectAll)
        self.markerBS.Add(self.btnClearAll, 0, border=0, flag=wx.EXPAND)

        self.markerBS.Add(0, 8, border=0, flag=wx.EXPAND)

        self.btnMarkAll = wx.Button(label='Mark All', parent=self.panel1, style=0)
        self.btnMarkAll.Bind(wx.EVT_BUTTON, self._OnSelectAll)
        self.markerBS.Add(self.btnMarkAll, 0, border=0, flag=wx.EXPAND)

        self.markerBS.Add(0, 8, 0, border=0, flag=wx.EXPAND)

        self.btnDownload = wx.Button(label='Download...', parent=self.panel1, style=0)
        self.btnDownload.Bind(wx.EVT_BUTTON, self._OnBtnDownload)
        self.btnDownload.Enable(False)
        self.markerBS.Add(self.btnDownload, 0, border=0, flag=wx.EXPAND)
        
        # Button to save the list
        self.sb4 = wx.StaticBox(label='...', parent=self.panel1, style=0)
        self.rightBS = wx.StaticBoxSizer(box=self.sb4, orient=wx.VERTICAL)

        self.btnSave = wx.Button(label='Save List', parent=self.panel1, style=0)
        self.btnSave.Bind(wx.EVT_BUTTON, self._OnBtnSave)
        #self.rightBS.Add(self.btnSave, 0, border=0, flag=wx.EXPAND|wx.ALIGN_RIGHT)
        self.rightBS.Add(self.btnSave, 0, border=0, flag=wx.EXPAND)

        self.rightBS.Add(0, 8, 0, border=0, flag=wx.EXPAND)
        
        # Button to close the frame
        self.btnClose = wx.Button(label='Close', id=wx.ID_CLOSE, parent=self.panel1, style=0)
        self.btnClose.Bind(wx.EVT_BUTTON, self._OnBtnClose)
        #self.btnBS.Add(self.btnClose, 0, border=0, flag=wx.EXPAND|wx.ALIGN_RIGHT)
        self.rightBS.Add(self.btnClose, 0, border=0, flag=wx.EXPAND)

        #self.rightBS.Add(0, 8, border=0, flag=wx.EXPAND)
        
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
        self.fileListCtrl = MyListCtrl(self.panel1, len(self.HEADERLIST), self.fileListDict)

        self.fileListCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self._OnItemSelected)
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
        cnt, size = self._populateFileListCtrl(self.fileList)
        self._update1StatusBar(cnt, size)
        
        self.panel1.SetSizerAndFit(self.topBS)
        self.SetClientSize(self.topBS.GetSize())
        self.Centre()
        self.SetFocus()


    # def OnColumnClick(self, event):
    #     myprint('Column clicked:',event.GetColumn() )
    #     #myprint('Refreshing rows','col=',event.GetColumn() )
    #     #self.fileListCtrl.RefreshRows()
    #     self._OnParamsSelector(0)

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
            if self.fileListCtrl.IsChecked(i):
                self.logTC.AppendText(filename + '\n')
                cnt  += 1
                size += self.fileListDict[filename][self.FL_SIZERAW] # Size
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
        print(self.checkedItems)

    def _OnItemSelected(self, event):
        #item = event.GetItem()
        #myprint('Item Selected:',item.GetId(), item.GetText(),item.GetData(),item.GetColumn())
        event.Skip()

    def _OnSelectAll(self, event):
        num = self.fileListCtrl.GetItemCount()
        for i in range(num):
            self.fileListCtrl.CheckItem(i)
        self.btnDownload.Enable(True)

    def _OnDeSelectAll(self, event):
        num = self.fileListCtrl.GetItemCount()
        for i in range(num):
            self.fileListCtrl.CheckItem(i, False)
        self.btnDownload.Enable(False)
        
    def _OnBtnDownload(self, event):
        myprint('Item checked:',self.checkedItems)
        # Loop thru the list of files, searching for marked files
        num = self.fileListCtrl.GetItemCount()
        for i in range(num):
            fileName = self.fileListCtrl.GetItem(i,self.HDR_FILENAME).GetText()
            if fileName in self.checkedItems:
                # myprint(self.fileListDict[fileName][self.FL_FILENAME],
                #         self.fileListDict[fileName][self.FL_SIZERAW],
                #         self.fileListDict[fileName][self.FL_DATERAW])
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
        self.btnMarkAll.Enable(False)
        
        c0,c1,c2 = self._getSortingParams()
        
        if c0 == self.FT_REMOTE: #'All Remote Files':
            self.fileListDict, self.fileList = buildFileListDict(list(globs.availRemoteFiles.items()), c1, c2)
            self.btnMarkAll.Enable(True)
        elif c0 == self.FT_LOCAL: #'All Local Files':
            self.fileListDict, self.fileList = buildFileListDict(list(globs.localFileInfos.items()), c1, c2)
        elif c0 == self.FT_NOTSYNCED:
            # Build a list of not synced files
            dictDiff = buildDiffDict()
            self.fileListDict, self.fileList = buildFileListDict(list(dictDiff.items()), c1, c2)
            self.btnMarkAll.Enable(True)
            if len(self.checkedItems):
                self.btnDownload.Enable(True)
        else: # Marked Files
            checkedItemsDict = dict()
            for f in self.checkedItems:
                checkedItemsDict[f] = globs.availRemoteFiles[f]
            myprint(checkedItemsDict)
            self.fileListDict, self.fileList = buildFileListDict(list(checkedItemsDict.items()), c1, c2)
        print('D',self.fileListDict)
        print('L',self.fileList)
        
        # Update ListCtrl data
        cnt, size = self._populateFileListCtrl(self.fileList)
        self._update1StatusBar(cnt, size)
        
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
        filePath = '%s-%s.csv' % (listType,currentDate) #'foobar'

        myprint('Saving list: %s to %s' % (listType, filePath))
        #myprint(self.fileList)
        with open(filePath, 'w') as f:
            wr = csv.writer(f, quoting=csv.QUOTE_ALL)
            wr.writerow(self.COL_HDRS)
            wr.writerows(self.fileList)
        dlg = wx.MessageDialog(self, "List saved to file %s" % (filePath), 'Information', wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
        event.Skip()
        
    def _OnClose(self, event):
        myprint("Closing")
        self.PopEventHandler(True)
        event.Skip()

    def _populateFileListCtrl(self, fileList):
        self.fileListCtrl.ClearAll()

        #wx.STEELBLUE = wx.Colour(30, 100, 180)
        
        col = 0
        for h in self.HEADERLIST:
            self.fileListCtrl.InsertColumn(col, h[0], width=h[1])
            item = self.fileListCtrl.GetColumn(col)
            #item.SetBackgroundColour(wx.GREEN)
            #print(item.GetBackgroundColour())
            col += 1
                
        self.FL_LIST = [self.FL_IDX,
                        self.FL_FILENAME,
                        self.FL_SIZEINMB,
                        self.FL_SIZERAW,
                        self.FL_DATE,
                        self.FL_DATERAW,
                        self.FL_TIME,
                        self.FL_SIZETOTAL] = [i for i in range(8)]

        self.COL_HDRS = ["Index",
                         "Filename",
                         "Size",
                         "Raw Size",
                         "Date",
                         "Raw Date",
                         "Time",
                         "Total Size"]

        idx = totalSize = 0
        myprint('Populating')
        for data in fileList:
            index = self.fileListCtrl.InsertItem(idx, '')
            self.fileListCtrl.SetItem(index, 1, str(data[self.FL_IDX]))		# index
            self.fileListCtrl.SetItem(index, 2, data[self.FL_FILENAME])		# filename
            self.fileListCtrl.SetItem(index, 3, data[self.FL_SIZEINMB])		# size (in MB)
            self.fileListCtrl.SetItem(index, 4, data[self.FL_DATE])		# date
            self.fileListCtrl.SetItem(index, 5, data[self.FL_TIME])		# time
            #self.fileListCtrl.SetItem(index, 6, data[self.FL_SIZETOTAL])	# total size
            totalSize = data[self.FL_SIZETOTAL]	# total size
            self.fileListCtrl.SetItemData(index, idx)
            if data[self.FL_FILENAME] in self.checkedItems:
                self.fileListCtrl.CheckItem(index, True)
            idx += 1

            if (idx % 10) == 0:
                unbufprint('[%d]\r' % (idx))

        myprint('Populated')
        self.fileListCtrl.Refresh()
        return(idx,totalSize)

    def _update1StatusBar(self, fileCnt, sizeTotal):
        self.infoSB.SetStatusText(str(fileCnt), self.SB_FILECNT)	# Total File count
        self.infoSB.SetStatusText(str(sizeTotal), self.SB_FILESIZECNT)	# Total File size

    def _updateMarkedFileList(self):
        # Rebuild the list of 'not synced' files
        notSyncedDict = buildDiffDict()

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
        myprint('Sorting Parameters: Type: %s Field: %d Order: %d' % (c0,c1,c2))
        return(c0,c1,c2)

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
def listDiff(li1, li2): 
    l = [i for i in li1 + li2 if i not in li1 or i not in li2] 
    return l

# Build a list containing elements of list1 NOT in list2
def listDiff2(li1, li2): 
    l = [i for i in li1 if i not in li2] 
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

    globs.localFileInfos['P8232966.JPG'] = ['P8232966.JPG',1538041,1598171028,'foo']
    globs.localFileInfos['P7032921.JPG'] = ['P7032921.JPG',1522484,1593782206,'bar']

    globs.osvmFilesDownloadUrl = 'http://192.168.0.10:80'
    globs.osvmDownloadDir = '/tmp'
    globs.tmpDir = '/tmp'
    globs.overwriteLocalFiles = True

    app = MyApp(0)
    app.MainLoop()

# Entry point    
if __name__ == "__main__":
    main()
