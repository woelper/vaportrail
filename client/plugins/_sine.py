"""
Plugin file.
They just need a run method and an INTERVAL int interval.
"""
from _base_plugin import *

# Import what you like here
import time
import math


# Those come in from the base_plugin as default. You can override them here
INTERVAL = 0.1
CATEGORY = None



# use the run funtion to do your logic
def run():
    """
    This function must return a dictionary
    """

    # to test high update rates, draw a sine curve
    return {'sine': math.sin(time.time()*2)+1}

if __name__ == '__main__':
    print run()