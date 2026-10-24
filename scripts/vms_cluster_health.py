#!/usr/bin/env python3
"""VAXcluster health check for FUSION/RISE (OpenVMS VAX V7.3).

Checks that actually work on this V7.3 image:
  - reachability + telnet
  - cluster interconnect controllers (MUA1/MUA2/MUA3 on RISE, PEA0 on FUSION)
  - cluster disk mounts (FUSION$DUA0:, RISE$DUA0:)
  - cluster server processes (CLUSTER_SERVER, CACHE_SERVER, CONFIGURE, LANACP, IPCACP)
  - OPCOM log scan for node loss / deactivation events
  - CLUSTER_AUTHORIZE.DAT group number + hash match across nodes

NOTE: `SHOW CLUSTER` is NOT used - it returns %SYSTEM-F-NOPRIV on this image
because SHOW.EXE has no cluster action compiled in. Do not use it as a health
signal; it is a red herring.
"""
import os
import re
import subprocess
import sys
import time
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vms_cmd import VMS
from vms_uaf import parse_expiry, read_record

NODES = {
    "FUSION": {"ip": "192.168.1.137"},
    "RISE": {"ip": "192.168.1.138"},
}
PW = os.environ.get("VMS_SYSTEM_PW", "4EFwFQ7tPdRzcKW")

# Warn when the SYSTEM password is within this many days of expiry.
PASSWORD_WARN_DAYS = 14

CLUSTER_PROCS = ["CLUSTER_SERVER", "CACHE_SERVER", "CONFIGURE", "LANACP", "IPCACP"]

# OPCOM events that indicate cluster trouble
BAD_EVENTS = [
    "lost connection to node",
    "is deactivating",
    "has been removed from the VAXcluster",
    "placing node in DEPARTED state",
    "has been disabled, username",
]
GOOD_EVENTS = [
    "has been enabled, username",
    "is activating",
    "membership request from node",
    "placing node in ACTIVE state",
    "Load succeeded for",
]


def ping(ip):
    try:
        r = subprocess.run(["ping", "-c", "2", "-W", "2", ip],
                           capture_output=True, text=True, timeout=10)
        return "0% packet loss" in r.stdout
    except Exception:
        return False


def telnet_open(ip):
    try:
        r = subprocess.run(["timeout", "3", "bash", "-c", f"echo > /dev/tcp/{ip}/23"],
                           capture_output=True, timeout=6)
        return r.returncode == 0
    except Exception:
        return False


def clean(txt):
    lines = []
    for l in txt.replace('\r\n', '\n').replace('\r', '\n').split('\n'):
        ls = l.strip()
        if ls and '\x1b' not in l and 'SET-I-UNKTERM' not in ls and 'SET-W' not in ls:
            lines.append(ls)
    return lines


def run_commands(ip, cmds, timeout=40):
    """Run a list of DCL commands in one session. Returns list of output strings."""
    v = VMS(ip, "SYSTEM", PW)
    if not v.login():
        return None
    out = []
    for c in cmds:
        out.append(v.run(c, timeout=timeout))
    v.logout()
    return out


def check_node(name, ip):
    res = {
        "node": name, "ip": ip,
        "ping": ping(ip),
        "telnet": telnet_open(ip),
        "errors": [],
        "warnings": [],
    }

    if not res["ping"]:
        res["errors"].append("ICMP unreachable")
        return res
    if not res["telnet"]:
        res["errors"].append("telnet port 23 closed")
        return res

    outs = run_commands(ip, [
        "SET NOON",
        "SET PROCESS/PRIVILEGE=(CMKRNL,OPER,SYSPRV)",
        "SHOW SYSTEM",
        "SHOW DEVICE DUA0:",
        "SHOW DEVICE MUA1:",
        "SHOW DEVICE MUA2:",
        "SHOW DEVICE MUA3:",
    ])
    if outs is None:
        res["errors"].append("authentication failed")
        return res

    sysout = outs[2]
    lines = clean(sysout)

    # Uptime
    m = re.search(r"Uptime\s+(\d+)\s+(\d+):(\d+):(\d+)", "\n".join(lines))
    if m:
        days, hh, mm, ss = m.groups()
        res["uptime"] = f"{days}d {int(hh):02d}:{mm}:{ss}"
    else:
        res["uptime"] = "unknown"

    # Cluster processes present?
    present = []
    for p in CLUSTER_PROCS:
        if any(re.search(rf"\b{p}\b", l) for l in lines):
            present.append(p)
    res["cluster_procs"] = present
    missing = [p for p in CLUSTER_PROCS if p not in present]
    if missing:
        res["warnings"].append(f"cluster process(es) not found: {', '.join(missing)}")

    # Interconnect (MUA*) status
    muas = []
    for idx in (4, 5, 6):
        for l in clean(outs[idx]):
            mm2 = re.search(r"(\S+\$MUA\d):\s+(\w+)\s+(\d+)", l)
            if mm2:
                muas.append({"dev": mm2.group(1), "status": mm2.group(2),
                             "errors": int(mm2.group(3))})
    res["interconnect"] = muas
    offline = [m for m in muas if m["status"].lower() != "online"]
    if offline:
        res["errors"].append("interconnect offline: " +
                             ", ".join(f"{m['dev']}={m['status']}" for m in offline))
    errd = [m for m in muas if m["errors"] > 0]
    if errd:
        res["warnings"].append("interconnect error count >0: " +
                               ", ".join(f"{m['dev']}({m['errors']})" for m in errd))

    # Cluster disk mounts
    mounts = []
    for l in clean(outs[3]):
        mm3 = re.match(r"(\S+\$DUA0):\s+(\w+)\s+\d+\s+(\S+)\s+(\d+)\s+(\d+)\s+(\d+)", l)
        if mm3:
            mounts.append({"dev": mm3.group(1), "status": mm3.group(2),
                           "label": mm3.group(3), "free": int(mm3.group(4)),
                           "trans": int(mm3.group(5)), "mnt": int(mm3.group(6))})
    res["mounts"] = mounts
    for mo in mounts:
        if mo["status"].lower() != "mounted":
            res["errors"].append(f"{mo['dev']} not mounted")
    if len(mounts) < 2:
        res["warnings"].append(f"only {len(mounts)} cluster disk(s) visible on {name}")

    return res


def check_opcom(ip, lookback_lines=4000):
    """Scan the OPCOM log for cluster membership events."""
    tmp = "/tmp/vms_opcom_scan.log"
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vms_type.py")
    try:
        subprocess.run([sys.executable, script, ip,
                        "SYS$SYSROOT:[SYSMGR]OPERATOR.LOG;30", tmp, PW],
                       capture_output=True, timeout=180)
        with open(tmp, "rb") as f:
            data = f.read().decode('latin-1', errors='replace')
    except Exception as e:
        return {"error": str(e)}

    lines = data.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    lines = lines[-lookback_lines:]

    events = []
    for l in lines:
        ls = l.strip()
        if not ls:
            continue
        for g in GOOD_EVENTS + BAD_EVENTS:
            if g.lower() in ls.lower():
                events.append({"event": ls, "kind": "good" if g in GOOD_EVENTS else "bad"})
                break
    # Only bad events occurring AFTER the most recent recovery count as
    # current faults. A crash already resolved (node rejoined and reached
    # ACTIVE) must not keep the cluster flagged unhealthy forever.
    last_good = -1
    for i, e in enumerate(events):
        if e["kind"] == "good":
            last_good = i
    current_bad = [e for i, e in enumerate(events) if e["kind"] == "bad" and i > last_good]

    return {"events": events[-25:],
            "bad_count": len(current_bad),
            "historical_bad_count": sum(1 for e in events if e["kind"] == "bad"),
            "current_bad": current_bad}


def check_auth(ip):
    """Read CLUSTER_AUTHORIZE.DAT group number + hash."""
    tmp = "/tmp/vms_auth_scan.bin"
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vms_binfile.py")
    try:
        subprocess.run([sys.executable, script, ip,
                        "SYS$COMMON:[SYSEXE]CLUSTER_AUTHORIZE.DAT", tmp, "25", PW],
                       capture_output=True, timeout=180)
        with open(tmp, "rb") as f:
            data = f.read()
    except Exception as e:
        return {"error": str(e)}

    # The file is {group_number:long, password_hash:long}. The low byte of
    # the group number is 0x7b == 123 == '{' in ASCII, so the '{' byte IS
    # the first byte of the data - do not skip it.
    idx = data.find(b"{")
    if idx < 0:
        return {"error": "no data marker in capture"}
    body = data[idx:]
    if len(body) < 8:
        return {"error": f"short capture ({len(body)} bytes)"}
    group = int.from_bytes(body[0:4], 'little')
    hsh = int.from_bytes(body[4:8], 'little')
    return {"group": group, "hash": hex(hsh), "bytes": len(body)}


def check_pwd_expiry(ip):
    """Read SYSTEM's UAF record and compute password expiry."""
    try:
        text = read_record(ip, PW, "SYSTEM", "SHOW")
    except Exception as e:
        return {"error": str(e)}
    if not text or text == "AUTH_FAIL":
        return {"error": "could not read UAF record"}
    info = parse_expiry(text)
    info["raw_pwdchange"] = info.get("pwdchange").isoformat() if info.get("pwdchange") else None
    if info.get("expires"):
        info["raw_expires"] = info["expires"].isoformat()
    if info.get("pwdchange"):
        info.pop("pwdchange", None)
    if info.get("expires"):
        info.pop("expires", None)
    return info


def main():
    report = {"timestamp": datetime.now().astimezone().isoformat(),
              "nodes": [], "auth": {}}

    for name, cfg in NODES.items():
        r = check_node(name, cfg["ip"])
        report["nodes"].append(r)
        time.sleep(1)

    for name, cfg in NODES.items():
        report["auth"][name] = check_auth(cfg["ip"])
        time.sleep(1)

    # Password expiry - checked before the credential actually lapses, so a
    # future expiry is never mistaken for a cluster fault.
    report["password_expiry"] = {}
    for name, cfg in NODES.items():
        report["password_expiry"][name] = check_pwd_expiry(cfg["ip"])
        time.sleep(1)

    groups = {n: a.get("group") for n, a in report["auth"].items()}
    hashes = {n: a.get("hash") for n, a in report["auth"].items()}
    report["auth_match"] = (len(set(groups.values())) == 1 and len(set(hashes.values())) == 1
                             and None not in groups.values())
    if not report["auth_match"]:
        report.setdefault("warnings", []).append(
            f"cluster auth mismatch across nodes: {groups} {hashes}")

    opcom = check_opcom(NODES["FUSION"]["ip"])
    report["opcom"] = opcom

    # Overall verdict
    all_errors = []
    for n in report["nodes"]:
        all_errors.extend(f"{n['node']}: {e}" for e in n.get("errors", []))
    if opcom.get("bad_count"):
        all_errors.append(f"OPCOM: {opcom['bad_count']} adverse cluster event(s) in log tail")
    if not report["auth_match"]:
        all_errors.append("cluster authorisation mismatch between nodes")

    # Password expiry: a warning, not a fault - but an expired password
    # breaks the monitor's own login, so treat that as an error.
    report["password_warnings"] = []
    for name, p in report["password_expiry"].items():
        if p.get("error"):
            report["password_warnings"].append(f"{name}: could not read password expiry ({p['error']})")
            continue
        if p.get("expired"):
            all_errors.append(
                f"{name}: SYSTEM password EXPIRED - monitor login will fail until it is reset")
        else:
            days = p.get("days_remaining")
            if days is not None and days <= PASSWORD_WARN_DAYS:
                report["password_warnings"].append(
                    f"{name}: SYSTEM password expires in {days} day(s) "
                    f"({p.get('raw_expires')}) - renew before it lapses")
            if p.get("login_fails"):
                report["password_warnings"].append(
                    f"{name}: {p['login_fails']} failed login attempt(s) recorded on SYSTEM")

    report["healthy"] = not all_errors
    report["errors"] = all_errors

    print(json.dumps(report, indent=2))
    return 0 if report["healthy"] else 1


if __name__ == "__main__":
    sys.exit(main())
