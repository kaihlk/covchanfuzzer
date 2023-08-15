#!/bin/bash
wireshark -r captured_packets.pcapng -o tls.keylog_file:sessionkeys.txt