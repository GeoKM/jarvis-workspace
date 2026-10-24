#!/usr/bin/env python3
"""Read a VMS user record via the AUTHORIZE utility (interactive prompt).

AUTHORIZE.EXE prompts "Username or authorization identifier:" and then
prints that account's UAF record. This is the only reliable way to read
SYSUAF.DAT entries (the file itself is binary and PTY mangles it).
"""
import os, re, time, sys
from datetime import datetime, timedelta

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


MONTHS = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
          "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}


def parse_vms_date(s):
    """Parse a VMS date like '3-OCT-2026 20:55' into a datetime."""
    m = re.search(r"(\d{1,2})-([A-Z]{3})-(\d{4})(?:\s+(\d{1,2}):(\d{2}))?", s)
    if not m:
        return None
    d, mon, y = int(m.group(1)), m.group(2), int(m.group(3))
    hh = int(m.group(4) or 0)
    mm = int(m.group(5) or 0)
    return datetime(y, MONTHS.get(mon, 1), d, hh, mm)


def parse_lifetime(s):
    """Parse a VMS lifetime like '30 00:00' into (days, hh, mm)."""
    m = re.search(r"(\d+)\s+(\d{1,2}):(\d{2})", s)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def parse_expiry(text):
    """Extract password expiry info from an AUTHORIZE SHOW record."""
    out = {"pwdchange": None, "pwdlifetime": None, "expires": None,
           "days_remaining": None, "expired": False, "login_fails": None}

    m = re.search(r"Pwdchange:\s*(\S+)\s+(\d{2}:\d{2})", text)
    if m:
        out["pwdchange"] = parse_vms_date(f"{m.group(1)} {m.group(2)}")

    m = re.search(r"Pwdlifetime:\s*(\d+)\s+(\d{1,2}):(\d{2})", text)
    if m:
        out["pwdlifetime"] = (int(m.group(1)), int(m.group(2)), int(m.group(3)))

    m = re.search(r"Login Fails:\s*(\d+)", text)
    if m:
        out["login_fails"] = int(m.group(1))

    if out["pwdchange"] and out["pwdlifetime"]:
        d, hh, mm = out["pwdlifetime"]
        expires = out["pwdchange"] + timedelta(days=d, hours=hh, minutes=mm)
        out["expires"] = expires
        now = datetime.now()
        out["days_remaining"] = (expires - now).days
        out["expired"] = expires < now

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
    text = read_record(host, pw, ident, verb)
    if text == "AUTH_FAIL":
        print("AUTH_FAIL")
    else:
        print(f"=== {host} UAF record for {ident} ({verb}) ===")
        print(clean(text))
        if verb.upper() == "SHOW":
            print("\n--- password expiry ---")
            info = parse_expiry(text)
            for k, v in info.items():
                print(f"{k}: {v}")
