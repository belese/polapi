from . import lastframe
import cv2
from picamera.array import bytes_to_rgb
from PIL import Image
import threading

face_cascade = cv2.CascadeClassifier('resources/cascade/haarcascade_frontalface_alt2.xml')

FACTOR = 0.5

class face_detection(lastframe) :
    def __init__(self,resolution,onface):
        lastframe.__init__(self,resolution)
        self.onface = onface
        threading.Thread(target=self.run).start()
        self.res = (int(self.resolution[0]*FACTOR),int(self.resolution[1]*FACTOR))
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))

    def run(self) :
        i=0
        while not self.finished.is_set() : 
            print ('Wait a photo')
            data= self.read()     
            print ('Get a photo')    
            i+=1
            frame = bytes_to_rgb(data,self.resolution)
             # create a CLAHE object (Arguments are optional).
            print ('clahe')
            gray = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)
            gray = self.clahe.apply(gray)                        
            print ('color')
            gray = cv2.resize(gray,self.res)
            print ('detect')
            faces = face_cascade.detectMultiScale(gray,scaleFactor=1.1, minNeighbors=5)            
            print ('lookup for faces done',faces)
            if len(faces) > 0 :
                faces =map(lambda x : [int(x[0]/FACTOR),int(x[1]/FACTOR),int(x[2]/FACTOR),int(x[3]*2/FACTOR)],faces)
                img = Image.fromarray(frame)
                self.onface(img,faces)