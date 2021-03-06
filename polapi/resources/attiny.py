#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  attiny.py
#  
#  Copyright 2018 belese <belese@belese>
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
import smbus
import time

ATTINY_SLAVE_ADDR = 10

class Attiny85 :
	def __init__(self) :
		self.bus = smbus.SMBus(1)		
	
	def getCommand(self,command):    
		data = []
		ok = False
		while not ok :
			try :        
			   self.bus.write_byte(ATTINY_SLAVE_ADDR,command)
			   start = self.bus.read_byte(ATTINY_SLAVE_ADDR)                     
			   dat = self.bus.read_byte(ATTINY_SLAVE_ADDR)	
			   while dat != 0xFF :
					data.append(dat)
					dat = self.bus.read_byte(ATTINY_SLAVE_ADDR)        					
			except IOError :
				print ('communication error')           
				time.sleep(0.1)
			else :
				if start == 0xDE :
					ok = True
		return data
	
	def isPressed(self) :
		return self.getCommand(0x03)[0] == 0x00
	
	def getVoltage(self) :
		vcc = False
		data = self.getCommand(0x01)
		if len(data) == 2 :
			try :
				vcc = (1024 * 1070) / ((data[1] << 8) | data[0])				
			except ZeroDivisionError:
				return self.getVoltage()
		return vcc
	
	def stop(self) :
		self.getCommand(0x05)
		

ATTINY85 = Attiny85()		
		
		

def main(args):
    att = Attiny85()
    #att.stop()
    while True :
		print att.getVoltage()
		print att.isPressed()

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
