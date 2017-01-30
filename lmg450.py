#!/usr/bin/python

# lmg450.py
#
# Implement interface to ZES Zimmer LMG450 4 Channel Power Analyzer
# via RS232 interface
#
# 2012-07, Jan de Cuveland, Dirk Hutter
# 2017-01, Robert Khasanov

import serial

EOS = "\r\n"
TIMEOUT = 10

class scpi_serial:
    
    def __init__(self, comport='/dev/ttyS0', baudrate=115200):
        self._serial = serial.Serial(comport, baudrate, rtscts = True, timeout = TIMEOUT)

    def close(self): 
        self._serial.close()

    def recv_str(self):
        response = self._serial.readline()
        if response[-len(EOS):] != EOS:
            print "error: recv timeout"
        return response[:-len(EOS)]

    def send(self, msg):
        self._serial.write(msg + EOS)

    def send_raw(self, msg):
        self._serial.write(msg)

    def query(self, cmd): 
        self.send(cmd) 
        return self.recv_str()

    def send_cmd(self, cmd):
        result = self.query(cmd + ";*OPC?")
        if result != "1":
            print "opc returned unexpected value: \"" + result + "\""

    def send_brk(self):
#        self.send_raw(chr(255) + chr(243))
        self._serial.send_break()

#    def get_socket(self):
#        return self._t.get_socket()

    def __del__(self):
        self.close()


class lmg450(scpi_serial):
    _short_commands_enabled = False

    def reset(self):
        self.send_brk()
        self.send_cmd("*cls")
        self.send_cmd("*rst")
    
    def goto_short_commands(self):
        if not self._short_commands_enabled:
            self.send("syst:lang short")
        self._short_commands_enabled = True

    def goto_scpi_commands(self):
        if self._short_commands_enabled:
            self.send("lang scpi")
        self._short_commands_enabled = False

    def send_short(self, msg):
        self.goto_short_commands()
        self.send(msg)

    def send_scpi(self, msg):
        self.goto_scpi_commands()
        self.send(msg)

    def send_short_cmd(self, cmd):
        self.goto_short_commands()
        self.send_cmd(cmd)

    def send_scpi_cmd(self, cmd):
        self.goto_scpi_commands()
        self.send_cmd(cmd)

    def query_short(self, msg):
        self.goto_short_commands()
        return self.query(msg)

    def query_scpi(self, msg):
        self.goto_scpi_commands()
        return self.query(msg)

    def goto_local(self):
        self.send("gtl")

    def read_id(self):
        return self.query("*idn?").split(",")

    def beep(self):
        self.send_short_cmd("beep")

    def read_errors(self):
        return self.query_scpi("syst:err:all?")

    def set_ranges(self, current, voltage):
        self.send_short_cmd("iam manual");
        self.send_short_cmd("irng " + str(current))
        self.send_short_cmd("uam manual");
        self.send_short_cmd("urng " + str(voltage))

    def select_values(self, values):
        self.send_short("actn;" + "?;".join(values) + "?")

    def read_values(self):
        values_raw = self.recv_str().split(";")
        return [ float(x) for x in values_raw ]

    def cont_on(self):
        self.send_short("cont on")

    def cont_off(self):
        self.send_short("cont off")
        
    def disconnect(self):
        self.read_errors()
        self.goto_local()
