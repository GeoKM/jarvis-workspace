#!/usr/bin/env python3
# encode-containers.py — merge docker ps (name|status) + docker stats (name|cpu|mem), emit JSON array
import sys, json

# First stdin: docker ps --format '{{.Name}}|{{.Status}}'
# Second argument: docker stats --format '{{.Name}}|{{.CPUPerc}}|{{.MemPerc}}' (optional)
ps_lines = sys.stdin.read().splitlines()
stats_lines = sys.argv[1:] if len(sys.argv) > 1 else []

# Build stats lookup: name -> {cpu, mem}
stats_map = {}
for line in stats_lines:
    p = line.split("|")
    if len(p) >= 3:
        stats_map[p[0].strip()] = {"cpu": p[1].strip(), "mem": p[2].strip()}

containers = []
for line in ps_lines:
    p = line.split("|")
    if len(p) >= 2 and p[0].strip():
        name = p[0].strip()
        stats = stats_map.get(name, {"cpu": "n/a", "mem": "n/a"})
        containers.append({
            "name": name,
            "status": p[1].strip(),
            "cpu": stats["cpu"],
            "mem": stats["mem"]
        })

print(json.dumps(containers))
