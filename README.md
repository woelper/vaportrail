# Welcome

PMC, or the Poor Man's Cloud, allows you to monitor and access all your devices running multiple OSes.

# Setup
## Client
Just start pmcClient.py.
Alternatively, create a systemd service by editing the provided sample
## Server
Just run setup_server.sh - all it will do is pull the submodule in git.
# SSH
If you want to manage mobile and LTE connected devices, an SSH tunnel can be beneficial. This software supports port forwarding to manage your devices remotely and securely.

in /etc/ssh/sshd_config, set:
GatewayPorts yes

