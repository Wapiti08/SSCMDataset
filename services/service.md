## Database Service -- MySql
sudo apt update
sudo apt install mysql-server

## DNSMasq Service ---- DNS
sudo apt-get update
sudo apt-get install dnsmasq


## Ubuntu
```
# find dnsmasq.conf file --- etc/dnsmasq.conf
# change configuration file according to pre-defined dnsmasq.conf

# add dnsmasq.hosts file --- etc/dnsmasq.hosts
# restart the service: sudo systemctl restart dnsmasq

# configure logging
sudo tail -f /var/log/syslog

```