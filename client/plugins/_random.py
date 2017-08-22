"""
Testing: emit random values
"""
from _base_plugin import *

# Import what you like here
import time
import math
import random

# Those come in from the base_plugin as default. You can override them here
INTERVAL = 0.5
CATEGORY = None

# use the run funtion to do your logic
def run():
    """
    This function must return a dictionary
    """

    random.seed()
    return {
        'Extraterrestrial signal': random.randint(5,30),
        'Huffmeister Interference': random.randint(1,25),
        }

if __name__ == '__main__':
    print run()