from resources.iocamera.qrcode import QrCode as qr
from resources.camera import CAMERA
from . import mode
from resources.log import LOG

log = LOG.log

class QrCode(mode) :
    def __init__(self,modes,ontouch,onCancel):
        log('Photo Initialisation')       
        mode.__init__(self,modes,ontouch,onCancel)
        self.camio = qr((640,480),self.onqrcode)
        self._res = None
        self._lastdata = None
    
    def enable(self) :
        mode.enable(self)
        self._res = CAMERA.resolution
        CAMERA.resolution = (640,480)
        CAMERA.startMode(self.camio)       

    def disable(self) :        
        mode.disable(self)
        CAMERA.stopMode()
        if self._res :
            CAMERA.resolution = self._res            
    
    def stop(self) :
        mode.stop(self)
        if self.enabled :
            CAMERA.stopMode()
    
    def onqrcode(self,data) :
        print ('QrCode detected',data)
        if data == self._lastdata :
            return
        self._lastdata = data
        self.oncancel('roman',data)