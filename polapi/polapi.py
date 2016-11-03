#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  polapi_v2.py
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
import signal
import sys
import threading
import time
from PIL import Image, ImageEnhance

from resources.printer import PRINTER
from resources.buttons import GPIO, MPR121, ATTINY, BUTTONS, ONTOUCHED, ONPRESSED, ONRELEASED
from resources.camera import CAMERA, SCAN_MODE, SCAN_MODE_FIX, SCAN_MODE_LIVE
from resources.vibrator import BUZZ
from resources.power import POWER,LOWER,HIGHER

from resources.log import LOG
#from resources.enhancer.ying import Ying_2017_CAIP

log = LOG.log


# GPIO PIN ID
DECLENCHEUR = 4  # gpio

# MPR121 PIN ID
AUTO = 2
LUM = 1
FORMAT = 0

VALUE0 = 3
VALUE1 = 4
VALUE2 = 5
VALUE3 = 6

#BATTERY OPTION
BATLOW = 4000
BATVERYLOW = 3900
BATCHARGE = 5300


# default mode timeout
TIMEOUT = 3
# Luminosity Option
LOW = 10
MEDIUM_LOW = 11
MEDIUM_HIGH = 12
HIGH = 13

#Buzzer (DutyCycle,time)
OK = ((1, 0.2), (0, 0.1), (1, 0.2), (0, 0.1))
READY = ((1, 0.3), (0, 0.3), (1, 0.3), (0, 0.3), (1, 0.3))
CANCEL = ((1, 0.1), (0, 0.1))
TOUCHED = ((1, 0.25), (0, 0.1))
def REPEAT(x): return ((1, 0.2), (0, 0.1)) * x


# FORMAT OPTION
IDENTITY = (296, 384)
SQUARE = (384, 384)
STANDARD = (576, 384)
PANO = (1152, 384)

# CAMERA SETTINGS
LUMDEFAULT = {"sharpness": 0,
              "contrast": 0,
              "brightness": 50,
              "saturation": 0,
              "drc_strength": "off",
              "ISO": 0,
              "exposure_compensation": 0,
              "exposure_mode": 'auto',
              "meter_mode": 'average',
              "awb_mode": 'auto',
              }
LUMLOW = {"sharpness": 0,
          "contrast": 50,
          "brightness": 70,
          "saturation": 0,
          "drc_strength": "high",
          "ISO": 800,
          "exposure_compensation": 0,
          "exposure_mode": 'night',
          "meter_mode": 'average',
          "awb_mode": 'incandescent',
          }

LUMMEDIUM = {"sharpness": 0,
             "contrast": 20,
             "brightness": 60,
             "saturation": 0,
             "ISO": 600,
             "exposure_compensation": 0,
             "exposure_mode": 'auto',
             "meter_mode": 'average',
             "drc_strength": "medium",
             "awb_mode": 'shade',
             }

LUMMEDIUMHIGH = {"sharpness": 0,
                 "contrast": 0,
                 "brightness": 50,
                 "saturation": 0,
                 "ISO": 300,
                 "exposure_compensation": 0,
                 "exposure_mode": 'auto',
                 "meter_mode": 'average',
                 "drc_strength": "low",
                 "awb_mode": 'cloudy',
                 }
LUMHIGH = {"sharpness": 0,
           "contrast": 0,
           "brightness": 50,
           "saturation": 0,
           "ISO": 100,
           "exposure_compensation": 0,
           "exposure_mode": 'auto',
           "meter_mode": 'average',
           "drc_strength": "off",
           "awb_mode": 'sunlight',
           }

BTNSHUTTER = BUTTONS.register(ATTINY)
BTNAUTO = BUTTONS.register(MPR121, AUTO)
BTNLUM = BUTTONS.register(MPR121, LUM)
BTNSIZE = BUTTONS.register(MPR121, FORMAT)
BTNVAL0 = BUTTONS.register(MPR121, VALUE0)
BTNVAL1 = BUTTONS.register(MPR121, VALUE1)
BTNVAL2 = BUTTONS.register(MPR121, VALUE2)
BTNVAL3 = BUTTONS.register(MPR121, VALUE3)
BTNSLITSCANMODE = BUTTONS.register(MPR121, VALUE0)


class mode:
    def setMode(self, value):
        pass

    def postProcess(self, img):
        return img


class luminosity(mode):
    def __init__(self):
        self.values = [LUMLOW, LUMMEDIUM, LUMMEDIUMHIGH, LUMHIGH, LUMDEFAULT]
        self.value = -1
        self.postvalue = ([1.5, 1.2], [1.2, 1.3], [
                          1, 1.5], [0.8, 1.6], [1.2, 1.5])

    def setMode(self, value):
        log("Select Luminosity %d" % value)
        self.value = value
        CAMERA.setSettings(self.values[value])        

    def postProcess(self, img):
        log("Luminosity post process")
        # img.save('original.jpg')
        #img = Ying_2017_CAIP(img) 
        img = ImageEnhance.Color(img)
        
        img = img.enhance(0)
        # img.save('bw.jpg')
        img = ImageEnhance.Brightness(img)
        img = img.enhance(self.postvalue[self.value][0])
        # img.save('brightness.jpg')
        img = ImageEnhance.Contrast(img)
        img = img.enhance(self.postvalue[self.value][1])
        return img


class size(mode):
    def __init__(self):
        self.values = [IDENTITY, SQUARE, STANDARD, PANO, STANDARD]
        self.value = -1

    def setMode(self, value):
        log("Select Mode %d" % value)
        self.value = value
        if value == 0:
            value += 1
        CAMERA.setSettings({'resolution': self.values[value]})

    def postProcess(self, img):
        log("Format post process")
        resolution = self.values[self.value]
        # resize, crop and rotate image before printing
        img_ratio = img.size[0] / float(img.size[1])
        ratio = resolution[0] / float(resolution[1])
        if ratio > img_ratio:
            img = img.resize(
                (resolution[0], int(
                    resolution[0] * img.size[1] / img.size[0])), Image.ANTIALIAS)
            box = (int((img.size[0] - resolution[0]) / 2), 0,
                   int((img.size[0] + resolution[0]) / 2), img.size[1])
            img = img.crop(box)
        elif ratio < img_ratio:
            img = img.resize(
                (int(
                    resolution[1] *
                    img.size[0] /
                    img.size[1]),
                    resolution[1]),
                Image.ANTIALIAS)
            box = (int((img.size[0] - resolution[0]) / 2), 0,
                   int((img.size[0] + resolution[0]) / 2), img.size[1])
            img = img.crop(box)
        else:
            img = img.resize((resolution[0], resolution[1]), Image.ANTIALIAS)
        return img.rotate(90, expand=1)


class effect(mode):
    def __init__(self):
        self.values = ['gpen', 'cartoon', 'pastel', 'oilpaint', 'none']
        self.value = -1

    def setMode(self, value):
        log("Set effect to %d" % value)
        CAMERA.setSettings({'image_effect': self.values[value]})


class shader(mode):
    pass


class polapi:
    def __init__(self):
        log('Enter in Polapi Main Application')
        self.timer = threading.Event()
        self.timeoutset = threading.Event()
        self.imageReady = threading.Event()
        self.lockTimer = threading.Lock()
        self.lock = False
        self.mode = -1
        self.lastMode = -1
        self.picture = None
        self.printID = None
        self.modes = [luminosity(), size(), effect(), shader()]
        for mode in self.modes:
            mode.setMode(self.mode)
        self.buttons = [BTNVAL0, BTNVAL1, BTNVAL2, BTNVAL3]
        for button in self.buttons:
            button.disable()
        self.slitscanmode = SCAN_MODE
        self.slitscanobject = None
        self.slitscan = False
        self.stopped = False
        threading.Thread(target=self.timeout).start()

        BTNSHUTTER.registerEvent(self.onShutterTouched, ONTOUCHED)
        BTNSHUTTER.registerEvent(self.onPhoto, ONPRESSED)
        BTNSHUTTER.registerEvent(self.onSlitScan, ONPRESSED, 1)
        BTNSHUTTER.registerEvent(self.onStopSlitScan, ONRELEASED)

        BUZZ.buzz(READY)

        BTNAUTO.registerEvent(self.onAuto, ONPRESSED)
        BTNAUTO.registerEvent(self.onlock, ONPRESSED, 3)
        BTNLUM.registerEvent(self.onModeSelect, ONPRESSED, 0, 0)
        BTNLUM.registerEvent(self.onModeSelect, ONPRESSED, 2, 2)
        BTNSIZE.registerEvent(self.onModeSelect, ONPRESSED, 0, 1)
        BTNSIZE.registerEvent(self.onModeSelect, ONPRESSED, 2, 3)

        BTNAUTO.registerEvent(self.ontouched, ONTOUCHED)
        BTNLUM.registerEvent(self.ontouched, ONTOUCHED)
        BTNSIZE.registerEvent(self.ontouched, ONTOUCHED)

        BTNSLITSCANMODE.registerEvent(self.onSlitScanMode, ONPRESSED, 4)
        BTNSLITSCANMODE.registerEvent(self.ontouched, ONTOUCHED)

        for i, btn in enumerate(self.buttons):
            btn.registerEvent(self.onValue, ONPRESSED, 0, i)
            if btn != BTNVAL0:
                # BTNVAL0 already registere with BTNSLITSCANMODE
                btn.registerEvent(self.ontouched, ONTOUCHED)

        CAMERA.register(self.onCameraEvent)
        PRINTER.register(self.onPrinterEvent)
        POWER.registerEvent(self.onLowBattery,LOWER,BATLOW)
        POWER.registerEvent(self.onVeryLowBattey,LOWER,BATVERYLOW)
        POWER.registerEvent(self.onCharge,HIGHER,BATCHARGE)

    def onLowBattery(self) :
        pass
    
    def onVeryLowBattey(self) :
        pass
    
    def onCharge(self) :
        pass
    
    def onSlitScanMode(self):
        if self.slitscanmode == SCAN_MODE:
            log("Select Scan mode fix")
            self.slitscanmode = SCAN_MODE_FIX
            BUZZ.buzz(REPEAT(1))
        elif self.slitscanmode == SCAN_MODE_FIX:
            log("Select Scan mode live")
            self.slitscanmode = SCAN_MODE_LIVE
            BUZZ.buzz(REPEAT(2))
        elif self.slitscanmode == SCAN_MODE_LIVE:
            log("Select Scan mode")
            self.slitscanmode = SCAN_MODE
            BUZZ.buzz(REPEAT(3))

    def onShutterTouched(self):
        log("Shutter touched")
        self.picture = CAMERA.getPhoto()
        if self.slitscanmode == SCAN_MODE_LIVE:
            for mode in self.modes:
                mode.setDefault()
        self.slitscanobject = CAMERA.startSlitScan(self.slitscanmode)

    def onPhoto(self):
        log("Photo mode selected")
        self.cancelTimer()
        self.slitscan = False
        self.imageReady.wait()
        self.printPhoto(self.picture)
        self.imageReady.clear()

    def printPhoto(self, img):
        log("Print photo")
        for mode in self.modes:
            img = mode.postProcess(img)
        self.printID = PRINTER.printToPage(img)

    def onSlitScan(self):
        log('Slitscan mode selected')
        self.slitscan = True
        if self.slitscanmode == SCAN_MODE_LIVE:
            self.printID = PRINTER.streamImages(self.slitscanobject)
        BUZZ.buzz(TOUCHED)

    def onStopSlitScan(self):
        log('Shutter released')
        CAMERA.stopSlitScan()
        CAMERA.sleep()
        BTNSHUTTER.disable()
        if self.slitscanmode == SCAN_MODE_LIVE:
            for mode in self.modes:
                mode.setMode(self.mode)

        if self.slitscan and self.slitscanmode in (SCAN_MODE, SCAN_MODE_FIX):
            img = self.slitscanobject.getImage()
            self.printPhoto(img)
        del(self.slitscanobject)
        self.slitscanobject = None

    def onCameraEvent(self, event, arg):
        if event == CAMERA.RETURN and arg[0] == self.picture:
            self.picture = arg[1]
            self.imageReady.set()

    def onPrinterEvent(self, event, arg):
        if event == PRINTER.RETURN and arg[0] == self.printID:
            log("Print finished")
            CAMERA.wake()
            BTNSHUTTER.enable()

    def onAuto(self):
        if not self.lock:
            self.cancelTimer()
            self.mode = -1
            for mode in self.modes:
                mode.setMode(self.mode)
            BUZZ.buzz(OK)
            for button in self.buttons:
                button.disable()

    def ontouched(self):
        BUZZ.buzz(TOUCHED)

    def onlock(self):
        self.cancelTimer()
        if self.lock:
            log("Unlock buttons")
            BTNLUM.enable()
            BTNSIZE.enable()
            BTNSLITSCANMODE.enable()
        else:
            log("lock buttons")
            BTNLUM.disable()
            BTNSIZE.disable()
            BTNSLITSCANMODE.disable()
            for button in self.buttons:
                button.disable()
        self.lock = not self.lock
        BUZZ.buzz(OK)

    def onModeSelect(self, mode):
        log("Enter in select mode")
        self.cancelTimer()
        self.setTimer()
        self.lastMode = self.mode    
        if mode == self.mode:
            return
        self.mode = mode
        for button in self.buttons:
            button.enable()

    def cancelTimer(self):
        if self.timer.is_set():
            self.timeoutset.set()

    def setTimer(self):
        self.timer.set()

    def timeout(self, timeout=3):
        while not self.stopped:
            self.timer.wait()
            if not self.timeoutset.wait(timeout):
                log("Select mode timeout")
                self.mode = self.lastMode
                BUZZ.buzz(CANCEL)
                for button in self.buttons:
                    button.disable()            
            self.timer.clear()
            self.timeoutset.clear()

    def onValue(self, val):
        log("Select choice done")
        self.cancelTimer()
        self.modes[self.mode].setMode(val)
        BUZZ.buzz(OK)
        for button in self.buttons:
            button.disable()


def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')

CAM = polapi()
signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to quit')
signal.pause()
CAMERA.stop()

'''
try:
    CAM = polapi()
    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C to quit')
    signal.pause()
finally:
    CAMERA.stop()
    BUTTONS.stop()
    PRINTER.stop()
    BUZZ.stop()
    //POWER.stop()
    log('Main exit')
    sys.exit(0)
'''
