import threading
import Queue
from PIL import Image

from . import allframes

SLITSCAN = 10

SLITSCAN_WIDTH = 640
SLITSCAN_HEIGHT = 384
SLITSCAN_SIZE = (SLITSCAN_WIDTH, SLITSCAN_HEIGHT)

NO_SCAN = 1
SCAN_MODE = 2
SCAN_MODE_FIX = 3
SCAN_MODE_LIVE = 4

SLIT_SCAN_FIX_WIDTH = 1

from picamera.array import bytes_to_rgb


class _SlitScan(allframes):    
    def getImage(self):
        self.finished.wait()
        if self.nb_image == 0:
            return None
        img = Image.new('RGB', self.resolution, 0)
        slitsize = self.resolution[0] / self.nb_image
        reste_img = self.resolution[0] % self.nb_image
        keyframe = []

        while reste_img > 0:
            val = (self.nb_image / reste_img)
            if self.nb_image % reste_img != 0:
                val += 1
            keyframe.append(val)
            reste_img = reste_img - (self.nb_image / val)

        x = 0
        for i in range(self.nb_image):
            frame = slitsize
            for k in keyframe:
                if (i + 1) % k == 0:
                    frame += 1
            if frame != 0:
                column = Image.frombuffer('L', self.resolution, self.read(), "raw", 'L', 0, 1)
                column = self.cropMethod(column, x, frame)
                img.paste(column, (x, 0))
                print ('got a image from array and paste it')
                del(column)
                x += frame
            else:
                # throw unecessery frame
                a = self.read()
                del(a)
        print ('ive returnend a slitscan image',img)
        return img    

class ScanMode(_SlitScan):
    def cropMethod(self, img, x, frame):
        return img.crop((x, 0, x + frame, img.size[1]))


class ScanModeFix(_SlitScan):
    def cropMethod(self, img, x, frame):
        return img.crop(((img.size[0] / 2) - frame / 2,
                         0,
                         (img.size[0] / 2) + (frame - (frame / 2)),
                         img.size[1]))


class ScanModeLive(ScanModeFix):
    def __init__(self, resolution=SLITSCAN_SIZE, slitSize=1):
        ScanModeFix.__init__(self, resolution)
        self.slitSize = slitSize

    def getImage(self):
        pass

    def get(self):        
        frame = self.read()
        if not frame:
            return
        #frame = bytes_to_rgb(frame,self.resolution)               
        frame = Image.frombuffer('L', self.resolution, frame, "raw", 'L', 0, 1)
        return self.cropMethod(frame, 0, self.slitSize).rotate(90, expand=1)