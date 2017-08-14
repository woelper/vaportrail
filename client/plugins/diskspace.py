"""
Plugin file.
They just need a run method and an INTERVAL int interval.
"""
from base_plugin import *

import subprocess
from subprocess import PIPE, Popen
import platform
import os

INTERVAL = 600

def get_free_space():
    directory = os.curdir

    if 'windows' in platform.platform().lower():
        proc = Popen('fsutil volume diskfree c:', stdout=PIPE, stderr=PIPE)
        output = proc.communicate()
        if output:
            output = output[0].replace(' ', '').splitlines()
            try:
                free = output[0].split(':')[1]
                free = int(free)/1024/1024
                return free
            except:
                return 'Could not get free disk space'
    else:
        statvfs = os.statvfs(os.curdir)
        free_mb = statvfs.f_frsize * statvfs.f_bfree/1024/1024
        return free_mb


def run():
    return {'Free space on root': get_free_space()}
