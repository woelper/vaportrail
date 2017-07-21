#!/usr/bin/env python
import time
import sys
import os
import hashlib
import json

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
urls = ("/", "Frontend" ,"/add", "add", '/request_port', 'request_port', '/dump', 'Dump', '/save', 'Save')

app = web.application(urls, globals())

def is_list_of_pure_type(list_, type_):
    # bool is instance of int in python
    if type_ == int:
        if any([isinstance(l, bool) for l in list_]):
            return False
    return all([isinstance(l, type_) for l in list_])

def boolify(string):
    """
    convert string to either True or False
    """
    if string == 'True':
        return True
    if string == 'False':
        return False
    raise ValueError("could not convert string to bool")

def autoconvert(string):
    """
    Convert a string to the most probable native type
    """

    # No need to convert if it is already it's own type.
    if not isinstance(string, str) and not isinstance(string, unicode):
        return string

    for fn in (boolify, int, float):
        try:
            #print s, fn(s)
            return fn(string)
        except ValueError:
            pass
    return str(string)


class Value(object):
    """
    Simple value class with history support.
    """
    def __init__(self, val=None, keyname=None):
        self.values = []
        self.timestamps = []
        self.max_values = 45
        self.annotation = 'undetected'
        self.uniform = False
        if keyname is not None:
            self.keyname = keyname
        if val is not None:
            self.add(val)

    def annotate(self, value):

        # === geo coordinate pair
        if isinstance(value, str):
            # ISO 6709 '+010000.0+0010000.0/'
            if value.startswith('-') or value.startswith('+') or value.endswith('/'):
                return 'location'
            if value.startswith('-') or value.startswith('+'):
                return 'location'

            if self.keyname == 'location' or self.keyname == 'position':
                return 'location'


        # if it's not some self-defined type, return the native type
        return type(value).__name__

    def add(self, value):
        now = time.time()
        self.values = [value] + self.values
        self.timestamps = [now] + self.timestamps

        # Throw away the oldest
        if len(self.values) > self.max_values:
            self.values.pop()
        if len(self.timestamps) > self.max_values:
            self.timestamps.pop()

        # Are all values coherent? maybe leave this to a client to judge?
        if is_list_of_pure_type(self.values, int) or is_list_of_pure_type(self.values, float):
            self.uniform = True

        self.annotation = self.annotate(value)

    def __repr__(self):
        return 'VALUE OBJECT ' + str(self.values)

    def deserialize(self, list_of_values, list_of_timestamps):
        self.values = list_of_values
        self.timestamps = list_of_timestamps
        if is_list_of_pure_type(self.values, int) or is_list_of_pure_type(self.values, float):
            self.uniform = True

    def serialize(self):
        return self.__dict__


class DataBase():
    def __init__(self):
        self.data = {}
        self.stats = {'updates': 0, 'values': 0}
        self.location = 'dump.db'

    def save(self):
        """
        Super simple JSON save method
        """
        print '\n\nSAVING'
        with open(self.location, 'w') as f:
            json.dump(self.serialize(), f, indent=4)
            return 'OK'

    def load(self):
        """
        Super simple JSON save method
        """
        if os.path.isfile(self.location):
            with open(self.location) as f:
                dump_dict = json.load(f)
            print 'LOADED DICT', dump_dict
            for host, values in dump_dict.iteritems():
                for vname, vlist in values.iteritems():
                    v = Value()
                    v.deserialize(vlist['values'], vlist['timestamps'])
                    values[vname] = v
            self.data = dump_dict

    def serialize(self, keyfilter=None):
        serialized_data = {}

        for key, value in self.data.iteritems():
            # if keyfilter is not None:
            if keyfilter is not None and key != keyfilter:
                continue

            serialized_data[key] = {k: v.serialize() for k, v in value.iteritems()}
        serialized_data['stats'] = self.stats
        return serialized_data



    def add_or_update(self, value_dict):


        value_dict = {k: autoconvert(v) for (k, v) in value_dict.iteritems()}

        # make sure there is a 'host entry'. Fail otherwise.
        if not 'host' in value_dict.keys():
            return 'You need to specify a value for "host."'

        host = value_dict['host']
        # as host will act as a key, we do not need to keep him around.
        del value_dict['host']

        if host not in self.data:
            self.data[host] = {}

        for key, value in value_dict.iteritems():
            if key in self.data[host]:
                self.stats['values'] += 1
                self.data[host][key].add(value)
            else:
                self.data[host][key] = Value(value, key)
                self.stats['values'] += 1

        self.stats['updates'] += 1
        return 'Your host {} was added.'.format(host)


DB = DataBase()
# Right now, this is the only point where we read from the disk. Once at startup.
DB.load()



class Frontend:

    def GET(self):
        # Right now this is symlinked to the frontend.
        # Works on Mac/Linux/Windows+Ubuntu subsystem, dunno about vanilla windows.
        raise web.seeother('static/frontend/index.html')



class Dump:

    @staticmethod
    def GET():
        data = dict(web.input())
        web.header('Content-Type', 'application/json')

        """
        Let's make that easy to use for clients from other ports.
        Comment if you think that's unsafe.
        """
        web.header('Access-Control-Allow-Origin', '*')

        """
        If the query contains a 'host' value to limit the scope,
        return just that. Otherwise return all.
        """
        try:
            host = data['host']
            d = DB.serialize()[host]
            return json.dumps(d)
        except Exception as e:
            return json.dumps(DB.serialize())


class Save:
    def GET(self):
        return DB.save()


class add:

    """
    Adds a host with associated data.
    """
    def add_host(self, data):
        # TODO add more sanity checks here
        if 'host' in data.keys():
            if data['host'] != '':
                return DB.add_or_update(data)
        return 'Host must be given and not an empty string.'

    def GET(self):
        """
        Let's support GET, too. No checking as of yet.
        """
        data = dict(web.input())
        return self.add_host(data)

    def POST(self):
        data = dict(web.input())
        return self.add_host(data)


if __name__ == "__main__":
    app.run()
