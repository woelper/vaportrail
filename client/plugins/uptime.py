"""
Plugin file.
They just need a run method and an INTERVAL int interval.
"""
from _base_plugin import *

# Import what you like here
import subprocess

INTERVAL = 600


def run():
    """
    Retrieve OS type
    returns: string
    """
    try:
        uptime = subprocess.check_output("uptime").rstrip()
        uptime = uptime.split("up ")[1].split("  ")[0][:-1]
        return {"Uptime": uptime}
    except OSError:
        return {}
    
if __name__ == '__main__':
    print run()