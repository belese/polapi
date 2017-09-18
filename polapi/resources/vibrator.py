#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  vibrator.py
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
from threading import Thread
from Queue import Queue
import RPi.GPIO as GPIO
 
#GPIO PIN ID
BUZZER = 26

#schema (DutyCycle,time)
OK =((100,0.2),(0,0.1),(100,0.2))
READY = ((100,0.2),(0,0.3),(100,0.2),(0,0.3),(100,0.2))
CANCEL =((100,1.5),)
TOUCHED = ((100,0.1),)

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER, GPIO.OUT)


q = Queue()

def worker():
    while True:
        schema = q.get()
        for action in schema :
			p = GPIO.PWM(BUZZER, 50)
			p.start(action[0])
			time.sleep(action[1])
			p.stop()
        q.task_done()



t = Thread(target=worker)
t.daemon = True
t.start()
	

def vibrator(schema) :
	q.put(schema)


def main(args):
    vibrator(READY)

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
