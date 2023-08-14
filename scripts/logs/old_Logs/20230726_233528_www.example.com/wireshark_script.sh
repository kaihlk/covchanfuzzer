#!/bin/bash
wireshark -r logs/20230726_233528_www.example.com/captured_packets.pcap -o tls.keylog_file:logs/20230726_233528_www.example.com/sessionkeys.txt