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

from threading import Thread, Event, Lock
import time


import RPi.GPIO as Gpio
import Adafruit_MPR121.MPR121 as mpr121
from attiny import ATTINY85

try:
    from resources.utils import log
    from resources.resource import Resource, queue_call
except BaseException:
    from resource import Resource, queue_call

    def log(value):
        print value

Gpio.setmode(Gpio.BCM)


# BUTTON TYPE
MPR121 = 0
GPIO = 1
ATTINY = 2

# EVENTS
ONTOUCHED = 1
ONPRESSED = 2
ONRELEASED = 3


def register_gpio(gpio, fn):
    Gpio.setup(gpio, Gpio.IN, pull_up_down=Gpio.PUD_UP)
    Gpio.add_event_detect(gpio, Gpio.BOTH, callback=fn, bouncetime=10)


class attiny85btn :
    def __init__(self, ONPRESSED, ONRELEASED):
        self.ONPRESSED = ONPRESSED
        self.ONRELEASED = ONRELEASED
        self.stopped = False
        Thread(None, self._attiny85, None).start()
    
    def register(self, data):
        pass
    
    def _attiny85(self):
        last_touched = ATTINY85.isPressed()
        time.sleep(0.1)      
        while not self.stopped:
            current_touched = ATTINY85.isPressed()
            if current_touched != last_touched:                
                if current_touched :
                   if self.ONPRESSED:
                      self.ONPRESSED(ATTINY, 0)
                else :
                   if self.ONRELEASED:
                      self.ONRELEASED(ATTINY, 0)
                last_touched = current_touched
            time.sleep(0.1)
        print ('_attiny85 Stopped')

    def stop(self):
        self.stopped = True



class GpioPi:
    def __init__(self, ONPRESSED, ONRELEASED):
        self.ONPRESSED = ONPRESSED
        self.ONRELEASED = ONRELEASED

    def register(self, gpioid):
        register_gpio(gpioid, self._onPress)

    def _onPress(self, gpioid):
        if not Gpio.input(gpioid):
            self.ONPRESSED(GPIO, gpioid)
        else:
            self.ONRELEASED(GPIO, gpioid)

    def stop(self):
        Gpio.cleanup()


class Mpr121:
    def __init__(self, ONPRESSED, ONRELEASED):
        self.stopped = False
        self.ONPRESSED = ONPRESSED
        self.ONRELEASED = ONRELEASED
        self.cap = mpr121.MPR121()
        if not self.cap.begin():
            log('Failed to initialize MPR121')
        self.registerPinId = []
        Thread(None, self.mpr121, None).start()

    def register(self, pinid):
        self.registerPinId.append(pinid)

    def mpr121(self):
        last_touched = self.cap.touched()
        while not self.stopped:
            current_touched = self.cap.touched()
            if current_touched != last_touched:
                for i in self.registerPinId:
                    pin_bit = 1 << i
                    if current_touched & pin_bit and not last_touched & pin_bit:
                        if self.ONPRESSED:
                            self.ONPRESSED(MPR121, i)
                    if not current_touched & pin_bit and last_touched & pin_bit:
                        if self.ONRELEASED:
                            self.ONRELEASED(MPR121, i)
                last_touched = current_touched
            time.sleep(0.1)
        print ('Mpr121 Stopped')

    def stop(self):
        self.stopped = True


class Button(Resource):
    def __init__(self):
        Resource.__init__(self)
        self.state = True
        self.events = {ONTOUCHED: [], ONPRESSED: [], ONRELEASED: []}
        self.buttonPressed = Event()
        self.buttonPressed.clear()
        self.buttonRelease = Event()
        self.buttonRelease.set()
        self.lock = Lock()
        self.lockStatus = Lock()
        self.thread = Thread(target=self._callEvent)
        self.thread.start()

    def stop(self):
        Resource.stop(self)
        self.disable()
        self.buttonPressed.set()

    def registerEvent(self, cb, event, delay=0, *args, **kwargs):
        self.events[event].append((cb, delay, args, kwargs))
        if event == ONPRESSED:
            self.events[ONPRESSED].sort(key=lambda colonnes: colonnes[1])

    def enable(self):
        with self.lockStatus:
            self.state = True

    def disable(self):
        with self.lockStatus:
            self.state = False

    def status(self):
        with self.lockStatus:
            return self.state

    def _callEvent(self):
        while not self.terminated:
            self.buttonPressed.wait()
            with self.lock:
                if not self.status():
                    #event is not enable
                    self.buttonRelease.wait()
                    self.buttonPressed.clear()
                    continue
                pressTime = time.time()
                map(self.onEvent, self.events[ONTOUCHED])
                for i, event in enumerate(self.events[ONPRESSED]):
                    wait = event[1] - (time.time() - pressTime)
                    if wait < 0:
                        wait = 0
                    if not self.buttonRelease.wait(wait):
                        if event == self.events[ONPRESSED][-1]:
                            self.onEvent(event)
                    elif wait == 0:
                        self.onEvent(self.events[ONPRESSED][i])
                        break
                    elif i > 0:
                        # button was released, call previous on pressed if
                        # exist.
                        self.onEvent(self.events[ONPRESSED][i - 1])
                        break
                self.buttonRelease.wait()
                map(self.onEvent, self.events[ONRELEASED])
                self.buttonPressed.clear()
        print ('button thread Terminated')

    def onEvent(self, event):
        event[0](*event[2], **event[3])

    @queue_call
    def _onPress(self):
        with self.lock:
            self.buttonRelease.clear()
            self.buttonPressed.set()

    @queue_call
    def _onRelease(self):
        self.buttonRelease.set()


class Buttons:

    def __init__(self):
        self.gpio = GpioPi(self.ONPRESSED, self.ONRELEASED)
        #self.mpr = Mpr121(self.ONPRESSED, self.ONRELEASED)
        self.att = attiny85btn(self.ONPRESSED, self.ONRELEASED)
        #self.buttons = {MPR121: {}, GPIO: {},ATTINY : {}}
        self.buttons = {GPIO: {},ATTINY : {}}

    def register(self, type, btn=0):
        if btn not in self.buttons[type]:
            self.buttons[type][btn] = []
            if type == GPIO:
                self.gpio.register(btn)
            elif type == MPR121:
                self.mpr.register(btn)
        self.buttons[type][btn].append(Button())
        return self.buttons[type][btn][-1]

    def ONPRESSED(self, type, btn):
        if btn in self.buttons[type]:
            for btn in self.buttons[type][btn]:
                btn._onPress()

    def ONRELEASED(self, type, btn):
        if btn in self.buttons[type]:
            for btn in self.buttons[type][btn]:
                btn._onRelease()

    def stop(self):
        for type in self.buttons.keys():
            for id in self.buttons[type].keys():
                for btn in self.buttons[type][id]:
                    btn.stop()
        self.gpio.stop()
        self.mpr.stop()


BUTTONS = Buttons()


def main(args):
    def touch():
        print "touched"

    def longpress():
        print "LongPress"

    def verylongpress():
        print "veryLongPress"

    def press(val=0):
        print "press", val

    def release():
        print "release"

    AUTO = BUTTONS.register(ATTINY)
    AUTO.registerEvent(press, ONPRESSED, 0, 2)
    AUTO.registerEvent(longpress, ONPRESSED, 2)
    #AUTO.registerEvent(verylongpress, ONPRESSED, 4)
    AUTO.registerEvent(touch, ONTOUCHED)
    AUTO.registerEvent(release, ONRELEASED)

    print ('done')


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
