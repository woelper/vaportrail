#!/usr/bin/python
import urllib
import urllib2
import socket
import time
import json
import subprocess
import sys
import multiprocessing

# Specify the SSH server you want to use as a port forwarder.
# You should have set up key-based passwordless access already.
SSH_RELAY = 'schdbr.de'
# The master server to sync to
URL = 'http://localhost:8080'
URL_ADD = URL + '/add'
URL_PORT = URL + '/request_port'

class Client():

    def __init__(self):
        self.tunnel_up = False

    @staticmethod
    def ask_for_port(server_address):
        REQUEST = urllib2.Request(URL_PORT)
        try:
            RESPONSE = urllib2.urlopen(REQUEST)
            return RESPONSE.read()
        except urllib2.URLError:
            print "Could not connect to " + URL_PORT
            return 'NULL'

    @staticmethod
    def init_tunnel(server_address, remote_port, local_port=22):
        cmd = ['ssh', '-f', '-N', '-T', '-R'+ str(remote_port) + ':127.0.0.1:' + str(local_port), server_address]
        #ssh -f -N -T -R22222:localhost:22 user@host
        return_value = subprocess.call(cmd)
        if return_value == 0:
            return True

    @staticmethod
    def get_ip():
        """Retrieve public ip"""
        try:
            public_ip = json.load(urllib2.urlopen('http://jsonip.com'))['ip']
        except urllib2.URLError:
            public_ip = False
            print "Could not connect to ip service"
        return public_ip

    @staticmethod
    def get_uptime():
        """Get uptime"""
        try:
            uptime = subprocess.check_output("uptime").rstrip()
            uptime = uptime.split("up ")[1].split("  ")[0][:-1]
        except OSError:
            uptime = False
        return uptime

    @staticmethod
    def get_meminfo():
        """Retrieve info about memory usage."""
        mem = False
        mem = " ".join(subprocess.check_output(["free", "-m"]).splitlines()[1].split()).split()
        mem_total = mem[1]
        mem_used = mem[2]
        return "{0} MB of {1} MB used".format(mem_used, mem_total)

    @staticmethod
    def get_os():
        """Retrieve OS type"""
        return sys.platform

    @staticmethod
    def get_cpuinfo():
        """Retrieve info about CPU usage."""
        num_cpu = multiprocessing.cpu_count()
        try:
            load = subprocess.check_output("uptime").rstrip()
            load = load.split("age: ")[1].split("  ")[0].split(",")[1]
        except OSError:
            load = False
        if load:
            try:
                load = float(load)
                load = load/num_cpu*100
            except ValueError:
                print "could not convert cpu to float value. Check uptime format."
        return load

    def updateloop(self, interval):
        """Updates the remote server's DB
        interval: seconds between updates
        """

        def loop():
            VALUES = {
            'ip': self.get_ip(),
            'host': socket.gethostname(),
            'time': time.time(),
            'uptime': self.get_uptime(),
            'memory': self.get_meminfo(),
            'os': self.get_os(),
            'cpu %': self.get_cpuinfo(),
            'ssh': 'ssh://' + SSH_RELAY + ':' + ssh_port
            }

            request = urllib2.Request(URL_ADD, urllib.urlencode(VALUES))
            try:
                response = urllib2.urlopen(request)
                print response.read()
            except urllib2.URLError:
                print "Could not connect to " + URL_ADD

            if not self.tunnel_up:
                print 'Tunnel init: port ' + ssh_port
                if self.init_tunnel(SSH_RELAY, ssh_port):
                    print 'Tunnel initialized'
                    self.tunnel_up = True
            time.sleep(interval)

        while True:
            loop()



c = Client()
ssh_port = c.ask_for_port(SSH_RELAY)
c.updateloop(360)

