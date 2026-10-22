#!/usr/bin/env python3
"""Read a VMS user record via the AUTHORIZE utility (interactive prompt).

AUTHORIZE.EXE prompts "Username or authorization identifier:" and then
prints that account's UAF record. This is the only reliable way to read
SYSUAF.DAT entries (the file itself is binary and PTY mangles it).
"""
import os, time, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vms_cmd import VMS


def read_record(host, pw, identifier, verb="SHOW"):
    v = VMS(host, "SYSTEM", pw)
    if not v.login():
        return "AUTH_FAIL"

    # Launch the AUTHORIZE utility
    v.buf = b""
    os.write(v.fd, b"RUN SYS$COMMON:[SYSEXE]AUTHORIZE.EXE\r\n")
    time.sleep(4)
    v._read(time.time() + 8)

    # Supply the AUTHORIZE command, e.g. "SHOW SYSTEM" / "LIST SYSTEM"
    v.buf = b""
    os.write(v.fd, f"{verb} {identifier}\r\n".encode())
    time.sleep(5)
    out = v._read(time.time() + 12).decode('latin-1')

    # Exit the utility
    try:
        os.write(v.fd, b"\r\n")
        time.sleep(1)
        v._read(time.time() + 3)
        os.write(v.fd, b"EXIT\r\n")
        time.sleep(1)
    except OSError:
        pass
    v.logout()
    return out


def clean(o, tail=70):
    lines = []
    for l in o.replace('\r\n', '\n').replace('\r', '\n').split('\n'):
        ls = l.strip()
        if ls and '\x1b' not in l and 'SET-I-UNKTERM' not in ls:
            lines.append(ls)
    return '\n'.join(lines[-tail:])


if __name__ == "__main__":
    host = sys.argv[1]
    pw = sys.argv[2]
    ident = sys.argv[3] if len(sys.argv) > 3 else "SYSTEM"
    verb = sys.argv[4] if len(sys.argv) > 4 else "SHOW"
    print(f"=== {host} UAF record for {ident} ({verb}) ===")
    print(clean(read_record(host, pw, ident, verb)))
