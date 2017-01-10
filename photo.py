import numpy as np
import cv2


EQUALIZEHIST = 1
CLAHE = 2

class polapi :
   def gamma_correction(self,image,gamma) :
       # build a lookup table mapping the pixel values [0, 255] to
	     # their adjusted gamma values
	     invGamma = 1.0 / gamma
	     table = np.array([((i / 255.0) ** invGamma) * 255
		   for i in np.arange(0, 256)]).astype("uint8")
	         # apply gamma correction using the lookup table
	         return cv2.LUT(image, table)
   
  def equalize(self,image,mode) :
		
	
	
   
      
