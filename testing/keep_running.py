#!/usr/bin/env python
import time
from test import Test
import signal



if __name__ == '__main__':
    t = Test()

    def signal_handler(signal, frame):
        print 'SHUTTING DOWN'
        t.teardown()

    signal.signal(signal.SIGINT, signal_handler)

    t.startup()
    t.tests()
    time.sleep(5000)
