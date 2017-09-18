#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  utils.py
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
import cv2

#Log Level - error will be print on Printer
LOG_INFO = 0
LOG_ERROR = 1

def log(msg,level=LOG_INFO) :
	print msg
	
def clahe(img) :
	return cv2.createCLAHE().apply(img)        
	
def histogramme(img) :
	return cv2.equalizeHist(img)

def blackandwhite(img) :
	return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	
def toFile(img,filename) :
	cv2.imwrite(filename,img)
	return filename
