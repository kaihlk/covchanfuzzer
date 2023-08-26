#!/bin/bash
script_dir="$(dirname "$0")"
cd "$script_dir" || exit 1
wireshark -r captured_packets.pcapng -o tls.keylog_file:sessionkeys.txt