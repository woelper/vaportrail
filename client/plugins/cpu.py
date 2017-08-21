"""
Plugin file.
They just need a run method and an INTERVAL int interval.
"""
from _base_plugin import *

# Import what you like here
import platform
import subprocess
from subprocess import Popen, PIPE
import multiprocessing

# Those come in from the base_plugin as default. You can override them here
INTERVAL = 60.0

def get_cpuinfo():
    """
    Retrieve CPU usage.
    returns: float
    """

    if 'windows' in platform.platform().lower():
        proc = Popen('wmic cpu get loadpercentage', stdout=PIPE, stderr=PIPE)
        output = proc.communicate()
        if output:
            loadstring = output[0].replace(' ', '').splitlines()
            for entry in loadstring:
                try:
                    return int(entry)
                    print 'CPU LOAD', entry
                except ValueError:
                    pass
        return 'Could not determine cpu usage'

    else:
        num_cpu = multiprocessing.cpu_count()
        load = False
        try:
            load = subprocess.check_output('uptime').rstrip()
            load = load.split('age: ')[1].split('  ')[0].split(',')[1]
        except:
            pass

        try:
            load = float(load)
            load = load/num_cpu*100
        except ValueError:
            print 'could not convert cpu to float value. Check uptime format.'
        return load

# use the run funtion to do your logic
def run():
    """
    This function must return a dictionary
    """

    return {'CPU usage': get_cpuinfo()}

if __name__ == '__main__':
    print run()