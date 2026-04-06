#!/usr/bin/env python3
# encode-net.py — read /sys/class/net/*/statistics files, emit JSON
import json, glob

ifaces = {}
for path in glob.glob("/sys/class/net/*"):
    iface = path.split("/")[-1]
    try:
        ifaces[iface] = {
            "rx_bytes": int(open(f"{path}/statistics/rx_bytes").read()),
            "tx_bytes": int(open(f"{path}/statistics/tx_bytes").read()),
            "rx_err": int(open(f"{path}/statistics/rx_errs").read()),
            "tx_err": int(open(f"{path}/statistics/tx_errs").read()),
            "rx_drop": int(open(f"{path}/statistics/rx_dropped").read()),
            "tx_drop": int(open(f"{path}/statistics/tx_dropped").read()),
        }
    except (IOError, ValueError):
        pass
print(json.dumps(ifaces))
