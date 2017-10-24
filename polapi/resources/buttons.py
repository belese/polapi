#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  buttons.py
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

from threading import Thread
import time

import RPi.GPIO as GPIO
import Adafruit_MPR121.MPR121 as MPR121
from resources.utils import log

GPIO.setmode(GPIO.BCM)

MPR121 = 0
GPIO = 1

#GPIO PIN ID
DECLENCHEUR = 4  #gpio 

#DELAY between shutter 
DELAY = 4

#MPR121 PIN ID
AUTO = 2
LUM = 1
FORMAT = 0

VALUE0 = 3
VALUE1 = 4
VALUE2 = 5
VALUE3 = 6

def register_gpio(gpio,fn) :
    GPIO.setup(gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(gpio, GPIO.BOTH, callback=fn,bouncetime=DELAY*1000)

class GpioPi :
    def __init__(self,onPress,onRelease) :
	self.onPress = onPress
	self.onRelease = onRelease
	
    def register(self,gpioid) :
	register_gpio(gpioid,self._onPress) :

    def _onPress(self,gpioid) :
	 if GPIO.input(gpioid):    
             self.onPress(GPIO,gpioid)
    	 else:
	     self.onRelease(GPIO,gpioid)
        	
	
	
    
 
class Mpr121 :
    def __init__(self,onPress,onRelease) :
	self.onPress = onPress
	self.onRelease = onRelease
	self.cap = MPR121.MPR121()
        if not self.cap.begin():
             log('Failed to initialize MPR121')
	self.registerPinId = []
	Thread(None, self.mpr121, None).start()
			
    def register(pinid) :
	self.registerPinId.append(pinid)
    
    def mpr121(self) :      
       last_touched = self.cap.touched()
       while True:
       current_touched = self.cap.touched()            
       if current_touched != last_touched :
           for i in self.registerPinId:
               pin_bit = 1 << i                    
                    if current_touched & pin_bit and not last_touched & pin_bit:
                        log('{0} touched!'.format(i))
                        if self.onPress :
                            self.onPress(MPR121,i)    
		    if not current_touched & pin_bit and last_touched & pin_bit:
			log('{0} released!'.format(i))
			if self.onRelease :
                            self.onRelease(MPR121,i)            		
                last_touched = current_touched
       time.sleep(0.1)
	
class Button :  
    def __init__(self,pinid,onPress,onRelease) :
        self.pinid = pinid
        self.state = True
        self.onPress = onPress
	self.onRelease = onRelease
	self.pressTime = 0
            
    def enable(self) :
        self.state = True
            
    def disable(self) :
        self.state = False

    def status(self) :
        return self.state
    
    def getPinId(self) :
        return self.pinid

    def _onPress(self) :
	self.pressTime = time.time()
	if self.onPress :
	      self.onPress()
    
    def _onRelease) :
	if self.onRelease :
	      self.onRelease(self.pressTime - time.time())
		
class Buttons : 
    def __init__(self) :
	self.gpio = GpioPi(self.onPress,self.onRelease)
	self.mpr = Mpr121(self.onPress,self.onRelease)	
        self.buttons = {MPR121:{},GPIO:{}}
                    
    def register(self,type,btn,cbOnPress,cbOnRelease):
        self.buttons[type][btn] = Button(btn,cbOnPress,cbOnRelease)
	if type == GPIO :
	     self.gpio.register(btn)
	elif type == MPR121 :
	     self.mpr.register(btn)
		
        return self.buttons[type][btn]
        
    def onPress(self,type,btn) :		
        if self.buttons[type].has_key(btn)
           self.buttons[type][btn]._onPress()

    def onRelease(self,type,btn) :		
        if self.buttons[type].has_key(btn)
           self.buttons[type][btn]._onRelease()
    
BUTTONS = Buttons()


def main(args):
    def cb() :
        print "touched"
    for i in range(7) :
        BUTTONS.register(i,cb)
    


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
