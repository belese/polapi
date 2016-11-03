from resources.buttons import MPR121, BUTTONS, ONTOUCHED, ONPRESSED
from resources.vibrator import BUZZ,OK,READY,CANCEL,TOUCHED,ERROR,REPEAT
from resources.wiring import VALUE3
from resources.printer import PRINTER

from resources.log import LOG
log = LOG.log

BTNREPRINT = BUTTONS.register(MPR121, VALUE3)



class mode(object) :
    def __init__(self,modes,ontouch=None,oncancel=None) :
        self.modes = modes
        self.enabled = False
        self.ontouch = ontouch
        self.oncancel = oncancel        
        self.stopped = False
        self.image = None
        BTNREPRINT.registerEvent(self.reprint, ONPRESSED, 3)
        BTNREPRINT.registerEvent(self.ontouch, ONTOUCHED) 
    
    
    def lock(self) :
        BTNREPRINT.disable()
    
    def unlock(self) :
        BTNREPRINT.enable()
        
    def enable(self) :
        self.enabled = True
    
    def onimage(self,image) :
        self.image = image
    
    def disable(self) :
        self.enabled = False
    
    def stop(self) :
        self.stopped = True
        
              
