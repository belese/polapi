#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  camera.py
#
#  Copyright 2017 belese <belese@belese>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
import time
import io
import threading
import Queue
import picamera
from lz4 import compress, decompress, compress_fast
import psutil

from PIL import Image

from resources.resource import Resource, queue_call

SLITSCAN_WIDTH = 640
SLITSCAN_HEIGHT = 384
SLITSCAN_SIZE = (SLITSCAN_WIDTH, SLITSCAN_HEIGHT)

NO_SCAN = 1
SCAN_MODE = 2
SCAN_MODE_FIX = 3
SCAN_MODE_LIVE = 4

SLIT_SCAN_FIX_WIDTH = 1

LOW_MEMORY = 50 * 1024 * 1024


class SlitScan(object):
    def __init__(self, resolution=SLITSCAN_SIZE):
        self.resolution = resolution
        self.queue = Queue.Queue()
        self.nb_image = 0
        self.finished = threading.Event()

    def _put(self, objet):
        if psutil.virtual_memory()[1] > LOW_MEMORY:
            self.queue.put(compress_fast(objet, 3))
            return True
        else:
            return False

    def _get(self):
        rc = self.queue.get()
        self.queue.task_done()
        return decompress(rc)

    def write(self, s):
        if not self._put(s):
            self.write = self._throw
            return
        self.nb_image += 1

    def _throw(self, s):
        pass

    def getImage(self):
        self.finished.wait()
        if self.nb_image == 0:
            return None
        img = Image.new('L', self.resolution, 0)
        slitsize = self.resolution[0] / self.nb_image
        reste_img = self.resolution[0] % self.nb_image
        keyframe = []

        while reste_img > 0:
            val = (self.nb_image / reste_img)
            if self.nb_image % reste_img != 0:
                val += 1
            keyframe.append(val)
            reste_img = reste_img - (self.nb_image / val)

        x = 0
        for i in range(self.nb_image):
            frame = slitsize
            for k in keyframe:
                if (i + 1) % k == 0:
                    frame += 1
            if frame != 0:
                column = Image.frombuffer(
                    'L', self.resolution, self._get(), "raw", 'L', 0, 1)
                column = self.cropMethod(column, x, frame)
                img.paste(column, (x, 0))
                del(column)
                x += frame
            else:
                # throw unecessery frame
                a = self._get()
                del(a)
        return img

    def flush(self):
        self.finished.set()


class ScanMode(SlitScan):
    def cropMethod(self, img, x, frame):
        return img.crop((x, 0, x + frame, img.size[1]))


class ScanModeFix(SlitScan):
    def cropMethod(self, img, x, frame):
        return img.crop(((img.size[0] / 2) - frame / 2,
                         0,
                         (img.size[0] / 2) + (frame - (frame / 2)),
                         img.size[1]))


class ScanModeLive(ScanModeFix):
    def __init__(self, resolution=SLITSCAN_SIZE, slitSize=1):
        ScanModeFix.__init__(self, resolution)
        self.slitSize = slitSize

    def getImage(self):
        return None

    def flush(self):
        self._put("")
        ScanModeFix.flush(self)

    def get(self):
        frame = self._get()
        if not frame:
            return None
        frame = Image.frombuffer('L', self.resolution, frame, "raw", 'L', 0, 1)
        return self.cropMethod(frame, 0, self.slitSize).rotate(90, expand=1)


class Camera(Resource):
    def __init__(self):
        Resource.__init__(self)
        self.camera = None
        self.initCamera()
        self.camlock = threading.Lock()
        self.img = None
        self.keepres = None

    @queue_call
    def setSettings(self, settings):
        for param in settings.keys():
            setattr(self.camera, param, settings[param])

    @queue_call
    def initCamera(self):
        self.camera = picamera.PiCamera()
        self.camera.framerate = 90
        self.camera.resolution = SLITSCAN_SIZE
        #self.camera.vflip = True

    @queue_call
    def getPhoto(self):
        stream = io.BytesIO()
        with self.camlock:
            self.camera.capture(stream, format='jpeg')
        stream.seek(0)
        return Image.open(stream)

    def startSlitScan(self, mode=SCAN_MODE, slitscansize=1):
        if mode == SCAN_MODE:
            slitScanProcess = ScanMode(self.camera.resolution)
        elif mode == SCAN_MODE_FIX:
            slitScanProcess = ScanModeFix(self.camera.resolution)
        elif mode == SCAN_MODE_LIVE:
            slitScanProcess = ScanModeLive(
                self.camera.resolution, slitscansize)
        self.startRecording(slitScanProcess, res)
        return slitScanProcess

    @queue_call
    def startRecording(self, stream, res):
        self.camlock.acquire()
        self.camera.start_recording(stream, format='yuv', resize=res)

    @queue_call
    def stopRecording(self):
        self.camera.stop_recording()
        if self.keepres:
            self.camera.resolution = self.keepres
            self.keepres = None
        self.camlock.release()

    def stopSlitScan(self):
        self.stopRecording()

    def stop(self):
        if self.camera.recording:
            self.stopSlitScan()
        with self.camlock:
            self.camera.close()
        Resource.stop(self)

    @queue_call
    def sleep(self):
        with self.camlock:
            self.camera.close()

    @queue_call
    def wake(self):
        with self.camlock:
            self.camera = picamera.PiCamera()
            self.camera.framerate = 90
            self.camera.resolution = SLITSCAN_SIZE
            time.sleep(2)


CAMERA = Camera()


def main(args):
    try:
        import time
        #CAMERA.camera.rotation = 180
        #CAMERA.camera.resolution = PRINTER_SIZE
        CAMERA.camera.framerate = 90
        #CAMERA.camera.contrast = 50
        CAMERA.getPhoto().save('test1.jpg')
        a = CAMERA.startSlitScan(SCAN_MODE_FIX)
        time.sleep(20)
        CAMERA.stopSlitScan()
        a.getImage().save("test.jpg")
    finally:
        CAMERA.stop()


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
