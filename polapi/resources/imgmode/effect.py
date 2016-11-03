from resources.camera import CAMERA
from resources.log import LOG
from . import mode

log = LOG.log

class effect(mode):
    def __init__(self):
        self.values = ['gpen', 'cartoon', 'pastel', 'oilpaint', 'none']
        self.value = -1

    def setMode(self, value=None):
        value = value if value else self.value
        log("Set effect to %d" % value)
        CAMERA.setSettings({'image_effect': self.values[value]})
