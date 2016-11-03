from .effect import Effect
from .luminosity import Luminosity
from .size import Size
from .slitscan import Slitscan
from .romanphoto import Romanphoto

MODES = [Effect,Luminosity,Size,Slitscan,Romanphoto]

class Enhancer(object) :

    def __init__(self) :
        self.modes = {}        
        self.maxlevel = 0
        orders =  []
        
        for mode in MODES :
            self.modes[mode.__name__] = mode()
            orders.append(self.modes[mode.__name__])
            self.maxlevel = max(self.maxlevel,mode.LEVEL)
        self.orders = sorted(orders,key=lambda x : x.ORDER)
        self.maxlevel  += 1
        self.default()
        
    def setMode(self,mode,value) :
        print ('Enhancer setMode',self.modes,mode,value)
        self.modes[mode].setMode(value)
            
    def postProcess(self, img):
        for level in range(0,self.maxlevel) :
            for mode in self.orders :
                if mode.enabled :
                    img = mode.postProcess(img,level=level)
                    if img == None :
                        return None    
        return img
    
    def enable(self) :
        for mode in self.orders :
            mode.enable()
    
    def disable(self) :
        for mode in self.orders :
            mode.disable()
    
    def default(self) :
        print ('enhancer set default')
        for mode in self.orders :
            print ('tom mode',mode)
            mode.setMode(-1)
