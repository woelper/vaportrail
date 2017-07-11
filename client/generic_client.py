#!/usr/bin/env python
import urllib
import urllib2
import time
import sys
import argparse
import os
import threading

class Client():

    def __init__(self, server, plugins, custom_hostname=None):
        
        self.custom_hostname = None
        if custom_hostname is not None:
            self.custom_hostname = custom_hostname
        if not server.startswith('http://'):
            server = 'http://' + server
        self.server = server
        self.post_url = server + '/add'
        self.plugins = plugins
        self.threads = []

    def run_plugin_in_background(self, plugin):
        """
        execute plugin.run() every plugin.INTERVAL
        """
        def loop():

            result = {}
            try:
                result = plugin.run()
            except:
                print 'plugin failed'
                return

            # dismiss empty values
            if result == {}:
                return

            result['host'] = plugin.CATEGORY

            if self.custom_hostname is not None:
                result['host'] = self.custom_hostname
            timer = time.time()
            request = urllib2.Request(self.post_url, urllib.urlencode(result))
            
            try:
                response = urllib2.urlopen(request)
                print response.read()
            except urllib2.URLError:
                print 'Could not connect to ' + self.post_url

            print 'ran', plugin.__name__, 'in', time.time() - timer
            time.sleep(plugin.INTERVAL)
        while True:
            loop()


    def dispatch_plugins(self):
        """
        Fire up each plugin in a thread
        """
        for p in self.plugins:
            print 'launch plugin', p.__name__
            t = threading.Thread(target=self.run_plugin_in_background, args=(p,))
            t.daemon = True
            self.threads.append(t)
            t.start()

        while True:
            #just stay active
            time.sleep(10)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update client')
    parser.add_argument('server', help='pmc server instance')
    parser.add_argument('--hostname', default=None, help='Set custom hostname')
    args = parser.parse_args()
       
    from plugins import *
    
    active_plugins = []
    for modname, mod in sys.modules.iteritems():
        if modname.startswith('plugins.') and not 'base_' in modname:
            plugin_directory = dir(mod)
            if 'run' in plugin_directory and 'INTERVAL' in plugin_directory:
                active_plugins.append(mod)
            else:
                if mod is not None:
                    print mod, 'invalid'
    c = Client(args.server, active_plugins, custom_hostname=args.hostname)
    c.dispatch_plugins()
