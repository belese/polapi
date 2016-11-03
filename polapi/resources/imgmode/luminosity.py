from PIL import Image, ImageEnhance
from resources.camera import CAMERA
from resources.log import LOG
from . import mode
import operator
log = LOG.log

# Luminosity Option
LOW = 10
MEDIUM_LOW = 11
MEDIUM_HIGH = 12
HIGH = 13

# CAMERA SETTINGS
LUMDEFAULT = {"sharpness": 0,
              "contrast": 0,
              "brightness": 50,
              "saturation": 0,
              "drc_strength": "off",
              "ISO": 0,
              "exposure_compensation": 0,
              "exposure_mode": 'auto',
              "meter_mode": 'average',
              "awb_mode": 'auto',
              }
LUMLOW = {"sharpness": 0,
          "contrast": 50,
          "brightness": 70,
          "saturation": 0,
          "drc_strength": "high",
          "ISO": 800,
          "exposure_compensation": 0,
          "exposure_mode": 'night',
          "meter_mode": 'average',
          "awb_mode": 'incandescent',
          }

LUMMEDIUM = {"sharpness": 0,
             "contrast": 20,
             "brightness": 60,
             "saturation": 0,
             "ISO": 600,
             "exposure_compensation": 0,
             "exposure_mode": 'auto',
             "meter_mode": 'average',
             "drc_strength": "medium",
             "awb_mode": 'shade',
             }

LUMMEDIUMHIGH = {"sharpness": 0,
                 "contrast": 0,
                 "brightness": 50,
                 "saturation": 0,
                 "ISO": 300,
                 "exposure_compensation": 0,
                 "exposure_mode": 'auto',
                 "meter_mode": 'average',
                 "drc_strength": "low",
                 "awb_mode": 'cloudy',
                 }
LUMHIGH = {"sharpness": 0,
           "contrast": 0,
           "brightness": 50,
           "saturation": 0,
           "ISO": 100,
           "exposure_compensation": 0,
           "exposure_mode": 'auto',
           "meter_mode": 'average',
           "drc_strength": "off",
           "awb_mode": 'sunlight',
           }

class luminosity(mode):
    def __init__(self):
        self.values = [LUMLOW, LUMMEDIUM, LUMMEDIUMHIGH, LUMHIGH, LUMDEFAULT]
        self.value = -1
        self.postvalue = ([1.5, 1.2], [1.2, 1.3], [
                          1, 1.5], [0.8, 1.6], [1, 1])

    def setMode(self, value=None):
        value = value if value else self.value
        log("Select Luminosity %d" % value)
        self.value = value
        CAMERA.setSettings(self.values[value])        

    def postProcess(self, img):
        log("Luminosity post process")
        # img.save('original.jpg')
        #img = Ying_2017_CAIP(img) 
        try :
            img = self.equalize(img)
        except :
            pass
        img = ImageEnhance.Color(img)        
        img = img.enhance(0)
        # img.save('bw.jpg')
        img = ImageEnhance.Brightness(img)
        img = img.enhance(self.postvalue[self.value][0])
        # img.save('brightness.jpg')
        img = ImageEnhance.Contrast(img)
        img = img.enhance(self.postvalue[self.value][1])
        return img

    def equalize(self,im):
        h = im.convert("L").histogram()
        lut = []
        for b in range(0, len(h), 256):
            # step size
            step = reduce(operator.add, h[b:b+256]) / 255
            # create equalization lookup table
            n = 0
            for i in range(256):
                lut.append(n / step)
                n = n + h[i+b]
        # map image through lookup table
        return im.point(lut*im.layers)