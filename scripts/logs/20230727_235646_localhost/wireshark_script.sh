#!/bin/bash
wireshark -r captured_packets.pcap -o tls.keylog_file:sessionkeys.txt