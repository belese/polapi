#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  resource.py
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
import Queue
from threading import Thread


def queue_call(func):
    def wrapper(self, *arg, **kw):
        self.count += 1
        self.queue.put((self.count, func, arg, kw))
        return self.count
    return wrapper


# event


class Resource():

    RETURN = 10

    NB_WORKER = 1

    def __init__(self):
        self.queue = Queue.Queue()
        self.count = 1
        self.terminated = False
        #self.registeredEvents = []
        for i in range(self.NB_WORKER):
            Thread(target=self.start).start()

    def start(self):
        while not self.terminated:
            i, fn, arg, kw = self.queue.get()
            try :
                rc = fn(self, *arg, **kw)
            except Exception as e:
                rc = None
                print ('Unmanaged esxception',e)
                raise
            finally :
                #self.onReturn(i, rc)
                pass
        print ('ressources thread stopped')

    def stop(self):
        self.terminated = True
        self.queue.put((0, self._stopped, [], {}))

    def _stopped(self, arg):
        print ('ressources stopped')

    """

    def register(self, cb):
        self.registeredEvents.append(cb)

    def onREvent(self, event, arg):
        for ev in self.registeredEvents:
            ev(event, arg)

    def onReturn(self, id, rc):
        self.onREvent(self.RETURN, (id, rc))
    """
    
    def sleep(self):
        pass

    def wake(self):
        pass
