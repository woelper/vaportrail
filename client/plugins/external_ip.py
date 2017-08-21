"""
Plugin file.
They just need a run method and an INTERVAL int interval.
"""
from _base_plugin import *

# Import what you like here
import urllib2
import json

INTERVAL = 600


def get_ip():
    """
    Retrieves public ip via ip service
    returns: False or public ip, depending on success
    """
    try:
        public_ip = json.load(urllib2.urlopen('http://jsonip.com'))['ip']
    except urllib2.URLError:
        public_ip = False
        print "Could not connect to ip service"
    return public_ip

def run():
    return {'IP Address': get_ip()}