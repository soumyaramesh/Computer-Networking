#!/bin/bash
sudo iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP
sudo python ECRawSockets.py $1
