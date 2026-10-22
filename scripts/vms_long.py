#!/usr/bin/env python3
"""Capture full OpenVMS command output (no early '$' termination)."""
import pty, os, time, select, sys


def run_long(host, user, pw, cmd, settle=25):
    pid, fd = pty.fork()
    if pid == 0:
        os.execvp("telnet", ["telnet", host, "23"])

    def drain(deadline):
        out = b""
        while time.time() < deadline:
            r, _, _ = select.select([fd], [], [], 1.0)
            if r:
                try:
                    d = os.read(fd, 8192)
                except OSError:
                    break
                if not d:
                    break
                out += d
            else:
                wp, _ = os.waitpid(pid, os.WNOHANG)
                if wp != 0:
                    break
        return out.decode('ascii', errors='replace')

    time.sleep(2)
    os.write(fd, f"{user}\r\n".encode())
    time.sleep(1.5)
    drain(time.time() + 3)
    os.write(fd, f"{pw}\r\n".encode())
    time.sleep(2)
    drain(time.time() + 4)

    os.write(fd, f"{cmd}\r\n".encode())
    out = drain(time.time() + settle)

    try:
        os.write(fd, "LOGOUT\r\n".encode())
        time.sleep(1)
        os.close(fd)
    except OSError:
        pass
    return out


def fmt(o, tail=80):
    lines = []
    for l in o.replace('\r\n', '\n').replace('\r', '\n').split('\n'):
        ls = l.strip()
        if ls and '\x1b' not in l and 'NOTSET' not in ls and 'Unknown' not in ls \
           and 'SET-W' not in ls and 'SET-I' not in ls:
            lines.append(ls)
    return '\n'.join(lines[-tail:])


if __name__ == "__main__":
    host = sys.argv[1]
    cmd = sys.argv[2]
    pw = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("VMS_PW", "")
    settle = int(sys.argv[4]) if len(sys.argv) > 4 else 25
    print(f"=== {host}: {cmd} ===")
    print(fmt(run_long(host, "SYSTEM", pw, cmd, settle)))
