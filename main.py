#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
An example of how to use wx or wxagg in an application with the new
toolbar - comment out the setA_toolbar line for no toolbar
"""

# Used to guarantee to use at least Wx2.8
import wxversion
#wxversion.ensureMinimal('2.8')

from numpy import arange, sin, pi, zeros
import matplotlib
import time
matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

import sys
import wx
import serial
from brewcontroller import BrewController

class CanvasFrame(wx.Frame):

    menuBar = None
    bc = None

    def addMenuItem(self, numId, label, desc, handler):
        tempMenu = wx.Menu()
        tempMenu.Append(numId, label, desc)
        self.Bind(wx.EVT_MENU, handler, id=numId)
        return tempMenu

    def SetTemp(self, event):
        dlg = wx.TextEntryDialog(
                self, 'Input regulator temp (degrees C)',
                'Set regulator temp', '')

        dlg.SetValue("70")

        if dlg.ShowModal() == wx.ID_OK:
            self.bc.set_temp(dlg.GetValue())

        dlg.Destroy()

    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'PyBrew', size=(550,350))

        self.SetBackgroundColour(wx.NamedColor("WHITE"))

        try:
            self.bc = BrewController()
        except Exception as e:
            wx.MessageBox(str(e), 'Fatal error')
            sys.exit(1)

        self.menubar = wx.MenuBar()

        i1 = self.addMenuItem(1, 'Quit', 'Quit application', self.OnQuit)
        self.menubar.Append(i1, '&File')
        
        i2 = self.addMenuItem(2, 'Set temp', 'Set regulator temp', self.SetTemp)
        self.menubar.Append(i2, '&Temp')
        
        self.SetMenuBar(self.menubar)

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.figure = Figure()
        if not hasattr(self, 'subplot'):
            self.axes = self.figure.add_subplot(111)

        self.canvas = FigureCanvas(self, -1, self.figure)
        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons = self.bc.VALVES.keys()
        buttons.sort()
        for k in buttons:
            valve_button = wx.ToggleButton(self, -1, label = self.bc.VALVES[k], name = k)
            valve_button.Bind(wx.EVT_TOGGLEBUTTON, self.OnValve)
            button_sizer.Add(valve_button)
        sizer.Add(button_sizer)

        self.SetSizer(sizer)
        self.Fit()

        self.axes.axis([0, 100, -1, 100])

        self.add_timer()

    def OnValve(self, evt):
        valve = evt.GetEventObject().GetName()
        self.bc.set_valve_open(valve, evt.IsChecked())

    def OnQuit(self, event):
        sys.exit(0)

    curPointXScale = 100
    curPointXRange = 100
    
    xLine = range(0, curPointXRange*1000)
    yLine = zeros(curPointXRange*1000)
    curPointIndex = 0

    sampleTemps = []

   # def sample100ms(self, event):

    
    def draw1000ms(self, event):
        tstart = time.time()

        self.axes.cla()
        self.axes.axis([0, 100, -1, 100])

#        if (len(self.sampleTemps) < 10):
#            return

#        ctemp = int(sum(self.sampleTemps)/len(self.sampleTemps))
#        self.sampleTemps = []

        self.bc.run()

        if (not self.bc.isready()):
            return
        
        ctemp = self.bc.get_temp()
        #self.sampleTemps.append(ctemp)
        print 'Temp:', ctemp
        
        if (ctemp == -255):
            self.yLine[self.curPointIndex] = -1
            self.curPointIndex+=1
            return
        else:
            self.yLine[self.curPointIndex] = ctemp
            self.curPointIndex+=1

        if (self.curPointIndex+self.curPointXScale > self.curPointXRange):
            self.curPointXRange += self.curPointXScale
            #self.xLine = range(0, self.curPointXRange+1)
            #self.yLine = zeros(self.curPointXRange+1)

        line, = self.axes.plot(self.xLine[:self.curPointXRange],
                               self.yLine[:self.curPointXRange], 'k')
        
        self.canvas.draw()


    ##    print 'FPS:' , 200/(time.time()-tstart)

    def add_timer(self):
        #self.sampleTimer = wx.Timer(self, -1)
        #self.Bind(wx.EVT_TIMER, self.sample100ms, self.sampleTimer)
        #self.sampleTimer.Start(milliseconds=100, oneShot=False)
        
        self.drawTimer = wx.Timer(self, -1)
        self.Bind(wx.EVT_TIMER, self.draw1000ms, self.drawTimer)
        self.drawTimer.Start(milliseconds=1000, oneShot=False)

    def OnPaint(self, event):
        self.canvas.draw()

class App(wx.App):

    def OnInit(self):
        'Create the main window and insert the custom frame'
        frame = CanvasFrame()
        frame.Show(True)

        return True

app = App(0)
app.MainLoop()
