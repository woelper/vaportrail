import web
import time


# TODO : historical view - save state each time as list

urls = ("/add", "add", '/state', 'State', '/', 'State', '/request_port', 'request_port')
app = web.application(urls, globals())
hostDB = []
PORT = 20000

def boolify(s):
    if s == 'True':
        return True
    if s == 'False':
        return False
    raise ValueError("huh?")


def autoconvert(s):
    for fn in (boolify, int, float):
        try:
            return fn(s)
        except ValueError:
            pass
    return s


class State:
    def GET(self):
        print "---------------------------- Client state: --------------------"
        stat_db = []
        print hostDB
        for dict_item in hostDB:
            client_dict = {}
            for key in dict_item:
                if key == "time":
                    t = dict_item[key]
                    t = float(t)
                    now = time.time()
                    timediff = now - t
                    hours, rest = divmod(timediff,3600)
                    minutes, seconds = divmod(rest, 60)
                          #hrt = time.asctime( timediff )
                    timediffstring = " ".join([ str(int(hours)),"h", str(int(minutes)),"m", str(int(seconds)),"s"]) 
                    client_dict["last update"] = timediffstring
                else:
                    client_dict[key] = dict_item[key]

            stat_db.append(client_dict)
        hello = web.template.frender('templates/stats.html')
        return hello(stat_db)


class request_port:
    def GET(self):
        global PORT
        PORT += 1
        return PORT



class add:
    def __init__(self):
        test = "hallo"

    def update_Entry(self, dict, data, key, id='host'):
        r = 0
        for row in dict:
            if row[id] == key:
                dict[r] = data
            r += 1

    def GET(self):
        return "You must use POST. Sorry."

    def POST(self):
        data = web.input()
        add_entry = True
        update_entry = False

        # let's convert the strings to appropriate vars
        for key in data:
            data[key] = autoconvert(data[key])

            if key == "host":
                for entry in hostDB:
                    if entry[key] == data[key]:
                        # comment in for real deal
                        add_entry = False
                        update_entry = data[key]
                        # TODO: only update if ip and/or hostname exists
        
        if add_entry:
            hostDB.append(data)
        if update_entry:
            self.update_Entry(hostDB, data, update_entry)

        return data


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
