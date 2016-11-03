from resources.camera import CAMERA
from resources.log import LOG
from resources.iocamera.slitscan import SCAN_MODE,SCAN_MODE_FIX,SCAN_MODE_LIVE
from . import mode
log = LOG.log

class slitscan(mode):
    def __init__(self) :
        self.values = [SCAN_MODE, SCAN_MODE_FIX, SCAN_MODE_LIVE,SCAN_MODE_FIX]
        self.value = -1
        self.fps = CAMERA.framerate

    def setMode(self, value=None):
        log("Select Mode %d" % value)
        value = value if value else self.value
        log('Slitscan set mode',value)
        if self.values[value] == SCAN_MODE_LIVE :
            self.fps = CAMERA.framerate
            CAMERA.framerate = 15
        elif self.fps != CAMERA.framerate :
            CAMERA.framerate = self.fps
        self.mode = value
    
    def getMode(self) :        
        return self.values[self.value]