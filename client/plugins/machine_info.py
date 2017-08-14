"""
Plugin file.
They just need a run method and an INTERVAL int interval.
"""
from base_plugin import *

# Import what you like here
import platform

INTERVAL = 600


def run():
    # Well, this is easy.
    return {
        'OS': platform.platform(),
        'CPU Type': platform.processor()
        }