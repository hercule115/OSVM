#!/usr/bin/env python
import wx
import wx.html

import sys
import os
import inspect

#import osvmGlobals
moduleList = ['osvmGlobals']

for m in moduleList:
    print('Loading: %s' % m)
    mod = __import__(m, fromlist=[None])
    globals()[m] = globals().pop('mod')	# Rename module in globals()

####
#print(__name__)

defHelpText = """<p>Sorry, the Help file cannot be found on your system. Please check your installation for file <b>help.htm</b>"""

class HtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id, size=(600,400)):
        wx.html.HtmlWindow.__init__(self, parent, id, size=size)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()

    def OnLinkClicked(self, link):
        wx.LaunchDefaultBrowser(link.GetHref())

class HelpDialog(wx.Dialog):
    def __init__(self, parent, globs):
        myStyle = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL
        wx.Dialog.__init__(self, None, wx.ID_ANY, "Help on %s" % (globs.myLongName), style=myStyle)

        self.panel1 = wx.Panel(id=wx.ID_ANY, name='panel1', parent=self,
                               size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)

        # Create a HTML window
        self.hwin = HtmlWindow(parent=self.panel1, id=wx.ID_ANY, size=(800,600))

        # Open the file containing the HTML info
        try:
            f = open(globs.helpPath, 'r', encoding="ISO-8859-1")
        except IOError as e:
            msg = "HelpDialog(): I/O error %s %s" % ("({0}): {1}".format(e.errno, e.strerror), globs.helpPath)
            print(msg)
            helpText = defHelpText
        else:
            helpText = f.read()
            f.close()

        # Display the HTML page
        self.hwin.SetPage(helpText)

        # Button to close the Help dialog
        self.btnClose = wx.Button(label='Close', id=wx.ID_CLOSE, parent=self.panel1, style=0)
        self.btnClose.Bind(wx.EVT_BUTTON, self.OnBtnClose)
        
        # Everything in a BoxSizer
        self.topBoxSizer = wx.BoxSizer(orient=wx.VERTICAL) 
        self.topBoxSizer.Add(self.hwin, 0, border=0, flag=0)
        self.topBoxSizer.Add(4, 4, 0, border=0, flag=0)
        self.topBoxSizer.Add(self.btnClose, 0, border=0, flag=wx.ALL | wx.EXPAND)
        
        self.panel1.SetSizerAndFit(self.topBoxSizer)
        self.SetClientSize(self.topBoxSizer.GetSize())
        self.Centre()
        self.SetFocus()

    def OnBtnClose(self, event):
        self.Close()
        event.Skip()

########################
def module_path(local_function):
    ''' returns the module path without the use of __file__.  
    Requires a function defined locally in the module.
    from http://stackoverflow.com/questions/729583/getting-file-path-of-imported-module'''
    return os.path.abspath(inspect.getsourcefile(local_function))
        
class MyFrame(wx.Frame):
    def __init__(self, parent, id, title, globs):
        wx.Frame.__init__(self, parent, id, title)
        panel = wx.Panel(self)
        dlg = HelpDialog(self, globs)
        ret = dlg.ShowModal()
        dlg.Destroy()

        self.Show()

def main():
    # Create Globals instance
    g = osvmGlobals.myGlobals()

    g.modPath         = module_path(main)
    g.helpPath        = os.path.join(os.path.dirname(g.modPath), 'help.htm')
    
    # Create DemoFrame frame, passing globals instance as parameter
    app = wx.App(False)
    frame = MyFrame(None, -1, title="Test", globs=g)
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()
        
