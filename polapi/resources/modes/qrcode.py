from pyzbar import pyzbar

from . import lastframe

class QrCode(lastframe):
    def __init__(self,resolution,onqrcodecb) :
        lastframe.__init__(self,resolution)
        self.cb = onqrcodecb        
        threading.thread(target = self.detect).start()
    
    def detect(self) :
        while not self.terminated.is_set() :
            frame = self.read()
            frame = Image.frombuffer('L', self.resolution, frame, "raw", 'L', 0, 1)
            barcodes = pyzbar.decode(frame)            
            # loop over the detected barcodes            
            for barcode in barcodes:                
                barcodeData = barcode.data.decode("utf-8")                                
                if barcodeData :                    
                    self.cb(barcodeData)
                    