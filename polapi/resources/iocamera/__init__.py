import Queue
from lz4 import compress, decompress, compress_fast
import psutil
import threading

LOW_MEMORY = 50 * 1024 * 1024

class allframes(object) :
    def __init__(self,resolution):        
        self.queue = Queue.Queue()
        self.nb_image = 0
        self.finished = threading.Event()
        self.resolution = resolution
    
    def write(self,frame) :
        if (self.nb_image+1) % 100 != 0 or psutil.virtual_memory()[1] > LOW_MEMORY:
            self.queue.put(compress_fast(frame, 3))
            self.nb_image += 1
    
    def read(self):
        if self.finished.is_set() and self.queue.empty() :
            return None
        rc = self.queue.get()
        self.queue.task_done()
        return decompress(rc)

    def flush(self) :
        self.finished.set()

class lastframe(object) :
    def __init__(self,resolution) :
        self._frame = None
        self.ready = threading.Event()
        self.finished = threading.Event()
        self.resolution = resolution
    
    def write(self,frame) :
        self._frame = frame
        self.ready.set()
    
    def read(self) :
        self.ready.wait()
        frame = self._frame        
        self.ready.clear()
        return frame

    def flush(self) :
        self.finished.set()
