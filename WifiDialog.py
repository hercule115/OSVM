#!/usr/bin/env python
import wx
import wx.lib.scrolledpanel as scrolled

import builtins as __builtin__
import inspect
import sys
import platform

import simpleQRScanner

import osvmGlobals

####
#print(__name__)

class WifiDialog(wx.Dialog):
    """
    Creates and displays a dialog to select the WIFI network to connect
    """
    def __init__(self, parent, globs):
        """
        Initialize the preferences dialog box
        """
        myStyle = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
        wx.Dialog.__init__(self, None, wx.ID_ANY, 'WIFI Selector', style=myStyle)

        self.parent = parent
        self.net = None # Selected network
        self.netkey = None
        self.favoriteCbList = list()

        # Build allNetworks list
        error = scanForNetworks(globs)
        if error:
            print(error)

        self._initialize(globs)

        self.panel2.SetSizer(self.gsNet)
        self.panel2.SetAutoLayout(True)
        self.panel2.SetupScrolling()

        self.panel1.SetSizerAndFit(self.topBoxSizer)
        self.SetClientSize(self.topBoxSizer.GetSize())
        self.Centre()

    def _initialize(self, globs):
        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self, size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)
        self.panel2 = scrolled.ScrolledPanel(parent=self.panel1, id=wx.ID_ANY, size=(680,200), style=wx.TAB_TRAVERSAL)

        self.wintitle = wx.StaticText(self.panel1)
        if globs.viewMode:
            m = "<big><span foreground='blue'>%s</span></big>" % 'Select a WIFI Network'
        else:
            m = "<big><span foreground='blue'>%s</span></big>" % 'Select the Camera Access Point'
        self.wintitle.SetLabelMarkup(m)

        # Sort networks by RSSI
        self.netwSorted = sorted(globs.allNetworks, key=lambda x: x[globs.NET_RSSI], reverse=True)

        # Store all WIFI networks information in a list
        self.netProps = list()
        self.netProps.append(('SSID', 'RSSI', 'Channel', 'BSSID', 'Security', 'Known', 'Favorite')) # Header
        for n in self.netwSorted:
            self.netProps.append((n[globs.NET_SSID],n[globs.NET_RSSI],n[globs.NET_CHANNEL],n[globs.NET_BSSID],n[globs.NET_SECURITY],n[globs.NET_KNOWN],n[globs.NET_FAVORITE]))
        # Grid containing the information
        rows = len(self.netProps)
        cols = len(self.netProps[0])
        self.gsNet = wx.FlexGridSizer(rows, cols, vgap=5, hgap=10)

        # Create all individual widgets in self.fields(). Each entry contains a list
        # of fields for each network
        self.fields = list()

        # Directory. key = (SSID,BSSID) value = Radiobutton
        self.btnDir = {}

        # first line header
        self.onerowfields = list()
        for i in range(len(self.netProps[0])):
            field = wx.StaticText(self.panel2)
            field.SetLabelMarkup("<span foreground='blue'>%s</span>" % self.netProps[0][i])
            self.onerowfields.append(field)
        self.fields.append(self.onerowfields) # append to self.fields

        for i in range(1,rows):
            self.onerowfields = list()
            btn = wx.RadioButton(self.panel2, 
                                 label=self.netProps[i][0],
                                 name=self.netProps[i][0], 
                                 style=(wx.RB_GROUP if i==1 else 0)) # SSID
            btn.Bind(wx.EVT_RADIOBUTTON, self.OnRadioButton)
            self.onerowfields.append(btn)
            for j in range(1,len(self.netProps[0])-2):
                self.onerowfields.append(wx.StaticText(self.panel2, label=str(self.netProps[i][j])))
            # Known Network checkbox
            knownCb = wx.CheckBox(self.panel2, label='')
            knownCb.SetValue(self.netProps[i][len(self.netProps[0])-2])
            knownCb.Bind(wx.EVT_CHECKBOX, lambda evt, temp=globs: self.OnKnownCb(evt, temp))
            self.onerowfields.append(knownCb)
            # Favorite Network checkbox
            favoriteCb = wx.CheckBox(self.panel2, label='')
            favoriteCb.SetValue(self.netProps[i][len(self.netProps[0])-1])
            #            favoriteCb.Bind(wx.EVT_CHECKBOX, self.OnFavoriteCb)
            favoriteCb.Bind(wx.EVT_CHECKBOX, lambda evt, temp=globs: self.OnFavoriteCb(evt, temp))
            self.onerowfields.append(favoriteCb)
            self.favoriteCbList.append(favoriteCb)
            # Create directory entry. key=(SSID,BSSID)
            k = (self.netwSorted[i-1][globs.NET_SSID],self.netwSorted[i-1][globs.NET_BSSID])
            self.btnDir[k] = btn
            if globs.iface.ssid() == btn.GetLabel() and globs.iface.bssid() == self.netwSorted[i-1][globs.NET_BSSID]:
                btn.SetValue(True)
                self.netkey = k
                myprint('Current Network:',k)
                self.panel2.ScrollChildIntoView(btn)
            self.fields.append(self.onerowfields) # append to self.fields

        # Add all widgets in the grid
        for r in range(rows):
            onerowfields = self.fields[r]
            for w in onerowfields:
                self.gsNet.Add(w, proportion=0, flag=wx.EXPAND)

        # widgets at the Bottom 
        # Scan QR Code button
        self.btnScanQR = wx.Button(id=wx.ID_ANY, label='Scan QR Code', parent=self.panel1, style=0)
        self.btnScanQR.SetToolTip('Scan QR Code from Camera')
#        self.btnScanQR.Bind(wx.EVT_BUTTON, self.OnBtnScanQR)
        self.btnScanQR.Bind(wx.EVT_BUTTON, lambda evt, temp=globs: self.OnBtnScanQR(evt, temp))
            
        # Cancel button
        self.btnCancel = wx.Button(id=wx.ID_CANCEL, parent=self.panel1, style=0)
        self.btnCancel.SetToolTip('Discard changes')
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnBtnCancel)

        # OK button
        self.btnOK = wx.Button(id=wx.ID_OK, parent=self.panel1, style=0)
        self.btnOK.SetToolTip('Close this Dialog and Proceed')
#        self.btnOK.Bind(wx.EVT_BUTTON, self.OnBtnOK)
        self.btnOK.Bind(wx.EVT_BUTTON,  lambda evt, temp=globs: self.OnBtnOK(evt, temp))
        self.btnOK.SetDefault()

        self.timer = wx.Timer(self)
#        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.timer.Bind(wx.EVT_TIMER, lambda evt, temp=globs: self.OnTimer(evt, temp))
        self.timer.Start(5000)

        self._init_sizers()

    def _init_topBoxSizer_Items(self, parent):
        parent.Add(self.titleBoxSizer, 0, border=10, flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER)
        parent.Add(self.panel2, 1, border=10, flag=wx.EXPAND | wx.ALL)
        parent.Add(self.bottomBoxSizer, 0, border=10, flag=wx.ALL | wx.ALIGN_RIGHT)

    def _init_titleBoxSizer_Items(self, parent):
        parent.Add(4, 4, 1, border=0, flag=wx.EXPAND)
        parent.Add(self.wintitle, 2, border=0, flag=wx.EXPAND)
        parent.Add(4, 4, 1, border=0, flag=wx.EXPAND)

    def _init_bottomBoxSizer_Items(self, parent):
        parent.Add(self.btnScanQR, 0, border=0, flag=wx.EXPAND)
        parent.Add(16, 4, border=0, flag=wx.EXPAND)
        parent.Add(self.btnCancel, 0, border=0, flag=wx.EXPAND)
        parent.Add(4, 4, border=0, flag=wx.EXPAND)
        parent.Add(self.btnOK, 0, border=0, flag=wx.EXPAND)

    def _init_sizers(self):
        # Create box sizers
        self.topBoxSizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.titleBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.bottomBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        # Initialize each sizer
        self._init_topBoxSizer_Items(self.topBoxSizer)
        self._init_titleBoxSizer_Items(self.titleBoxSizer)
        self._init_bottomBoxSizer_Items(self.bottomBoxSizer)

    # Events
    def OnRadioButton(self, event):
        button = event.GetEventObject()
        for k,v in self.btnDir.items():
            if v == button:
                myprint('Selecting Network:',k)
                self.netkey = k
        event.Skip()

    def OnFavoriteCb(self, event, globs):
        cb = event.GetEventObject()
        self.timer.Stop()

        oldValue = cb.GetValue()

        # Disable all favorite checkboxes
        for w in self.favoriteCbList:
            w.SetValue(False)

        # Set this checkbox
        cb.SetValue(oldValue)

        if oldValue == False: # Clear favoriteNetwork
            globs.favoriteNetwork = ('','')
            self.timer.Start(5000)
            event.Skip()
            return

        # Get associated network
        for onerowfields in self.fields:
            if cb in onerowfields:
                ssid = onerowfields[0].GetLabel()
                for net in globs.allNetworks:
                    if net[globs.NET_SSID] == ssid:
                        break
        globs.favoriteNetwork = (net[globs.NET_SSID],net[globs.NET_BSSID])
        self.timer.Start(5000)
        event.Skip()

    def OnKnownCb(self, event, globs):
        cb = event.GetEventObject()
        self.timer.Stop()

        # Get associated network
        for onerowfields in self.fields:
            if cb in onerowfields:
                ssid = onerowfields[0].GetLabel()
                for net in globs.allNetworks:
                    if net[globs.NET_SSID] == ssid:
                        break

        if cb.GetValue():
            # Popup a dialog to ask for this known network password
            dlg = PasswordDialog(net=net, globs=globs)
            ret = dlg.ShowModal()
            if ret == wx.ID_CANCEL:
                cb.SetValue(False)
            dlg.Destroy()
        else:
            # Popup a dialog to ask for removing this known network password
            # Ask confirmation
            dlg = wx.MessageDialog(None, 
                                   'Do you really want to DELETE password for Network %s ?' % ssid, 
                                   'Question', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
            ret = dlg.ShowModal()
            if ret == wx.ID_YES:
                delKnownNetwork(net[globs.NET_SSID], net[globs.NET_BSSID], globs)

        self.timer.Start(5000)
        event.Skip()

    def OnBtnOK(self, event, globs):
        for i in range(1, len(self.fields)): # Skip header
            onerowfields = self.fields[i]
            btn = onerowfields[0]
            if btn.GetValue() and btn.GetLabel() == self.netkey[globs.NET_SSID]:
                try:
                    self.net = self.netwSorted[i-1] # -1 for header
                except:
                    self.net = None
                else:
                    myprint('Using network:',self.net)
                    break
        if not self.net:
            self.EndModal(wx.ID_OK)
            return

        self.timer.Stop()

        if globs.iface.ssid() == self.net[globs.NET_SSID] and globs.iface.bssid() == self.net[globs.NET_BSSID]:
            myprint('Using already selected network')
            self.EndModal(wx.ID_OK)
            event.Skip()
            return

        # Check for open network
        if self.net[globs.NET_SECURITY] == '':
            myprint('No password required. Connecting to %s' % self.net[globs.NET_SSID])
            success, error = globs.iface.associateToNetwork_password_error_(self.net[globs.NET_NET], None, None)
            if success:
                self.EndModal(wx.ID_OK)
                event.Skip()
                return
            else:
                print(error)
                self.EndModal(ID_CONNECT_ERROR)
                event.Skip()
                return

        # Check for already known network
        for kn in globs.knownNetworks: # kn='ssid,bssid,passwd'
            params = kn.split(',')
            if self.net[globs.NET_SSID] == params[globs.NET_SSID] and self.net[globs.NET_BSSID] == params[globs.NET_BSSID]:
                password = params[globs.NET_PASSWD]
                myprint('Connecting to known network %s, bssid %s password %s' % (self.net[globs.NET_SSID], self.net[globs.NET_BSSID], password))
                success, error = globs.iface.associateToNetwork_password_error_(self.net[globs.NET_NET], password, None)
                if success:
                    self.EndModal(wx.ID_OK)
                    event.Skip()
                    return
                else:
                    print(error)
                    # Remove entry from knownNetworks
                    delKnownNetwork(params[globs.NET_SSID], params[globs.NET_BSSID], globs)
                    # Known password is invalid, Ask for a new password
                    dlg = PasswordDialog(net=self.net, globs=globs)
                    ret = dlg.ShowModal()
                    dlg.Destroy()
                    return

        # Unknown network/password
        dlg = PasswordDialog(net=self.net, globs=globs)
        ret = dlg.ShowModal()
        dlg.Destroy()
        self.EndModal(wx.ID_OK)
        event.Skip()

    def OnBtnScanQR(self, event, globs):
        myprint('Launching QR Scanner')
        dlg = simpleQRScanner.ShowCapture(self, -1, globs.tmpDir)
        ret = dlg.ShowModal()
        dlg.Destroy()
        myprint('End of Capture Session')
#        simpleQRScanner.OISData = ['OIS1', 'TG-4-P-BHJ310474', '69074749']
#        simpleQRScanner.OISData = ['OIS1', 'HomeSweetHome_EXT', '2128819390']
        print(simpleQRScanner.OISData)
        if simpleQRScanner.OISData[0] == 'OIS1':
            scannedSSID = simpleQRScanner.OISData[1]
            scannedPasswd = simpleQRScanner.OISData[2]
            myprint('Looking for scanned SSID %s in detected networks' % scannedSSID)
            for onerowfields in self.fields:
                ssid = onerowfields[0].GetLabel()
                if ssid == scannedSSID:
                    break
            #print(onerowfields)
            for net in globs.allNetworks:
                if net[globs.NET_SSID] == scannedSSID:
                    break
            #print(net)
	    # Add scanned network to knownNetworks
            addKnownNetwork(scannedSSID,net[globs.NET_BSSID],scannedPasswd,globs)
            # Simulate a radiobutton press to select the scanned network
            evt = wx.PyCommandEvent(wx.EVT_RADIOBUTTON.typeId, onerowfields[0].GetId())
            evt.SetEventObject(onerowfields[0])
            wx.PostEvent(onerowfields[0], evt)
            event.Skip()

    def OnBtnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)
        event.Skip()

    def OnTimer(self, event, globs):
        error = scanForNetworks(globs)
        if error:
            print(error)
            return
        self.SetTitle('WIFI Selector: %d networks detected' % len(globs.allNetworks))

        # Sort allNetworks by RSSI
        self.netwSorted = sorted(globs.allNetworks, key=lambda x: x[globs.NET_RSSI], reverse=True)

        # Store all WIFI networks information in a list
        self.netProps = list()
        self.netProps.append(('SSID', 'RSSI', 'Channel', 'BSSID', 'Security', 'Known', 'Favorite')) # Header
        for n in self.netwSorted:
            self.netProps.append((n[globs.NET_SSID],n[globs.NET_RSSI],n[globs.NET_CHANNEL],n[globs.NET_BSSID],n[globs.NET_SECURITY],n[globs.NET_KNOWN],n[globs.NET_FAVORITE]))
        rows = len(self.netProps)
        cols = len(self.netProps[0])

        # Delete all existing widgets in the grid
        for onerowfields in self.fields: 
            for w in onerowfields:
                w.Destroy()

        # Create all individual widgets in self.fields
        self.fields = list()

        # Create a directory containing the radio buttons
        self.btnDir = {}

        # Clear existing list of favorite checkboxes
        self.favoriteCbList = list()

        # first line header
        self.onerowfields = list()
        for i in range(len(self.netProps[0])):
            field = wx.StaticText(self.panel2)
            field.SetLabelMarkup("<span foreground='blue'>%s</span>" % self.netProps[0][i])
            self.onerowfields.append(field)
        self.fields.append(self.onerowfields) # append to self.fields

        if self.net:
            myprint(self.netkey)

        for i in range(1,rows):
            self.onerowfields = list()
            btn = wx.RadioButton(self.panel2, label=self.netProps[i][0], style=(wx.RB_GROUP if i==1 else 0)) # SSID
            btn.SetLabelMarkup("<b>%s</b>" % self.netProps[i][0])
            btn.Bind(wx.EVT_RADIOBUTTON, self.OnRadioButton)
            self.onerowfields.append(btn)
            for j in range(1,len(self.netProps[0])-2):#-1
                self.onerowfields.append(wx.StaticText(self.panel2, label=str(self.netProps[i][j])))
            knownCb = wx.CheckBox(self.panel2, label='')
            knownCb.SetValue(self.netProps[i][len(self.netProps[0])-2]) #-1
            knownCb.Bind(wx.EVT_CHECKBOX, self.OnKnownCb)
            self.onerowfields.append(knownCb)
            # Favorite Checkbox button
            favoriteCb = wx.CheckBox(self.panel2, label='')
            favoriteCb.SetValue(self.netProps[i][len(self.netProps[0])-1])
            favoriteCb.Bind(wx.EVT_CHECKBOX, self.OnFavoriteCb)
            self.favoriteCbList.append(favoriteCb)
            self.onerowfields.append(favoriteCb)

            self.fields.append(self.onerowfields) # append to self.fields

            # Create a new directory entry
            k = (self.netwSorted[i-1][globs.NET_SSID],self.netwSorted[i-1][globs.NET_BSSID]) # -1 for header
            self.btnDir[k] = btn 

#        self.panel2.Refresh()

        if self.netkey:
            try:
                btn = self.btnDir[self.netkey]
                btn.SetValue(True)
                self.panel2.ScrollChildIntoView(btn)
            except:
                myprint('Network has disapeared:',self.net)
                self.net = None
        else:
            k = (iface.ssid(),iface.bssid())
            try:
                btn = self.btnDir[k]
                print('1',btn.GetLabel())
                btn.SetValue(True)
                self.panel2.ScrollChildIntoView(btn)
            except:
                pass

        # Add all widgets in the grid
        self.gsNet.SetRows(rows)
        for r in range(rows):
            onerowfields = self.fields[r]
            for w in onerowfields:
                self.gsNet.Add(w, proportion=0, flag=wx.EXPAND)

        self.panel2.SetAutoLayout(1)
        self.panel2.SetupScrolling()


#
# Scan for networks, update the allNetworks list
#
def scanForNetworks(globs):
    setBusyCursor(True)
    networks, error = globs.iface.scanForNetworksWithName_error_(None, None)
    setBusyCursor(False)
    if error:
        return error

    globs.allNetworks = list()
    for n in networks:
        n_ssid         = n.ssid()
        n_rssi         = n.rssiValue()
        n_channel      = n.channel()
        n_bssid        = n.bssid()
        n_securityMode = globs.CWSecurityModes[n.securityMode()]
        n_known = False
        n_favorite = False
        for kn in globs.knownNetworks:
                ssid,bssid,passwd = kn.split(',')
                if n_ssid == ssid and n_bssid == bssid:
                    n_known = True
                    break
        if globs.favoriteNetwork[globs.NET_SSID] == n_ssid and globs.favoriteNetwork[globs.NET_BSSID] == n_bssid:
            n_favorite = True
        globs.allNetworks.append((n_ssid,n_bssid,'',n_rssi,n_channel,n_securityMode,n_known,n_favorite,n))
    return None

#
# Update the knownNetworks global list if needed
#
def addKnownNetwork(ssid, bssid, password, globs):
    v = '%s,%s,%s' % (ssid,bssid,password)
    myprint('Adding %s' % v)

    for i in range(len(globs.knownNetworks)):
        if globs.knownNetworks[i] == v:
            myprint(v, 'is already known')
            return
    globs.knownNetworks.append(v)
    myprint('Added %s' % v)

    #DPDPDP
# 
# Remove a network from knownNetworks
#
def delKnownNetwork(ssid, bssid, globs):
    sub = '%s,%s' % (ssid,bssid)
    myprint('Removing %s' % sub)
    e = [s for s in globs.knownNetworks if sub in s]
    globs.knownNetworks.remove(e[0])
    myprint('Removed %s' % e)

def switchToFavoriteNetwork(globs):
    if globs.iface.ssid() == globs.favoriteNetwork[globs.NET_SSID] and globs.iface.bssid() == globs.favoriteNetwork[globs.NET_BSSID]:
        # Nothing to do
        return 0

    myprint('Switching to favorite network:', globs.favoriteNetwork)

    # Update network list
    error = scanForNetworks(globs)
    if error:
        myprint(error)
        return -1

    # Check in all networks
    ssid = None
    for net in globs.allNetworks:
        if net[globs.NET_SSID] == globs.favoriteNetwork[globs.NET_SSID] and net[globs.NET_BSSID] == globs.favoriteNetwork[globs.NET_BSSID]:
            for kn in globs.knownNetworks: # kn='ssid,bssid,passwd'
                knParms = kn.split(',')
                if knParms[globs.NET_SSID] == globs.favoriteNetwork[globs.NET_SSID] and knParms[globs.NET_BSSID] == globs.favoriteNetwork[globs.NET_BSSID]:
                    ssid = knParms[globs.NET_SSID]
                    bssid = knParms[globs.NET_BSSID]
                    password = knParms[globs.NET_PASSWD]
                    break
            break
    if ssid is None:
        myprint('Favorite network not found in networks list')
        return -1

    myprint('Connecting to known network %s, bssid %s password %s' 
          % (ssid, bssid, password))
    success, error = globs.iface.associateToNetwork_password_error_(net[globs.NET_NET], password, None)
    if success:
        return 0
    myprint(error)
    return -1

#### PasswordDialog
class PasswordDialog(wx.Dialog):
    """
    Creates and displays a dialog to enter a password
    """
    def __init__(self, net, globs):
        self.net = net

        myStyle = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
        wx.Dialog.__init__(self, None, wx.ID_ANY, 'Network Password', style=myStyle)

        self._initialize(globs)

        self.panel1.SetSizerAndFit(self.topBoxSizer)
        self.SetClientSize(self.topBoxSizer.GetSize())
        self.Centre()

    def _initialize(self, globs):
        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self, size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        self.wintitle = wx.StaticText(self.panel1)
        t = 'Enter Password to connect to: '
        m = "<span foreground='red'>%s</span><big><span foreground='blue'>%s</span></big>" % (t,self.net[globs.NET_SSID])
        self.wintitle.SetLabelMarkup(m)

        self.passwdST = wx.StaticText(id=wx.ID_ANY, label='Password:', parent=self.panel1, style=0)
        self.passwdHideTC = wx.TextCtrl(id=wx.ID_ANY,
                                        parent=self.panel1, 
                                        style=wx.TE_PROCESS_ENTER | wx.TE_PASSWORD, 
                                        size=wx.Size(300, -1))
        self.passwdHideTC.SetToolTip('Enter password')
        self.passwdHideTC.SetAutoLayout(True)
        self.passwdHideTC.SetCursor(wx.STANDARD_CURSOR)
        self.passwdHideTC.Bind(wx.EVT_TEXT_ENTER, self.OnPasswdTC)
        self.passwdHideTC.SetFocus()

        self.passwdShowTC = wx.TextCtrl(id=wx.ID_ANY,
                                        parent=self.panel1, 
                                        style=wx.TE_PROCESS_ENTER,
                                        size=wx.Size(300, -1))
        self.passwdShowTC.SetToolTip('Enter password')
        self.passwdShowTC.SetAutoLayout(True)
        self.passwdShowTC.SetCursor(wx.STANDARD_CURSOR)
        self.passwdShowTC.Bind(wx.EVT_TEXT_ENTER, self.OnPasswdTC)
        self.passwdShowTC.Hide()

        self.cb1 = wx.CheckBox(self.panel1, id=wx.ID_ANY, label='Save Password')
        self.cb1.SetValue(True)

        self.cb2 = wx.CheckBox(self.panel1, id=wx.ID_ANY, label='Show Password')
        self.cb2.SetValue(False)
        self.cb2.Bind(wx.EVT_CHECKBOX, self.OnCb2)

        # widgets at the Bottom 
        # Cancel button
        self.btnCancel = wx.Button(id=wx.ID_CANCEL, parent=self.panel1, style=0)
        self.btnCancel.SetToolTip('Discard changes')
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnBtnCancel)

        # OK button
        self.btnOK = wx.Button(id=wx.ID_OK, parent=self.panel1, style=0)
        self.btnOK.SetToolTip('Save changes')
#        self.btnOK.Bind(wx.EVT_BUTTON, self.OnBtnOK)
        self.btnOK.Bind(wx.EVT_BUTTON, lambda evt, temp=globs: self.OnBtnOK(evt, temp))

        # Connect button
        self.btnConnect = wx.Button(id=wx.ID_ANY, label='Connect', 
                                    parent=self.panel1, style=0)
        self.btnConnect.SetToolTip('Connect to this network')
#        self.btnConnect.Bind(wx.EVT_BUTTON, self.OnBtnConnect)
        self.btnConnect.Bind(wx.EVT_BUTTON, lambda evt, temp=globs: self.OnBtnConnect(evt, temp))

        self._init_sizers()

    def _init_topBoxSizer_Items(self, parent):
        parent.Add(self.titleBoxSizer, 0, border=10, flag=wx.ALL | wx.EXPAND | wx.ALIGN_CENTER)
        parent.Add(self.passwdBoxSizer, 1, border=10, flag=wx.EXPAND | wx.ALL)
        parent.Add(self.bottomBoxSizer, 0, border=10, flag=wx.ALL | wx.ALIGN_RIGHT)

    def _init_titleBoxSizer_Items(self, parent):
        parent.Add(0, 4, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.wintitle, 1, border=0, flag=wx.EXPAND)
        parent.Add(0, 4, 0, border=0, flag=wx.EXPAND)

    def _init_passwdBoxSizer_Items(self, parent):
        parent.Add(self.passwdSubBoxSizer1, 0, border=0, flag=wx.EXPAND | wx.ALL)
        parent.Add(0, 16, 1, border=0, flag=wx.EXPAND)
        parent.Add(self.passwdSubBoxSizer2, 0, border=0, flag=wx.EXPAND | wx.ALL)

    def _init_passwdSubBoxSizer1_Items(self, parent):
        parent.Add(self.passwdST, 0, border=0, flag=wx.EXPAND | wx.ALL)
        parent.Add(4, 4, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.passwdShowTC, 0, border=0, flag=wx.EXPAND | wx.ALL)
        parent.Add(self.passwdHideTC, 0, border=0, flag=wx.EXPAND | wx.ALL)

    def _init_passwdSubBoxSizer2_Items(self, parent):
        parent.Add(self.cb1, 0, border=0, flag=wx.EXPAND | wx.ALL)
        parent.Add(4, 4, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.cb2, 0, border=0, flag=wx.EXPAND | wx.ALL)

    def _init_bottomBoxSizer_Items(self, parent):
        parent.Add(self.btnCancel, 0, border=0, flag=wx.EXPAND)
        parent.Add(4, 4, border=0, flag=wx.EXPAND)
        parent.Add(self.btnOK, 0, border=0, flag=wx.EXPAND)
        parent.Add(4, 4, border=0, flag=wx.EXPAND)
        parent.Add(self.btnConnect, 0, border=0, flag=wx.EXPAND)

    def _init_sizers(self):
        # Create box sizers
        self.topBoxSizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.titleBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.passwdBoxSizer = wx.BoxSizer(orient=wx.VERTICAL)
        self.passwdSubBoxSizer1 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.passwdSubBoxSizer2 = wx.BoxSizer(orient=wx.VERTICAL)
        self.bottomBoxSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        # Initialize each sizer
        self._init_topBoxSizer_Items(self.topBoxSizer)
        self._init_titleBoxSizer_Items(self.titleBoxSizer)
        self._init_passwdBoxSizer_Items(self.passwdBoxSizer)
        self._init_passwdSubBoxSizer1_Items(self.passwdSubBoxSizer1)
        self._init_passwdSubBoxSizer2_Items(self.passwdSubBoxSizer2)
        self._init_bottomBoxSizer_Items(self.bottomBoxSizer)

    def OnCb2(self, event):
        if self.cb2.GetValue():
            self.passwdShowTC.Show(True)
            self.passwdHideTC.Show(False)
            self.passwdShowTC.SetValue(self.passwdHideTC.GetValue())
            self.passwdShowTC.SetFocus()
        else:
            self.passwdShowTC.Show(False)
            self.passwdHideTC.Show(True)
            self.passwdHideTC.SetValue(self.passwdShowTC.GetValue())
            self.passwdHideTC.SetFocus()
        self.passwdHideTC.GetParent().Layout()
        event.Skip()
            
    def OnPasswdTC(self, event):
        event.Skip()

    def OnBtnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnBtnOK(self, event, globs):
        if self.cb2.GetValue():
            passwd = self.passwdShowTC.GetValue()
        else:
            passwd = self.passwdHideTC.GetValue()
        myprint(self.net,'password:', passwd)
        addKnownNetwork(self.net[globs.NET_SSID],self.net[globs.NET_BSSID],passwd,globs)
        self.EndModal(wx.ID_OK)
        event.Skip()

    def OnBtnConnect(self, event, globs):
        if self.cb2.GetValue():
            passwd = self.passwdShowTC.GetValue()
        else:
            passwd = self.passwdHideTC.GetValue()

        print('OnBtnConnect(): network:',self.net,'password:', passwd)
        success, error = globs.iface.associateToNetwork_password_error_(self.net[globs.NET_NET], passwd, None)
        if success:
            print('success')
            if self.cb1.GetValue(): # Must save network entry
                print('Must save Network Entry:',self.net[globs.NET_SSID],self.net[globs.NET_BSSID],passwd)
                addKnownNetwork(self.net[globs.NET_SSID],self.net[globs.NET_BSSID],passwd,globs)
            self.EndModal(wx.ID_OK)
            event.Skip()
        else:
            print(error)

################################################
class MyFrame(wx.Frame):
    def __init__(self, parent, id, title, globs):
        wx.Frame.__init__(self, parent, id, title)
        panel = wx.Panel(self)
        dlg = WifiDialog(self, globs)
        ret = dlg.ShowModal()
        dlg.Destroy()

        self.Show()

def main():
    # Create Globals instance
    g = osvmGlobals.myGlobals()

    g.system = platform.system()    # Linux or Windows or MacOS (Darwin)

    try:
        import objc # WifiDialog
    except ImportError:
        msg = 'Objc module not installed. Disabling Network Selector'
        print(msg)
        g.networkSelector = False
        g.disabledModules.append(('Objc',msg))
    else:
        g.networkSelector = True
    
    # Init network (Mac only!!!)
    if g.system == 'Darwin' and g.networkSelector:
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

        g.iface = CWInterface.interface()
        if not g.iface:
            print('No Network Interface')
    
    # Create DemoFrame frame, passing globals instance as parameter
    app = wx.App(False)
    frame = MyFrame(None, -1, title="Test", globs=g)
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    #
    # Set/unset busy cursor (from thread)
    #
    def setBusyCursor(state):
        if state:
            wx.BeginBusyCursor(cursor=wx.HOURGLASS_CURSOR)
        else:
            wx.EndBusyCursor()

    def myprint(*args, **kwargs):
        """My custom print() function."""
        # Adding new arguments to the print function signature 
        # is probably a bad idea.
        # Instead consider testing if custom argument keywords
        # are present in kwargs
        __builtin__.print('%s():' % inspect.stack()[1][3], *args, **kwargs)

    main()
