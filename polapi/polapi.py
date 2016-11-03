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
from resources.vibrator import BUZZ,OK,READY,CANCEL,TOUCHED,ERROR,REPEAT
from resources.power import POWER,LOWER,HIGHER
#from resources.modes.slitscan import SlitScan, SCAN_MODE, SCAN_MODE_FIX, SCAN_MODE_LIVE
from resources.cammode.qrcode import QrCode
from resources.wiring import DECLENCHEUR,AUTO,LUM,VALUE0,VALUE1,VALUE2,VALUE3,FORMAT
from resources.imgmode.luminosity import luminosity
from resources.imgmode.effect import effect
from resources.imgmode.size import size
from resources.imgmode.slitscan import slitscan
from resources.cammode.photo import Photo
from resources.cammode.qrcode import QrCode
from resources.cammode.romanphoto import RomanPhoto

from resources.log import LOG,log as l
#from resources.enhancer.ying import Ying_2017_CAIP

log = LOG.log




#BATTERY OPTION
BATLOW = 4400
BATVERYLOW = 4300
BATCHARGE = 5300


# default mode timeout
TIMEOUT = 3

#Auto off delay
AUTOOFF = 600





BTNAUTO = BUTTONS.register(MPR121, AUTO)
BTNLUM = BUTTONS.register(MPR121, LUM)
BTNSIZE = BUTTONS.register(MPR121, FORMAT)
BTNVAL0 = BUTTONS.register(MPR121, VALUE0)
BTNVAL1 = BUTTONS.register(MPR121, VALUE1)
BTNVAL2 = BUTTONS.register(MPR121, VALUE2)
BTNVAL3 = BUTTONS.register(MPR121, VALUE3)
BTNQRCODE = BUTTONS.register(MPR121, VALUE1)
BTNPRINTMANUAL = BUTTONS.register(MPR121, VALUE2)

import operator

class polapi:
    def __init__(self):
        log('Enter in Polapi Main Application')
        self.timer = threading.Event()
        self.timeoutset = threading.Event()        
        self.lockTimer = threading.Lock()                
        self.imgmodes = [luminosity(), size(), effect(), slitscan()]
        self.imgselectedmode = None
        for mode in self.imgmodes:
            mode.setMode(-1)
        self.buttons = [BTNVAL0, BTNVAL1, BTNVAL2, BTNVAL3]
        for button in self.buttons:
            button.disable()
       
        self.stopped = False
        self.lastTouched = time.time()

        self.lock = False
        self.modes = {'photo' : Photo(self.imgmodes,self.ontouched,self.oncancel),'qrcode' : QrCode(self.imgmodes,self.ontouched,self.oncancel), 'roman' : RomanPhoto(self.imgmodes,self.ontouched,self.oncancel)}
        print self.modes

        self.actualmode = self.modes['photo']
        print self.actualmode
        self.actualmode.enable()

        threading.Thread(target=self.timeout).start()
        threading.Thread(target=self.autostop).start()
        
        BUZZ.buzz(READY)

        BTNAUTO.registerEvent(self.onAuto, ONPRESSED)
        BTNAUTO.registerEvent(self.onlock, ONPRESSED, 3)
        BTNLUM.registerEvent(self.onImgModeSelect, ONPRESSED, 0, 0)
        BTNLUM.registerEvent(self.onImgModeSelect, ONPRESSED, 2, 2)
        BTNSIZE.registerEvent(self.onImgModeSelect, ONPRESSED, 0, 1)
        BTNSIZE.registerEvent(self.onImgModeSelect, ONPRESSED, 2, 3)

        BTNAUTO.registerEvent(self.ontouched, ONTOUCHED)
        BTNLUM.registerEvent(self.ontouched, ONTOUCHED)
        BTNSIZE.registerEvent(self.ontouched, ONTOUCHED)

        

        BTNPRINTMANUAL.registerEvent(self.onPrintManual, ONPRESSED, 3)
        BTNPRINTMANUAL.registerEvent(self.ontouched, ONTOUCHED)
        BTNQRCODE.registerEvent(self.onQrCodeMode, ONPRESSED, 3)
        BTNQRCODE.registerEvent(self.ontouched, ONTOUCHED)
        for i,btn in enumerate(self.buttons) :
            btn.registerEvent(self.onValue, ONPRESSED, 0, i)

        POWER.registerEvent(self.onLowBattery,LOWER,BATLOW)
        POWER.registerEvent(self.onVeryLowBattey,LOWER,BATVERYLOW)
        POWER.registerEvent(self.onCharge,HIGHER,BATCHARGE)        

        
    def onPrintManual(self) :
        print ('Print manual')
        BUZZ.buzz(OK)
        with open('resources/manual/manual.fr.txt','r') as manual : 
            for line in manual :
                PRINTER.print_txt(line)        

    def onQrCodeMode(self) :        
        if self.actualmode == self.modes['qrcode'] :
            self.oncancel()
        else :
            self.oncancel('qrcode')
        
    def onLowBattery(self) :
        print ('Low Battery')
    
    def onVeryLowBattey(self) :
        print ('Very Low Battery')
    
    def onCharge(self) :
        pass
    
    def onForceHalt(self) :
        print ('Forced Halt')
        self.halt()
                           
    def onAuto(self):
        if not self.lock:
            self.cancelTimer()
            for mode in self.imgmodes:
                mode.setMode(-1)
            BUZZ.buzz(OK)

    def ontouched(self):
        BUZZ.buzz(TOUCHED)
        self.lastTouched = time.time()

    def onlock(self):
        self.cancelTimer()
        if self.lock:
            log("Unlock buttons")
            BTNLUM.enable()
            BTNSIZE.enable()
            BTNQRCODE.enable()
            BTNPRINTMANUAL.enable()
            #BTNREPRINT.enable()
        else:
            log("lock buttons")
            BTNLUM.disable()
            BTNSIZE.disable()
            BTNQRCODE.disable()
            BTNPRINTMANUAL.disable()
            #BTNREPRINT.disable()
            for button in self.buttons:
                button.disable()
        self.lock = not self.lock
        BUZZ.buzz(OK)

    def onImgModeSelect(self, mode):
        log("Enter in select mode")
        if mode > 1 :
            BUZZ.buzz(TOUCHED)
        self.cancelTimer()
        self.setTimer()    
        self.imgselectedmode = mode 
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
                self.imgselectedmode = None
                BUZZ.buzz(CANCEL)
                for button in self.buttons:
                    button.disable()            
            self.timer.clear()
            self.timeoutset.clear()

    def onValue(self, val):
        log("Select choice done")
        self.cancelTimer()
        self.imgmodes[self.imgselectedmode].setMode(val)
        BUZZ.buzz(OK)
        for button in self.buttons:
            button.disable()
        self.imgselectedmode = None
    
    def oncancel(self,nextmode=None,*args,**kwargs) :
        print ('oncancel, set mode to ',nextmode)
        self.actualmode.disable()
        self.actualmode = self.modes[nextmode] if nextmode!= None else self.modes['photo']
        self.actualmode.enable(*args,**kwargs)
        print ('oncancel, modeset to ',nextmode)

    def stop(self) :
        self.stopped = True
        self.timer.set()
        self.cancelTimer()
        self.actualmode.disable()                
        CAMERA.stop()
        BUTTONS.stop()
        PRINTER.stop()
        BUZZ.stop()
        POWER.stop()
    
    def autostop(self) :
        while not self.stopped :
            if time.time() >= (self.lastTouched + (AUTOOFF)) :                
                self.halt()            
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
    try :
        CAM.stop()
    except :
        CAMERA.stop()
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
