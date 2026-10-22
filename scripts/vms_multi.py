#!/usr/bin/env python3
"""Run multiple OpenVMS DCL commands in a single PTY telnet session."""
import pty, os, time, select, sys


def run_many(host, user, pw, cmds, timeout=12):
    pid, fd = pty.fork()
    if pid == 0:
        os.execvp("telnet", ["telnet", host, "23"])

    def wait_for(pred, deadline):
        out = b""
        while time.time() < deadline:
            r, _, _ = select.select([fd], [], [], 0.5)
            if r:
                d = os.read(fd, 1024)
                out += d
                if pred(out):
                    break
            else:
                wp, _ = os.waitpid(pid, os.WNOHANG)
                if wp != 0:
                    break
        return out.decode('ascii', errors='replace')

    time.sleep(2)
    os.write(fd, f"{user}\r\n".encode())
    time.sleep(1.5)
    wait_for(lambda o: b"Password:" in o or b"Username:" in o, time.time() + 4)
    os.write(fd, f"{pw}\r\n".encode())
    time.sleep(2)
    banner = wait_for(lambda o: b"$" in o or b"Username:" in o, time.time() + 5)
    if "authorization failure" in banner.lower():
        os.write(fd, "exit\r\n".encode())
        os.close(fd)
        return {"__auth__": "AUTH_FAIL"}

    results = {}
    for cmd in cmds:
        os.write(fd, f"{cmd}\r\n".encode())
        out = wait_for(lambda o: b"$" in o, time.time() + timeout)
        time.sleep(1.5)
        try:
            out += os.read(fd, 8192).decode('ascii', errors='replace')
        except OSError:
            pass
        results[cmd] = out

    os.write(fd, "LOGOUT\r\n".encode())
    time.sleep(1)
    os.close(fd)
    return results


def fmt(o, tail=45):
    lines = []
    for l in o.replace('\r\n', '\n').replace('\r', '\n').split('\n'):
        ls = l.strip()
        if ls and '\x1b' not in l and 'NOTSET' not in ls and 'Unknown' not in ls \
           and 'SET-W' not in ls and 'SET-I' not in ls:
            lines.append(ls)
    return '\n'.join(lines[-tail:])


if __name__ == "__main__":
    host = sys.argv[1]
    pw = sys.argv[2]
    cmds = sys.argv[3:]
    res = run_many(host, "SYSTEM", pw, cmds)
    if "__auth__" in res:
        print("AUTH_FAIL")
    else:
        for cmd, out in res.items():
            print(f"\n>>> {cmd}")
            print(fmt(out) or "(no output)")
