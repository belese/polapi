#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  polapi_v2.py
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
from threading import Timer

from resources.printer import PRINTER
from resources.buttons import BUTTONS,DECLENCHEUR,AUTO,LUM,FORMAT,VALUE0,VALUE1,VALUE2,VALUE3
from resources.camera import CAMERA
from resources.utils import log,blackandwhite,clahe,histogramme,toFile
import resources.vibrator as BUZZ

#TMP PHOTO FILE
FILE = "/tmp/photo.png"

#default mode timeout
TIMEOUT = 3
#Luminosity Option
LOW = 10
MEDIUM_LOW = 11
MEDIUM_HIGH = 12
HIGH = 13

#FORMAT OPTION (camera setting,printer settings)
IDENTITY = ((419,544),"X48MMY37MM")
SQUARE = ((544,544),"X48MMY48MM")
STANDARD = ((724,544),"X48MMY64MM")
PANO = ((1448,544),"X48MMY128MM")

#CAMERA SETTINGS
SETTINGS = {
			AUTO : {"sharpness" : 0,
					"contrast" : 0,
					"brightness" : 50,
                    "saturation" : 0,
                    "drc_strength" : "off",
					"ISO" : 0,				
					"exposure_compensation" : 0,
					"exposure_mode" : 'auto',
					"meter_mode" : 'average',
					"awb_mode" : 'auto',
					},
			LOW : {"sharpness" : 0,
					"contrast" : 0,
					"brightness" : 70,
                    "saturation" : 0,
                    "drc_strength" : "high",
					"ISO" : 800,				
					"exposure_compensation" : 0,
					"exposure_mode" : 'night',
					"meter_mode" : 'average',
					"awb_mode" : 'incandescent',
					},
			MEDIUM_LOW : {"sharpness" : 0,
					"contrast" : 0,
					"brightness" : 60,
                    "saturation" : 0,
					"ISO" : 600,				
					"exposure_compensation" : 0,
					"exposure_mode" : 'auto',
					"meter_mode" : 'average',
					"drc_strength" : "medium",
					"awb_mode" : 'shade',
					},
			MEDIUM_HIGH : {"sharpness" : 0,
					"contrast" : 0,
					"brightness" : 50,
                    "saturation" : 0,
					"ISO" : 300,				
					"exposure_compensation" : 0,
					"exposure_mode" : 'auto',
					"meter_mode" : 'average',
					"drc_strength" : "low",
					"awb_mode" : 'cloudy',
					},
			HIGH : {"sharpness" : 0,
					"contrast" : 0,
					"brightness" : 50,
                    "saturation" : 0,
					"ISO" : 100,				
					"exposure_compensation" : 0,
					"exposure_mode" : 'auto',
					"meter_mode" : 'average',
					"drc_strength" : "off",
					"awb_mode" : 'sunlight',
					}
			}

class polapi :
	
	LUMINOSITY =0
	FORMAT = 1
	
	def __init__(self) :		
		self.timer = None				
		
		#register all buttons
		self.declencheur = BUTTONS.register(DECLENCHEUR,self.takePhoto)
		self.auto = BUTTONS.register(AUTO,self.onAuto)
		self.lum = BUTTONS.register(LUM,self.onLuminosity)
		self.bsize = BUTTONS.register(FORMAT,self.onFormat)
		self.value0 = BUTTONS.register(VALUE0,self.onValue0)		
		self.value1 = BUTTONS.register(VALUE1,self.onValue1)		
		self.value2 = BUTTONS.register(VALUE2,self.onValue2)
		self.value3 = BUTTONS.register(VALUE3,self.onValue3)				
		self.mode = None
		self.onValue(AUTO,STANDARD)
		BUZZ.vibrator(BUZZ.READY)
	
	
	def takePhoto(self) :
		log ("Take a photo")
		BUZZ.vibrator(BUZZ.TOUCHED)
		img = CAMERA.takePicture()
		img = self.postProcess(img)				
		PRINTER.print_img(toFile(img,FILE),self.size[1])
	
	def postProcess(self,img) :
		img = blackandwhite(img)		
		if self.luminosity > MEDIUM_HIGH :
			return clahe(img)
		else :
			return histogramme(img)
			
	def onAuto(self) :		
		log ("Reset settings to auto")
		BUZZ.vibrator(BUZZ.TOUCHED)
		self.mode = None
		self.onValue(AUTO,STANDARD)
		
	def idle(self) :		
		self.value0.disable()
		self.value1.disable()
		self.value2.disable()
		self.value3.disable()
		self.mode = None
		
	def wait(self) :
		self.value0.enable()
		self.value1.enable()
		self.value2.enable()
		self.value3.enable()
		self.enableTo(TIMEOUT)

	def onFormat(self) :
		BUZZ.vibrator(BUZZ.TOUCHED)				
		self.mode = self.FORMAT
		self.wait()
	
	def onLuminosity(self) :
		BUZZ.vibrator(BUZZ.TOUCHED)
		self.mode = self.LUMINOSITY
		self.wait()
		
	def onValue0(self) :
		BUZZ.vibrator(BUZZ.OK)
		self.onValue(LOW,IDENTITY)
						
	def onValue1(self) :
		BUZZ.vibrator(BUZZ.OK)		
		self.onValue(MEDIUM_LOW,SQUARE)
		
	def onValue2(self) :
		BUZZ.vibrator(BUZZ.OK)		
		self.onValue(MEDIUM_HIGH,STANDARD)
			
	def onValue3(self) :
		BUZZ.vibrator(BUZZ.OK)		
		self.onValue(HIGH,PANO)
	
	def onValue(self,lum,size) :						
		if self.timer : self.timer.cancel()
		if self.mode in (self.LUMINOSITY,None) :
			log ("Set luminosity to %d"%lum)
			self.luminosity  = lum
			CAMERA.setLuminosity(SETTINGS[lum])
		if self.mode in (self.FORMAT,None) :
			self.size = size
			log ("Set format to ",size[0])
			CAMERA.setFormat(size[0])		
		self.idle()
	
	def enableTo(self,delay) :	
		if self.timer :
			self.timer.cancel()	
		self.timer = Timer(delay, self.onTimeout, ())
		self.timer.start()
	
	def onTimeout(self) :
		self.timer = None
		BUZZ.vibrator(BUZZ.CANCEL)
		self.idle()

a = polapi()

import time
time.sleep(100)
