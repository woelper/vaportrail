# Vapor Trail

Got some live data you want visualized? You like uncomplicated stuff? Maybe this is for you. It's like Twitter(tm) for logging. 

Use cases:
 * Have some computers you want to monitor? Have a live view into their stats.
 * IOT (sorry, buzzword): Have your router, weather station or doorbell send data and graph it.
 * Sometimes, you want to log with a super high frequency - you might see anomalies that never show on long term stats. With traditional logging, this will spam your logs.
 * Instead of graphing values, graph events, like CPU above 70%.
 * Aggregate different stock values
 * You have a mixed OS environment behind routers? If your machines have SSH, they can tunnel out to a relay to have access to them. No more dyndns.
 * Setting up some Raspberry Pis to report any data periodically
 * Monitor the progress of some task
 * Your renderfarm / buildbots can output momentary data

Features:

* Automatic detection and display for incoming data. "Widgets" are selected based on data type.
* Sample client and example plugins included
* Client/Server model: Server logs, Server frontent displays, client reports
* The server is a central hub to access and monitor your machines
* Superfast charts: Canvas rendering delivers realtime updates of dynamic data
* given sufficient network speed rendering can happen at 60 fps
* Responsive modern UI
* Logging data is as easy as opening http://yourhost.com/add?host=mydevice&temperature=300&key=value

![](screenshots/livepreview.gif)

 Cut the bullshit:

 * In-memory time-series database server
 * JSON output
 * Client side data evaluation and graphing, custom high-speed graphing using canvas rendering
 * Auto-detects data type and selects display method (Float/int/string/location, more to come)

## Setup

### Server

For the python server, you need python (obviously) and web.py.
in the server/python directory, run python server.py <yourport>.

### Client 

Although any http capable tool can be used as client, there is a sample client provided to get you started and give you some ideas. It is located in the client directory. "generic_client.py" takes an optional hostname as argument (defaults to current hostname) and needs a server address to send data to. It comes with some plugins, such as:
```
├── base_plugin.py      (You can copy this and make your own)
├── cpu_live.py         (Based off cpu.py and has a high update rate)
├── cpu_peak.py         (Monitors peak CPU events)
├── cpu.py              (Periodically monitors CPU)
├── diskspace.py        (Monitors free disk space)
├── external_ip.py      (Gets your external IP)
├── machine_info.py     (Logs basic system info such as OS rev and # CPUs)
├── memory.py           (Logs free memory)
├── __sine.py           (For testing, logs sine wave)
├── ssh_tunnel.py       (Inits SSH tunnel so you can log in to your device)
└── uptime.py           (Logs uptime - who would've thought...)
```
The only thing you really need is a "host" identifier. Everything else is up to you.


## WIP:

* Android client support
* Rust server
* I get it, sometimes you want to keep old data around. Eventually, I will add redis support or something like that.
