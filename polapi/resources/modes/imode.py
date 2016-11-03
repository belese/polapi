class mode:
    
    values = []
    value = None

    ORDER = 99
    LEVEL = 0

    enabled = True

    def getMode(self) :        
        return self.values[self.value]
    
    def setMode(self, value):
        pass

    def postProcess(self, img,level = 0):
        return img
    
    def enable(self) :
        self.enabled = True
    
    def disable(self) :
        self.enabled = False