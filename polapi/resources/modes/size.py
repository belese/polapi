from PIL import Image
from resources.camera import CAMERA
from resources.log import LOG
from .imode import mode
log = LOG.log

# FORMAT OPTION
IDENTITY = (296, 384)
SQUARE = (384, 384)
STANDARD = (576, 384)
PANO = (1152, 384)

class Size(mode):
    
    LEVEL = 2
    
    def __init__(self):
        print ('----------------------------------Init Size mode')
        self.values = [IDENTITY, SQUARE, STANDARD, PANO, STANDARD]
        self.value = -1

    def setMode(self, value=None):
        log("------------------------------------Select Size Mode",value)
        value = value if value else self.value
        self.value = value 
        if value == 0:
            value += 1
        print ('-----------------------------------Set camera resolution to ',self.values[value])
        CAMERA.setSettings({'resolution': self.values[value]})

    def postProcess(self, img,level=0):
        log("Format post process",level)
        if level == 2 :
            log("Format post process")
            resolution = self.values[self.value]
            # resize, crop and rotate image before printing
            img_ratio = img.size[0] / float(img.size[1])
            ratio = resolution[0] / float(resolution[1])
            if ratio > img_ratio:
                img = img.resize(
                    (resolution[0], int(
                        resolution[0] * img.size[1] / img.size[0])), Image.ANTIALIAS)
                box = (int((img.size[0] - resolution[0]) / 2), 0,
                    int((img.size[0] + resolution[0]) / 2), img.size[1])
                img = img.crop(box)
            elif ratio < img_ratio:
                img = img.resize(
                    (int(
                        resolution[1] *
                        img.size[0] /
                        img.size[1]),
                        resolution[1]),
                    Image.ANTIALIAS)
                box = (int((img.size[0] - resolution[0]) / 2), 0,
                    int((img.size[0] + resolution[0]) / 2), img.size[1])
                img = img.crop(box)
            else:
                img = img.resize((resolution[0], resolution[1]), Image.ANTIALIAS)
            img = img.rotate(90, expand=1)
        return img
