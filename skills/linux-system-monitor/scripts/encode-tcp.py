#!/usr/bin/env python3
# encode-tcp.py — count TCP connection states from /proc/net/tcp, emit JSON
import sys, json, glob, re

state_counts = {}
for path in ["/proc/net/tcp", "/proc/net/tcp6"]:
    try:
        with open(path) as f:
            for line in f.readlines()[1:]:  # skip header
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        state = "0x" + parts[3].strip()
                        state_counts[state] = state_counts.get(state, 0) + 1
                    except ValueError:
                        pass
    except IOError:
        pass
print(json.dumps(state_counts))
