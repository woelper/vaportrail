# Welcome

PMC, or the Poor Man's Cloud, allows you to monitor and access all your devices running multiple OSes.

Just imagine something like New Relic (tm) in underpants. Or don't.

Features:

* Client runs on a variety of platforms. Since it uses POST, this means almost any platforms running python or curl.
* Client can be run as a daemon
* The server is a central hub to access and monitor your machines
* With any publicly-accessible ssh server, PMC manages port forwarding so your machines remain accessible


> Yet another of those tools - I don't get the point.

There are a lot of great tools that monitor your servers. PMC is unique in those aspects:
 
* It tries to be OS agnostic. At least the client only will require python 2.7 with no extra modules.
* You have a mixed OS environment behind routers? If your machines have SSH, they can tunnel out to a relay to have access to them.

> Isn't the tunnel functionality a security issue?

Not if you have passwordless SSH set up and a strong key.

> I use dyndns and I am happy. Why should I bother?

Dyndns is not automatic (try to add several hosts behind your router) and does not scale well.

Dyndns / port forwarding does not work on most mobile / LTE networks. PMC with SSH does.

> So what exactly is this for?

This is meant as a toolbox rather than a complete package. Some apllications could include:

Setting up some Raspberry Pis to report any data periodically

Leave your workstation at home running, allowing you to log in later

Add some servers / NAS / routers together with service output to monitor health of your hardware or software

## Planned:

* Android client support
* Better arbitrary service monitoring
Clients can register any service, which is then monitored by the server
* Maybe historical diagrams or logging

 
## Setup

### Server
Just run setup_server.sh - all it will do is pull the submodule in git.

### Client

In the simplest form, you can use anything that understands POST, such as curl:
`curl --data "host=testmachine2&ip=10.10.0.12" http://localhost:8080/add`

The only thing you really need is a "host" identifier. Everything else is up to you.

Alternatively, a sample client program has been supplied that stays active in a loop and provides basic system info without any non-standard modules. In Addition, it is able to create an SSH tunnel and make it known to the server.

There is a basic systemd service file to get you started if you happen to run systemd.


## SSH
If you want to manage mobile and LTE connected devices, an SSH tunnel can be beneficial. This software supports port forwarding to manage your devices remotely and securely.

in /etc/ssh/sshd_config, set:
GatewayPorts yes

