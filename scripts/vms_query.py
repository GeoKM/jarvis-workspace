#!/usr/bin/env python3
"""PTY-based VMS telnet session for reliable OpenVMS command output capture.

Raw telnetlib strips VMS output because the VAX node paginates and the
terminal type is unknown. Wrapping telnet in a PTY (pty.fork) forces a
real terminal session so DCL renders full output.
"""
import pty, os, time, select, sys


def run_vms_cmd(host, user, pw, cmd, timeout=15):
    pid, fd = pty.fork()
    if pid == 0:
        os.execvp("telnet", ["telnet", host, "23"])
    else:
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
            return "AUTH_FAIL"

        time.sleep(0.5)
        os.write(fd, f"{cmd}\r\n".encode())
        out = wait_for(lambda o: b"$" in o, time.time() + timeout)
        time.sleep(2)
        try:
            out += os.read(fd, 8192).decode('ascii', errors='replace')
        except OSError:
            pass

        os.write(fd, "LOGOUT\r\n".encode())
        time.sleep(1)
        os.close(fd)
        return out


def fmt(o):
    lines = []
    for l in o.replace('\r\n', '\n').replace('\r', '\n').split('\n'):
        ls = l.strip()
        if ls and '\x1b' not in l and 'NOTSET' not in ls and 'Unknown' not in ls \
           and 'SET-W' not in ls and 'SET-I' not in ls:
            lines.append(ls)
    return '\n'.join(lines[-60:])


if __name__ == "__main__":
    host = sys.argv[1]
    cmd = sys.argv[2] if len(sys.argv) > 2 else "SHOW CLUSTER /BRIEF"
    user = sys.argv[3] if len(sys.argv) > 3 else "SYSTEM"
    pw = sys.argv[4] if len(sys.argv) > 4 else "Uvd4hBrn7uZR63t"
    print(f"=== {host}: {cmd} ===")
    out = run_vms_cmd(host, user, pw, cmd)
    print(fmt(out) if out and out != "AUTH_FAIL" else (out or "(no output)"))
