#!/bin/bash

sudo -l
find / -writable -type d 2>/dev/null


echo "[*]Scan for Internal Network Device"
nmap -sP 192.168.1.0/24
fping -g 192.168.1.0/24

echo "[*]check valid credentials"
cat ~/.ssh/id_rsa
ssh-add -L