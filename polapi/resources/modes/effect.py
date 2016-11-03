from resources.camera import CAMERA
from resources.log import LOG
from .imode import mode

log = LOG.log

class Effect(mode):

    ORDER = 20

    def __init__(self):
        self.values = ['gpen', 'cartoon', 'pastel', 'oilpaint', 'none']
        self.value = -1

    def setMode(self, value=None,level=0):        
        value = value if value else self.value
        log("Set effect to %d" % value)
        CAMERA.setSettings({'image_effect': self.values[value]})
