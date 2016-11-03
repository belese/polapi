#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  camera.py
#
#  Copyright 2017 belese <belese@belese>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
import time
import io
import threading
import Queue
import picamera

import cv2

import imutils
import numpy


from PIL import Image

from resources.resource import Resource, queue_call


class Camera(Resource):

    def __init__(self,resolution=(640,384)):
        Resource.__init__(self)
        self.camera = None
        self.recordlock = threading.Lock()
        self.frameready = threading.Event()
        self.initCamera()
        self.img = None
        self.keepres = None
        self.resolution =  resolution
        self.stopped = False
        self.mode = None
        self._mode = self.mode
        self._args = []
        self._kwargs = {}
        self.framerate = 15
        
    @queue_call
    def setSettings(self, settings):        
        for param in settings.keys(): 
            try :          
                setattr(self.camera, param, settings[param])
            except Exception as e:
                print ('Cannot set attr ',param,settings[param],str(e))
                pass
        self.resolution = self.camera.resolution 

    @queue_call
    def initCamera(self):
        print ('Start camera')
        #with self.camlock :
        self.camera = picamera.PiCamera()
        self.camera.framerate = self.framerate
        self.camera.resolution = self.resolution 
        self.camera.vflip = False

    @queue_call
    def getPhoto(self,onPhoto,*args,**kwargs):
        print ('getPhoto')
        photo = self._getPhoto(*args,**kwargs)
        onPhoto(photo)
        return photo
    
    def _getPhoto(self,format='jpeg',*args,**kwargs) :   
        print ('_getPhoto')     
        stream = io.BytesIO()        
        self.camera.capture(stream, format=format)
        stream.seek(0)
        print ('_getPhoto return')     
        return Image.open(stream)
    
    def startMode(self,iostream,format='rgb') :
        print ('startmode self.resolution',self.resolution)
        #self.camera.resolution = self.resolution 
        self.startRecording(iostream,format)        


    def stopMode(self):
        print ('STOP MODE')
        #if self.mode :
        self.stopRecording()            

    
    @queue_call
    def startRecording(self, iostream,format='rgb'):        
        self.recordlock.acquire()        
        self.camera.start_recording(iostream, format=format, resize=self.resolution)        

    @queue_call
    def stopRecording(self):         
        print ('in stop recording')
        try :
            if self.camera.recording:
                self.camera.stop_recording()            
        except :
            raise
        finally :
            self.recordlock.release()
            print ('stop recording, release lock')                        
                    
    @property
    def sequence(self) :        
       # with self.recordlock :
        print ('yield photo')
        while not self.stopped :
            self.frameready.clear()
            self.getPhoto(self.onFrame)
            print ('wait photo ready')
            self.frameready.wait()
            print ('yield frame')
            yield self.frame        
        
    def onFrame(self,img) :
        self.frame = img
        self.frameready.set()
            
    @queue_call
    def stop(self):
        self.stopped = True
        if self.camera.recording:
            self.stopMode()
        #with self.camlock:
        self.camera.close()
        Resource.stop(self)

    @queue_call
    def sleep(self):        
        #with self.camlock:
        print ('Pause camera')
        self.camera.close()
        
    def wake(self):        
        self.initCamera()        

CAMERA = Camera()

def main(args):
    try:
        import time
        #CAMERA.camera.rotation = 180
        #CAMERA.camera.resolution = PRINTER_SIZE
        CAMERA.camera.framerate = 90
        #CAMERA.camera.contrast = 50
        CAMERA.getPhoto().save('test1.jpg')
        a = CAMERA.startSlitScan(SCAN_MODE_FIX)
        time.sleep(20)
        CAMERA.stopSlitScan()
        a.getImage().save("test.jpg")
    finally:
        CAMERA.stop()


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
