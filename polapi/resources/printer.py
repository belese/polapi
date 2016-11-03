from threading import Thread, Lock
from thermal import ThermalPrinter
from PIL import Image
from resources.resource import Resource, queue_call

PRINTER_HEIGHT = 384


class Printer(Resource):
    def __init__(self):
        Resource.__init__(self)
        self.printer = ThermalPrinter("/dev/serial0", 9600)
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
            # self.printer.wake()
            im_width, im_height = image.size
            ratio = (PRINTER_HEIGHT / float(im_width))
            height = int((float(im_height) * float(ratio)))
            image = image.resize((PRINTER_HEIGHT, height), Image.ANTIALIAS)
            self.printer.printImage(image, Laat)
            self.printer.feed(3)
            # self.printer.sleep()

    @queue_call
    def print_txt(self, text):
        with self.lock:
            # self.printer.wake()
            self.printer.println(text)
            # self.printer.sleep()


PRINTER = Printer()


def main(args):
    a = Image.open('../test2.jpg')
    # PRINTER.printer.offline()
    PRINTER.printer.sleep()
    import time
    time.sleep(2)
    PRINTER.printer.println('test')
    # PRINTER.printer.online()
    PRINTER.printer.println('test')

    # PRINTER.printImage(a,False)
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
