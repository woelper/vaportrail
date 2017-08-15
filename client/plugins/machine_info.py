"""
Plugin file.
They just need a run method and an INTERVAL int interval.
"""
from base_plugin import *

# Import what you like here
import platform
import multiprocessing
INTERVAL = 600


def run():
    # Well, this is easy.
    platform_info = platform.system_alias(platform.system(), platform.release(), platform.version())
    return {
        'OS': 'System: {} || Release: {} || Version: {}'.format(platform_info[0], platform_info[1], platform_info[2]),
        'CPU Type':  '{} x {}'.format(platform.processor(), multiprocessing.cpu_count()),

        }