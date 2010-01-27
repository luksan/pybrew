#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import serial

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qwt5 import *

from pybrewMainWindow import MainWindow

from brewcontroller import BrewController, BrewControllerException

class Pybrew(MainWindow):
    def __init__(self):
        MainWindow.__init__(self)

        self.tempUpdateInterval = 1000 # update interval in milliseconds
        
        self.target_temp = 0

        try:
            self.bc = BrewController(3)
        except BrewControllerException as e:
            QMessageBox.critical(None, "Fatal error", str(e))
            sys.exit(1)
        
        self.set_target_temp(self.bc.get_target_temp())

        buttons = self.bc.VALVES.keys()
        buttons.sort()
        self.valve_buttons = []
        def get_callback(id, button):
            def cb():
                self.valve_button_clicked(id, button)
            return cb

        for k in buttons:
            v = QPushButton(self.bc.VALVES[k], self)
            v.connect(v, SIGNAL('clicked()'), get_callback(k, v))
            v.setObjectName(k)
            v.setCheckable(True)
            self.valveButtonLayout.addWidget(v)
            self.valve_buttons.append(v)
            
        self.tempCurve = QwtPlotCurve("Temperature")
        self.tempCurve.attach(self.tempQwtPlot)
        
        self.tempXData = []
        self.tempYData = []
        
        self.Thermo.setAlarmLevel(25)
        self.Thermo.setAlarmColor(Qt.green)

        self.tempUpdateTimer = QTimer(self)
        self.connect(self.tempUpdateTimer, SIGNAL('timeout()'), self.tempUpdateEvent)
        self.tempUpdateTimer.start(self.tempUpdateInterval)
            
    def setTargetTempEvent(self):
        temp = self.targetTempLineEdit.text()
        self.set_target_temp(temp)
    
    def tempUpdateEvent(self):
        temp = self.bc.get_temp("0")
        
        try:
            temp = float(temp)
        except:
            print "Float conversion error", temp
            return
        
        self.Thermo.setValue(temp)
        if not self.tempXData:
            self.tempXData = [0]
        else:
            self.tempXData.append(self.tempXData[-1] + self.tempUpdateInterval/1000.0)
        self.tempYData.append(int(temp))
        self.tempCurve.setData(self.tempXData, self.tempYData)
        self.tempQwtPlot.replot()
    
    def set_target_temp(self, temp):
        try:
            temp = int(temp)
        except ValueError:
            print temp, "is not a valid temperature."
        if temp == self.target_temp:
            return
        temp = self.bc.set_temp(temp)
        self.target_temp = temp
        self.targetTempLineEdit.setText(str(temp))

    def valve_button_clicked(self, valve_id, button):
        self.bc.set_valve_open(valve_id, button.isChecked())
        is_open = self.bc.get_valve_open(valve_id)
        button.setChecked(is_open)
        pal = button.palette()
        if is_open:
            color = Qt.green
        else:
            color = Qt.yellow
        pal.setColor(button.backgroundRole(), color)
        button.setPalette(pal)

    def closeEvent(self, ev):
        sys.exit(0)

def main():
    qApp = QApplication(sys.argv)
    pybrew = Pybrew()
    pybrew.show()
    sys.exit(qApp.exec_())

if __name__ == "__main__":
    main()

app = App(0)
app.MainLoop()
