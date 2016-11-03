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

from threading import Thread,Timer
import time

import RPi.GPIO as Gpio
import Adafruit_MPR121.MPR121 as mpr121
try :
    from resources.utils import log
except :
    def log(value) :
        print value

Gpio.setmode(Gpio.BCM)

#LONGPRESSCBFN
LONGPRESS = 3

#DELAY between shutter
DELAY = 4

#don't change value behind this

MPR121 = 0
GPIO = 1

#GPIO PIN ID
DECLENCHEUR = 4  #gpio


#MPR121 PIN ID
AUTO = 2
LUM = 1
FORMAT = 0

VALUE0 = 3
VALUE1 = 4
VALUE2 = 5
VALUE3 = 6

def register_gpio(gpio,fn) :
    Gpio.setup(gpio, Gpio.IN, pull_up_down=Gpio.PUD_UP)
    Gpio.add_event_detect(gpio, Gpio.BOTH, callback=fn,bouncetime=DELAY*1000)

class GpioPi :
    def __init__(self,onPress,onRelease) :
        self.onPress = onPress
        self.onRelease = onRelease

    def register(self,gpioid) :
        register_gpio(gpioid,self._onPress)

    def _onPress(self,gpioid) :
     if Gpio.input(gpioid):
         self.onPress(GPIO,gpioid)
     else:
         self.onRelease(GPIO,gpioid)





class Mpr121 :
    def __init__(self,onPress,onRelease) :
        self.onPress = onPress
        self.onRelease = onRelease
        self.cap = mpr121.MPR121()
        if not self.cap.begin():
            log('Failed to initialize MPR121')
        self.registerPinId = []
        Thread(None, self.mpr121, None).start()

    def register(self,pinid) :
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
    def __init__(self,onPress,onLongPress) :
        self.state = True
        self.value = False
        self.onPress = onPress
        self.onLongPress = onLongPress
        self.onLongPressTimer = None
        self.pressTime = 0
        self.done = True

    def enable(self) :
        self.state = True

    def disable(self) :
        self.state = False

    def status(self) :
        return self.state

    def _onPress(self) :        
        self.done = False
        self.value = True
        self.pressTime = time.time()
        if self.onPress and self.state and not self.onLongPress:
            self.onPress()
            self.done = True
        elif self.onLongPress and self.state:         
            self.onLongPressTimer = Timer(LONGPRESS, self.onLongPressTO)
            self.onLongPressTimer.start()
            
    def onLongPressTO(self) :
        self.onLongPressTimer = None
        if self.value and self.state:
            self.done = True
            self.onLongPress()
        
    def _onRelease(self) :
        self.value = False
        if self.onLongPressTimer :
            self.onLongPressTimer.cancel()
            self.onLongPressTimer = None
        if self.onLongPress and self.state and not self.done:
            self.done = True
            self.onPress()

class Buttons :
    def __init__(self) :
        self.gpio = GpioPi(self.onPress,self.onRelease)
        self.mpr = Mpr121(self.onPress,self.onRelease)
        self.buttons = {MPR121:{},GPIO:{}}

    def register(self,type,btn,cbOnPress=None,cbOnLongPress=None):
        if not self.buttons[type].has_key(btn) :
             self.buttons[type][btn] = []
             if type == GPIO :
                self.gpio.register(btn)
             elif type == MPR121 :
                self.mpr.register(btn)
        self.buttons[type][btn].append(Button(cbOnPress,cbOnLongPress))
        return self.buttons[type][btn][-1]

    def onPress(self,type,btn) :
        if self.buttons[type].has_key(btn) :
            for btn in self.buttons[type][btn] :
                btn._onPress()

    def onRelease(self,type,btn) :
        if self.buttons[type].has_key(btn) :
            for btn in self.buttons[type][btn] :
                btn._onRelease()

BUTTONS = Buttons()


def main(args):
    def touch() :
        print "touched"
    def longpress() :
        print "LongPress"

    for i in range(7) :
        BUTTONS.register(MPR121,i,touch,longpress)



if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
