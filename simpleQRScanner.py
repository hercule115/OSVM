#! /usr/bin/python
import sys
#sys.path.insert(1, "/usr/local/lib/python3.6/site-packages") # for cv2

import wx
import pyzbar.pyzbar as pyzbar
import numpy as np
import cv2
import time
import os

import builtins as __builtin__
import inspect


moduleList = {'osvmGlobals':'globs'}

for k,v in moduleList.items():
    print('Loading: %s as %s' % (k,v))
    mod = __import__(k, fromlist=[None])
    globals()[v] = globals().pop('mod')	# Rename module in globals()

####
#print(__name__)

# Olympus use a rather simple encoding scheme (kind of Caesar cypher)
# Using the following encoding. 
# All Olympus signatures start with a non-encoded 'OIS1' string to ease
# detection

#          -->      A --> V    L --> K    W --> 9
#        0 --> /    B --> U    M --> J    X --> 8
#        1 --> -    C --> T    N --> I    Y --> 7
#        2 --> +    D --> S    O --> H    Z --> 6
#        3 --> *    E --> R    P --> G    $ --> 5
#        4 --> %    F --> Q    Q --> F    % --> 4
#        5 --> $    G --> P    R --> E    * --> 3
#        6 --> Z    H --> O    S --> D    + --> 2
#        7 --> Y    I --> N    T --> C    - --> 1
#        8 --> X    J --> M    U --> B    , --> ,
#        9 --> W    K --> L    V --> A    / --> 0

# we need 2 helper mappings, from letters to ints and the inverse
C2I = dict(zip(" 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ$%*+-,/",range(44)))
I2C = dict(zip(range(44), " /-+*%$ZYXWVUTSRQPONMLKJIHGFEDCBA987654321,0"))

OISData = ['BOGUS']

def decode(im): 
    # Find barcodes and QR codes
    decodedObjects = pyzbar.decode(im)
    # Print results
    for obj in decodedObjects:
        print('Type : ', obj.type)
        print('Data : ', obj.data,'\n')     
    return decodedObjects

def pyzbarDecode(frame, capturepath):
    global OISData

    OISData = ['BOGUS'] # Reset data

    # Our operations on the frame come here
#    im = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    decodedObjects = decode(frame)

    for decodedObject in decodedObjects: 
        if decodedObject.type != 'QRCODE':
            print('Skipping over non QRCODE object')
            continue

        points = decodedObject.polygon
     
        # If the points do not form a quad, find convex hull
        if len(points) > 4 : 
          hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
          hull = list(map(tuple, np.squeeze(hull)))
        else : 
          hull = points;
         
        # Number of points in the convex hull
        n = len(hull)     
        # Draw the convext hull
        for j in range(0,n):
          cv2.line(frame, hull[j], hull[ (j+1) % n], (255,0,0), 3)

        x = decodedObject.rect.left
        y = decodedObject.rect.top

        barCode = str(decodedObject.data)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, barCode, (x, y), font, 1, (0,255,255), 2, cv2.LINE_AA)

        OISData = decypherData(decodedObject.data.decode("utf-8"))

    # Save the resulting frame if success
    key = cv2.waitKey(1)
    if OISData[0] == 'OIS1':
        print('Saving QR image to Capture.png')
        cv2.imwrite(os.path.join(capturepath, 'Capture.png'), frame)
    return frame

def decypherData(cipherText):
    tmp1 = cipherText.split(',')
    plainText = list()
    # Check for Olympus signature
    if tmp1[0] != 'OIS1':
        print('Invalid QR Code (Not Olympus)')
        return plainText

    plainText.append(tmp1[0])
    for word in tmp1[1:]:
        tmp2 = ''
        for c in word.upper():
            tmp2 += I2C[C2I[c]]
        plainText.append(tmp2)

    print(plainText)
    return plainText

class ShowCapture(wx.Dialog):
    def __init__(self, parent, id, capturepath, title="Scan your Olympus QR Code"):
        wx.Dialog.__init__(self, parent, id, title)
        self.capturepath = capturepath

        self.imgSizer = (640, 480)
        self.panel1 = wx.Panel(self)

        self.mainSizer   = wx.BoxSizer(wx.VERTICAL)
        self.bottomSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btnSizer    = wx.BoxSizer(wx.HORIZONTAL)

        self.image = wx.Image(self.imgSizer[0],self.imgSizer[1])
        self.imageBit = wx.Bitmap(self.image)
        self.staticBit = wx.StaticBitmap(self.panel1, wx.ID_ANY, self.imageBit)

        self.qrInfo = wx.StaticText(self.panel1)

        self.btnContinue = wx.Button(self.panel1, label='Continue')
        self.btnContinue.SetToolTip('Continue scanning')
        self.btnContinue.Bind(wx.EVT_BUTTON, self.OnBtnContinue)
        self.btnContinue.Disable()

        self.btnCancel = wx.Button(self.panel1, id=wx.ID_CANCEL)
        self.btnCancel.SetToolTip('Cancel scanner, Dont use any scanned information')
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnBtnCancel)

        self.btnClose = wx.Button(self.panel1, id=wx.ID_CLOSE)
        self.btnClose.SetToolTip('Close and use detected information (if any)')
        self.btnClose.Bind(wx.EVT_BUTTON, self.OnBtnClose)

        self.btnSizer.Add(self.btnContinue, 0, flag=wx.ALL, border=5)
        self.btnSizer.Add(self.btnCancel, 0, flag=wx.ALL, border=5)
        self.btnSizer.Add(self.btnClose, 0, flag=wx.ALL, border=5)

        self.bottomSizer.Add(self.qrInfo, 0, flag=wx.ALL | wx.ALIGN_LEFT)
        self.bottomSizer.AddStretchSpacer(prop=1)
        self.bottomSizer.Add(self.btnSizer, 0, flag=wx.ALL)

        self.mainSizer.Add(self.staticBit)
        self.mainSizer.Add(wx.StaticLine(self.panel1), 0, flag=wx.ALL|wx.EXPAND, border=5)
        self.mainSizer.Add(self.bottomSizer, flag= wx.EXPAND)#211 | wx.ALIGN_RIGHT)

        # Start acquisition
        self.capture = cv2.VideoCapture(0)
        self.capture.set(3,640)
        self.capture.set(4,480)
        time.sleep(1)

        ret, self.frame = self.capture.read()
        if ret:
            self.height, self.width = self.frame.shape[:2]
            self.bmp = wx.Bitmap.FromBuffer(self.width, self.height, self.frame)

            self.timex = wx.Timer(self)
            self.timex.Start(1000./24)
            self.Bind(wx.EVT_TIMER, self.redraw)
            self.SetSize(self.imgSizer)
        else:
            print('Error no webcam image')
        self.panel1.SetSizer(self.mainSizer)
        self.mainSizer.Fit(self)
        self.Show()
        
    def redraw(self,e):
        global OISData

        ret, self.frame = self.capture.read()
        if ret:
            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            self.frame = pyzbarDecode(self.frame, self.capturepath)
            self.bmp.CopyFromBuffer(self.frame)
            self.staticBit.SetBitmap(self.bmp)
            self.Refresh()
            if OISData[0] == 'OIS1':
                self.timex.Stop()
                m = 'SSID: %s  Password: %s' % (OISData[1], OISData[2])
                s = "<span foreground='blue'>%s</span>" % m
                self.qrInfo.SetLabelMarkup(s)
                self.btnContinue.Enable()

    def OnBtnContinue(self, event):
        self.timex.Start(1000./24)
        self.qrInfo.SetLabel('')
        self.btnContinue.Disable()

    def OnBtnCancel(self, event):
        # When everything done, release the capture
        self.capture.release()
        cv2.destroyAllWindows()
        OISData = ['BOGUS'] # Reset data
        self.EndModal(wx.ID_OK)

    def OnBtnClose(self, event):
        # When everything done, release the capture
        self.capture.release()
        cv2.destroyAllWindows()
        self.EndModal(wx.ID_OK)

########
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

        dlg = ShowCapture(self, -1, globs.tmpDir)
        ret = dlg.ShowModal()
        dlg.Destroy()
        myprint(OISData)
        if OISData[0] == 'OIS1':
            scannedSSID = OISData[1]
            scannedPasswd = OISData[2]
            myprint('Scanned SSID: %s, Scanned Password: %s' % (scannedSSID,scannedPasswd))

        self.Destroy()
        
def main():
    # Init Globals instance
    globs.tmpDir = '/tmp'
    
    app = wx.App(False)
    frame = MyFrame(None, -1, title="Test")
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
