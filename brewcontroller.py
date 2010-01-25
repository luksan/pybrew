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

class BrewController():
    def __init__(self):
        self.sport = None
        
        self.serial_state = SERIAL_STATE_INIT
        self.ticker = 0
        
        self.read_temp1 = -255
        self.has_read_temp1 = False
        
        self.set_temp1 = 0
        self.do_set_temp1 = False
        
        self.send_queue = []

        self.last_command_ok = False
        
        self.VALVES = {
            '0': 'Ventil 1',
            '1': 'Ventil 2',
            '2': 'Ventil 3',
            '3': 'Ventil 4',
            }

        try:
            self.sport = serial.Serial('/dev/ttyUSB0')
            self.sport.timeout = 0.1
        except Exception, e:
            print e
            raise Exception('Failed to init COM4')
            class A:
                def readlines(self):
                    return []
            self.sport = A()
            return

    def _parse_serial(self, lines):
        self.last_command_ok = False
        
        if (len(lines) < 1):
            return
        if (lines[0].find("accepting commands") != -1):
            self.serial_state = SERIAL_STATE_ACTIVE
            print 'Serial line active'
            return
        if (self.serial_state != SERIAL_STATE_ACTIVE):
            return

        for i in range(0, len(lines)):
            if (lines[0].find('GT') != -1):
                try:
                    self.read_temp1 = int(lines[1])
                    self.has_read_temp1 = True
                    self.last_command_ok = True
                except:
                    self.read_temp1 = -255
                    self.has_read_temp1 = False
            if (lines[0].find('SR') != -1):
                try:
                    result = lines[1]
                    if (result.find('OK') != -1):
                        self.last_command_ok = True
                except:
                    pass

    def send(self, line):
        self.send_queue.append(line)

    def set_valve_open(self, valve, open):
        print "Setting", self.VALVES[valve], open
        s = '0'
        if open:
            s = '1'
        self.send("SV " + str(valve) + " " + s)

    def set_temp(this, temp):
        self.send("SR " + str(this.set_temp1))
        
    def get_temp(this):
        return this.read_temp1

    def isready(self):
        if ((self.serial_state == SERIAL_STATE_ACTIVE) and
            (self.has_read_temp1)):
            return True
        else:
            return False

    def run(self):      
        lines = self.sport.readlines()
        self._parse_serial(lines)
        self.ticker += 1

        if (self.serial_state != SERIAL_STATE_ACTIVE):
            return

        if ((self.ticker % 2) == 0):
            self.sport.write("GT 0")

        if (((self.ticker+1) % 2) == 0):
            for l in self.send_queue:
                self.sport.write(l)
            self.send_queue = []

def main():
    bc = BrewController()
    while(True):
        bc.run()
        time.sleep(0.1)
    
#main()
