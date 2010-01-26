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
            self.sport = serial.Serial(port_name)
            self.sport.timeout = 0.2
        except Exception, e:
            print e
            #raise BrewControllerException('Failed to init COM4')
            class A:
                def __init__(self):
                    self.s = "Fake controller ready\n"
                    self.target_temp = "40\n"
                def readlines(self):
                    return [self.read()]
                def read(self):
                    s = self.s
                    self.s = "OK\n"
                    if s == "GT 0\n":
                        self.s = "32\n"
                    if s.startswith("GV"):
                        self.s = "0\n"
                    if s == "GR\n":
                        self.s = self.target_temp
                    if self.s[-1] != "\n":
                        self.s = self.s + "\n"
                    return s
                def readline(self):
                    return self.read()
                def write(self, s):
                    if s.startswith("SR"):
                        self.target_temp = s.split()[1]
                    self.s = s
            self.sport = A()
        
        # Flush initialization lines
        for l in self.sport.readlines():
            print l

    def __send(self, line):
        if line[-1] != '\n':
            line = line + '\n'
        self.sport.write(line)
        r = self.sport.readline()
        if r != line:
            raise BrewControllerException("Read error. Sent '"+line + "', received '" + r + "'")
        result = self.sport.readline().strip()
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
        return int(r)

    def get_temp(self, sensor_id):
        """Read the actual temperature from sensor sensor_id."""
        return self.__send("GT " + str(sensor_id))
