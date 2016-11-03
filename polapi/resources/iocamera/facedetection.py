from . import lastframe
import cv2
from picamera.array import bytes_to_rgb
from PIL import Image
import threading
import numpy as np
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
        while not self.finished.is_set() : 
            print ('Wait a photo',self.resolution)
            data= self.read()
            if not data :
                continue
     
            print ('Get a photo')                
            frame = bytes_to_rgb(data,self.resolution)
            #frame = np.transpose(frame, (2,1,0))
             # create a CLAHE object (Arguments are optional).
            print ('clahe')            
            gray = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)
            clahe = self.clahe.apply(gray)                        
            print ('color')
            clahe = cv2.resize(clahe,self.res)
            print ('detect')
            faces = face_cascade.detectMultiScale(clahe,scaleFactor=1.1, minNeighbors=5)            
            print ('lookup for faces done',faces)
            if len(faces) > 0 :
                #frame = Image.frombuffer('RGB', self.resolution, data, "raw", 'L', 0, 1)
                faces =map(lambda x : [(int(x[0]/FACTOR) + 9)/ 10 * 10,(int(x[1]/FACTOR)+9) / 10 *10,(int(x[2]/FACTOR) +9 )/10 *10,(int(x[3]/FACTOR)+9)/10*10],faces)
                img = Image.fromarray(frame)
                #img = img.rotate(Image.ROTATE_270, expand=True)
                self.onface(img,faces)