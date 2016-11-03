import cv2
import numpy
from PIL import Image
  
FACTOR = 0.6
face_cascade = cv2.CascadeClassifier('resources/cascade/haarcascade_frontalface_alt2.xml')
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))

def face(img) :
    face = []
    res = (int(img.size[0]*FACTOR),int(img.size[1]*FACTOR))
    image = cv2.cvtColor(numpy.array(img.convert('RGB')),cv2.COLOR_RGB2GRAY)
    image = clahe.apply(image)                            
    image = cv2.resize(image,res)  
    #cv2.imwrite('facedetect.jpeg',image)  
    faces = face_cascade.detectMultiScale(image,scaleFactor=1.1, minNeighbors=5)            
    if len(faces) > 0 :
        face = map(lambda x : [(int(x[0]/FACTOR) + 9)/ 10 * 10,(int(x[1]/FACTOR)+9) / 10 *10,(int(x[2]/FACTOR) +9 )/10 *10,(int(x[3]/FACTOR)+9)/10*10],faces)
    print ('Faces detected : ',face)
    return face