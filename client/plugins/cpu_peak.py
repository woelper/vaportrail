"""
Plugin file.
They just need a run method and an INTERVAL int interval.
"""
from base_plugin import *

# Import what you like here
import platform
import subprocess
from subprocess import Popen, PIPE
import multiprocessing

# Those come in from the base_plugin as default. You can override them here
INTERVAL = 5

from cpu import get_cpuinfo

# use the run funtion to do your logic
def run():
    """
    This function must return a dictionary
    """

    load = get_cpuinfo()
    if load > 80:
        return {'cpu_peak': load}
    return {}

if __name__ == '__main__':
    print run()