#!/bin/bash
script_dir="$(dirname "$0")"cd "$script_dir" || exit 1wireshark -r captured_packets.pcapng -o tls.keylog_file:sessionkeys.txt