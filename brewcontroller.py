import serial
import time

class BrewController():
    sport = None

    SERIAL_STATE_INIT = 1
    SERIAL_STATE_ACTIVE = 2
    SERIAL_STATE_ERROR = 3

    serial_state = SERIAL_STATE_INIT
    ticker = 0

    read_temp1 = -255
    has_read_temp1 = False

    set_temp1 = 0
    do_set_temp1 = False

    last_command_ok = False

    def __init__(this):
        try:
            this.sport = serial.Serial(3)
            this.sport.timeout = 0.1
        except:
            raise Exception('Failed to init COM4')

    def _parse_serial(this, lines):
        this.last_command_ok = False
        
        if (len(lines) < 1):
            return
        if (lines[0].find("accepting commands") != -1):
            this.serial_state = this.SERIAL_STATE_ACTIVE
            print 'Serial line active'
            return
        if (this.serial_state != this.SERIAL_STATE_ACTIVE):
            return

        for i in range(0, len(lines)):
            if (lines[0].find('GT') != -1):
                try:
                    this.read_temp1 = int(lines[1])
                    this.has_read_temp1 = True
                    this.last_command_ok = True
                except:
                    this.read_temp1 = -255
                    this.has_read_temp1 = False
            if (lines[0].find('SR') != -1):
                try:
                    result = lines[1]
                    if (result.find('OK') != -1):
                        this.last_command_ok = True
                except:
                    pass
                        

    def set_temp(this, temp):
        this.set_temp1 = temp
        this.do_set_temp1 = True

    def get_temp(this):
        return this.read_temp1

    def isready(this):
        if ((this.serial_state == this.SERIAL_STATE_ACTIVE) and
            (this.has_read_temp1)):
            return True
        else:
            return False

    def run(this):      
        lines = this.sport.readlines()
        this._parse_serial(lines)
        this.ticker += 1

        if (this.serial_state != this.SERIAL_STATE_ACTIVE):
            return

        if ((this.ticker % 2) == 0):
            this.sport.write("GT 0")

        if (((this.ticker+1) % 2) == 0):
            if (this.do_set_temp1):
                this.sport.write("SR " + str(this.set_temp1))
                this.do_set_temp1 = False

def main():
    bc = BrewController()
    while(True):
        bc.run()
        time.sleep(0.1)
    
#main()
