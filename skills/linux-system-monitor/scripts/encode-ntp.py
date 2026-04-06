#!/usr/bin/env python3
# encode-ntp.py — check NTP offset, emit JSON
import subprocess, json

# Try chronyc first
r = subprocess.run(["chronyc", "tracking"], capture_output=True, text=True)
offset_ms = None
if r.returncode == 0:
    for line in r.stdout.splitlines():
        if "Last offset" in line:
            try:
                offset_ms = float(line.split()[-1]) * 1000
                break
            except ValueError:
                pass

# Fall back to timedatectl
if offset_ms is None:
    r = subprocess.run(["timedatectl", "show", "-p", "NTPSynchronized", "--value"],
                      capture_output=True, text=True)
    if r.stdout.strip() == "yes":
        offset_ms = 0.0

print(json.dumps(offset_ms))
