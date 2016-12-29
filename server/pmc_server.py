#!/usr/bin/env python
import time
import sys
import os
import hashlib

"""
Web.py has a structure that dictates it can not imported as-is.
We'll just do some sanity checks and add the folder to the path.
"""
try:
    import web
except ImportError:
    print 'You need web.py to be importable. Either clone it to a folder called "web" in this dir or install it via pip.'
    sys.exit(1)

# The accessible urls
urls = ("/", "State" ,"/add", "add", '/request_port', 'request_port')

app = web.application(urls, globals())
PORT = 20000
DEFAULT_UPDATE_RATE = 1000
DEFAULT_ICON = 'fa-server'
DB = {}
STATS = {'updates': 111}

def is_list_of_pure_type(list_, type_):
    # bool is instance of int in python
    if type_ == int:
        if any([isinstance(l, bool) for l in list_]):
            return False
    return all([isinstance(l, type_) for l in list_])


class Value(object):
    """
    Simple value class with history support.
    """
    def __init__(self, val):
        self.values = []
        self.timestamps = []
        self.max_values = 45
        self.latest = None
        self.timestamp = None
        self.graphable = False
        self.add(val)

    def add(self, value):
        now = time.time()
        value = autoconvert(value)
        print 'adding', value
        self.latest = value
        self.values = [value] + self.values
        self.timestamps = [now] + self.timestamps
        self.timestamp = now
        if len(self.values) > self.max_values:
            self.values.pop()
        if is_list_of_pure_type(self.values, int) or is_list_of_pure_type(self.values, float):
            self.graphable = True

    def __repr__(self):
        return str(self.values)


    def serialize(self, array_of_values):
        self.values = array_of_values

    def deserialize(self):
        return self.values


class DataBase():
    def __init__(self):
        pass




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
        timediff = now - float(hostinfo['timestamp'].latest)

        if timediff > hostinfo['update_rate'].latest:
            hostinfo['inactive'] = Value(True)
        else:
            hostinfo['inactive'] = Value(True)
        # add some human-readable timing
        hours, rest = divmod(timediff, 3600)
        minutes, seconds = divmod(rest, 60)
        timediffstring = '{}h {}m {}s ago'.format(int(hours), int(minutes), int(seconds))
        hostinfo['last seen'] = Value(timediffstring)

        stat_db[host] = hostinfo
    return database


def add_or_update(value_dict):

    # make sure there is a 'host entry'. Fail otherwise.
    if not 'host' in value_dict.keys():
        return 'You need to specify a value for "host."'

    now = time.time()

    # Now add some mandatory stuff.
    value_dict['timestamp'] = now

    host = value_dict['host']
    # as host will act as a key, we do not need to keep him around.
    del value_dict['host']

    value_dict['id'] = 'id' + str(hashlib.md5(host).hexdigest())

    if 'update_rate' not in value_dict:
        value_dict['update_rate'] = DEFAULT_UPDATE_RATE
    else:
        if not isinstance(value_dict['update_rate'], int):
            value_dict['update_rate'] = DEFAULT_UPDATE_RATE

    # enable users to pass their icon. Set a default one if unset.
    if 'icon' not in value_dict:
        value_dict['icon'] = DEFAULT_ICON


    if host not in DB:
        DB[host] = {}

    for key, value in value_dict.iteritems():
        if key in DB[host]:
            DB[host][key].add(value)
        else:
            DB[host][key] = Value(value)


    #print value_dict
    print 'update:', DB
    # finally add host and data
#    DATA.add_kv(host, value_dict)
    return 'Your host {} was added.'.format(host)




class State:

    def GET(self):
        print "\n\n\n                 ### GET ###"
        html = web.template.frender('templates/stats.html', globals={"str": str, "type": type})
        print DB
        #return DB
        return html(updated_host_data(DB), STATS)
        #return html(DATA.historic(), DATA.stats())


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
