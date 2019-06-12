import Queue
from lz4 import compress, decompress, compress_fast
import psutil
import threading
from resources.camera import CAMERA


LOW_MEMORY = 50 * 1024 * 1024

class allframes(object) :
    def __init__(self,resolution):        
        self.queue = Queue.Queue()
        self.nb_image = 0
        self.finished = threading.Event()
        self.resolution = resolution
        self.stopped = False
    
    def _run(self) :
        while not self.stopped :
            CAMERA.getPhoto(self.write)        

    def write(self,frame) :
        print ('write image')
        if (self.nb_image+1) % 100 != 0 or psutil.virtual_memory()[1] > LOW_MEMORY:            
            self.queue.put(frame,)            
            self.nb_image += 1            
    
    def read(self):
        if self.queue.empty() :
            return None
        rc = self.queue.get()
        self.queue.task_done()
        return rc
        #return rc

    def flush(self) :
        self.finished.set()
    
    def stop(self) :
        self.stopped = True

