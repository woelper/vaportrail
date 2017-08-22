import sys
import subprocess
import time
import os
import SimpleHTTPServer
import SocketServer
import signal
import threading

# for plugins
sys.path.append("../client")
from generic_client import Client
import plugins
for plugin in plugins.__all__:
    plug = '{}.{}'.format(plugins.__name__, plugin)
    print plug
    try:
        __import__(plug)
    except Exception as e:
        print e

class Test(object):
    def __init__(self):
        self.web_port = 8000
        self.server_port = 4000
        self.server_executable = ['python', '../server/python/server.py', str(self.server_port)]
        self.webapp_executable = ['python', '-m', 'SimpleHTTPServer', str(self.web_port)]
        self.server_process = None
        self.web_process = None
        self.clients = []

        signal.signal(signal.SIGINT, self.signal_handler)


    def signal_handler(self, signal, frame):
            self.teardown()

    def start_db_server(self):
        """
        Since the server might be in another language, let's keep
        it simple
        """
        print '>> Starting DB'
        return subprocess.Popen(self.server_executable)


    def start_web_server(self):
        print '>> Starting web service'
        curdir = os.getcwd()
        os.chdir("../server/frontend")
        return subprocess.Popen(self.webapp_executable)
        os.chdir(curdir)



    def startup(self):
        self.server_process = self.start_db_server()
        self.web_process = self.start_web_server()

    def teardown(self):
        print 'Shutting down'
        for c in self.clients:
            c.shutdown = True
        self.server_process.terminate()
        self.web_process.terminate()


    def tests(self):

        active_plugins = []
        for modname, mod in sys.modules.iteritems():

            if modname.startswith('plugins.') and  mod is not None:
                active_plugins.append(mod)


        for n in ['Mars', 'Phobos', 'Deimos', 'Keppler', 'Objekt 42']:
            c = Client('localhost:4000', active_plugins, custom_hostname=n)
            self.clients.append(c)
            c.dispatch_plugins()

        # print self.clients
        # for client in self.clients:
        #     c.dispatch_plugins()


if __name__ == '__main__':
    t = Test()
    t.startup()
    t.tests()
    time.sleep(30)
    t.teardown()