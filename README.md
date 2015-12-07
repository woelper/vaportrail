# Welcome

PMC, or the Poor Man's Cloud, allows you to monitor and access all your devices running multiple OSes.

Features:

* Client runs on a variety of platforms
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

Dyndns / port forwarding does not work on most mobile / LTE networks. PMC with SSH does


## Planned:

* Android client support
* Arbitrary service monitoring
Clients can register any service, which is then monitored bey the server
* Historical diagrams

 
## Setup
### Client
Just start pmcClient.py.
Alternatively, create a systemd service by editing the provided sample
### Server
Just run setup_server.sh - all it will do is pull the submodule in git.
## SSH
If you want to manage mobile and LTE connected devices, an SSH tunnel can be beneficial. This software supports port forwarding to manage your devices remotely and securely.

in /etc/ssh/sshd_config, set:
GatewayPorts yes

