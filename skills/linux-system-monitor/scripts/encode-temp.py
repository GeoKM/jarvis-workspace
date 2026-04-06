#!/usr/bin/env python3
# encode-temp.py — read thermal zones, emit JSON
import json, glob

zones = {}
for path in sorted(glob.glob("/sys/class/thermal/thermal_zone*")):
    try:
        zone_name = path.split("/")[-1]
        temp_milli = int(open(f"{path}/temp").read())
        zones[zone_name] = temp_milli / 1000.0
    except (IOError, ValueError):
        pass
print(json.dumps(zones))
