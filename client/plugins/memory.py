from base_plugin import *

import subprocess
import platform
import subprocess
from subprocess import Popen, PIPE

# Those come in from the base_plugin as default. You can override them here
INTERVAL = 600


def get_meminfo():
    """
    Retrieve info about memory usage.
    returns: three ints: total, used, free
    """
    mem = False

    if 'windows' in platform.platform().lower():

        def query_wmic(query):
            proc = Popen(query, stdout=PIPE, stderr=PIPE)
            output = proc.communicate()
            if output:
                output = output[0].replace(' ', '').splitlines()
                for o in output:
                    try:
                        return int(o)/1024
                    except ValueError:
                        pass
            return 'Not found'

        total = query_wmic('wmic ComputerSystem get TotalPhysicalMemory')
        if isinstance(total, int):
            total = total/1024

        free = query_wmic('wmic OS get FreePhysicalMemory')
        if isinstance(total, int) and isinstance(free, int):
            used = total - free
        else:
            used = 'Not found'
        return total, used, free

    else:
        try:
            mem = ' '.join(subprocess.check_output(['free', '-m']).splitlines()[1].split()).split()
            mem_total = int(mem[1])
            mem_used = int(mem[2])
            mem_free = mem_total - mem_used
            return mem_total, mem_used, mem_free
        except OSError:
            return 'free -m returned an error', 0, 0


# use the run funtion to do your logic
def run():
    """
    This function must return a dictionary
    """

    # to test high update rates, draw a sine curve
    return {'mem': get_meminfo()}

if __name__ == '__main__':
    print run()