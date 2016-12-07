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

urls = ("/", "State" ,"/add", "add", '/state', 'State', '/request_port', 'request_port')
app = web.application(urls, globals())
PORT = 20000
DEFAULT_UPDATE_RATE = 1000
DEFAULT_ICON = 'fa-server'

class Database(object):
    """
    Simple Database class with history support.
    """
    def __init__(self):
        self.data = {}
        self.updates = 0
        self.queue_count = 45

    def read_kv(self, id, key):
        if id in self.data.keys():
            return self.data[id][key]

    def add_kv(self, id, dictionary):
        self.updates += 1
        dictionary = {key: [val] for (key, val) in dictionary.iteritems()}

        # update
        if id in self.data.keys():
            for key, value in dictionary.iteritems():
                if key in self.data[id].keys():
                    self.data[id][key] = value + self.data[id][key]
                    if len(self.data[id][key]) > self.queue_count:
                        self.data[id][key].pop()
        # create
        else:
            self.data[id] = dictionary

    def latest(self):
        return self.data

    def historic(self):
        return updated_host_data(self.data)

    def stats(self):
        return {'updates': self.updates}

DATA = Database()

def boolify(s):
    """
    convert string to either True or False
    """
    if s == 'True':
        return True
    if s == 'False':
        return False
    raise ValueError("could not convert string to bool")

def autoconvert(s):
    """
    Convert a string to the most probable type
    """
    for fn in (boolify, int, float):
        try:
            return fn(s)
        except ValueError:
            pass
    return s

def updated_host_data(database):
    """
    return up-to date data for display.
    this should go into the database class later
    """

    # TODO: make this a little leaner
    stat_db = {}
    for host, hostinfo in database.iteritems():

        # The timing logic
        now = time.time()
        timediff = now - float(hostinfo['timestamp'][0])

        if timediff > hostinfo['update_rate'][0]:
            hostinfo['inactive'] = [True]
        else:
            hostinfo['inactive'] = [False]
        # add some human-readable timing
        hours, rest = divmod(timediff, 3600)
        minutes, seconds = divmod(rest, 60)
        timediffstring = '{}h {}m {}s ago'.format(int(hours), int(minutes), int(seconds))
        hostinfo['last seen'] = [timediffstring]

        # for generating DIV ids, we need a clean id string without spaces and other funky stuff
        hostinfo['id'] = [hashlib.md5(host).hexdigest()]

        stat_db[host] = hostinfo
    return database


def add_or_update(value_dict):

    # make sure there is a 'host entry'. Fail otherwise.
    if not 'host' in value_dict.keys():
        return 'You need to specify a value for "host."'

    # let's convert the strings to appropriate vars
    for key in value_dict:
        value_dict[key] = autoconvert(value_dict[key])

    # Now add some mandatory stuff.
    value_dict['timestamp'] = time.time()

    if 'update_rate' not in value_dict:
            value_dict['update_rate'] = DEFAULT_UPDATE_RATE
    else:
        if not isinstance(value_dict['update_rate'], int):
            value_dict['update_rate'] = DEFAULT_UPDATE_RATE

    # enable users to pass their icon. Set a default one if unset.
    if 'icon' not in value_dict:
        value_dict['icon'] = DEFAULT_ICON

    host = value_dict['host']
    # as host will act as a key, we do not need to keep him around.
    del value_dict['host']

    print value_dict
    # finally add host and data
    DATA.add_kv(host, value_dict)

    return 'Your host {} was added.'.format(host)



class State:

    def GET(self):
        print "\n\n\n                 ### GET ###"

        html = web.template.frender('templates/stats.html', globals={"str": str, "type": type})

        return html(DATA.historic(), DATA.stats())


class request_port:
    def GET(self):
        global PORT
        PORT += 1
        return PORT


class add:

    @staticmethod
    def GET():
        """
        Let's support GET, too. No checking as of yet.
        """
        data = dict(web.input())
        return add_or_update(data)

    @staticmethod
    def POST():
        data = dict(web.input())
        return add_or_update(data)




if __name__ == "__main__":
    app.run()
