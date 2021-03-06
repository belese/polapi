from .imode import mode
from resources.vibrator import BUZZ,TOUCHED,OK
from resources.camera import CAMERA
from resources.buttons import BUTTONS,ATTINY,ONRELEASED
from resources.libs.romanphoto import Dialogues,RomanPhoto
from resources.libs.facedetection import face
from PIL import Image, ImageOps
class Romanphoto(mode):
    
    ORDER = 0
    LEVEL = 1

    def __init__(self):
        self.values = [True, False]
        self.value = -1
        self.canceled = False
        self.btnshutter = BUTTONS.register(ATTINY)
        self.btnshutter.registerEvent(self.oncancel, ONRELEASED)
        self.btnshutter.disable()

    def oncancel(self) :
        print ('roman photo canceled')
        BUZZ.buzz(OK)
        self.disable()
        self.btnshutter.disable()
        self.canceled = True

    def setMode(self, value=-1):
        print ('Set roman phot mode')
        if not isinstance(value,int) :
            try :
                self.dialogue = Dialogues(value)
                self.value = 1
            except :
                self.value = -1
                raise

    def postProcess(self, img,level=0) :                
        if self.value == 1 :
            if level == 0 :
                img = img.rotate(180, expand=1)
                img2 = ImageOps.autocontrast(img)
                img2 = ImageOps.equalize(img2)
                self.canceled = False
                self.btnshutter.enable()
                BUZZ.buzz(TOUCHED)
                self.faces = face(img2)
                #self.faces = face(img) #.rotate(180, expand=1))
                print "check faces", len(self.faces), self.dialogue.nbpersons              
                while len(self.faces) < self.dialogue.nbpersons :
                    if self.canceled :                  
                        return None
                    BUZZ.buzz(TOUCHED)
                    img = next(CAMERA.sequence).rotate(180, expand=1)
                    img2 = ImageOps.autocontrast(img)
                    img2 = ImageOps.equalize(img2)
                    self.faces = face(img2)                
                self.btnshutter.disable()
                BUZZ.buzz(OK)
            elif level == 1 :
                print "roman photo set"
                romanphoto = RomanPhoto(img,img.size,self.faces,self.dialogue)
                img = romanphoto.getBubbles()
                img = img.rotate(180, expand=1)
                self.value = -1
                self.disable()
        return img