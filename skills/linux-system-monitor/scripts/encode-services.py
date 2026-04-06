#!/usr/bin/env python3
# encode-services.py — check which of the given services are active, emit JSON dict
import subprocess, json, sys

services = sys.argv[1:] if len(sys.argv) > 1 else ["ssh", "sshd", "systemd-journald", "ntp", "ntpd", "chrony", "chronyd", "docker"]
active = {}
for svc in services:
    r = subprocess.run(["systemctl", "is-active", svc], capture_output=True, text=True)
    if r.stdout.strip() == "active":
        active[svc] = "up"
print(json.dumps(active))
