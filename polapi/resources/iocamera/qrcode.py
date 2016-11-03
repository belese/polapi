import threading
from PIL import Image
from pyzbar import pyzbar
from picamera.array import bytes_to_rgb

from . import lastframe

class QrCode(lastframe):
    def __init__(self,resolution,onqrcodecb) :
        lastframe.__init__(self,resolution)
        self.cb = onqrcodecb        
        threading.Thread(target = self.detect).start()
    
    def detect(self) :
        i = 0
        while not self.finished.is_set() :
            i+=1
            frame = self.read()
            print ('check Qrcode')
            frame = bytes_to_rgb(frame,self.resolution)               
            frame = Image.fromarray(frame)

            #frame = Image.frombuffer('L', self.resolution, frame, "raw", 'L', 0, 1)
            frame.save('qrcode%d.jpeg'%i, "JPEG")
            barcodes = pyzbar.decode(frame)            
            # loop over the detected barcodes            
            for barcode in barcodes:                
                barcodeData = barcode.data.decode("utf-8")                                
                if barcodeData :                    
                    self.cb(barcodeData)
                    