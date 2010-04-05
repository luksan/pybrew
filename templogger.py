#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time, csv

from brewcontroller import BrewController, BrewControllerException

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Templogger(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        try:
            self.bc = BrewController()
            self.bc.open_port('/dev/ttyUSB0')
        except BrewControllerException as e:
            print "Brewcontrol failed", e
            sys.exit(1)
            
        self.bc.getTempSignal.connect(self.serialGetTempEvent, Qt.QueuedConnection)

        self.temps = [0,0,0,0,0,0]

        self.tempUpdateTimer = QTimer(self)
        self.connect(self.tempUpdateTimer, SIGNAL('timeout()'), self.tempUpdateEvent)
        self.tempUpdateTimer.start(1000)
    
    def serialGetTempEvent(self, sensor, temp):
        self.temps[int(sensor)] = temp

    def tempUpdateEvent(self):
        print time.time(),
        for i in range(6):
            self.bc.get_temp(i)
            print ",", self.temps[i],
        print

def main():
    qApp = QApplication(sys.argv)
    logger = Templogger()
    logger.show()
    sys.exit(qApp.exec_())

if __name__ == "__main__":
    main()