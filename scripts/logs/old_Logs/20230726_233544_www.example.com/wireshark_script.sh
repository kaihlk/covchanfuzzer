#!/bin/bash
wireshark -r logs/20230726_233544_www.example.com/captured_packets.pcap -o tls.keylog_file:logs/20230726_233544_www.example.com/sessionkeys.txt