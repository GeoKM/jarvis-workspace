#!/usr/bin/env python3
# encode-logins.py — read 'last -n 3' output, emit JSON array
import sys, json
logins = []
for line in sys.stdin.read().splitlines():
    parts = line.split()
    if len(parts) >= 6:
        logins.append({"user": parts[0], "from": parts[2], "time": " ".join(parts[3:6])})
print(json.dumps(logins))
