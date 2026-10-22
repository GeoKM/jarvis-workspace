#!/usr/bin/env python3
"""Capture the OpenVMS telnet login banner (no auth needed)."""
import pty, os, time, select, sys

def banner(host, port=23, wait=6):
    pid, fd = pty.fork()
    if pid == 0:
        os.execvp("telnet", ["telnet", host, str(port)])
    out = b""
    deadline = time.time() + wait
    while time.time() < deadline:
        r, _, _ = select.select([fd], [], [], 0.5)
        if r:
            try:
                out += os.read(fd, 4096)
            except OSError:
                break
    try:
        os.write(fd, b"\x03")
        os.close(fd)
    except OSError:
        pass
    return out.decode('ascii', errors='replace')

for host in sys.argv[1:]:
    b = banner(host)
    clean = []
    for l in b.replace('\r\n', '\n').replace('\r', '\n').split('\n'):
        ls = l.strip()
        if ls and '\x1b' not in l:
            clean.append(ls)
    print(f"=== {host} ===")
    print('\n'.join(clean[:25]) or "(no banner)")
    print()
