#!/usr/bin/env python3
"""Drive the SYSMAN utility on an OpenVMS node.

SYSMAN runs as a utility with its own command prompt, so the DCL prompt
synchroniser in vms_cmd.py cannot be used. This sends a list of SYSMAN
commands and captures the output between them.
"""
import os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vms_cmd import VMS


def run_sysman(host, pw, commands, settle=12):
    v = VMS(host, "SYSTEM", pw)
    if not v.login():
        return "AUTH_FAIL"

    # Enter SYSMAN
    v.buf = b""
    os.write(v.fd, b"RUN SYS$SYSTEM:SYSMAN\r\n")
    time.sleep(4)
    v._read(time.time() + 8)

    out = ""
    for cmd in commands:
        v.buf = b""
        os.write(v.fd, f"{cmd}\r\n".encode())
        time.sleep(2)
        out += v._read(time.time() + settle).decode('latin-1')

    try:
        os.write(v.fd, b"EXIT\r\n")
        time.sleep(1)
    except OSError:
        pass
    v.logout()
    return out


def clean(o, tail=120):
    lines = []
    for l in o.replace('\r\n', '\n').replace('\r', '\n').split('\n'):
        ls = l.strip()
        if ls and '\x1b' not in l and 'SET-I-UNKTERM' not in ls and 'SET-W' not in ls:
            lines.append(ls)
    return '\n'.join(lines[-tail:])


if __name__ == "__main__":
    host = sys.argv[1]
    pw = sys.argv[2]
    cmds = sys.argv[3:]
    print(f"=== {host} SYSMAN ===")
    print(clean(run_sysman(host, pw, cmds)))
