#!/bin/bash

echo "[*] Gather Basic System Information..."

uname -a
cat /etc/os-release
whoami
id
hostname

echo "[*] List Users & Groups"

cat /etc/passwd
cat /etc/group

echo "[*] Network Information"
ifconfig || ip a
netstat -tulnp