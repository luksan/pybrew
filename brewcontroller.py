# -*- coding: utf-8 -*-
import serial
import time

from PyQt4 import QtCore
from PyQt4.QtCore import SIGNAL, QThread, pyqtSignal, QWaitCondition, QMutex

SERIAL_STATE_INIT = 1
SERIAL_STATE_ACTIVE = 2
SERIAL_STATE_ERROR = 3

# Commands:
# SV <ventilnummer> <1|0> ändra ventilläge
# GT <tempnummer> läs temperatur
# GV <ventilnummer> läs ventilläge
# GR läser regulatorns börvärde
# SR <temperatur> sätter regulatorns börvärde

class BrewControllerException(Exception):
    pass

class FakeSerial:
    def __init__(self):
        self.s = "Fake controller ready\n"
        self.target_temp = 40
        self.delta = 1
        self.temp = 20
        self.lines = []
    def readlines(self):
        time.sleep(0.3)
        r = self.lines
        self.lines = []
        return r
    def read(self):
        try:
            s = self.lines.pop(0)
        except:
            return ""
        return s
    def readline(self):
        return self.read()
    def write(self, s):
        self.lines.append(s)
        if s.startswith("SR"):
            self.target_temp = int(s.split()[1])
            self.delta = max((self.target_temp - self.temp)/3.0, 0.5)
        if s == "GT 0\n":
            if self.temp < self.target_temp:
                self.temp = self.temp + self.delta
            self.lines.append("%i\n" % self.temp)
        elif s.startswith("GV"):
            self.lines.append("0\n")
        elif s == "GR\n":
            self.lines.append(str(self.target_temp) + '\n')
        else:
            self.lines.append("OK\n")
        self.s = s

class BrewController(QThread):
    serialErrorSignal = pyqtSignal(str)
    
    getTempSignal = pyqtSignal(str, float)
    getTargetTempSignal = pyqtSignal(float)
    getValveStateSignal = pyqtSignal(str, str)

    def __init__(self):
        QThread.__init__(self)
        
        self._wait = QWaitCondition()
        self._mutex = QMutex()
        self._cmd_queue = []
        
        self.terminate = False

        self.sport = None
        self.serial_state = SERIAL_STATE_INIT
        self.port_name = None
        self._do_init = False

        self.VALVES = {
            '0': u'Utlopp',
            '1': u'Buffertvatten f. v. vxl.',
            '2': u'V. vxl. inlopp',
            '3': u'Mäsk ut',
            }
        
        self.start()
    
    def run(self):
        while True:
            self._mutex.lock()
            self._wait.wait(self._mutex)
            self._mutex.unlock()
            if self.terminate:
                return
            if self._do_init:
                self._serial_init()
                self._do_init = False
            while len(self._cmd_queue):
                if self.terminate:
                    return
                self._mutex.lock()
                cmd = self._cmd_queue.pop(0)
                self._mutex.unlock()
                try:
                    self.__send_serial(cmd)
                except Exception, e:
                    print e
                    self.serialErrorSignal.emit(str(e))
            if self.terminate:
                return

    def open_port(self, port_name):
        try:
            self.sport = serial.Serial(port_name, timeout = 0.5)
        except Exception, e:
            print e
            #raise BrewControllerException('Failed to init COM4')
            self.sport = FakeSerial()
        self.port_name = port_name
        self._do_init = True
        self._wait.wakeOne()

    def _push_cmd(self, cmd):
        self._mutex.lock()
        self._cmd_queue.append(str(cmd))
        self._mutex.unlock()
        self._wait.wakeOne()

    def _serial_init(self):
        print "init start"
        self.serial_state = SERIAL_STATE_INIT
        # Flush initialization lines
        self.sleep(1)
        while True:
            l = self.sport.readline()
            if not l:
                break
        print "init done"
        self.serial_state = SERIAL_STATE_ACTIVE

    def __send_serial(self, line):
        if self.serial_state != SERIAL_STATE_ACTIVE:
            raise BrewControllerException("Attempting to send with non-active interface.")

        line = str(line) # it is a QString

        if line[-1] != '\n':
            line = line + '\n'
        try:
            self.sport.write(line)
            echo = self.sport.readline()
            result = self.sport.readline()
        except OSError, e:
            #FIXME stop all further communication attempts
            print "Read/write failed:", e
            self.serial_state = SERIAL_STATE_ERROR
            return False

        line = line.strip()

        echo = echo.strip()
        result = result.strip()
        if echo != line:
            raise BrewControllerException("Read error. Sent '" + line + 
                       "', received '" + result + "'")
        # print line,":", echo,":", result
        if result in ('NCK', 'NOK'):
            raise BrewControllerException("Command failed." + line + ", " + echo + ", " + result)
        
        self.__parse_result(echo, result)

    def __parse_result(self, command, result):
        if result == "OK":
            return # command executed ok, no data returned
        c = command.split()
        cmd = c.pop(0)
        if cmd == 'GV': # read valve status
            state = None
            if result == "1":
                state = "open"
            elif result == "0":
                state = "closed"
            if state != None and len(c) == 1:
                self.getValveStateSignal.emit(c[0], state)
                return
        elif cmd == "GT": # read temp sensor
            try:
                result = float(result)
            except:
                pass
            else:
                if len(c) == 1:
                    self.getTempSignal.emit(c[0], result)
                    return
        elif cmd == "GR": # get regulator target temperature
            if len(c) == 0:
                try:
                    result = float(result)
                except:
                    pass
                else:
                    self.getTargetTempSignal.emit(result)
                    return
        self.serialErrorSignal.emit("Bad command response." + str(command) + "->" + str(result))
        
    def set_valve_open(self, valve, open):
        """Set the valve to open or closed."""
        s = '0'
        if open:
            s = '1'
        self._push_cmd("SV " + str(valve) + " " + s)
    
    def get_valve_state(self, valve):
        if not valve in self.VALVES.keys():
            raise BrewControllerException("Valve " + str(valve) + " does not exist.")
        self._push_cmd("GV " + str(valve))

    def set_target_temp(self, temp):
        """Sets target temperature to temp and returns the actual
           target temperature from the controller."""
        try:
            temp = int(temp)
        except ValueError:
            raise BrewControllerException("Bad temperature value: " + str(temp))
        self._push_cmd("SR " + str(temp))
    
    def get_target_temp(self):
        """Read the target temperature from the controller."""
        self._push_cmd("GR")

    def get_temp(self, sensor_id):
        """Read the actual temperature from sensor sensor_id."""
        self._push_cmd("GT " + str(sensor_id))
