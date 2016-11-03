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
        self.stopped = False
    
    def write(self,frame) :
        print ('write image')
        if (self.nb_image+1) % 100 != 0 or psutil.virtual_memory()[1] > LOW_MEMORY:
            print ('Put in queue')
            self.queue.put(compress_fast(frame, 3))
            #self.queue.put(frame)
            self.nb_image += 1
            print ('Put in q done',self.nb_image)

    
    def read(self):
        if self.queue.empty() :
            return None
        rc = self.queue.get()
        self.queue.task_done()
        return decompress(rc)
        #return rc

    def flush(self) :
        self.finished.set()
    
    def stop(self) :
        self.stopped = True

class lastframe(object) :
    def __init__(self,resolution) :
        self._frame = None
        self.ready = threading.Event()
        self.ready.clear()
        self.finished = threading.Event()
        self.resolution = resolution
        self.stopped = False
    
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
        self._frame = None
        self.ready.clear()
    
    def stop(self) :
        self.stopped = True
        self._frame = None
        self.ready.set()

