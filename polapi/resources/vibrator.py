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
from resources.resource import Resource, queue_call
import RPi.GPIO as GPIO

# GPIO PIN ID
BUZZER = 18

#Buzzer (DutyCycle,time)
OK = ((1, 0.2), (0, 0.1), (1, 0.2),(0, 0.1))
READY = ((1, 0.3), (0, 0.3), (1, 0.3), (0, 0.3), (1, 0.3))
CANCEL = ((1, 0.1),)
TOUCHED = ((1, 0.25),)
ERROR =((1,0.5),(0,0.1),(1,0.5),(0,0.1),(1,0.5))
def REPEAT(x): return ((1, 0.2), (0, 0.1)) * x




GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER, GPIO.OUT)


class Vibrator(Resource):
    @queue_call
    def buzz(self, schema):
        for action in schema:
            GPIO.output(BUZZER, action[0])
            time.sleep(action[1])
        GPIO.output(BUZZER, 0)


BUZZ = Vibrator()


def main(args):
    BUZZ.buzz(((1, 0.5),))
    time.sleep(10)
    BUZZ.stop()


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
