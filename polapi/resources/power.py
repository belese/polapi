#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  power.py
#  
#  Copyright 2018 belese <belese@belese>
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
from threading import Thread
import time
 
from attiny import ATTINY85

LOWER = 0x01
HIGHER = 0x02

class Power :   
    def __init__(self) :
        self.stopped = False
        self.voltages = []
        self.events = {LOWER: [], HIGHER: []}
        self.thread = Thread(target=self._callEvent)
        self.thread.start()
            
    def stop(self) :
		self.stopped = True
		
    def getVoltage(self) :
        volt = False            
        while not volt :
            volt = ATTINY85.getVoltage()
        return volt
        
    def registerEvent(self, cb, event,value, *args, **kwargs):
        self.events[event].append([cb, value,False,args, kwargs])                    
        
    def onEvent(self, event):
        event[0](*event[3], **event[4])
    
    def _callEvent(self) :
        for i in range(40) :                  
            self.voltages.append(self.getVoltage())
        
        while not self.stopped :
            avg = sum(self.voltages)/len(self.voltages) 
            print avg
            for event in self.events[LOWER] :
                if not event[2] and event[1] > avg :
                    self.onEvent(event)
                    event[2] = True
                elif event[2] and event[1] <= avg :
                    event[2] = False
            for event in self.events[HIGHER] :
                if not event[2] and event[1] < avg :
                    self.onEvent(event)
                    event[2] = True 
                elif event[2] and event[1] >= avg :
                    event[2] = False            
            time.sleep(1)
            self.voltages.pop(0)
            self.voltages.append(self.getVoltage())

POWER = Power() 

def main(args):
    def onLower() :
        print 'low cb'
    def onHigher() :
        print 'high cb'
    POWER.registerEvent(onLower,LOWER,5070)
    POWER.registerEvent(onHigher,HIGHER,5069)
    print "done"

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
