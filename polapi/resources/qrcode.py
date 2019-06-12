import time
import threading
from pyzbar import pyzbar
from PIL import Image
from .camera import CAMERA
from .vibrator import BUZZ,OK
from .resource import Resource
import time
import json

class QRCode(Resource) :
     
    def __init__(self) :
        print ('****************init QRCODE')
        self.events = {}
        self.enabled = threading.Event()
        self.enabled.set()
        Resource.__init__(self)
    
    def start(self):        
        print 'start QRcode'
        time.sleep(5)
        for img in CAMERA.sequence :
            if self.terminated:
                break
            self.enabled.wait()
            datas = pyzbar.decode(img)
            if datas :
                BUZZ.buzz(OK)
            for data in datas :
                #data = json.loads(data.data.decode("utf-8"))
                dat={}
                dat['event'] = 'r'
                dat['data'] = data.data.decode("utf-8")
                print ('****************',self.events,dat)
                if  dat['event'] in self.events :
                    for event in self.events[dat['event']] :                        
                        event['cb'](dat['data'],*event['args'],**event['kwargs'])
                        time.sleep(2)
            time.sleep(0.1)

    
    def enable(self) :        
        self.enabled.set()
    
    def disable(self) :
        self.enabled.clear()
    
    def registerEvent(self,cb,event,*args,**kwargs) :
        self.events[event] = self.events.get(event,[])
        self.events[event].append({'cb' : cb, 'args' : args, 'kwargs' : kwargs})


QRCODE = QRCode()