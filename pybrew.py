#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time, csv

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qwt5 import *

import cPickle as pickle

from pybrewMainWindow import MainWindow

from brewcontroller import BrewController, BrewControllerException

class TempCurve(QwtPlotCurve):
    def __init__(self, name, startTime):
        QwtPlotCurve.__init__(self, name)
        self.startTime = startTime
        self.xData = []
        self.yData = []

    def add_temp(self, temp, when = None):
        if when == None:
            when = time.time()
        self.xData.append(when - self.startTime)
        self.yData.append(temp)
        self.setData(self.xData, self.yData)

    def set_last_time(self, when):
        try:
            self.xData[-1] = when - self.startTime
        except IndexError:
            return # we don't have any data. ignore
        self.setData(self.xData, self.yData)

class TempPlot:
    def __init__(self, qwt_plot):
        self.start_time = time.time()
        self.qwt_plot = qwt_plot
        
        self.tempCurve = TempCurve("Temperature", self.start_time)
        #sym = self.tempCurve.symbol()
        #sym.setStyle(QwtSymbol.Ellipse)
        #sym.setSize(QSize(7, 7))
        #self.tempCurve.setSymbol(sym)
        pen = self.tempCurve.pen()
        pen.setColor(Qt.blue)
        pen.setWidth(2)
        self.tempCurve.setPen(pen)
        self.tempCurve.attach(self.qwt_plot)
        
        self.targetCurve = TempCurve("Target temperature", self.start_time)
        self.targetCurve.setStyle(QwtPlotCurve.Steps) # make it look like a step function
        pen = self.targetCurve.pen()
        pen.setWidth(2)
        pen.setColor(Qt.darkGreen)
        self.targetCurve.setPen(pen)
        self.targetCurve.attach(self.qwt_plot)
    
    def add_target_temp(self, temp):
        now = time.time()
        self.targetCurve.add_temp(temp, now)
        # extra data point wich is moved forward in time in add_temp()
        self.targetCurve.add_temp(temp, now)
        self.qwt_plot.replot()

    def add_temp(self, temp):
        now = time.time()
        self.tempCurve.add_temp(temp, now)
        self.targetCurve.set_last_time(now)
        self.qwt_plot.replot()
    
    def getTempData(self):
        ret = []
        target_index = 0 
        for i in range(len(self.tempCurve.xData)):
            if target_index+1 < len(self.targetCurve.xData):
                if self.targetCurve.xData[target_index+1] < self.tempCurve.xData[i]:
                    target_index += 1
            ret.append( (self.tempCurve.xData[i],
                         self.tempCurve.yData[i],
                         self.targetCurve.yData[target_index]) )
        return ret
            
    
class TargetTempProfileModel(QAbstractTableModel):
    def __init__(self, parent = None):
        QAbstractTableModel.__init__(self, parent)
        
        self.headerdata = ["Temp", "Time"]
        self.tempdata = []
    
    def rowCount(self, parent = QModelIndex()):
        if not parent.isValid():
            return len(self.tempdata)
        return 0
    
    def columnCount(self, parent = QModelIndex()):
        if not parent.isValid():
            return 2
        return 0
    
    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled

    def data(self, index, role):
        if index.isValid() and (role == Qt.DisplayRole or role == Qt.EditRole):
            return QVariant(self.tempdata[index.row()][index.column()])
        return QVariant()
    
    def getTemp(self, row):
        return int(str(self.tempdata[row][0]))

    def getTime(self, row):
        return int(str(self.tempdata[row][1]))

    def setData(self, index, data, role = Qt.EditRole):
        self.tempdata[index.row()][index.column()] = int(str(data.toPyObject()))
        self.dataChanged.emit(index, index)
        return True
    
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headerdata[col])
        return QVariant()
    
    def insertRows(self, row, count = 1, parent = QModelIndex(), data = None):
        if data != None:
            count = len(data)
        else:
            data = [[0, 0] for i in range(count)]
        self.beginInsertRows(parent, row, row+count-1)
        for i in range(count):
            self.tempdata.insert(row+i, data[i])
        self.endInsertRows()
        self.layoutChanged.emit()
        return True
    
    def removeRows(self, row, count = 1, parent = QModelIndex()):
        self.beginRemoveRows(parent, row, row+count-1)
        for i in range(count):
            del self.tempdata[row]
        self.endRemoveRows()
        return True
        
class Pybrew(MainWindow):
    def __init__(self):
        MainWindow.__init__(self)

        self.tempUpdateInterval = 1000 # update interval in milliseconds
        
        self.target_temp = 0
        self.target_temp_time = None # The time when the target temp was reached
        self.target_profile_line = None # The current line in progress in the temp profile

        try:
            self.bc = BrewController()
            self.bc.open_port(3)
        except BrewControllerException as e:
            QMessageBox.critical(None, "Fatal error", str(e))
            sys.exit(1)
        
        self.bc.serialErrorSignal.connect(self.serialErrorEvent, Qt.QueuedConnection)
        
        self.bc.getTempSignal.connect(self.serialGetTempEvent, Qt.QueuedConnection)
        self.bc.getTargetTempSignal.connect(self.serialGetTargetTempEvent, Qt.QueuedConnection)
        self.bc.getValveStateSignal.connect(self.serialGetValveStateEvent, Qt.QueuedConnection)

        buttons = self.bc.VALVES.keys()
        buttons.sort()
        self.valve_buttons = {}
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
            self.valve_buttons[k] = v

        self.tempPlot = TempPlot(self.tempQwtPlot)

        self.targetTempProfileModel = TargetTempProfileModel(parent = self)
        self.tempProfileTableView.setModel(self.targetTempProfileModel)
        
        self.tempUpdateTimer = QTimer(self)
        self.connect(self.tempUpdateTimer, SIGNAL('timeout()'), self.tempUpdateEvent)
        self.tempUpdateTimer.start(self.tempUpdateInterval)

        self.read_serial_state()

    def read_serial_state(self):
        for b in self.valve_buttons:
            self.bc.get_valve_state(b)
        self.bc.get_target_temp()
        print "read serial state done"
    
    def serialErrorEvent(self, msg):
        print "Serial error:", msg

    def serialGetTempEvent(self, sensor, temp):
        #print "got temp", sensor, temp
        self.Thermo.setValue(temp)
        self.tempPlot.add_temp(temp)
        if temp >= self.target_temp and self.target_profile_line != None:
            self.check_temp_profile()

    def check_temp_profile(self):
        if self.target_temp_time == None:
            self.target_temp_time = time.time()
        # check if we have stayed at this temp long enough
        ttime = self.targetTempProfileModel.getTime(self.target_profile_line)
        if time.time() - self.target_temp_time >= ttime:
            self.target_profile_line += 1
            self.target_temp_time = None
            if self.target_profile_line >= self.targetTempProfileModel.rowCount():
                # The temp profile is complete. Turn off heating
                self.runTempProfileButton.setChecked(False)
                self.set_target_temp(20)
            else:
                self.set_target_temp(self.targetTempProfileModel.getTemp(self.target_profile_line))            
    
    def serialGetTargetTempEvent(self, temp):
        print "got target temp", repr(temp), "old", repr(self.target_temp)
        temp = int(temp)
        self.tempPlot.add_target_temp(temp)
        self.target_temp = temp        
        self.targetTempLineEdit.setText(str(temp))
    
    def serialGetValveStateEvent(self, valve_id, state):
        print "got valve state:", valve_id, state
        valve_id = str(valve_id)
        state = str(state)
        if state == "open":
            is_open = True
        elif state == "closed":
            is_open = False
        else:
            print "Bad valve state", valve_id, state
            return
        button = self.valve_buttons[valve_id]
        button.setChecked(is_open)
        pal = button.palette()
        if is_open:
            color = Qt.green
        else:
            color = Qt.yellow
        pal.setColor(button.backgroundRole(), color)
        button.setPalette(pal)

    def newTargetTempEvent(self):
        row = self.tempProfileTableView.currentIndex().row()
        self.targetTempProfileModel.insertRows(row + 1)
        self.tempProfileTableView.resizeRowsToContents()

    def setTargetTempEvent(self):
        temp = self.targetTempLineEdit.text()
        try:
            temp = int(temp)
        except ValueError:
            print "Bad temp value entered:", str(temp)
            self.targetTempLineEdit.setText(str(self.target_temp))
            return    
        self.set_target_temp(temp)
    
    def removeTargetTempEvent(self):
        self.targetTempProfileModel.removeRows(self.tempProfileTableView.currentIndex().row())
    
    def runTempProfileToggledEvent(self, toggled):
        if toggled:
            self.target_profile_line = 0
            self.set_target_temp(self.targetTempProfileModel.getTemp(0))
        else:
            self.target_profile_line = None            

    def tempUpdateEvent(self):
        self.bc.get_temp("0")

    def saveTempProfileEvent(self):
        filename = QFileDialog.getSaveFileName(self, "Save file", ".", "Temp profile (*.tpr)")
        filename = str(filename)
        if not filename:
            return
        if not filename.endswith(".tpr"):
            filename += ".tpr"        
        pickle.dump(self.targetTempProfileModel.tempdata, open(filename, 'w'))
    
    def loadTempProfileEvent(self):
        filename = QFileDialog.getOpenFileName(self, "Open file", ".", "Temp profile (*.tpr)")
        filename = str(filename)
        if not filename:
            return
        data = pickle.load(open(filename, 'r'))
        self.targetTempProfileModel.removeRows(0, self.targetTempProfileModel.rowCount())
        self.targetTempProfileModel.insertRows(0, data = data)
        self.tempProfileTableView.resizeRowsToContents()
    
    def saveTempDataEvent(self):
        filename = QFileDialog.getSaveFileName(self, "Save file", ".", "Temp data (*.csv)")
        filename = str(filename)
        if not filename:
            return
        if not filename.endswith(".csv"):
            filename += ".csv"        
        c = csv.writer(open(filename, 'w'))
        c.writerows(self.tempPlot.getTempData())

    def set_target_temp(self, temp):
        print "Setting target temp to", temp
        try:
            temp = int(temp)
        except ValueError:
            print temp, "is not a valid temperature."
            raise
        if temp == self.target_temp:
            return
        self.bc.set_target_temp(temp)
        self.bc.get_target_temp() # read back the setting to verify

    def valve_button_clicked(self, valve_id, button):
        self.bc.set_valve_open(valve_id, button.isChecked())
        self.bc.get_valve_state(valve_id)

    def closeEvent(self, ev):
        sys.exit(0)

def main():
    qApp = QApplication(sys.argv)
    pybrew = Pybrew()
    pybrew.show()
    sys.exit(qApp.exec_())

if __name__ == "__main__":
    main()
