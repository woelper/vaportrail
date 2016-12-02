#!/usr/bin/env python
import time
import sys
import os
import hashlib

"""
Web.py has a structure that dictates it can not imported as-is.
We'll just do some sanity checks and add the folder to the path.
"""

current_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
webpy_location = os.path.join(current_dir, 'webpy')
if not os.path.isdir(webpy_location):
    print 'please clone web.py to this folder:', current_dir
    sys.exit(1)
else:
    sys.path.append(webpy_location)
    import web

# TODO : historical view - save state each time as list

urls = ("/", "State" ,"/add", "add", '/state', 'State', '/request_port', 'request_port')
app = web.application(urls, globals())
hostDB = {}
PORT = 20000
UPDATES = 0

def boolify(s):
    if s == 'True':
        return True
    if s == 'False':
        return False
    raise ValueError("could not convert string to bool")

def autoconvert(s):
    for fn in (boolify, int, float):
        try:
            return fn(s)
        except ValueError:
            pass
    return s


class State:
    inactive_delta = 2000

    def GET(self):
        print "---------------------------- Client state: --------------------"
        stat_db = []

        for dict_item in hostDB.itervalues():
            client_dict = dict_item

            # The timing logic
            # do we have a timastamp at all?
            if 'time' in dict_item.keys():
                float_time = float(dict_item['time'])
                now = time.time()
                timediff = now - float_time

                # init rate with our default inactive delta. Anything older is inactive.
                rate = self.inactive_delta
                # if the client sent 'update_rate', we use this to determine if it's inactive
                if 'update_rate' in dict_item.keys():
                    try:
                        rate = float(dict_item['update_rate'])
                    except ValueError:
                        print 'wrong value for update_rate'

                if timediff > rate:
                    client_dict['inactive'] = True
                else:
                    client_dict['inactive'] = False

                hours, rest = divmod(timediff, 3600)
                minutes, seconds = divmod(rest, 60)
                #hrt = time.asctime( timediff )
                timediffstring = ' '.join([str(int(hours)),'h', str(int(minutes)), 'm', str(int(seconds)), 's'])
                client_dict['last update'] = timediffstring
            # for generating DIV ids, we need a clean id string without spaces and other funky stuff
            client_dict['id'] = hashlib.md5(client_dict['host']).hexdigest()
            # enable users to pass their icon to do so, set a default one,
            if 'icon' not in client_dict.keys():
                client_dict['icon'] = 'fa-server'

            stat_db.append(client_dict)
        html = web.template.frender('templates/stats.html')

        server_stats = {}
        server_stats['updates'] = UPDATES
        return html(stat_db, server_stats)


class request_port:
    def GET(self):
        global PORT
        PORT += 1
        return PORT


class add:

    @staticmethod
    def GET():
        return "You must use POST. Sorry."

    @staticmethod
    def POST():
        data = dict(web.input())
        # set the time
        data['time'] = time.time()

        # make sure there is a 'host entry'
        if not 'host' in data.keys():
            return 'You need to specify a value for "host."'

        host = data['host']

        # let's convert the strings to appropriate vars
        for key in data:
            data[key] = autoconvert(data[key])

        hostDB[host] = data

        global UPDATES
        UPDATES += 1
        return 'Your host {} was added.'.format(host)


class Status():
    def GET(self):
        print "status"



'''
class RequestHandler():
    def POST():
        data = web.data() # you can get data use this method
'''


if __name__ == "__main__":
    app.run()
