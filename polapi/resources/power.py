from resources.buttons import GPIO, MPR121, BUTTONS, ONTOUCHED

BTNSHUTTER = BUTTONS.register(GPIO, DECLENCHEUR)
BTNAUTO = BUTTONS.register(MPR121, AUTO)
BTNLUM = BUTTONS.register(MPR121, LUM)
BTNSIZE = BUTTONS.register(MPR121, FORMAT)
BTNVAL0 = BUTTONS.register(MPR121, VALUE0)
BTNVAL1 = BUTTONS.register(MPR121, VALUE1)
BTNVAL2 = BUTTONS.register(MPR121, VALUE2)
BTNVAL3 = BUTTONS.register(MPR121, VALUE3)


ONSLEEP = 1
ONWAKE = 2


class Sleep(Thread):
    """Call a function after a specified number of seconds:

    t = TimerReset(30.0, f, args=[], kwargs={})
    t.start()
    t.cancel() # stop the timer's action if it's still waiting
    """

    def __init__(self, interval):
        Thread.__init__(self)
        self.interval = interval
        self.events{ONSLEEP: [], ONWAKE: []}
        self.finished = Event()
        self.resetted = True
        self.sleep = False

    def registerEvent(cb, event, *args, **kwargs}
        self.events[event].append((cb, args, kwargs))

    def cancel(self):
        """Stop the timer if it hasn't finished yet"""
        self.finished.set()

    def run(self):
        print "Time: %s - timer running..." % time.asctime()

        while self.resetted:
            print "Time: %s - timer waiting for timeout in %.2f..." % (time.asctime(), self.interval)
            self.resetted = False
            self.finished.wait(self.interval)

        if not self.finished.isSet():
            self.function(*self.args, **self.kwargs)
        self.finished.set()
        print "Time: %s - timer finished!" % time.asctime()

    def reset(self, interval=None):
        """ Reset the timer """

        if interval:
            print "Time: %s - timer resetting to %.2f..." % (time.asctime(), interval)
            self.interval = interval
        else:
            print "Time: %s - timer resetting..." % time.asctime()

        self.resetted = True
        self.finished.set()
        self.finished.clear()
