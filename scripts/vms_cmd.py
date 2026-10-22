#!/usr/bin/env python3
"""OpenVMS DCL command runner with proper prompt synchronisation.

Raw telnetlib and naive PTY reads lose commands because they are typed
before the DCL prompt is ready. This waits for the '$' prompt between
every command so each command's output is captured cleanly.
"""
import pty, os, time, select, sys


class VMS:
    def __init__(self, host, user="SYSTEM", pw=None, port=23):
        self.host, self.user, self.pw, self.port = host, user, pw, port
        self.pid, self.fd = pty.fork()
        if self.pid == 0:
            os.execvp("telnet", ["telnet", host, str(port)])
        self.buf = b""

    def _read(self, deadline):
        while time.time() < deadline:
            r, _, _ = select.select([self.fd], [], [], 0.5)
            if r:
                try:
                    d = os.read(self.fd, 8192)
                except OSError:
                    break
                if not d:
                    break
                self.buf += d
            else:
                wp, _ = os.waitpid(self.pid, os.WNOHANG)
                if wp != 0:
                    break
        return self.buf

    def wait_prompt(self, timeout=30):
        """Wait until a '$' DCL prompt appears at the tail of the buffer.

        Returns the captured buffer text (does NOT clear it) so callers
        can read the command output. Caller is responsible for clearing.
        """
        deadline = time.time() + timeout
        while time.time() < deadline:
            self._read(min(deadline, time.time() + 1.0))
            tail = self.buf.rstrip(b" \t\r\n\x00")
            if tail.endswith(b"$"):
                return self.buf.decode('latin-1')
        return self.buf.decode('latin-1')

    def login(self, timeout=30):
        deadline = time.time() + timeout
        # wait for Username:
        while time.time() < deadline:
            self._read(min(deadline, time.time() + 1.0))
            if b"Username:" in self.buf:
                break
        self.buf = b""
        os.write(self.fd, f"{self.user}\r\n".encode())
        time.sleep(1.5)
        self.buf = b""
        while time.time() < deadline:
            self._read(min(deadline, time.time() + 1.0))
            if b"Password:" in self.buf:
                break
        self.buf = b""
        os.write(self.fd, f"{self.pw}\r\n".encode())
        time.sleep(2)
        # Capture the post-password banner BEFORE wait_prompt clears the buffer
        deadline = time.time() + 20
        while time.time() < deadline:
            self._read(min(deadline, time.time() + 1.0))
            if b"$" in self.buf or b"Username:" in self.buf:
                break
        banner = self.buf.decode('latin-1')
        if "authorization failure" in banner.lower():
            return False
        self.wait_prompt(timeout=20)
        self.buf = b""
        return True

    def run(self, cmd, timeout=25):
        self.buf = b""
        os.write(self.fd, f"{cmd}\r\n".encode())
        out = self.wait_prompt(timeout=timeout)
        # HELP (and some SHOW commands) drop into a "Subtopic?" prompt.
        # A bare RETURN backs out to the DCL prompt so the next command
        # is not swallowed as a subtopic query.
        tail = out.rstrip(" \t\r\n\x00")
        if tail.endswith("?"):
            os.write(self.fd, b"\r\n")
            out += self.wait_prompt(timeout=timeout)
        self.buf = b""
        return out

    def logout(self):
        try:
            os.write(self.fd, b"LOGOUT\r\n")
            time.sleep(1)
            os.close(self.fd)
        except OSError:
            pass


def clean(o, tail=60):
    lines = []
    for l in o.replace('\r\n', '\n').replace('\r', '\n').split('\n'):
        ls = l.strip()
        if ls and 'SET-I-UNKTERM' not in ls and 'NOTSET' not in ls \
           and '\x1b' not in ls:
            lines.append(ls)
    return '\n'.join(lines[-tail:])


if __name__ == "__main__":
    host = sys.argv[1]
    pw = sys.argv[2]
    cmds = sys.argv[3:]
    v = VMS(host, "SYSTEM", pw)
    if not v.login():
        print("AUTH_FAIL")
        sys.exit(1)
    for c in cmds:
        out = v.run(c, timeout=40)
        print(f"\n>>> {c}")
        print(clean(out) or "(empty)")
    v.logout()
