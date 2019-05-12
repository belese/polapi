from . import lastframe
import cv2
from picamera.array import bytes_to_rgb
from PIL import Image

class face_detection(lastframe) :
    def __init__(self,resolution,onface):
        lastframe.__init__(self,resolution)
        self.onface = onface
        threading.thread(target=self.run).start()

    def run(self) :
        while not self.terminated.is_set() :   
            data= self.read()         
            frame = bytes_to_rgb(data,self.resolution)               
            gray = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 20)            
            if len(faces) > 0 :
                self.onface(Image.frombuffer('L', self.resolution, data, "raw", 'L', 0, 1),faces)