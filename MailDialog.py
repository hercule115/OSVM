#!/usr/bin/env python
import wx

import sys
import os
import builtins as __builtin__
import inspect
import time
import platform
import socket

# Import the email modules we'll need
from email.message import EmailMessage
from email.mime.text  import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders

import mimetypes # To guess file type
import smtplib	# actual sending function

moduleList = {'osvmGlobals':'globs',
              'MailPreferencesDialog':'MailPreferencesDialog'}

for k,v in moduleList.items():
    print('Loading: %s as %s' % (k,v))
    mod = __import__(k, fromlist=[None])
    globals()[v] = globals().pop('mod')	# Rename module in globals()
    
####
#print(__name__)

# Send a MultiPart mail
def sendMultiPartMail(smtpParams, sender, recipient, subject, textbody, attachments=[]):
   # Create the enclosing (outer) message
    outer = MIMEMultipart()    

    outer['Subject'] = subject
    outer['From']    = sender
    outer['To']      = recipient
    outer.preamble   = 'Files sent by OSVM'

    for path in attachments:
        myprint('Attaching %s' % path)
        if not os.path.isfile(path):
            myprint('Skipping over %s' % path)
            continue
        
        # Guess the content type based on the file's extension.  Encoding
        # will be ignored, although we should check for simple things like
        # gzip'd or compressed files.
        ctype, encoding = mimetypes.guess_type(path)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        if maintype == 'text':
            with open(path) as fp:
                # Note: we should handle calculating the charset
                msg = MIMEText(fp.read(), _subtype=subtype)
        elif maintype == 'image':
            with open(path, 'rb') as fp:
                msg = MIMEImage(fp.read(), _subtype=subtype)
        elif maintype == 'audio':
            with open(path, 'rb') as fp:
                msg = MIMEAudio(fp.read(), _subtype=subtype)
        else:
            with open(path, 'rb') as fp:
                msg = MIMEBase(maintype, subtype)
                msg.set_payload(fp.read())
            # Encode the payload using Base64
            encoders.encode_base64(msg)
        # Set the filename parameter
        msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(path))
        outer.attach(msg)

    # Attach mail's body
    msg = MIMEText(textbody)
    outer.attach(msg)

    # Send the mail
    myprint('Sending mail via %s:%d' % (smtpParams['smtpServer'],smtpParams['smtpServerPort']))
    
    wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)
    try:
        smtp = smtplib.SMTP_SSL(smtpParams['smtpServer'],smtpParams['smtpServerPort'])
    except (smtplib.SMTPException, socket.error, socket.gaierror) as e:
        msg = "Error: %s" % ("{0}".format(e.strerror))
        myprint(msg)
        dlg = wx.MessageDialog(None, msg, 'ERROR', wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        wx.EndBusyCursor()
        return(-1)

    # smtp.set_debuglevel(1)
    
    if smtpParams['smtpServerUseAuth']:
        try:
            smtp.login(smtpParams['smtpServerUserName'],smtpParams['smtpServerUserPasswd'])
        except (smtplib.SMTPHeloError, smtplib.SMTPAuthenticationError) as e:
            myprint('smtp.login Error: {0}'.format(e))
            msg = 'Error while connecting to the SMTP Server. Check your Credentials'
            dlg = wx.MessageDialog(None, msg, 'ERROR', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            wx.EndBusyCursor()
            return(-1)
        try:
            smtp.sendmail(sender, recipient, outer.as_string())
        except:
            msg = 'Error while sending mail.\nCheck Mail Parameters'
            myprint(msg)
            dlg = wx.MessageDialog(None, msg, 'ERROR', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            wx.EndBusyCursor()
            return(-1)
    wx.EndBusyCursor()                    
    smtp.quit()
    return(0)

class ToFieldMenu(wx.Menu):
    """
    Creates and displays a menu that allows the user to
    select a recipient from a list
    """
    def __init__(self, parent):
        """
        Initialize the menu dialog box
        """
        self.parent = parent

        super(ToFieldMenu,self).__init__()

        # Get the mouse position
        self.clickedPos = self.parent.panel1.ScreenToClient(wx.GetMousePosition())
        
        # Creates a Menu containing previous recipients:
        self.popupMenu = wx.Menu()
        self.popupMenuEntries = []

        # Id of each menu entry. 
        if globs.system == 'Darwin':
            id = 1
        else:
            id = 0  

        #myprint('globs.smtpRecipientsList:',globs.smtpRecipientsList)
        
        for recv in globs.smtpRecipientsList:
            self.popupMenuEntries.append((id, recv))
            menuItem = wx.MenuItem(self.popupMenu, id, recv)
            self.popupMenu.Append(menuItem)
            # Register Properties menu handler with EVT_MENU
            self.popupMenu.Bind(wx.EVT_MENU, self._SelectRecipient, menuItem)
            id += 1

        # Displays the menu at the current mouse position
        self.parent.panel1.PopupMenu(self.popupMenu, self.clickedPos)
        self.popupMenu.Destroy() # destroy to avoid mem leak

    def _SelectRecipient(self, event):
        recipient = self.popupMenuEntries[event.GetId()-1][1] # Platform dependance ??
        #myprint(recipient)
        wx.CallAfter(self.parent.setToField, recipient)
        event.Skip()
        
#### MailDialog
class MailDialog(wx.Dialog):
    def __init__(self, parent, attachmentlist):
        self.attachmentList = attachmentlist

        myStyle = wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL|wx.RESIZE_BORDER
        wx.Dialog.__init__(self, None, wx.ID_ANY, 'Compose Mail', style=myStyle)

        self._initialize()

        self.panel1.SetSizerAndFit(self.topBoxSizer)
        self.SetClientSize(self.topBoxSizer.GetSize())
        self.Centre()

    """
    Create and layout the widgets in the dialog
    """
    def _initialize(self):
        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self,
                               size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        # Grid containing mail header fields
        rows = 3
        cols = 2
        self.mailHdrGrid = wx.FlexGridSizer(rows, cols, vgap=5, hgap=10)

        self.mailHdrName = ['From', 'To', 'Subject']
        self.mailHdrVal = []
        for i in range(3):
            self.mailHdrVal.append(wx.StaticText(self.panel1, label=self.mailHdrName[i]))
            self.mailHdrVal.append(wx.TextCtrl(self.panel1))

        self.mailHdrVal[1].SetValue(globs.smtpFromUser)
        self.mailHdrVal[3].SetValue('')    # Clear To: field

        if not globs.smtpFromUser: 
            self.mailHdrVal[1].SetFocus()    # Set focus to "From" field
        else:
            self.mailHdrVal[5].SetFocus()    # Set focus to "Subject" field

        for i in range(rows * cols):
            if i%2 :
                self.mailHdrGrid.Add(self.mailHdrVal[i], proportion=1, flag=wx.EXPAND)
                self.mailHdrVal[i].Bind(wx.EVT_TEXT, self.OnMailHdrCtrlText)
            else:
                self.mailHdrGrid.Add(self.mailHdrVal[i], proportion=1, flag=wx.CENTER)

        # Bind Mouse Click event in To: Field
        self.mailHdrVal[3].Bind(wx.EVT_TEXT, self.OnText)
        
        self.mailHdrVal[3].Bind(wx.EVT_LEFT_DOWN, self.OnToFieldLeftDown)
        self.mailHdrVal[3].SetDefaultStyle(wx.TextAttr(wx.BLUE))

        self.mailHdrGrid.AddGrowableRow(rows-1, 1)
        self.mailHdrGrid.AddGrowableCol(cols-1, 1)

        # Grid containing mail attachments fields
        rows = 1
        cols = 2
        self.attachmentsGrid = wx.FlexGridSizer(rows, cols, vgap=5, hgap=10)

        self.attachmentLB = wx.ListBox(choices=[os.path.basename(v) for v in self.attachmentList], parent=self.panel1, id=wx.ID_ANY, style=wx.LB_NEEDED_SB | wx.LB_SINGLE, size=wx.Size(200,-1))

        self.attachmentsGrid.Add(wx.StaticText(self.panel1, label='Attachments'), proportion=0, flag=wx.CENTER)
        self.attachmentsGrid.Add(self.attachmentLB, proportion=1, flag=wx.EXPAND)

        # Buttons to deal with Attachments 
        self.btnAdd = wx.Button(id=wx.ID_DEFAULT, label='Add', parent=self.panel1, style=0)
        self.btnAdd.SetToolTip('Add a new attachment to the list')
        self.btnAdd.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnAdd(evt))

        self.btnRemove = wx.Button(id=wx.ID_DEFAULT, label='Remove', parent=self.panel1, style=0)
        self.btnRemove.SetToolTip('Remove attachment from the list')
        self.btnRemove.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnRemove(evt))
        
        self.btnClear = wx.Button(id=wx.ID_DEFAULT, label='Clear', parent=self.panel1, style=0)
        self.btnClear.SetToolTip('Clear attachment list')
        self.btnClear.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnClear(evt))
        if not self.attachmentLB.GetCount():
            self.btnRemove.Disable()
            self.btnClear.Disable()
        else:
            self.btnRemove.Enable()
            self.btnClear.Enable()

        if globs.smtpServerUseAuth:
            val = '%s | %s(%d), Auth: %s | %s' % (globs.smtpServer,
                                                  globs.smtpServerProtocol,
                                                  globs.smtpServerPort,
                                                  globs.smtpServerUserName,
                                                  globs.smtpServerUserPasswd)
        else:
            val = '%s | %s(%d)' % (globs.smtpServer,
                                   globs.smtpServerProtocol,
                                   globs.smtpServerPort)
        self.smtpConfigInfo = wx.StaticText(label=val, id=wx.ID_ANY, parent=self.panel1)
        self.smtpConfigInfo.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'WhatElse'))
            
        # Message ...
        self.msgTextCtrl = wx.TextCtrl(id=wx.ID_ANY,
                                       name=u'msgTextCtrl', 
                                       parent=self.panel1, 
                                       style=wx.TE_MULTILINE,
                                       size=wx.Size(400, 150), 
                                       value=u'')
        self.msgTextCtrl.SetToolTip(u'This is your message')
        self.msgTextCtrl.SetAutoLayout(True)
        self.msgTextCtrl.SetCursor(wx.STANDARD_CURSOR)
        self.msgTextCtrl.Bind(wx.EVT_TEXT, self.OnMsgTextCtrlText)

        # Finally add bottom buttons in a sizer
        self.btnPrefs = wx.Button(label='Preferences', id=wx.ID_ANY, parent=self.panel1, style=0)
        self.btnPrefs.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnPrefs(evt))

        self.btnCancel = wx.Button(label='Cancel', id=wx.ID_ANY, parent=self.panel1, style=0)
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnBtnCancel)

        self.btnSend = wx.Button(id=wx.ID_ANY, label='send',
                                 name='Send', parent=self.panel1, style=0)
        self.btnSend.SetToolTip(u'Send this mail')
        self.btnSend.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnSend(evt))
        self.btnSend.Disable()

        self._init_sizers()

    def _init_topBoxSizer_Items(self, parent):
        parent.Add(self.mailHdrBoxSizer, 0, border=10,
                        flag=wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT)
        parent.Add(self.attachmentsBoxSizer, 0, border=10,
                        flag=wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT)
        parent.Add(self.msgBoxSizer, 0, border=10,
                        flag=wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT)
        parent.Add(self.infoBoxSizer, 0, border=10,
                        flag=wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT)
        parent.Add(self.bottomBoxSizer, 1, border=10,
                        flag=wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT)

    def _init_mailHdrBoxSizer_Items(self, parent):
        parent.Add(self.mailHdrGrid, proportion=1, border=5, flag=wx.ALL|wx.EXPAND)

    def _init_attachmentsBtnBS_Items(self, parent):
        parent.Add(self.btnAdd, 0, border=0, flag=0)        
        parent.Add(wx.Size(4, 4), 0, border=0, flag=0)
        parent.Add(self.btnRemove, 0, border=0, flag=0)        
        parent.Add(wx.Size(4, 4), 0, border=0, flag=0)
        parent.Add(self.btnClear, 0, border=0, flag=0)
        parent.Add(wx.Size(4, 4), 1, border=0, flag=0)
        
    def _init_attachmentsBoxSizer_Items(self, parent):
        parent.Add(self.attachmentsGrid, proportion=1, border=5, flag=wx.ALL|wx.EXPAND)
        parent.Add(wx.Size(4, 4), 0, border=0, flag=0)
        parent.Add(self.attachmentsBtnBS, 0, border=5, flag=wx.ALL|wx.EXPAND)
        
    def _init_infoBoxSizer_Items(self, parent):
        parent.Add(self.smtpConfigInfo, 0, border=5, flag=wx.EXPAND | wx.ALL)
        parent.Add(wx.Size(4, 4), 1, border=0, flag=0)

    def _init_msgBoxSizer_Items(self, parent):
        parent.Add(self.msgTextCtrl, 1, border=0, flag=wx.EXPAND)

    def _init_bottomBoxSizer_Items(self, parent):
        parent.Add(wx.Size(4, 4), 0, border=0, flag=0)
        parent.Add(self.btnPrefs, 0, border=0, flag=0)        
        parent.Add(wx.Size(4, 4), 1, border=0, flag=0)
        parent.Add(self.btnCancel, 0, border=0, flag=0)
        parent.Add(wx.Size(8, 4), 0, border=0, flag=0)
        parent.Add(self.btnSend, 0, border=0, flag=0)

    def _init_sizers(self):
        # Create box sizers
        self.topBoxSizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.mailHdrBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.attachmentsBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.attachmentsBtnBS = wx.BoxSizer(orient=wx.VERTICAL)
        self.infoBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.msgBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.bottomBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        # Initialize each sizer
        self._init_topBoxSizer_Items(self.topBoxSizer)
        self._init_mailHdrBoxSizer_Items(self.mailHdrBoxSizer)
        self._init_attachmentsBtnBS_Items(self.attachmentsBtnBS)
        self._init_attachmentsBoxSizer_Items(self.attachmentsBoxSizer)
        self._init_infoBoxSizer_Items(self.infoBoxSizer)
        self._init_msgBoxSizer_Items(self.msgBoxSizer)
        self._init_bottomBoxSizer_Items(self.bottomBoxSizer)

    # Enable SEND button if all fields are filled
    def _enableSendBtn(self):
        val  = self.mailHdrVal[1].GetValue() != ''
        val += self.mailHdrVal[3].GetValue() != ''
        val += self.mailHdrVal[5].GetValue() != ''
        val += self.msgTextCtrl.GetValue() != ''

        if val > 3 :
            self.btnSend.Enable(True)
        else:
            self.btnSend.Enable(False)

    def setToField(self, recipient):
        self.mailHdrVal[3].SetValue(recipient)    # Set To: field
        # myprint(self.mailHdrVal[3].GetValue())
        
    ## Events
    def OnText(self, event):
        event.Skip()
        
    def OnToFieldLeftDown(self, event):
        tc = self.mailHdrVal[3]
        ToFieldMenu(self)
        myprint('Selected Entry:', tc.GetValue())
        if tc.GetValue() == '':
            myprint('Refreshing')
            self.Refresh()
        else:
            # curPos = tc.GetInsertionPoint()
            # insertionPointRowColumnPosition = tc.PositionToXY(curPos)
            # print(insertionPointRowColumnPosition)
            # lineNum = curRow
            # lineText = tc.GetLineText(0)#lineNum)
            # newPos = tc.XYToPosition(len(lineText), curRow)
            # myprint(curPos,curVal,curCol,curRow,lineText,newPos)
            # tc.SetInsertionPoint(newPos)
            pass
        #event.Skip()
    
    def OnBtnSend(self, event):
        # Mail Headers
        sender   = self.mailHdrVal[1].GetValue()
        recipient = self.mailHdrVal[3].GetValue()
        subject  = "[OSVM]: " + self.mailHdrVal[5].GetValue()

        # Mail Text
        text = self.msgTextCtrl.GetValue()

        # Build & Send the mail
        smtpParams = dict()
        smtpParams['smtpServer']           = globs.smtpServer
        smtpParams['smtpServerPort']       = globs.smtpServerPort
        smtpParams['smtpServerProtocol']   = globs.smtpServerProtocol
        smtpParams['smtpServerUseAuth']    = globs.smtpServerUseAuth
        smtpParams['smtpServerUserName']   = globs.smtpServerUserName
        smtpParams['smtpServerUserPasswd'] = globs.smtpServerUserPasswd
        smtpParams['smtpFromUser']         = globs.smtpFromUser        

        if not globs.smtpServer or not globs.smtpServerPort or not globs.smtpServerProtocol:
            msg = "SMTP Server Parameters not set.\nCheck Mail Preferences"
            myprint(msg)
            dlg = wx.MessageDialog(None, msg, 'ERROR', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            event.Skip()
            return
        
        if not sendMultiPartMail(smtpParams, sender, recipient, subject, text, self.attachmentList):
            self.Close()

        # Add this recipient at head of the recipient list
        myprint('Recipient list 0',globs.smtpRecipientsList)
        globs.smtpRecipientsList.insert(0, recipient)
        myprint('Recipient list 1',globs.smtpRecipientsList)
        # Keep unique values
        globs.smtpRecipientsList = unique(globs.smtpRecipientsList)[:globs.SMTP_RECIPIENTS_LIST_LEN]
        myprint('Recipient list 2',globs.smtpRecipientsList)
        event.Skip()

    def OnBtnPrefs(self, event):
        dlg = MailPreferencesDialog.MailPreferencesDialog(self)
        ret = dlg.ShowModal()
        dlg.Destroy()
        if ret == wx.ID_APPLY:
            if globs.smtpServerUseAuth:
                val = '%s | %s(%d), Auth: %s | %s' % (globs.smtpServer,
                                                      globs.smtpServerProtocol,
                                                      globs.smtpServerPort,
                                                      globs.smtpServerUserName,
                                                      globs.smtpServerUserPasswd)
            else:
                val = '%s | %s(%d)' % (globs.smtpServer,
                                       globs.smtpServerProtocol,
                                       globs.smtpServerPort)
            self.smtpConfigInfo.SetLabel(val)
        event.Skip()

    def OnBtnAdd(self, event):
        with wx.FileDialog(self, "Add File", defaultDir=globs.osvmDownloadDir, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            basename = os.path.basename(pathname)
            self.attachmentLB.Append(basename)
            self.attachmentList.append(pathname)
            self.btnRemove.Enable()
            self.btnClear.Enable()
        event.Skip()
        
    def OnBtnRemove(self, event):
        sel = self.attachmentLB.GetSelection()
        if sel == wx.NOT_FOUND:
            myprint('No file selected')
            event.Skip()
            return
        self.attachmentLB.Delete(sel)
        self.attachmentList.remove(self.attachmentList[sel])
        if not self.attachmentLB.GetCount():
            self.btnRemove.Disable()
            self.btnClear.Disable()
        else:
            self.btnRemove.Enable()
            self.btnClear.Enable()
        event.Skip()

    def OnBtnClear(self, event):
        self.attachmentLB.Clear()
        self.attachmentList.clear()
        self.btnRemove.Disable()
        self.btnClear.Disable()
        event.Skip()
        
    def OnBtnCancel(self, event):
        self.Close()
        event.Skip()

    def OnMailHdrCtrlText(self, event):
        self._enableSendBtn()
        event.Skip()

    def OnMsgTextCtrlText(self, event):
        self._enableSendBtn()
        event.Skip()
        
########################
def myprint(*args, **kwargs):
    """My custom print() function."""
    # Adding new arguments to the print function signature 
    # is probably a bad idea.
    # Instead consider testing if custom argument keywords
    # are present in kwargs
    __builtin__.print('%s():' % inspect.stack()[1][3], *args, **kwargs)

# Return a list with unique values, keeping original order. Input: a list
def unique(sequence):
    seen = list()
    #[x for x in reversed(sequence) if not (x in seen or seen.insert(0,x))]
    [x for x in sequence if not (x in seen or seen.append(x))]
    return(seen)

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)

        attachmentList = list()
        attachmentList.append(os.path.join(globs.osvmDownloadDir,'PB102070.JPG'))
        attachmentList.append(os.path.join(globs.osvmDownloadDir,'PB102071.JPG'))
        dlg = MailDialog(self, attachmentlist=attachmentList)
        ret = dlg.ShowModal()
        dlg.Destroy()
        self.Destroy()

def main():
    # Init Globals instance
    globs.system = platform.system()		# Linux or Windows or MacOS (Darwin)
    globs.pythonVersion = (sys.version).split()[0]	# 2.x or 3.x ?

    globs.osvmDownloadDir = '/Users/didier/SynologyDrive/Photo/Olympus TG4/'

    globs.smtpServer           = 'smtp.gmail.com'
    globs.smtpServerProtocol   = 'SSL'
    globs.smtpServerPort       = 465
    globs.smtpServerUseAuth    = True
    globs.smtpServerUserName   = 'dspoirot@gmail.com'
    globs.smtpServerUserPasswd = 'foobar'
    globs.smtpFromUser         = 'Didier Poirot'
    tmp='alain,bernard,cloe,didier,eric,fabrice'
    globs.smtpRecipientsList   = list(filter(None, tmp.split(',')))[:globs.SMTP_RECIPIENTS_LIST_LEN]
    # Create empty recipient list 
    #globs.smtpRecipientsList   = list(filter(None, ''.split(',')))[:globs.SMTP_RECIPIENTS_LIST_LEN]
    # Create DemoFrame frame, passing globals instance as parameter
    app = wx.App(False)
    frame = MyFrame(None, -1, title="Test")
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
