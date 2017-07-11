
# TODO: add argparse to configure the parameters

# Specify the SSH server you want to use as a port forwarder.
# You should have set up key-based passwordless access already. Otherwise you will be asked for a password.
# as in SSH, you may enter user@host here, too.


"""
Plugin file.
They just need a run method and an INTERVAL int interval.
"""
from base_plugin import *

# Import what you like here
import time
import socket
import time
import json
import subprocess
from subprocess import Popen, PIPE
import multiprocessing
import argparse
import platform
import os
import psutil


# Those come in from the base_plugin as default. You can override them here
INTERVAL = 500.0
CATEGORY = 'ssh'
PID = None

def init_tunnel(server_address, remote_port, local_port=22):
    """
    Initializes a SSH tunnel
    returns: None or True depending on success
    """
    global PID
    cmd = ['ssh', '-f', '-N', '-T', '-R'+ str(remote_port) + ':127.0.0.1:' + str(local_port), server_address]
    #ssh -f -N -T -R22222:localhost:22 user@host
    try:
        proc = Popen(cmd, preexec_fn=os.setsid)
        
        # return_value = subprocess.call(cmd)
        PID = proc.pid
        return proc.pid
    except:
        return False

# use the run funtion to do your logic
def run():
    """
    This function must return a dictionary
    """

    ssh_port = 22222
    ssh_relay = 'schdbr.de'
    if PID is None:
        print 'Tunnel init: port {}'.format(ssh_port) 
        if init_tunnel(ssh_relay, ssh_port):
            print 'Tunnel initialized'
            return {'ssh tunnel entry': 'ssh://{}:{}'.format(ssh_relay, ssh_port)}
        return {}



if __name__ == '__main__':
    print run()