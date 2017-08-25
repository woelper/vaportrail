#!/usr/bin/env python
import urllib
import urllib2
import time
import sys
import argparse
import os
import threading
import socket

class Client():

    def __init__(self, server, plugins, custom_hostname=None):
        
        self.custom_hostname = None
        if custom_hostname is not None:
            self.custom_hostname = custom_hostname
        if not server.startswith('http://'):
            server = 'http://' + server
        self.post_url = server + '/add'
        self.plugins = plugins
        self.threads = []

    def __repr__(self):
        output = '\n{} class\n'.format(self.__class__.__name__)
        for k, v in self.__dict__.iteritems():
            output += '\t{}: {}\n'.format(k, v)
        return output


    def run_plugin_in_background(self, plugin):
        """
        execute plugin.run() every plugin.INTERVAL
        """
        def loop():

            result = {}
            try:
                result = plugin.run()
            except Exception as e:
                print 'plugin failed to run:', e
                return

            # dismiss empty values
            if result == {}:
                return

            # a CATEGORY could override the reporter's host if set.
            if plugin.CATEGORY is not None:
                result['host'] = plugin.CATEGORY
            else:
                result['host'] = socket.gethostname()

            if self.custom_hostname is not None:
                result['host'] = self.custom_hostname
            timer = time.time()
            request = urllib2.Request(self.post_url, urllib.urlencode(result))
            
            msg =  [plugin.__name__, ':']

            try:
                response = urllib2.urlopen(request)
                #ccmsg.append(response.read())
            except urllib2.URLError:
                msg += ['Could not connect to', self.post_url]
                msg = [str(s) for s in msg]
                print '{}'.format(' '.join(msg))


            # msg += ['in', round(1/(time.time() - timer)*10)/10, 'Hz']
        
        while True:
            loop()
            time.sleep(plugin.INTERVAL)
            


    def dispatch_plugins(self):
        """
        Fire up each plugin in a thread
        """
        for p in self.plugins:
            assert p is not None

            print '[[[ Launching Plugin: {} ]]]'.format(p.__name__)
            t = threading.Thread(target=self.run_plugin_in_background, args=(p,))
            t.daemon = True
            self.threads.append(t)
            t.start()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update client')
    parser.add_argument('server', help='pmc server instance')
    parser.add_argument('--hostname', default=None, help='Set custom hostname')
    args = parser.parse_args()
       
    import plugins

    for plugin in plugins.__all__:
        try:
            __import__('{}.{}'.format(plugins.__name__, plugin))
        except Exception as e: # This is broad on purpose, I have no idea what errors could happen here...
            print plugin, 'could not be loaded:', e

    active_plugins = []
    for modname, mod in sys.modules.iteritems():
        if modname.startswith(plugins.__name__ + '.') and not modname.startswith(plugins.__name__ + '._'):
            plugin_directory = dir(mod)
            if 'run' in plugin_directory and 'INTERVAL' in plugin_directory:
                active_plugins.append(mod)
            else:
                if mod is not None:
                    print mod, 'invalid'
    c = Client(args.server, active_plugins, custom_hostname=args.hostname)
    c.dispatch_plugins()

    while True:
    # just stay active
        time.sleep(20)
        print c.threads
