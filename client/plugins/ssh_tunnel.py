
# TODO: add argparse to configure the parameters

# Specify the SSH server you want to use as a port forwarder.
# You should have set up key-based passwordless access already. Otherwise you will be asked for a password.
# as in SSH, you may enter user@host here, too.


"""
Plugin file.
They just need a run method and an INTERVAL int interval.
"""
from _base_plugin import *

# Import what you like here
import time
import socket
import time
import subprocess
from subprocess import Popen, PIPE
import multiprocessing
import os


# Those come in from the base_plugin as default. You can override them here
INTERVAL = 30.0
PID = None
SSH_HOST = None

def init_tunnel(server_address, remote_port, local_port=22):
    """
    Initializes a SSH tunnel
    returns: None or True depending on success
    """
    def get_pid(appstring):
        # print 'determining PID'
        processes = subprocess.check_output(['ps', '-fx'])
        for line in processes.splitlines():
            if appstring in line:
                pid = line.split()[0]
                return pid

    global PID
    cmd = ['ssh', '-f', '-N', '-T', '-R{}:127.0.0.1:{}'.format(remote_port,local_port), server_address]
    try:
        proc = Popen(cmd, preexec_fn=os.setsid)
        proc.wait() # otherwise the PID won't be correct. proc.pid is of no help.
        PID = get_pid(' '.join(cmd))
        return True
    except Exception as e:
        print e
        return False

# use the run funtion to do your logic
def run():
    """
    This function must return a dictionary
    """

    if SSH_HOST is None:
            print 'SSH_HOST not set. Please configure if you want tunnel support.'
            return {}


    def connect():
        port = find_open_port(SSH_HOST)
        if init_tunnel(SSH_HOST, port):
            print 'Tunnel initialized, pid:', PID
            return {'ssh tunnel entry': 'ssh://{}:{}'.format(SSH_HOST, port)}
        return {}

    def is_pid_alive(pid):
        processes = subprocess.check_output(['ps', '-fx'])
        for line in processes.splitlines():
            lpid = line.split()[0]
            if lpid == pid:
                return True
        return False

    def find_open_port(host, start_port=22222):
        i = 0
        while i < 1000:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((host, start_port + i))
            if result == 0:
                print "Port is already used: ", start_port + i
                i += 1
            else:
                return start_port + i
    

    

    if PID is None:
        return connect()
    else:
        # check if process is still alive
        if is_pid_alive(PID):
            print 'Tunnel still active. Not doing anything.'
        else:
            return connect()            

if __name__ == '__main__':
    print run()