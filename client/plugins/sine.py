"""
Plugin file.
They just need a run method and an INTERVAL int interval.
"""
from base_plugin import *

# Import what you like here
import time
import math


# Those come in from the base_plugin as default. You can override them here
INTERVAL = 20
CATEGORY = 'test'



# use the run funtion to do your logic
def run():
    """
    This function must return a dictionary
    """

    return {'sine': math.sin(time.time()*2)+1}
