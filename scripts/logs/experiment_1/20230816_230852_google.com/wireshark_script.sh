#!/bin/bash
script_dir="$(dirname "$0")"
cd "$script_dir" || exit 1
echo "Current working directory: $(pwd)"

wireshark -r captured_packets.pcapng -o tls.keylog_file:sessionkeys.txt
