#!/bin/bash
wireshark -r captured_packets.pcap -o tls.keylog_file:logs/20230726_234436_www.example.com/sessionkeys.txt