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
import os
from PIL import Image, ImageEnhance

from resources.printer import PRINTER
from resources.buttons import GPIO, MPR121, ATTINY, BUTTONS, ONTOUCHED, ONPRESSED, ONRELEASED
from resources.camera import CAMERA
from resources.vibrator import BUZZ
from resources.power import POWER,LOWER,HIGHER
from resources.modes.slitscan import SlitScan, SCAN_MODE, SCAN_MODE_FIX, SCAN_MODE_LIVE
from resources.modes.qrcode import QrCode

from resources.log import LOG,log as l
#from resources.enhancer.ying import Ying_2017_CAIP

log = LOG.log


# GPIO PIN ID
DECLENCHEUR = 4  # gpio


# MPR121 PIN ID
AUTO = 5
LUM = 4
FORMAT = 6

VALUE0 = 3
VALUE1 = 2
VALUE2 = 1
VALUE3 = 0

#BATTERY OPTION
BATLOW = 4400
BATVERYLOW = 4300
BATCHARGE = 5300


# default mode timeout
TIMEOUT = 3

#Auto off delay
AUTOOFF = 600
CAMERAAUTOOFF = 120

# Luminosity Option
LOW = 10
MEDIUM_LOW = 11
MEDIUM_HIGH = 12
HIGH = 13

#Buzzer (DutyCycle,time)
OK = ((1, 0.2), (0, 0.1), (1, 0.2),(0, 0.1))
READY = ((1, 0.3), (0, 0.3), (1, 0.3), (0, 0.3), (1, 0.3))
CANCEL = ((1, 0.1),)
TOUCHED = ((1, 0.25),)
ERROR =((1,0.5),(0,0.1),(1,0.5),(0,0.1),(1,0.5))
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
BTNFORCESTOP = BUTTONS.register(ATTINY)

BTNAUTO = BUTTONS.register(MPR121, AUTO)
BTNLUM = BUTTONS.register(MPR121, LUM)
BTNSIZE = BUTTONS.register(MPR121, FORMAT)
BTNVAL0 = BUTTONS.register(MPR121, VALUE0)
BTNVAL1 = BUTTONS.register(MPR121, VALUE1)
BTNVAL2 = BUTTONS.register(MPR121, VALUE2)
BTNVAL3 = BUTTONS.register(MPR121, VALUE3)
BTNQRCODE = BUTTONS.register(MPR121, VALUE1)
BTNPRINTMANUAL = BUTTONS.register(MPR121, VALUE2)
BTNREPRINT = BUTTONS.register(MPR121, VALUE3)


class mode:
    def setMode(self, value):
        pass

    def postProcess(self, img):
        return img



import operator


class luminosity(mode):
    def __init__(self):
        self.values = [LUMLOW, LUMMEDIUM, LUMMEDIUMHIGH, LUMHIGH, LUMDEFAULT]
        self.value = -1
        self.postvalue = ([1.5, 1.2], [1.2, 1.3], [
                          1, 1.5], [0.8, 1.6], [1, 1])

    def setMode(self, value):
        log("Select Luminosity %d" % value)
        self.value = value
        CAMERA.setSettings(self.values[value])        

    def postProcess(self, img):
        log("Luminosity post process")
        # img.save('original.jpg')
        #img = Ying_2017_CAIP(img) 
        try :
            img = self.equalize(img)
        except :
            pass
        img = ImageEnhance.Color(img)        
        img = img.enhance(0)
        # img.save('bw.jpg')
        img = ImageEnhance.Brightness(img)
        img = img.enhance(self.postvalue[self.value][0])
        # img.save('brightness.jpg')
        img = ImageEnhance.Contrast(img)
        img = img.enhance(self.postvalue[self.value][1])
        return img

    def equalize(self,im):
        h = im.convert("L").histogram()
        lut = []
        for b in range(0, len(h), 256):
            # step size
            step = reduce(operator.add, h[b:b+256]) / 255
            # create equalization lookup table
            n = 0
            for i in range(256):
                lut.append(n / step)
                n = n + h[i+b]
        # map image through lookup table
        return im.point(lut*im.layers)


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


class slitscan(mode):
    def __init__(self) :
        self.values = [SCAN_MODE, SCAN_MODE_FIX, SCAN_MODE_LIVE,SCAN_MODE_FIX]
        self.mode = -1
        self.fps = CAMERA.framerate

    def setMode(self,value) :
        print ('Slitscan set mode',value)
        if self.values[value] == SCAN_MODE_LIVE :
            self.fps = CAMERA.framerate
            CAMERA.framerate = 15
        elif self.fps != CAMERA.framerate :
            CAMERA.framerate = self.fps
        self.mode = value
    
    def getMode(self) :
        print ('Slitscan get mode',self.mode,self.values[self.mode])
        return self.values[self.mode]



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
        self.modes = [luminosity(), size(), effect(), slitscan()]
        for mode in self.modes:
            mode.setMode(self.mode)
        self.buttons = [BTNVAL0, BTNVAL1, BTNVAL2, BTNVAL3]
        for button in self.buttons:
            button.disable()
        self.slitscanobject = None
        self.slitscan = False
        self.stopped = False
        self.sleeping = False
        self.lastTouched = time.time()

        threading.Thread(target=self.timeout).start()
        threading.Thread(target=self.autostop).start()

        BTNSHUTTER.registerEvent(self.wakeup, ONTOUCHED)
        BTNSHUTTER.registerEvent(self.onShutterTouched, ONTOUCHED)
        BTNSHUTTER.registerEvent(self.onPhoto, ONPRESSED)
        BTNSHUTTER.registerEvent(self.onSlitScan, ONPRESSED, 1)
        BTNSHUTTER.registerEvent(self.onStopSlitScan, ONRELEASED)
        BTNFORCESTOP.disable()
        BTNFORCESTOP.registerEvent(self.onForceHalt, ONPRESSED, 2)
        BTNFORCESTOP.registerEvent(self.wakeup, ONTOUCHED)
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

        BTNQRCODE.registerEvent(self.onQrCodeMode, ONPRESSED, 3)
        BTNQRCODE.registerEvent(self.ontouched, ONTOUCHED)

        BTNPRINTMANUAL.registerEvent(self.onPrintManual, ONPRESSED, 3)
        BTNPRINTMANUAL.registerEvent(self.ontouched, ONTOUCHED)
        BTNREPRINT.registerEvent(self.reprint, ONPRESSED, 3)
        BTNREPRINT.registerEvent(self.ontouched, ONTOUCHED)

        for i, btn in enumerate(self.buttons):
            btn.registerEvent(self.onValue, ONPRESSED, 0, i)
            #if btn != BTNVAL1:
                # BTNVAL0 already registere with BTNSLITSCANMODE
            #    btn.registerEvent(self.ontouched, ONTOUCHED)

        POWER.registerEvent(self.onLowBattery,LOWER,BATLOW)
        POWER.registerEvent(self.onVeryLowBattey,LOWER,BATVERYLOW)
        POWER.registerEvent(self.onCharge,HIGHER,BATCHARGE)        

    
    @property
    def slitscanmode(self) :
        print ('slitscanmode : ',self.modes[3].getMode())
        return self.modes[3].getMode()
    
    def onPrintManual(self) :
        print ('Print manual')
        BUZZ.buzz(OK)
        with open('resources/manual/manual.fr.txt','r') as manual : 
            for line in manual :
                PRINTER.print_txt(line)        

    def onQrCodeMode(self) :
        CAMERA.startMode(QrCode(camera.resolution))
    
    def onQrCode(self,data) :
        print ('qr code decoded',data)
        
    def onLowBattery(self) :
        print ('Low Battery')
    
    def onVeryLowBattey(self) :
        print ('Very Low Battery')
    
    def onCharge(self) :
        pass
    
    def onForceHalt(self) :
        print ('Forced Halt')
        self.halt()
    
    def wakeup(self) :
        self.lastTouched = time.time()
        if self.sleeping :
            print ('Disable force stop')
            BTNFORCESTOP.disable()
            BTNSHUTTER.enable()            
            CAMERA.wake()
            self.sleeping = False            
    
    def sleep(self) :
        if not self.sleeping :
            BTNSHUTTER.disable()
            print ('Enable force stop')
            BTNFORCESTOP.enable()
            CAMERA.sleep()
            self.sleeping = True
        
    def onShutterTouched(self):
        log("Shutter touched")        
        #self.lastTouched = time.time()        
        self.imageReady.clear()
        self.picture = CAMERA.getPhoto(self.onImageReady)
        #if self.slitscanmode == SCAN_MODE_LIVE:
        #    for mode in self.modes:
        #        mode.setMode(-1)        
        self.slitscanobject = SlitScan(CAMERA.resolution,self.slitscanmode)
        CAMERA.startMode(self.slitscanobject)

    def reprint(self) :        
        if self.picture :
            BUZZ.buzz(OK)
            self.printPhoto(self.picture)        

    def onPhoto(self):
        log("Photo mode selected")
        self.cancelTimer()        
        self.slitscan = False
        print ('Wait for image')
        self.imageReady.wait()
        print ('Wait for image done')
        self.printPhoto(self.picture)

    def printPhoto(self, img):
        log("Print photo")
        try :
            for mode in self.modes:        
                img = mode.postProcess(img)
        except Exception as e :
            log('Exception',str(e),level=30)
            BUZZ.buzz(ERROR)
            raise
        else :            
            self.printID = PRINTER.printToPage(img,self.onprintfinished)

    def onSlitScan(self):
        log('Slitscan mode selected')
        self.slitscan = True
        if self.slitscanmode == SCAN_MODE_LIVE:
            self.printID = PRINTER.streamImages(self.slitscanobject,self.onprintfinished)
        BUZZ.buzz(TOUCHED)

    def onStopSlitScan(self):
        log('Shutter released')
        CAMERA.stopMode()                
        if self.slitscan and self.slitscanmode in (SCAN_MODE, SCAN_MODE_FIX):            
            img = self.slitscanobject.getImage()
            self.picture = img
            self.printPhoto(img)
        elif self.slitscan :
            for mode in self.modes:
                mode.setMode(self.mode)
        
        
        del(self.slitscanobject)
        self.slitscan = False
        self.slitscanobject = None

    def onImageReady(self, picture):  
        print ('Image ready')
        self.imageReady.set()                
        self.picture = picture
            

    def onprintfinished(self):                    
        BUZZ.buzz(OK)        
        self.wakeup()            
            
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
        self.lastTouched = time.time()
        #self.wakeup()

    def onlock(self):
        self.cancelTimer()
        if self.lock:
            log("Unlock buttons")
            BTNLUM.enable()
            BTNSIZE.enable()
            BTNQRCODE.enable()
            BTNPRINTMANUAL.enable()
            BTNREPRINT.enable()
        else:
            log("lock buttons")
            BTNLUM.disable()
            BTNSIZE.disable()
            BTNQRCODE.disable()
            BTNPRINTMANUAL.disable()
            BTNREPRINT.disable()
            for button in self.buttons:
                button.disable()
        self.lock = not self.lock
        BUZZ.buzz(OK)

    def onModeSelect(self, mode):
        log("Enter in select mode")
        if mode > 1 :
            BUZZ.buzz(TOUCHED)
        self.cancelTimer()
        self.setTimer()
        self.lastMode = self.mode    
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
            
    def stop(self) :
        self.stopped = True
        self.timer.set()
        self.cancelTimer()        
        CAMERA.stop()
        BUTTONS.stop()
        PRINTER.stop()
        BUZZ.stop()
        POWER.stop()
    
    def autostop(self) :
        while not self.stopped :
            if time.time() >= (self.lastTouched + (AUTOOFF)) :                
                self.halt()            
            #if not  self.sleeping and time.time() >= (self.lastTouched + (CAMERAAUTOOFF)) :
            #    self.sleep()                
            time.sleep(10)
    
    def halt(self) :
        try :
            self.stop()
        except :
            raise
        finally :
            os.system("shutdown now -h")



def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')

#CAM = polapi()


#"""
try:
    CAM = polapi()
    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C to quit')
    signal.pause()
except :
    raise
finally :
    CAM.stop()
#"""
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
