
# import the necessary packages
from picamera.array import PiRGBArray,bytes_to_rgb
from picamera import PiCamera
import time
import cv2
import numpy as np
import threading
import time
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 384)
camera.framerate = 15
camera.vflip = True
import Image
import math
rawCapture = PiRGBArray(camera, size=(640, 384))
from PIL import Image, ImageFont, ImageDraw, ImageEnhance 
import textwrap
# allow the camera to warmup
time.sleep(0.1)

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt2.xml')


class Rectangle:
# Create rectangle with center at (x, y)
# width x, and height h

    def __init__(self, x, y, w, h):
        self._x = float(x)
        self._y = float(y)
        self._width = float(w)
        self._height = float(h)
        # Extended four instance variables
        self._x0 = self._x - self._width / 2
        self._x1 = self._x + self._width / 2
        self._y0 = self._y - self._height / 2
        self._y1 = self._y + self._height/2
    
    # True if self intersects other; False otherwise
    def intersects(self, other):

        # find which rectangle is on the left
        leftRec = None
        rightRec = None
        if self._x1 >= other._x1:
            leftRec = other
            rightRec = self
        else:
            leftRec = self
            rightRec = other

        # find which rectangle is on the top
        topRec = None
        lowRec = None
        if self._y1 >= other._y1:
            topRec = self
            lowRec = other
        else:
            topRec = other
            lowRec = self

        if (leftRec._x0 + leftRec._width <= rightRec._x0) or (lowRec._y0 + lowRec._height <= topRec._y0):
            # Not overlap
            return False
        elif (leftRec._x0 + leftRec._width <= rightRec._x0 + rightRec._width) or (lowRec._y0 + lowRec._height <= topRec._y0 + topRec._height):
            # full overlap, contains
            return False
        else:
            # intersect
            return True



class face_detection(threading.Thread) :
    def __init__(self,cb) :
        threading.Thread.__init__(self)
        self.cb =cb
        self._frame = None
        self.stopped = False
        self.lock = threading.Lock()
    
    @property
    def frame (self):
        with self.lock :
            return self._frame
    
    @frame.setter
    def frame(self, rgbbytearray) :
        with self.lock :
            self._frame = bytes_to_rgb(rgbbytearray,camera.resolution)
    

    def run(self) :
        while self.frame == None and not self.stopped :            
            time.sleep(0.01)                
            print self.frame
        print('HEeeeeeeeeeeeeeeeeeeeeeeeeeeeeere')
        while not self.stopped :            
            frame = self.frame               
            gray = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 20)
            print faces
            if len(faces) > 0 :
                self.cb(frame,faces)


# Python program to find all  
# rectangles filled with 0 

def infaces(y,x,faces) :
    for (x0,y0,w,h) in faces :
        print 'check in face',x,y,x0,y0,w,h
        if ((x <= x0 + w) and (x >= x0)) and ((y <= y0+h) and (y >= y0)) :
            print ('in face')
            return True    
    return False


def findPositions(self,img,faces,bubble) :
    position = []
    x=0
    y=0
    while True :




  
# Python program to find all  
# rectangles filled with 0 
  
def findend(i,j,a,output,index,faces,bubblesize): 
    print ('here2')
    x = len(a) 
    y = len(a[0]) 
  
    # flag to check column edge case, 
    # initializing with 0 
    flagc = 0
  
    # flag to check row edge case, 
    # initializing with 0 
    flagr = 0
    print a
    for m in range(i,x):  
        # loop breaks where first 1 encounters 
        print 'here3',m,a[m][j] 
        if infaces(m*10,j*10,faces):  #a[m][j] != 5 and 
            flagr = 1 # set the flag 
            break
  
        # pass because already processed 
        if a[m][j] :
            continue              
  
        for n in range(j, y):  
            print ('here 4',n,a[m][n])
  
            # loop breaks where first 1 encounters 
            if  infaces(m*10,n*10,faces): 
                print ('HERE 8888888888888888888888888888888888888888',m,n,a[m][n])
                flagc = 1 # set the flag 
                break
  
            # fill rectangle elements with any 
            # number so that we can exclude 
            # next time 
            a[m][n] = True
        if flagc :
            break
    
    print flagr, flagc
  
    if flagr == 1: 
        output[index].append( (m-1)*10) 
    else: 
        # when end point touch the boundary 
        output[index].append(m*10)  
  
    if flagc == 1: 
        output[index].append((n-1)*10) 
    else: 
        # when end point touch the boundary 
        output[index].append(n*10)  
  
  
def get_rectangle_coordinates(imgsize,faces,bubblesize):
    print imgsize
    b = [False] * (imgsize[0] / 10)
    a = [b] * (imgsize[1] / 10)
  
    # retrieving the column size of array 
    size_of_array = len(a)  
  
    # output array where we are going 
    # to store our output  
    output = []  
  
    # It will be used for storing start 
    # and end location in the same index 
    index = -1
  
    for i in range(0,size_of_array): 
        for j in range(0, len(a[0])): 
            if not a[i][j] and not infaces(i*10,j*10,faces) :  #(not a[i][j] == 5) and
                print ('here')
                # storing initial position  
                # of rectangle 
                output.append([i*10, j*10])  
                # will be used for the  
                # last position 
                index = index + 1        
                findend(i, j, a, output, index,faces,bubblesize)  
  
  
    return output


class SlitScan(object):
    def __init__(self):
        self.i = 0
        self.detection = face_detection(self.onDetection)
        self.detection.start()        

    def write(self, s):        
        self.detection.frame = s
    
    def onDetection(self,img,faces) :
        print 'found faces'
        img = Image.fromarray(img)
        img = self.drawBubble("Hello, this is a very long text to test the text wrapping. Hope it will work",img,faces)
        img.save("img%d.png"%self.i,"PNG")
        self.i += 1
    
    def getSquareBubble(self,text,lr=5,hr=3,font="resources/fonts/dreamorphans.ttf",size=20) :
        font = ImageFont.truetype(font,size)        
        # get text size
        text_size = font.getsize(text)
        area = text_size[0]*text_size[1]
        length = int(math.sqrt((lr*area/hr)))
        height = area / length
        average_char_width = text_size[0]/len(text)        
        text = textwrap.fill(text, length/average_char_width)
        line_height = 0
        bull_width = 0
        lines = text.split('\n')
        for line in lines  :
            size = font.getsize(line)
            bull_width = max(bull_width,size[0])
            line_height = max(line_height,size[1])            
        bull_width+=20
        bull_height= (line_height*len(lines)) + 20
        bull_img = Image.new('RGBA', (bull_width,bull_height), "white")
        bull_draw = ImageDraw.Draw(bull_img)
        y=10
        x=10
        for line in lines  :
            bull_draw.text((x, y), line, font=font,fill="black")
            y+=line_height        
        return bull_img

        
    def findBubblePosition(self,imgsize,bubblesize,faces,faceidx) :
        print ('rectangle')
        rects =  get_rectangle_coordinates(imgsize,faces,bubblesize)
        return rects

    
    
    def drawBubble(self,text,img,faces) :                
        """
        # set button size + 10px margins
        button_size = (text_size[0]+20, text_size[1]+20)
        # create image with correct size and black background
        button_img = Image.new('RGBA', button_size, "white")
        # put text on button with 10px margins
        button_draw = ImageDraw.Draw(button_img)
        button_draw.text((10, 10), text, font=font,fill="black")
        # put button on source image in position (0, 0)
        
        """
        bubble = self.getSquareBubble(text)        
        rects = self.findBubblePosition(img.size,bubble.size,faces,0)
        print rects
        pos = rects[0]        
        img.paste(bubble, (pos[1], pos[0]))
        img_draw = ImageDraw.Draw(img)
        for (x,y,w,h) in faces :
            img_draw.rectangle((x,y,x+w,y+h),(255,0,0),2)
        for (y0,x0,y1,x1) in rects :
            img_draw.rectangle((x0,y0,x1-x0,y1-y0))
        return img
        
try :
    print ('yop')
    a = SlitScan()    
    camera.start_recording(a, format='rgb')
    camera.wait_recording(120)
    camera.stop_recording()
except :
    raise
finally :
    camera.close()
    a.detection.stopped = True

"""

try :
    # capture frames from the camera
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # grab the raw NumPy array representing the image, then initialize the timestamp
        # and occupied/unoccupied text
        image = frame.array
        print 1
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        print 2
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)
        print 3
        for (x,y,w,h) in faces:
            print ('found face')
            cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)
        # show the frame
        cv2.imshow("Frame", image)
        print ('yop')
        key = cv2.waitKey(1) & 0xFF
    
        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)
except :
    raise    
finally :
    camera.close()
"""