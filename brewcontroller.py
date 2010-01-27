# -*- coding: utf-8 -*-
import serial
import time

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

class BrewController():
    def __init__(self, port_name = None):
        self.sport = None
        self.serial_state = SERIAL_STATE_INIT
        
        self.VALVES = {
            '0': 'Ventil 1',
            '1': 'Ventil 2',
            '2': 'Ventil 3',
            '3': 'Ventil 4',
            }
        
        if port_name != None:
            self.open_port(port_name)
        
    def open_port(self, port_name):
        try:
            self.sport = serial.Serial(port_name, timeout = 0.5)
        except Exception, e:
            print e
            #raise BrewControllerException('Failed to init COM4')
            class A:
                def __init__(self):
                    self.s = "Fake controller ready\n"
                    self.target_temp = "40\n"
                    self.lines = []
                def readlines(self):
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
                        self.target_temp = s.split()[1]
                    if s == "GT 0\n":
                        self.lines.append("32\n")
                    elif s.startswith("GV"):
                        self.lines.append("0\n")
                    elif s == "GR\n":
                        self.lines.append(str(self.target_temp) + '\n')
                    else:
                        self.lines.append("OK\n")
                    self.s = s
            self.sport = A()
        
        # Flush initialization lines
        time.sleep(1)
        while True:
            l = self.sport.readline()
            if not l:
                break

    def __send(self, line):
        if line[-1] != '\n':
            line = line + '\n'
        try:
            self.sport.write(line)
            r = self.sport.readlines()
        except OSError, e:
            #FIXME stop all further communication attempts
            print "Read/write failed:", e
            return False

        if len(r) != 2:
            raise BrewControllerException("Didn't read 2 lines" + str(r))
        line = line.strip()
        
        echo = r[0].strip()
        result = r[1].strip()
        if echo != line:
            raise BrewControllerException("Read error. Sent '" + line + 
                       "', received '" + result + "'")
        print line,":", echo,":", result
        if result in ('NCK', 'NOK'):
            return False
        if result == 'OK':
            return True
        return result

    def set_valve_open(self, valve, open):
        """Set the valve to open or closed."""
        s = '0'
        if open:
            s = '1'
        r = self.__send("SV " + str(valve) + " " + s)
        if r != True:
            raise BrewControllerException("Valve command failed. Got: " + str(r))
    
    def get_valve_open(self, valve):
        r = self.__send("GV " + str(valve))
        if r == "1":
            return True
        if r == "0":
            return False
        raise BrewControllerException("GV command returned bad response: '" + r + "'.")

    def set_temp(self, temp):
        """Sets target temperature to temp and returns the actual
           target temperature from the controller."""
        if not self.__send("SR " + str(temp)):
            raise BrewControllerException("Setting of target temp failed.")
        return self.get_target_temp()
    
    def get_target_temp(self):
        """Read the target temperature from the controller."""
        r = self.__send("GR")
        try:
            return int(r)
        except:
            raise BrewControllerException("Target temp read failed." + str(r))

    def get_temp(self, sensor_id):
        """Read the actual temperature from sensor sensor_id."""
        r = self.__send("GT " + str(sensor_id))
        if r == False or r == True:
            raise BrewControllerException("Temp read failed." + str(r))
        try:
            r = float(r)
        except:
            raise BrewControllerException("Temp read failed." + str(r))
        return r
