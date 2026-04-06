#!/usr/bin/env python3
# encode-disks.py — read df -B1 output, emit JSON array
import sys, json
entries = []
for line in sys.stdin.read().splitlines():
    parts = line.split()
    if len(parts) >= 6:
        mount = parts[5]
        entries.append({
            "mount": mount.replace("/", "_") or "_root",
            "total": int(parts[1]) if parts[1].isdigit() else 0,
            "used": int(parts[2]) if parts[2].isdigit() else 0,
            "avail": int(parts[3]) if parts[3].isdigit() else 0,
            "use_pct": parts[4]
        })
print(json.dumps(entries))
