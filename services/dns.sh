#!/bin/bash

# Update the package list
echo "Updating package list..."
sudo apt update

# Install BIND9 and related packages
echo "Installing BIND9..."
sudo apt install -y bind9 bind9utils bind9-doc

# Configure the main BIND configuration file
echo "Configuring BIND..."
sudo tee /etc/bind/named.conf.local > /dev/null <<EOF
zone "example.com" {
    type master;
    file "/etc/bind/db.example.com";
};
EOF

# Create the zone file
echo "Creating zone file..."
sudo tee /etc/bind/db.example.com > /dev/null <<EOF
;
; BIND data file for example.com
;
\$TTL    604800
@       IN      SOA     ns1.example.com. admin.example.com. (
                              2024012201         ; Serial
                              604800             ; Refresh
                              86400              ; Retry
                              2419200            ; Expire
                              604800 )           ; Negative Cache TTL
;
@       IN      NS      ns1.example.com.
ns1     IN      A       192.0.2.1
@       IN      A       192.0.2.1
www     IN      A       192.0.2.2
EOF

# Restart BIND to apply the configuration
echo "Restarting BIND9 service..."
sudo systemctl restart bind9

# Enable BIND9 to start on boot
echo "Enabling BIND9 to start on boot..."
sudo systemctl enable bind9

echo "DNS server setup is complete. You can test it using dig or nslookup."