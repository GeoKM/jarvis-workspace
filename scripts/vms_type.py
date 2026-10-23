#!/usr/bin/env python3
"""Type a VMS text file with paging disabled and save it locally."""
import os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vms_cmd import VMS

host = sys.argv[1]
spec = sys.argv[2]
outfile = sys.argv[3]
pw = sys.argv[4] if len(sys.argv) > 4 else "4EFwFQ7tPdRzcKW"

v = VMS(host, "SYSTEM", pw)
if not v.login():
    print("AUTH_FAIL")
    sys.exit(1)

# Kill paging so long files stream through
v.run("SET TERMINAL/PAGE=0", timeout=20)
v.run("SET NOON", timeout=15)

v.buf = b""
os.write(v.fd, f"TYPE {spec}\r\n".encode())
out = v._read(time.time() + 40).decode('latin-1')
v.logout()

with open(outfile, "wb") as f:
    f.write(out.encode('latin-1', errors='replace'))
print(f"saved {len(out)} bytes to {outfile}")
