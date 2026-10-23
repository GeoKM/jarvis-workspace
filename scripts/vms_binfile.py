#!/usr/bin/env python3
"""Capture a binary VMS file with a fixed settle window (no prompt-wait).

CLUSTER_AUTHORIZE.DAT is full of NUL bytes, which confuse the '$' prompt
detection. This reads a fixed duration instead and saves the raw bytes.
"""
import os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vms_cmd import VMS

host = sys.argv[1]
spec = sys.argv[2]
outfile = sys.argv[3]
settle = float(sys.argv[4]) if len(sys.argv) > 4 else 25
pw = sys.argv[5] if len(sys.argv) > 5 else "4EFwFQ7tPdRzcKW"

v = VMS(host, "SYSTEM", pw)
if not v.login():
    print("AUTH_FAIL")
    sys.exit(1)

v.run("SET TERMINAL/PAGE=0", timeout=15)
v.run("SET NOON", timeout=10)

v.buf = b""
os.write(v.fd, f"TYPE {spec}\r\n".encode())
raw = v._read(time.time() + settle)
v.logout()

with open(outfile, "wb") as f:
    f.write(raw)

# Report the interesting non-zero region
data = raw.replace(b'\r\n', b'\n')
idx = data.find(b'{')
if idx >= 0:
    body = data[idx:]
    print(f"file bytes: {len(body)}")
    print("hex:", body[:48].hex())
else:
    print(f"captured {len(raw)} bytes, no data marker")
    print("raw head:", raw[:80])
