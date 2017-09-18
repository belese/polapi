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



class Printer :
    def __init__(self):
        self.cupconn = cups.Connection()
        self.printer = self.cupconn.getPrinters().keys()[0]
    
    def print_img(self,photo_file,size) :
        option = {"media" : size,"orientation-requested":"4"}
        print ("Print to size = %s"%size)
        #option = {"media" : size}
        self.cupconn.printFile(self.printer,photo_file,"None",option)
    
    def print_txt(self,txt) :
        pass

PRINTER = Printer()


def main(args):
    PRINTER.print_img("/tmp/photo.png","X48MMY32MM")
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
