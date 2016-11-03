import time
from threading import Thread, Lock
from thermal import ThermalPrinter
from camera import CAMERA
from PIL import Image

try :
   from resources.resource import Resource, queue_call
except :
   from resource import Resource, queue_call
   
PRINTER_HEIGHT = 384


class Printer(Resource):
    def __init__(self):
        Resource.__init__(self)
        self.printer = ThermalPrinter("/dev/serial0", 9600, timeout=0, rtscts=True)
        self.printer.wake()
        self.lock = Lock()

    @queue_call
    def streamImages(self, streamer):
        with self.lock:
            # self.printer.wake()
            self.printer.streamImage(streamer)
            self.printer.feed(3)
            # self.printer.sleep()

    @queue_call
    def printToPage(self, image, Laat=False):
        with self.lock:
            print ('Printing...')           
            im_width, im_height = image.size
            ratio = (PRINTER_HEIGHT / float(im_width))
            height = int((float(im_height) * float(ratio)))
            image = image.resize((PRINTER_HEIGHT, height), Image.ANTIALIAS)
            self.printer.printImage(image, Laat)
            self.printer.feed(3)
            time.sleep(3)   

    @queue_call
    def print_txt(self, text):
        with self.lock:
            # self.printer.wake()
            self.printer.println(text)
            # self.printer.sleep()


PRINTER = Printer()


def main(args):
    a = Image.open('test.png')
    # PRINTER.printer.offline()
    #PRINTER.printer.sleep()
    #import time
    #time.sleep(2)
    #PRINTER.printer.println('''Anyone who reads Old and Middle English literary texts will be familiar with the mid-brown volumes of the EETS, with the symbol of Alfred's jewel embossed on the front cover. Most of the works attributed to King Alfred or to Aelfric, along with some of those by bishop Wulfstan and much anonymous prose and verse from the pre-Conquest period, are to be found within the Society's three series; all of the surviving medieval drama, most of the Middle English romances, much religious and secular prose and verse including the English works of John Gower, Thomas Hoccleve and most of Caxton's prints all find their place in the publications. Without EETS editions, study of medieval English texts would hardly be possible. As its name states, EETS was begun as a 'club', and it retains certain features of that even now. It has no physical location, or even office, no paid staff or editors, but books in the Original Series are published in the first place to satisfy subscriptions paid by individuals or institutions. This means that there is need for a regular sequence of new editions, normally one or two per year; achieving that sequence can pose problems for the Editorial Secretary, who may have too few or too many texts ready for publication at any one time. Details on a separate sheet explain how individual (but not institutional) members can choose to take certain back volumes in place of the newly published volumes against their subscriptions. On the same sheet are given details about the very advantageous discount available to individual members on all back numbers. In 1970 a Supplementary Series was begun, a series which only appears occasionally (it currently has 24 volumes within it); some of these are new editions of texts earlier appearing in the main series. Again these volumes are available at publication and later at a substantial discount to members. All these advantages can only be obtained through the Membership Secretary (the books are sent by post); they are not available through bookshops, and such bookstores as carry EETS books have only a very limited selection of the many published.''')
    # PRINTER.printer.online()
    PRINTER.print_txt('Bonjour Cyprien')

    PRINTER.printToPage(a,False)
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
