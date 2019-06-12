import threading
from resources.camera import CAMERA
from resources.printer import PRINTER
from resources.buttons import BUTTONS,ATTINY,ONTOUCHED,ONPRESSED,ONRELEASED
from resources.vibrator import BUZZ,TOUCHED
from resources.log import LOG
from .slitscans.slitscans import ScanMode,ScanModeFix,ScanModeLive
from .imode import mode
log = LOG.log


SLITSCAN = 10

SCAN_MODE = 2
SCAN_MODE_FIX = 3
SCAN_MODE_LIVE = 4

class Slitscan(mode):

    ORDER = 0

    def __init__(self) :
        self.values = [SCAN_MODE,SCAN_MODE, SCAN_MODE_FIX, SCAN_MODE_LIVE,SCAN_MODE_FIX]
        self.value = -1
        self.fps = CAMERA.framerate
        self.slitscanio = None
        self.btnshutter = BUTTONS.register(ATTINY)
        self.btnshutter.registerEvent(self.onShutterTouched, ONTOUCHED)
        self.btnshutter.registerEvent(self.onSlitScan, ONPRESSED,1.5)
        self.btnshutter.registerEvent(self.onStopSlitScan, ONRELEASED)
        self.slitscanobj = None
        self.slitscan = False
        self.image = None    
        self.lock = threading.Event()            

    def enable(self) :
        mode.enable(self)
        self.btnshutter.enable()
    
    def disable(self) :
        mode.disable(self)
        self.btnshutter.disable()
        
    def setMode(self, value=None):
        mode = self.values[value]
        print ('set slitcan mode',mode)
        if mode == SCAN_MODE:
            self.slitScanIO = ScanMode
        elif mode == SCAN_MODE_FIX:
            self.slitScanIO = ScanModeFix
        elif mode == SCAN_MODE_LIVE:
            self.slitScanIO = ScanModeLive        
        self.value = value if value else self.value    

    def postProcess(self,img,level=0) :
        self.lock.wait()
        if self.slitscan and level == 0 :
            if self.slitscan :
                if self.slitScanIO == ScanModeLive :
                   img = None
                else :
                    img = self.slitscanobj.getImage()                            
                del(self.slitscanobj)
                self.slitscan = False
                self.slitscanobj = None    
        return img            

    def onShutterTouched(self):
        self.lock.clear()          
        self.slitscanobj = self.slitScanIO(CAMERA.resolution)
        CAMERA.startMode(self.slitscanobj,format='yuv')        
        
    def onSlitScan(self):
        log('Slitscan mode selected')
        self.slitscan = True
        if self.slitScanIO == ScanModeLive :
            PRINTER.streamImages(self.slitscanobj)
        BUZZ.buzz(TOUCHED)
    
    def onStopSlitScan(self):
        log('Shutter released')        
        CAMERA.stopMode()    
        self.lock.set()            
        
        
