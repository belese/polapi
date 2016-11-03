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
from resources.vibrator import BUZZ,OK,READY,CANCEL,TOUCHED,ERROR,REPEAT
from resources.power import POWER,LOWER,HIGHER
from resources.wiring import DECLENCHEUR,AUTO,LUM,VALUE0,VALUE1,VALUE2,VALUE3,FORMAT
from resources.modes import Enhancer

from resources.log import LOG,log as l
from resources.camera import CAMERA

from resources.qrcode import QRCODE

log = LOG.log

#BATTERY OPTION
BATLOW = 4400
BATVERYLOW = 4300
BATCHARGE = 5300

# default mode timeout
TIMEOUT = 3

#Auto off delay
AUTOOFF = 600

import operator

class Power(object) :
    #POWER.registerEvent(self.onLowBattery,LOWER,BATLOW)
    #POWER.registerEvent(self.onVeryLowBattey,LOWER,BATVERYLOW)
    #POWER.registerEvent(self.onCharge,HIGHER,BATCHARGE)        

    def __init__(self) :
        self.stopped = False
        self.lastTouched = time.time()
        threading.Thread(target=self.autostop).start()
        self.btnauto = BUTTONS.register(MPR121, AUTO)
        self.btnlum = BUTTONS.register(MPR121, LUM)
        self.btnsize = BUTTONS.register(MPR121, FORMAT)
        self.btnval0 = BUTTONS.register(MPR121, VALUE0)
        self.btnval1 = BUTTONS.register(MPR121, VALUE1)
        self.btnval2 = BUTTONS.register(MPR121, VALUE2)
        self.btnval3 = BUTTONS.register(MPR121, VALUE3)
        self.btnshutter = BUTTONS.register(ATTINY)
        

        self.btnauto.registerEvent(self.ontouched,ONTOUCHED)
        self.btnauto.registerEvent(self.onForceHalt,ONPRESSED,6)
        self.btnlum.registerEvent(self.ontouched,ONTOUCHED)
        self.btnsize.registerEvent(self.ontouched,ONTOUCHED)
        self.btnval0.registerEvent(self.ontouched,ONTOUCHED)
        self.btnval1.registerEvent(self.ontouched,ONTOUCHED)
        self.btnval2.registerEvent(self.ontouched,ONTOUCHED)
        self.btnval3.registerEvent(self.ontouched,ONTOUCHED)
        self.btnshutter.registerEvent(self.ontouched,ONTOUCHED)
    
    def ontouched(self) :    
        self.lastTouched = time.time()
    
    def autostop(self) :
        while not self.stopped :
            if time.time() >= (self.lastTouched + (AUTOOFF)) :                
                self.halt()            
            time.sleep(10)
    
    def onForceHalt(self) :
        BUZZ.buzz(OK)
        print ('Forced Halt')
        self.halt()

    def halt(self) :  
        self.stop()
        os.system("shutdown now -h")

    def stop(self) :
        self.stopped = True      

class polapi:
    def __init__(self):
        log('Enter in Polapi Main Application')
        self.power = Power()
        self.btnauto = BUTTONS.register(MPR121, AUTO)
        self.btnlum = BUTTONS.register(MPR121, LUM)
        self.btnsize = BUTTONS.register(MPR121, FORMAT)
        self.btnval0 = BUTTONS.register(MPR121, VALUE0)
        self.btnval1 = BUTTONS.register(MPR121, VALUE1)
        self.btnval2 = BUTTONS.register(MPR121, VALUE2)
        self.btnval3 = BUTTONS.register(MPR121, VALUE3)
                
        
        self.btnprintmanual = BUTTONS.register(MPR121, VALUE2)
        self.btnreprint = BUTTONS.register(MPR121, VALUE3)
        self.btnshutter = BUTTONS.register(ATTINY)
        
        self.stopchineseprint = BUTTONS.register(ATTINY)
        self.stopchineseprint.disable()
        


        self.btnauto.registerEvent(self.onAuto, ONPRESSED)
        self.btnauto.registerEvent(self.onlock, ONPRESSED, 3)
        self.btnauto.registerEvent(self.onbuzz, ONTOUCHED)
        
        self.btnlum.registerEvent(self.onModeSelect, ONPRESSED, 0, 'Luminosity')
        self.btnlum.registerEvent(self.onModeSelect, ONPRESSED, 2, 'Effect')
        self.btnlum.registerEvent(self.onbuzz, ONTOUCHED)
        
        self.btnsize.registerEvent(self.onModeSelect, ONPRESSED, 0, 'Size')
        self.btnsize.registerEvent(self.onModeSelect, ONPRESSED, 2, 'Slitscan') 
        self.btnsize.registerEvent(self.onbuzz, ONTOUCHED)               

        self.btnprintmanual.registerEvent(self.onPrintManual, ONPRESSED, 2)
        self.btnprintmanual.registerEvent(self.onbuzz, ONTOUCHED)               

        self.btnreprint.registerEvent(self.onReprint, ONPRESSED, 2)
        self.btnreprint.registerEvent(self.onbuzz, ONTOUCHED)               
        
        self.btnshutter.registerEvent(self.onShutterTouched, ONTOUCHED)
        self.btnshutter.registerEvent(self.onPhoto, ONRELEASED)

        self.stopchineseprint.registerEvent(self.power.onForceHalt,ONPRESSED,2)

        self.buttons = [self.btnval0, self.btnval1, self.btnval2, self.btnval3]
        for button in self.buttons:
            button.disable()        
        
        for i,btn in enumerate(self.buttons) :
            btn.registerEvent(self.onValue, ONPRESSED, 0, i)
            #btn.registerEvent(self.onbuzz, ONTOUCHED)

                       
        
        QRCODE.registerEvent(self.onRomanPhoto,'r')
        
        self.timer = threading.Event()
        self.timeoutset = threading.Event()   
        self.imageReady = threading.Event()
        self.imageReady.clear()
        self.lockTimer = threading.Lock()  
        self.enhancer = Enhancer()              
        
        
        self.stopped = False
        
        self.lock = False
        
        self._lastphoto = None
        self._lastqrdata = None

        threading.Thread(target=self.timeout).start()
        threading.Thread(target=self.printPhoto).start()
        
                
        BUZZ.buzz(READY)
                
    def onPrintManual(self) :
        print ('Print manual')
        BUZZ.buzz(OK)
        with open('resources/manual/manual.fr.txt','r') as manual : 
            for line in manual :
                PRINTER.print_txt(line)        

    def onReprint(self) :
        if self._lastphoto :
            BUZZ.buzz(OK)
            self.printPhoto(self._lastphoto) 
        else :
            BUZZ.buzz(ERROR)

    
    def printPhoto(self):
        log("Print photo")  
        self.imageReady.wait()
        while not self.stopped:                                                          
            img = self.enhancer.postProcess(self.picture)        
            if img is not None:            
                img.save('roman','JPEG')
                self.enhancer.disable()
                self.stopchineseprint.enable()            
                PRINTER.printToPage(img,self.onprintfinished)
            else :            
                print ('******************img = None, enable btn shutter')
                time.sleep(1)
                QRCODE.enable()                
                self.btnshutter.enable()                
            self.imageReady.clear()
            self.imageReady.wait()

    def onShutterTouched(self):
        log("Shutter touched")  
        QRCODE.disable()        
        CAMERA.getPhoto(self.onImageReady)        
    
    def onPhoto(self):
        log("Photo mode selected")
        print ('************disable btn shutter')
        self.btnshutter.disable() 
        
    def onRomanPhoto(self,data) :
        print ('on Roman photo selected')
        self.enhancer.modes['Slitscan'].disable()
        self.enhancer.modes['Romanphoto'].enable()
        self.enhancer.modes['Romanphoto'].setMode(data)
        
    def onImageReady(self, picture):  
        print ('Image ready')                       
        self.picture = picture
        self.imageReady.set() 
    
    def onprintfinished(self):                    
        self.enhancer.enable()        
        self.enhancer.modes['Slitscan'].enable()
        QRCODE.enable()
        self.stopchineseprint.disable()
        self.btnshutter.enable()
        BUZZ.buzz(OK)

                                        
    def onAuto(self):
        if not self.lock:
            self.cancelTimer()
            self.enhancer.default()             
            BUZZ.buzz(OK)

    def onbuzz(self):
        BUZZ.buzz(TOUCHED)    

    def onlock(self):
        self.cancelTimer()
        if self.lock:
            log("Unlock buttons")
            self.btnlum.enable()
            self.btnsize.enable()
            self.btnreprint.enable()
            self.btnprintmanual.enable()
        else:
            log("lock buttons")
            self.btnlum.disable()
            self.btnsize.disable()
            self.btnreprint.disable()
            self.btnprintmanual.disable()
            for button in self.buttons:
                button.disable()
        self.lock = not self.lock
        BUZZ.buzz(OK)

    def onModeSelect(self, mode):
        log("Enter in select mode")
        if mode in ('Effect','Slitscan') :
            BUZZ.buzz(TOUCHED)
        self.cancelTimer()
        self.setTimer()    
        self.selectedmode = mode 
        self.btnprintmanual.disable()
        self.btnreprint.disable()
        
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
                self.selectedmode = None
                BUZZ.buzz(CANCEL)
            for button in self.buttons:
                   button.disable()
            self.btnprintmanual.enable()
            self.btnreprint.enable()             
            self.timer.clear()
            self.timeoutset.clear()

    def onValue(self, val):
        log("Select choice done")
        self.cancelTimer()
        print ('set enhancer mode',self.selectedmode,val)
        self.enhancer.setMode(self.selectedmode,val)
        BUZZ.buzz(OK)        
        self.selectedmode = None
    
    def stop(self) :
        self.stopped = True
        self.timer.set()
        self.imageReady.set()
        self.cancelTimer()
        self.enhancer.disable()
        self.power.stop()
        CAMERA.stop()
        BUTTONS.stop()
        PRINTER.stop()
        BUZZ.stop()
        POWER.stop()
    


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
