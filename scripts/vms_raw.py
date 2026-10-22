#!/usr/bin/env python3
"""Run a VMS command and save the RAW captured bytes to a local file.

Needed for binary VMS files (e.g. CLUSTER_AUTHORIZE.DAT) so they can be
analysed with local tools (strings etc.) without terminal mangling.
"""
import pty, os, time, select, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vms_cmd import VMS

host = sys.argv[1]
cmd = sys.argv[2]
outfile = sys.argv[3]
pw = sys.argv[4] if len(sys.argv) > 4 else os.environ.get("VMS_PW", "")

v = VMS(host, "SYSTEM", pw)
if not v.login():
    print("AUTH_FAIL")
    sys.exit(1)
out = v.run(cmd, timeout=40)
with open(outfile, "wb") as f:
    f.write(out.encode('latin-1', errors='replace'))
v.logout()
print(f"saved {len(out)} bytes to {outfile}")
