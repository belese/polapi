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

import picamera
from picamera.array import PiRGBArray
from resources.utils import log


class Camera :
    def __init__(self) :
        #pass
        self.camera = picamera.PiCamera()
        self.camera.vflip = True
                                                
    def setLuminosity(self,luminosity) :        
        for param in luminosity.keys() :
            #pass
            setattr(self.camera,param,luminosity[param])
    
    def setFormat(self,size) :      
        #pass
        self.camera.resolution = size
        
    def takePicture(self) :
        #pass
        self.camera.start_preview()
        rawCapture = PiRGBArray(self.camera)          
        self.camera.capture(rawCapture,format="bgr")
        self.camera.stop_preview()
        return rawCapture.array     

CAMERA = Camera()

