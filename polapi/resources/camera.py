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
        self.camlock = threading.Lock()
        self.initCamera()
        self.img = None
        self.keepres = None
        self.resolution =  resolution
        self.stopped = False
        self.mode = None
        self._mode = self.mode
        self._args = []
        self._kwargs = {}
        self.framerate = 90

    @queue_call
    def setSettings(self, settings):
        for param in settings.keys():            
            setattr(self.camera, param, settings[param])
        self.resolution = self.camera.resolution 

    @queue_call
    def initCamera(self):
        print ('Start camera')
        #with self.camlock :
        self.camera = picamera.PiCamera()
        self.camera.framerate = self.framerate
        self.camera.resolution = self.resolution 
            #self.camera.vflip = True

    @queue_call
    def getPhoto(self,onPhoto):
        print ('getPhoto')
        photo = self._getPhoto()
        onPhoto(photo)
        return photo
    
    def _getPhoto(self) :        
        stream = io.BytesIO()        
        self.camera.capture(stream, format='jpeg')
        stream.seek(0)
        return Image.open(stream)
    
    def startMode(self,iostream) :                                
        self.startRecording(iostream)        

    def registerEvent(self,cb,event) :
        self.events[event].append(cb)

    
    @queue_call
    def startRecording(self, iostream):
        print ('start recoreding, acquire lock')
        #self.camlock.acquire()        
        print ('start recoreding, lock acquire')
        self.camera.framerate = self.framerate
        self.camera.start_recording(iostream, format='yuv', resize=self.resolution)
        print ('Leave startrecording')

    @queue_call
    def stopRecording(self):         
        print ('in stop recording')
        try :
            self.camera.stop_recording()            
        except :
            raise
        finally :
            print ('stop recording, release lock')            
            #self.camlock.release()
            

    def stopMode(self):
        print ('STOP MODE')
        #if self.mode :
        self.stopRecording()            

    @queue_call
    def stop(self):
        self.stopped = True
        if self.camera.recording:
            self.stopSlitScan()
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
