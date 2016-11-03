import threading
import time

from resources.camera import CAMERA
from resources.printer import PRINTER
from resources.buttons import ATTINY, BUTTONS, ONTOUCHED, ONPRESSED, ONRELEASED
from resources.vibrator import BUZZ,OK,READY,CANCEL,TOUCHED,ERROR,REPEAT
from resources.wiring import DECLENCHEUR,AUTO,LUM,VALUE0,VALUE1,VALUE2,VALUE3
from resources.log import LOG,log as l
from resources.iocamera.facedetection import face_detection
from resources.libs.romanphoto import Dialogues,RomanPhoto as rp
from . import mode
#from resources.enhancer.ying import Ying_2017_CAIP

log = LOG.log

BTNSHUTTER = BUTTONS.register(ATTINY)
BTNFORCESTOP = BUTTONS.register(ATTINY)

class RomanPhoto(mode) :
    def __init__(self,modes,ontouch,onCancel):
        log('Roman Photo Initialisation')        
        mode.__init__(self,modes,ontouch,onCancel)
                                
        self.imageReady = threading.Event()        
        self.picture = None
        self.dialogue = None
                        
        self.sleeping = False        
        
        BTNSHUTTER.disable()
        BTNSHUTTER.registerEvent(self.onShutterTouched, ONTOUCHED)
       
        BTNFORCESTOP.disable()
        #BTNFORCESTOP.registerEvent(self.onForceHalt, ONPRESSED, 2)
        #BTNFORCESTOP.registerEvent(self.wakeup, ONTOUCHED)            
                
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
        CAMERA.startMode(face_detection(CAMERA.resolution,self.onFaceDetected),format='rgb')                        
        
    
    def onFaceDetected(self,img,faces) :
        print ('find faces',img,faces)
        if len(faces) >= self.dialogue.nbpersons and self.enabled :
            self.disable()
            BUZZ.buzz(OK)            
            try :
                for mode in (self.modes[0],self.modes[2]):        
                    img = mode.postProcess(img)
                    pass
            except Exception as e :
                log('Exception',str(e),level=30)
                BUZZ.buzz(ERROR)
                raise
            bull = rp(img,img.size,faces,self.dialogue)
            imgbull = bull.getBubbles()            
            imgbull = self.modes[1].postProcess(imgbull)
            self.onimage(imgbull)    
            self.printPhoto(imgbull)
            

    def printPhoto(self, img):
        log("Print photo") 
        PRINTER.printToPage(img,self.onprintfinished)
        
    def onprintfinished(self):                    
        BUZZ.buzz(OK)       
        print('Printer finished, set qrcode mode') 
        self.oncancel('qrcode')            
    
    def enable(self,dialogue) :
        print ('set dialogue',dialogue)
        self.dialogue = Dialogues(dialogue)
        mode.enable(self)
        CAMERA.camera.vflip = True
        BTNSHUTTER.enable()        

    def disable(self) :
        mode.disable(self)
        CAMERA.camera.vflip = False        
        BTNSHUTTER.disable()
        CAMERA.stopMode()        
    
    def stop(self) :
        mode.stop(self)        
        if self.enabled :
            CAMERA.stopMode()
