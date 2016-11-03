#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  printer.py
#  
#  Copyright 2017 belese <belese@belese>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
# 
import cups
from serial import Serial

PRT = "zj58"

class Printer :
    def __init__(self):
        printer = Serial("/dev/serial0", 9600)

        ESC = chr(27)
        heatTime=185
        heatInterval=160
        heatingDots=6
        printDensity = 00
        printBreakTime = 00

        printer.write(ESC) # ESC - command
        printer.write(chr(64)) # @   - initialize
        printer.write(ESC) # ESC - command
        printer.write(chr(55)) # 7   - print settings
        printer.write(chr(heatingDots))  # Heating dots (20=balance of darkness vs no jams) default = 20
        printer.write(chr(heatTime)) # heatTime Library default = 255 (max)
        printer.write(chr(heatInterval)) # Heat interval (500 uS = slower, but darker) default = 250
        printer.write(chr(18))
        printer.write(chr(35))
        printer.write(chr((printDensity << 4) | printBreakTime))
        #printer.write(chr(255))
        self.cupconn = cups.Connection()
        self.printer = PRT
    
    def print_img(self,photo_file,size) :
        option = {"media" : size,"orientation-requested":"4"}
        print ("Print to size = %s"%size)
        #option = {"media" : size}
        self.cupconn.printFile(self.printer,photo_file,"None",option)
    
    def print_txt(self,txt) :
        pass

PRINTER = Printer()


def main(args):
    PRINTER.print_img("/tmp/photo.png","X48MMY64MM")
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
