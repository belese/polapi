import threading
import time

from resources.camera import CAMERA
from resources.printer import PRINTER
from resources.buttons import ATTINY, BUTTONS, ONTOUCHED, ONPRESSED, ONRELEASED
from resources.vibrator import BUZZ,OK,READY,CANCEL,TOUCHED,ERROR,REPEAT
from resources.wiring import DECLENCHEUR,AUTO,LUM,VALUE0,VALUE1,VALUE2,VALUE3
from resources.iocamera.slitscan import SlitScan, SCAN_MODE, SCAN_MODE_FIX, SCAN_MODE_LIVE
from resources.log import LOG,log as l
from . import mode
#from resources.enhancer.ying import Ying_2017_CAIP

log = LOG.log

BTNSHUTTER = BUTTONS.register(ATTINY)
BTNFORCESTOP = BUTTONS.register(ATTINY)

class Photo(mode) :
    def __init__(self,modes,ontouch,onCancel):
        log('Photo Initialisation')
        
        mode.__init__(self,modes,ontouch,onCancel)
                                
        self.imageReady = threading.Event()        
        self.picture = None
        
        self.slitscanobject = None
        self.slitscan = False
                
        self.sleeping = False        
        
        BTNSHUTTER.disable()
        BTNSHUTTER.registerEvent(self.onShutterTouched, ONTOUCHED)
        BTNSHUTTER.registerEvent(self.onPhoto, ONPRESSED)
        BTNSHUTTER.registerEvent(self.onSlitScan, ONPRESSED, 1)
        BTNSHUTTER.registerEvent(self.onStopSlitScan, ONRELEASED) 
      
        BTNFORCESTOP.disable()
        #BTNFORCESTOP.registerEvent(self.onForceHalt, ONPRESSED, 2)
        #BTNFORCESTOP.registerEvent(self.wakeup, ONTOUCHED)
            
        
    @property
    def slitscanmode(self) :        
        return self.modes[3].getMode()
        
    def wakeup(self) :        
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
        self.ontouch()
        self.imageReady.clear()
        self.picture = CAMERA.getPhoto(self.onImageReady)        
        self.slitscanobject = SlitScan(CAMERA.resolution,self.slitscanmode)
        CAMERA.startMode(self.slitscanobject)
    
    def onPhoto(self):
        log("Photo mode selected")             
        self.slitscan = False
        self.imageReady.wait()    
        self.onimage(self.picture)
    
        self.printPhoto(self.picture)
    
    def onStopSlitScan(self):
        log('Shutter released')
        CAMERA.stopMode()                
        self.sleep()
        if self.slitscan and self.slitscanmode in (SCAN_MODE, SCAN_MODE_FIX):            
            img = self.slitscanobject.getImage()
            self.onimage(img)
            self.picture = img            
            self.printPhoto(img)
        elif self.slitscan :
            for mode in self.modes:
                mode.setMode(self.mode)
                
        del(self.slitscanobject)
        self.slitscan = False
        self.slitscanobject = None

    def onSlitScan(self):
        log('Slitscan mode selected')
        self.slitscan = True
        if self.slitscanmode == SCAN_MODE_LIVE:
            PRINTER.streamImages(self.slitscanobject,self.onprintfinished)
        BUZZ.buzz(TOUCHED)
    
    def onImageReady(self, picture):  
        print ('Image ready')
        self.imageReady.set()                
        self.picture = picture
    
    def onprintfinished(self):                    
        BUZZ.buzz(OK)        
        self.wakeup()            
    
    def enable(self) :
        mode.enable(self)
        BTNSHUTTER.enable()        

    def disable(self) :
        mode.disable(self)
        BTNSHUTTER.disable()        
    
    def stop(self) :
        mode.stop(self)
        if self.slitscan :
            CAMERA.stopMode()
