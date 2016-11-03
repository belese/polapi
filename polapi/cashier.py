#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  cashier.py
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

from polapi import polapi
from resources.caisse import CAISSE
from resources.printer import PRINTER

class caisse (polapi) :
	def onChangeMode(self) :
		if self.prt == PRINTER :
			print 'mode = caisse'
			self.prt = CAISSE
		else :
			print 'mode = normal'
			self.prt = PRINTER

def main(args):
    a = caisse()
    

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
