#!/usr/bin/env python
import wx

import sys
import os
import builtins as __builtin__
import inspect
import time
import platform

moduleList = {'osvmGlobals':'globs'}

for k,v in moduleList.items():
    print('Loading: %s as %s' % (k,v))
    mod = __import__(k, fromlist=[None])
    globals()[v] = globals().pop('mod')	# Rename module in globals()

####
#print(__name__)

#### MailPreferencesDialog
class MailPreferencesDialog(wx.Dialog):
    def __init__(self, parent):
        myStyle = wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL|wx.RESIZE_BORDER
        wx.Dialog.__init__(self, None, wx.ID_ANY, 'Mail Preferences', style=myStyle)

        self._initialize()

        self.panel1.SetSizerAndFit(self.topBS)
        self.SetClientSize(self.topBS.GetSize())
        self.Centre()

    """
    Create and layout the widgets in the dialog
    """
    def _initialize(self):
        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self,
                               size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        self.sb1 = wx.StaticBox(label='Mail Server Parameters', id=wx.ID_ANY, parent=self.panel1, style=0)

        self.serverST = wx.StaticText(self.panel1)
        self.serverST.SetLabelMarkup("<span foreground='blue'>%s</span>" % 'SMTP Server')
        self.serverTC = wx.TextCtrl(self.panel1, value=globs.smtpServer, size=wx.Size(200, -1))
        self.serverTC.Bind(wx.EVT_TEXT, self.OnServerTC)

        # Store all protocol information in a list
        self.mailProps = list()
        self.mailProps.extend((('Protocol','Port'), ('SMTP',25), ('SSL',465), ('TLS',587)))

        self.fields = list()
        
        # first line header
        self.onerowfields = list()
        for i in range(len(self.mailProps[0])):
            field = wx.StaticText(self.panel1)
            field.SetLabelMarkup("<span foreground='blue'>%s</span>" % self.mailProps[0][i])
            self.onerowfields.append(field)
        self.fields.append(self.onerowfields) # append to self.fields

        rows = len(self.mailProps)        
        for i in range(1,rows):
            self.onerowfields = list()
            btn = wx.RadioButton(self.panel1, 
                                 label=self.mailProps[i][0],
                                 name=self.mailProps[i][0], 
                                 style=(wx.RB_GROUP if i==1 else 0))
            if self.mailProps[i][0] == globs.smtpServerProtocol:
                btn.SetValue(True)
            btn.Bind(wx.EVT_RADIOBUTTON, self.OnRadioButton)
            self.onerowfields.append(btn)
            for j in range(len(self.mailProps[0])-1):
                w = wx.TextCtrl(self.panel1, value=str(self.mailProps[i][j+1]))
                if self.mailProps[i][0] == globs.smtpServerProtocol:
                    w.Enable()
                else:
                    w.Disable()
                self.onerowfields.append(w)
            self.fields.append(self.onerowfields) # append to self.fields

        #print(self.fields)
        
        self.useAuthCB = wx.CheckBox(self.panel1, id=wx.ID_ANY)#, style=wx.ALIGN_LEFT) #label='Use Authentication',
        self.useAuthCB.SetLabelMarkup("<span foreground='blue'>%s</span>" % 'Use Authentication')        
        self.useAuthCB.Bind(wx.EVT_CHECKBOX, lambda evt: self.OnUseAuthCB(evt))
        self.useAuthCB.SetValue(globs.smtpServerUseAuth)
        self.useAuthCB.SetToolTip('Use Authentication to Connect to the SMTP Server')

        self.authPrefs = dict()
        w1 = wx.StaticText(self.panel1, label='Username:')
        w2 = wx.TextCtrl(self.panel1, size=wx.Size(200, -1), value=globs.smtpServerUserName)
        w2.Bind(wx.EVT_TEXT, self.OnAuthTC)
        self.authPrefs['Username'] = (w1,w2)

        w3 = wx.StaticText(self.panel1, label='Password:')
        w4 = wx.TextCtrl(self.panel1, size=wx.Size(200, -1), value=globs.smtpServerUserPasswd)
        w4.Bind(wx.EVT_TEXT, self.OnAuthTC)
        self.authPrefs['Password'] = (w3,w4)

        if not self.useAuthCB.GetValue(): # Disable auth parameters if no authentication is required
            w2.Disable()
            w4.Disable()

        # Bottom buttons
        self.btnReset = wx.Button(id=wx.ID_DEFAULT, label='Default', parent=self.panel1, style=0)
        self.btnReset.SetToolTip('Reset to factory defaults')
        self.btnReset.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnReset(evt))
        
        self.btnCancel = wx.Button(label='Cancel', id=wx.ID_ANY, parent=self.panel1, style=0)
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnBtnCancel)

        self.btnApply = wx.Button(id=wx.ID_APPLY, parent=self.panel1, style=0)
        self.btnApply.SetToolTip(u'Apply modifications and Close')
        self.btnApply.Bind(wx.EVT_BUTTON, lambda evt: self.OnBtnApply(evt))

        self._init_sizers()

    def _init_topBS_Items(self, parent):
        parent.Add(self.prefsBS, 0, border=10,
                        flag=wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT)
        parent.Add(self.bottomBS, 1, border=10,
                        flag=wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT)

    def _init_prefsGBS_Items(self, parent):
        lineno = 0
        parent.Add(self.serverST, pos=(lineno,0), border=0, flag=wx.ALL|wx.EXPAND)
        parent.Add(self.serverTC, pos=(lineno,1), border=0, flag=wx.ALL|wx.EXPAND)
        parent.Add(self.useAuthCB, pos=(lineno,2), border=0, flag=wx.ALL|wx.EXPAND)

        # Skip line #1
        
        lineno += 2
        i = 0
        for i in range(len(self.fields)):
            colno = 0
            for w in self.fields[i]:
                parent.Add(w, pos=(lineno,colno), border=0, flag=wx.ALL|wx.EXPAND)
                colno += 1
            lineno += 1

        lineno = 1
        colno  = 2
        i = 0
        for i in range(2):
            parent.Add(self.authPrefs['Username'][i], pos=(lineno,colno+i), border=0, flag=wx.ALL|wx.EXPAND)

        lineno += 1
        colno = 2
        i = 0
        for i in range(2):
            parent.Add(self.authPrefs['Password'][i], pos=(lineno,colno+i), border=0, flag=wx.ALL|wx.EXPAND)
        
    def _init_prefsBS_Items(self, parent):
        parent.Add(self.prefsGBS, proportion=1, border=5, flag=wx.ALL|wx.EXPAND)

    def _init_bottomBS_Items(self, parent):
        parent.Add(wx.Size(4, 4), 2, border=0, flag=0)
        parent.Add(self.btnReset, 0, border=0, flag=0)
        parent.Add(wx.Size(4, 4), 1, border=0, flag=0)
        parent.Add(self.btnCancel, 0, border=0, flag=0)
        parent.Add(wx.Size(8, 4), 0, border=0, flag=0)
        parent.Add(self.btnApply, 0, border=0, flag=0)

    # Create box sizers
    def _init_sizers(self):
        self.topBS    = wx.BoxSizer(orient=wx.VERTICAL)
        self.prefsBS  = wx.StaticBoxSizer(box=self.sb1, orient=wx.HORIZONTAL)
        self.prefsGBS = wx.GridBagSizer(hgap=15, vgap=0)
        self.bottomBS = wx.BoxSizer(orient=wx.HORIZONTAL)

        # Initialize each sizer
        self._init_topBS_Items(self.topBS)
        self._init_prefsGBS_Items(self.prefsGBS)
        self._init_prefsBS_Items(self.prefsBS)
        self._init_bottomBS_Items(self.bottomBS)

    ## Events
    def OnServerTC(self, event):
        event.Skip()
        
    def OnRadioButton(self, event):
        for i in range(1,len(self.fields)):	# Loop thru all radio buttons
            # Enable associated text field for input
            self.fields[i][1].Enable( self.fields[i][0].GetValue())
        event.Skip()

    def OnUseAuthCB(self, event):
        if self.useAuthCB.GetValue():
            self.authPrefs['Username'][1].Enable()
            self.authPrefs['Password'][1].Enable()
        else:
            self.authPrefs['Username'][1].Disable()
            self.authPrefs['Password'][1].Disable()
        event.Skip()

    def OnAuthTC(self, event):
        event.Skip()

    def OnBtnApply(self, event):
        globs.smtpServer = self.serverTC.GetValue()
        for i in range(1,len(self.fields)):	# Loop thru all radio buttons
            if self.fields[i][0].GetValue():	# Check if radio button is selected
                globs.smtpServerProtocol = self.fields[i][0].GetLabel()
                globs.smtpServerPort = int(self.fields[i][1].GetValue())

        if self.useAuthCB.GetValue():
            globs.smtpServerUseAuth = True
            globs.smtpServerUserName   = self.authPrefs['Username'][1].GetValue()
            globs.smtpServerUserPasswd = self.authPrefs['Password'][1].GetValue()
        else:
            globs.smtpServerUseAuth = False
            globs.smtpServerUserName   = ''
            globs.smtpServerUserPasswd = ''
            
        # print(globs.smtpServer)
        # print(globs.smtpServerProtocol)
        # print(globs.smtpServerPort)
        # print(globs.smtpServerUseAuth)
        # print(globs.smtpServerUserName)
        # print(globs.smtpServerUserPasswd)
        
        self.Close()
        self.EndModal(wx.ID_APPLY)
        event.Skip()

    def OnBtnCancel(self, event):
        self.Close()
        self.EndModal(wx.ID_CANCEL)
        event.Skip()

    def OnBtnReset(self, event):
        self._GUIReset()
        event.Skip()

    def _GUIReset(self):
        self.serverTC.SetValue(globs.DEFAULT_SMTP_SERVER)
        
        for i in range(1,len(self.fields)):	# Loop thru all radio buttons
            if self.fields[i][1].GetValue() == globs.DEFAULT_SMTP_SERVER_PROTOCOL:
                self.fields[i][0].SetValue(True)
                break
            
        self.useAuthCB.SetValue(globs.DEFAULT_SMTP_SERVER_USE_AUTH)
        self.authPrefs['Username'][1].SetValue(globs.DEFAULT_SMTP_SERVER_USER_NAME)
        self.authPrefs['Password'][1].SetValue(globs.DEFAULT_SMTP_SERVER_USER_PASSWD)
        
        # globs.smtpServer           = globs.DEFAULT_SMTP_SERVER
        # globs.smtpServerProtocol   = globs.DEFAULT_SMTP_SERVER_PROTOCOL
        # globs.smtpServerPort       = int(globs.DEFAULT_SMTP_SERVER_PORT)
        # globs.smtpServerUseAuth    = str2bool(globs.DEFAULT_SMTP_SERVER_USE_AUTH))
        # globs.smtpServerUserName   = globs.DEFAULT_SMTP_SERVER_USER_NAME
        # globs.smtpServerUserPasswd = globs.DEFAULT_SMTP_SERVER_USER_PASSWD
        
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

        dlg = MailPreferencesDialog(self)
        ret = dlg.ShowModal()
        dlg.Destroy()

        self.Show()

def main():
    # Init Globals instance
    globs.system = platform.system()		# Linux or Windows or MacOS (Darwin)
    globs.pythonVersion = (sys.version).split()[0]	# 2.x or 3.x ?

    globs.smtpServer 		= 'smtp.gmail.com'
    globs.smtpServerProtocol	= 'SMTP'
    globs.smtpServerPort	= 25
    globs.smtpServerUseAuth	= True
    globs.smtpServerUserName	= 'dspoirot@gmail.com'
    globs.smtpServerUserPasswd	= 'foobar'
    
    # Create DemoFrame frame, passing globals instance as parameter
    app = wx.App(False)
    frame = MyFrame(None, -1, title="Test")
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
