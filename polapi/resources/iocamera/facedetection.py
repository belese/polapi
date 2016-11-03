from . import lastframe
import cv2
from picamera.array import bytes_to_rgb
from PIL import Image
import threading

face_cascade = cv2.CascadeClassifier('resources/cascade/haarcascade_frontalface_alt2.xml')


class face_detection(lastframe) :
    def __init__(self,resolution,onface):
        lastframe.__init__(self,resolution)
        self.onface = onface
        threading.Thread(target=self.run).start()

    def run(self) :
        i=0
        while not self.finished.is_set() :   
            data= self.read()         
            i+=1
            frame = bytes_to_rgb(data,self.resolution)               
            gray = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)
            cv2.imwrite("img%d.jpeg"%i, gray)
            faces = face_cascade.detectMultiScale(gray, 1.1, 20)            
            print ('lookup for faces',faces)
            if len(faces) > 0 :
                img = Image.fromarray(frame)
                self.onface(img,faces)