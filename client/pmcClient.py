#!/usr/bin/python
import urllib
import urllib2
import socket
import time
import json
import subprocess
import sys
import multiprocessing
import argparse



class Client():

    def __init__(self):
        self.tunnel_up = False
        self.ssh_target_port = False
        self.ssh_process = False
        settings_file = 'pmcClient.conf'
        settings = False
        with open(settings_file) as logfile:  
            settings = json.load(logfile)
        if settings:
            self.ssh_relay = settings['SSH_RELAY']
            server_url = settings['SERVER_URL']
            self.url_add = server_url + '/add'
            self.url_port = server_url + '/request_port'
        else:
            print 'could not parse config file ' + settings_file
            sys.exit(1)

    def ask_for_port(self, server_address):
        if not self.ssh_target_port:
            print "requesting port from", server_address
            REQUEST = urllib2.Request(server_address)
            try:
                RESPONSE = urllib2.urlopen(REQUEST)
                self.ssh_target_port = RESPONSE.read()
                print 'got port ', RESPONSE.read()
                return RESPONSE.read()
            except urllib2.URLError:
                print "Could not connect to " + server_address
                return False
        else:
            return self.ssh_target_port

    def init_tunnel(self, server_address, remote_port, local_port=22):
        #cmd = ['ssh', '-oBatchMode=yes', '-f', '-N', '-T', '-R'+ str(remote_port) + ':127.0.0.1:' + str(local_port), server_address]
        cmd = ['ssh', '-oBatchMode=yes', '-f', '-N', '-T', '-R'+ str(remote_port) + ':127.0.0.1:' + str(local_port), server_address]

        # Is the process still running?

        if self.ssh_process:
            #print self.ssh_process.returncode
            if self.ssh_process.returncode is None:
                print "Tunnel connected"
            else:
                print "Tunnel down. Restarting."
                self.ssh_process.kill()
                proc = subprocess.Popen(cmd)
                self.ssh_process = proc  
        else:
            print 'SSH tunnel not running. Starting it.'
            proc = subprocess.Popen(cmd)
            self.ssh_process = proc        
        

        """
        else:
            print 'Init ssh tunnel'
            print self.ssh_process
            cmd = ['ssh', '-oBatchMode=yes', '-N', '-T', '-R'+ str(remote_port) + ':127.0.0.1:' + str(local_port), server_address]#ssh -f -N -T -R22222:localhost:22 user@host
            proc = subprocess.Popen(cmd)
            self.ssh_process = proc
        """
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
        try:
            mem = " ".join(subprocess.check_output(["free", "-m"]).splitlines()[1].split()).split()
        except OSError:
            print "could not determine free mem"
            mem = ["0", "0", "0"]
        mem_total = mem[1]
        mem_used = mem[2]
        return "{0} MB of {1} MB used".format(mem_used, mem_total)

    @staticmethod
    def get_os():
        """Retrieve OS type"""
        return sys.platform

    def get_cpuinfo(self):
        """Retrieve info about CPU usage."""
        num_cpu = multiprocessing.cpu_count()
        try:
            load = subprocess.check_output("uptime").rstrip()
            if self.get_os() == "darwin":
                load = load.split("ages: ")[1].split(" ")[0]
                print load
            elif "linux" in self.get_os():
                load = load.split("age: ")[1].split("  ")[0].split(",")[1]
            else:
                return False
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
            ssh_port = self.ask_for_port(self.url_port)
            

            VALUES = {
            'ip': self.get_ip(),
            'host': socket.gethostname(),
            'time': time.time(),
            'uptime': self.get_uptime(),
            'memory': self.get_meminfo(),
            'os': self.get_os(),
            'cpu %': self.get_cpuinfo(),
            'ssh': 'ssh://' + self.ssh_relay + ':' + ssh_port
            }

            request = urllib2.Request(self.url_add, urllib.urlencode(VALUES))
            try:
                response = urllib2.urlopen(request)
                #print response.read()
            except urllib2.URLError:
                print "Could not connect to " + self.url_add

            if ssh_port:
                if self.init_tunnel(self.ssh_relay, ssh_port):
                    pass
            time.sleep(interval)

        while True:
            loop()



c = Client()
# seconds between updates
c.updateloop(100)

