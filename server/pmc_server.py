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
urls = ("/", "State" ,"/add", "add", '/request_port', 'request_port', '/dump', 'Dump', '/dash', 'Dashboard')

app = web.application(urls, globals())
PORT = 20000
DEFAULT_UPDATE_RATE = 1000
DEFAULT_ICON = 'fa-server'

def is_list_of_pure_type(list_, type_):
    # bool is instance of int in python
    if type_ == int:
        if any([isinstance(l, bool) for l in list_]):
            return False
    return all([isinstance(l, type_) for l in list_])

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

    # No need to convert if it is already it's own type.
    if not isinstance(s, str) and not isinstance(s, unicode):
        return s

    for fn in (boolify, int, float):
        try:
            #print s, fn(s)
            return fn(s)
        except ValueError:
            pass
    return str(s)


def human_timediff(timestamp):
    now = time.time()
    timediff = now - timestamp
    #print now, timestamp
    hours, rest = divmod(timediff, 3600)
    minutes, seconds = divmod(rest, 60)

    if hours != 0:
        return '{}h {}m {}s'.format(int(hours), int(minutes), int(seconds))
    else:
        if minutes != 0:
            return '{}m {}s'.format(int(minutes), int(seconds))
        else:
            return '{}s'.format(int(seconds))
    # return timediff
    # return '{}h {}m {}s ago'.format(int(hours), int(minutes), int(seconds))


class Value(object):
    """
    Simple value class with history support.
    """
    def __init__(self, val=None):
        self.values = []
        self.timestamps = []
        self.deltatimes = []
        self.max_values = 45
        self.latest = None
        self.graphable = False
        if val is not None:
            self.add(val)

    def refresh(self):
        self.deltatimes = [human_timediff(t) for t in self.timestamps]
        #print self.deltatimes
        #self.deltatimes = self.timestamps


    def add(self, value):
        now = time.time()
        #value = autoconvert(value)
        self.latest = value
        self.values = [value] + self.values
        self.timestamps = [now] + self.timestamps

        if len(self.values) > self.max_values:
            self.values.pop()
        if len(self.timestamps) > self.max_values:
            self.timestamps.pop()

        #self.deltatimes = [human_timediff(t) for t in self.timestamps]
        
        if is_list_of_pure_type(self.values, int) or is_list_of_pure_type(self.values, float):
            self.graphable = True

    def __repr__(self):
        return 'VALUE OBJECT ' + str(self.values)


    def deserialize(self, list_of_values, list_of_timestamps):
        self.values = list_of_values
        self.timestamps = list_of_timestamps
        self.latest = list_of_values[0]
        if is_list_of_pure_type(self.values, int) or is_list_of_pure_type(self.values, float):
            self.graphable = True
        

    def serialize(self):
        return [self.values, self.timestamps, self.graphable]


class DataBase():
    def __init__(self):
        self.data = {}
        self.stats = {'updates': 0, 'values': 0}
        self.location = 'dump.db'

    def save(self):
        print '\n\nSAVING'
        #print self.data
        serialized_data = {}

        for key, value in self.data.iteritems():
            serialized_data[key] = {k: v.serialize() for k, v in value.iteritems()}

        with open(self.location, 'w') as f:
            json.dump(serialized_data, f, indent=4)

    def load(self):
        if os.path.isfile(self.location):
            with open(self.location) as f:
                dump_dict = json.load(f)
            print 'LOADED DICT', dump_dict
            for host, values in dump_dict.iteritems():
                #dump_dict[host] = {k: Value(v) for k, v in values.iteritems()}
                for vname, vlist in values.iteritems():
                    v = Value()
                    v.deserialize(vlist[0], vlist[1])
                    
                    values[vname] = v
            self.data = dump_dict

    def serialize(self, keyfilter=None):
        #print 'DUMPING JSON'
        serialized_data = {}

        #for key, value in self.data.iteritems():
        for key, value in self.updated_host_data(solo=keyfilter).iteritems():
            serialized_data[key] = {k: v.serialize() for k, v in value.iteritems()}
        return serialized_data


    def updated_host_data(self, solo=None):
        """
        return up-to date data for display.
        this should go into the database class later
        """

        # TODO: make this a little leaner
        for host, hostinfo in self.data.iteritems():
            if solo is not None:
                if host != solo:
                    continue

            # The timing logic
            now = time.time()
            #print 'latest:', hostinfo['timestamp'].latest
            latest_stamp = float(hostinfo['timestamp'].latest)
            timediff = now - latest_stamp
#            timediff = now - float(hostinfo['timestamp'].latest)


            if timediff > hostinfo['update_rate'].latest:
                hostinfo['inactive'] = Value(True)
            else:
                hostinfo['inactive'] = Value(False)

            hostinfo['last seen'] = Value(human_timediff(latest_stamp))
            #hostinfo['last seen'] = Value(timediffstring)

            for val in hostinfo.itervalues():
                #pass
                val.refresh()
            #self.deltatimes = [human_timediff(t) for t in self.timestamps]

        return self.data


    def add_or_update(self, value_dict):


        value_dict = {k: autoconvert(v) for (k, v) in value_dict.iteritems()}


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
            # set default update rat if not given
            value_dict['update_rate'] = DEFAULT_UPDATE_RATE
        else:
            value_dict['update_rate'] = autoconvert(value_dict['update_rate'])
            if not isinstance(value_dict['update_rate'], int):
                value_dict['update_rate'] = DEFAULT_UPDATE_RATE

        # enable users to pass their icon. Set a default one if unset.
        if 'icon' not in value_dict:
            value_dict['icon'] = DEFAULT_ICON

        if host not in self.data:
            self.data[host] = {}

        for key, value in value_dict.iteritems():
            if key in self.data[host]:
                self.stats['values'] += 1
                self.data[host][key].add(value)
            else:
                self.data[host][key] = Value(value)
                self.stats['values'] += 1

        #print 'update:', self.data
        self.stats['updates'] += 1
        return 'Your host {} was added.'.format(host)



DB = DataBase()
# Right now, this is the only point where we read from the disk. Once at startup.
DB.load()



class State:

    def GET(self):
        print "\n\n\n                 ### GET ###"
        html = web.template.frender('templates/stats.html', globals={"str": str, "type": type})
        #return DB
        return html(DB.updated_host_data(), DB.stats)
        #return html(DATA.historic(), DATA.stats())

class Dashboard:
    def GET(self):
        html = web.template.frender('templates/dash.html', globals={"str": str, "type": type})
        return html(DB.updated_host_data(), DB.stats)
    

class request_port:
    def GET(self):
        global PORT
        PORT += 1
        return PORT

class Dump:
    
    @staticmethod
    def GET():
        data = dict(web.input())
        web.header('Content-Type', 'application/json')
        try:
            host = data['host']
            d = DB.serialize()[host]
            return json.dumps(d)
        except Exception as e:
            return json.dumps(DB.serialize())
            #return DB.serialize()


class add:

    """
    Adds a host with associated data. Right now, this is also the entry point fo
    saving the database to disk. Once, this thing should not save at all, but so what. 
    The server should run off memory as much as possible, so this just triggers when new
    hosts are added.
    """
    def add_host(self, data):
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
