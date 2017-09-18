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



#GPIO PIN ID
DECLENCHEUR = 14  #gpio +10 

#DELAY between shutter 
DELAY = 4

#MPR121 PIN ID
AUTO = 0
LUM = 1
FORMAT = 2

VALUE0 = 4
VALUE1 = 3
VALUE2 = 5
VALUE3 = 6

def init_gpio(fn) :
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DECLENCHEUR -10, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(DECLENCHEUR -10 , GPIO.FALLING, callback=fn,bouncetime=DELAY*1000)

class Button :  
    def __init__(self,pinid,cb) :
        self.pinid = pinid
        self.state = True
        self.cb = cb        
            
    def enable(self) :
        self.state = True
        
    
    def disable(self) :
        self.state = False

    def status(self) :
        return self.state
    
    def getPinId(self) :
        return self.pinid
    

class Buttons : 
    def __init__(self) :
        self.cap = MPR121.MPR121()
        if not self.cap.begin():
            log('Failed to initialize MPR121')
        self.buttons = {}
        Thread(None, self.mpr121, None).start()

    
    def mpr121(self) :      
        last_touched = self.cap.touched()
        while True:
            current_touched = self.cap.touched()            
            if current_touched != last_touched :
                for i in range(7):
                    pin_bit = 1 << i                    
                    if current_touched & pin_bit and not last_touched & pin_bit:
                        log('{0} touched!'.format(i))
                        if self.onPress :
                            self.onPress(i)                                                 
                last_touched = current_touched
            time.sleep(0.1) 
        
    def register(self,btn,cb):
        self.buttons[btn] = Button(btn,cb)
        return self.buttons[btn]
        
    def onPress(self,btn) :		
        if self.buttons.has_key(btn) and self.buttons[btn].status() :
           self.buttons[btn].cb()
    
    def onGpioPress(self,btn) :
		self.onPress(btn +10 )
    
BUTTONS = Buttons()
init_gpio(BUTTONS.onGpioPress)



def main(args):
    def cb() :
        print "touched"
    for i in range(7) :
        BUTTONS.register(i,cb)
    


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
