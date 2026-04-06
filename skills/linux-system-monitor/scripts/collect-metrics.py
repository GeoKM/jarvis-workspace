#!/usr/bin/env python3
"""Collect system metrics from the local host and emit JSON to stdout."""
import subprocess, json, os, sys
from pathlib import Path


def run(cmd, stderr=True):
    """Run a shell command, return stdout or empty string on failure."""
    try:
        kw = {} if stderr else {"stderr": subprocess.DEVNULL}
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, **kw)
        return r.stdout.strip()
    except Exception:
        return ""


def run_out(cmd):
    return run(cmd, stderr=False)


def int_or_0(s):
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return 0


def float_or_0(s):
    try:
        return float(s)
    except (ValueError, TypeError):
        return 0


# ---- Host info ----
hostname = run("hostname")
timestamp = run("date -u +'%Y-%m-%dT%H:%M:%SZ'")
kernel = run("uname -r")
arch = run("uname -m")
nproc = int_or_0(run("nproc"))
uptime_s = int_or_0(run("cat /proc/uptime | awk '{print int($1)}'"))

# ---- CPU ----
cpu_line = run("head -1 /proc/stat")
fields = cpu_line.split()
# fields[0] = 'cpu', fields[1..8] = user,nice,system,idle,iowait,irq,softirq,steal
try:
    user, nice, system, idle, iowait, irq, softirq, steal = [int(fields[i]) for i in range(1, 9)]
    total = user + nice + system + idle + iowait + irq + softirq + steal
    cpu_pct = {
        "user_pct": round(user / max(total, 1) * 100, 1),
        "system_pct": round(system / max(total, 1) * 100, 1),
        "idle_pct": round(idle / max(total, 1) * 100, 1),
        "iowait_pct": round(iowait / max(total, 1) * 100, 1),
    }
except (ValueError, IndexError):
    cpu_pct = {"user_pct": 0, "system_pct": 0, "idle_pct": 0, "iowait_pct": 0}

# ctx and intr
ctx_switches = int_or_0(run("awk '{print $2}' /proc/stat | head -1"))
interrupts = int_or_0(run("awk '{print $2}' /proc/stat | tail -1"))

# Load
loadavg = run("cat /proc/loadavg")
parts = loadavg.split()
load = {"1m": float_or_0(parts[0]), "5m": float_or_0(parts[1]), "15m": float_or_0(parts[2])}

# ---- Memory ----
def mem_kb(field):
    val = run(f"awk '/^{field}:/ {{print int($2)*1024}}' /proc/meminfo")
    return int_or_0(val)

swap_total = mem_kb("SwapTotal")
swap_free = mem_kb("SwapFree")
mem_available = mem_kb("MemAvailable")
mem_total = mem_kb("MemTotal")
# Cap available at total — Proxmox VMs can report virtual address space as MemAvailable
if mem_total > 0:
    mem_available = min(mem_available, mem_total)
mem = {
    "total": mem_total,
    "free": mem_kb("MemFree"),
    "available": mem_available,
    "buffers": mem_kb("Buffers"),
    "cached": mem_kb("Cached"),
    "swap_total": swap_total,
    "swap_free": swap_free,
    "swap_used": max(swap_total - swap_free, 0),
}

# ---- Disk ----
disk_entries = []
for line in run("df -B1 -x tmpfs -x devtmpfs -x squashfs -x overlay 2>/dev/null | tail -n+2").splitlines():
    parts = line.split()
    if len(parts) >= 6:
        disk_entries.append({
            "mount": parts[5].replace("/", "_") or "_root",
            "total": int_or_0(parts[1]),
            "used": int_or_0(parts[2]),
            "avail": int_or_0(parts[3]),
            "use_pct": parts[4],
        })

# ---- Network interfaces ----
net_ifaces = {}
for iface_path in Path("/sys/class/net").iterdir():
    iface = iface_path.name
    try:
        net_ifaces[iface] = {
            "rx_bytes": int_or_0(Path(f"/sys/class/net/{iface}/statistics/rx_bytes").read_text()),
            "tx_bytes": int_or_0(Path(f"/sys/class/net/{iface}/statistics/tx_bytes").read_text()),
            "rx_err": int_or_0(Path(f"/sys/class/net/{iface}/statistics/rx_errs").read_text()),
            "tx_err": int_or_0(Path(f"/sys/class/net/{iface}/statistics/tx_errs").read_text()),
            "rx_drop": int_or_0(Path(f"/sys/class/net/{iface}/statistics/rx_dropped").read_text()),
            "tx_drop": int_or_0(Path(f"/sys/class/net/{iface}/statistics/tx_dropped").read_text()),
        }
    except (IOError, ValueError, PermissionError):
        pass

# ---- TCP states ----
tcp_states = {}
for proto in ["tcp", "tcp6"]:
    path = f"/proc/net/{proto}"
    if os.path.exists(path):
        with open(path) as f:
            for line in f.readlines()[1:]:
                parts = line.split()
                if len(parts) >= 4:
                    state = f"0x{parts[3].strip()}"
                    tcp_states[state] = tcp_states.get(state, 0) + 1

# ---- Processes ----
proc_count = int_or_0(run("ls /proc/ | grep -c '^[0-9]' 2>/dev/null"))
zombies = int_or_0(run(r"find /proc -maxdepth 2 -name status -exec grep -l '^State:.*Z' {} \; 2>/dev/null | wc -l"))

def top_procs(sort="cpu"):
    flag = "-%cpu" if sort == "cpu" else "-%mem"
    lines = run(f"ps aux --sort={flag} 2>/dev/null | awk 'NR>=2 && NR<=5 {{print $2\"|\"$3\"|\"$4\"|\"$11}}'").splitlines()
    procs = []
    for line in lines:
        p = line.split("|")
        if len(p) >= 4:
            procs.append({"pid": p[0], "cpu": p[1], "mem": p[2], "cmd": p[3]})
    return procs

top_cpu = top_procs("cpu")
top_mem = top_procs("mem")

# ---- Services ----
SERVICES = ["ssh", "sshd", "systemd-journald", "ntp", "ntpd", "chrony", "chronyd", "ufw", "firewalld", "docker"]
services = {}
for svc in SERVICES:
    r = None
    try:
        r = subprocess.run(["systemctl", "is-active", svc], capture_output=True, text=True)
    except FileNotFoundError:
        pass
    if r is not None and r.stdout.strip() == "active":
        services[svc] = "active"

# ---- Security ----
ssh_fails = int_or_0(run("journalctl -u ssh -u sshd --since '1 hour ago' --no-pager 2>/dev/null | grep -ci 'Failed password' || echo 0"))
sudo_fails = int_or_0(run("grep -c 'incorrect password attempt' /var/log/auth.log 2>/dev/null || echo 0"))

logins = []
for line in run("last -n 3 2>/dev/null").splitlines():
    parts = line.split()
    if len(parts) >= 6:
        logins.append({"user": parts[0], "from": parts[2], "time": " ".join(parts[3:6])})

# ---- NTP ----
ntp_offset = None
r = None
try:
    r = subprocess.run(["chronyc", "tracking"], capture_output=True, text=True)
    if r.returncode == 0:
        for line in r.stdout.splitlines():
            if "Last offset" in line:
                try:
                    ntp_offset = float(line.split()[-1]) * 1000
                    break
                except ValueError:
                    pass
except FileNotFoundError:
    pass
if ntp_offset is None:
    try:
        r = subprocess.run(["timedatectl", "show", "-p", "NTPSynchronized", "--value"],
                          capture_output=True, text=True)
        if r.stdout.strip() == "yes":
            ntp_offset = 0.0
    except FileNotFoundError:
        pass

# ---- Temperature ----
temp_zones = {}
for zone_path in sorted(Path("/sys/class/thermal").glob("thermal_zone*")):
    try:
        name = zone_path.name
        temp_mc = int(zone_path.joinpath("temp").read_text())
        temp_zones[name] = round(temp_mc / 1000.0, 1)
    except (IOError, ValueError, PermissionError):
        pass

# ---- Docker ----
docker_available = False
containers_running = "0"
containers_total = "0"
unhealthy = "0"
restarting = "0"
containers_list = []

r = None
try:
    r = subprocess.run(["docker", "info", "--format", "{{.ServerVersion}}"],
                  capture_output=True, text=True)
except FileNotFoundError:
    r = None
if r is not None and r.returncode == 0 and r.stdout.strip():
    docker_available = True
    containers_running = str(int_or_0(run("docker ps -q 2>/dev/null | wc -l")))
    containers_total = str(int_or_0(run("docker ps -aq 2>/dev/null | wc -l")))
    unhealthy = str(int_or_0(run("docker ps -a --format '{{.Names}} {{.Status}}' 2>/dev/null | grep -ci 'unhealthy' || echo 0")))
    restarting = str(int_or_0(run("docker ps -a --format '{{.Names}} {{.Status}}' 2>/dev/null | grep -ci 'Restarting' || echo 0")))
    # Get container name+status via docker ps, CPU/mem via docker stats (handles older Docker without stats in --format)
    for line in run("docker ps --format '{{.Names}}|{{.Status}}' 2>/dev/null").splitlines():
        p = line.split("|")
        if len(p) >= 2 and p[0].strip():
            containers_list.append({"name": p[0].strip(), "status": p[1].strip(), "cpu": "n/a", "mem": "n/a"})
    stats_raw = run("docker stats --no-stream --format '{{.Name}}|{{.CPUPerc}}|{{.MemPerc}}' 2>/dev/null")
    stats_map = {}
    for sline in stats_raw.splitlines():
        sp = sline.split("|")
        if len(sp) >= 3:
            stats_map[sp[0].strip()] = {"cpu": sp[1].strip(), "mem": sp[2].strip()}
    for c in containers_list:
        if c["name"] in stats_map:
            c["cpu"] = stats_map[c["name"]]["cpu"]
            c["mem"] = stats_map[c["name"]]["mem"]

import json as _json
_CONTAINER_JSON = _json.dumps(containers_list)
# ---- Assemble ----
data = {
    "hostname": hostname,
    "timestamp": timestamp,
    "kernel": kernel,
    "arch": arch,
    "nproc": nproc,
    "uptime_seconds": uptime_s,
    "cpu": {**cpu_pct, "ctx_switches": ctx_switches, "interrupts": interrupts},
    "load": load,
    "memory": mem,
    "disk": disk_entries,
    "network": {"interfaces": net_ifaces, "tcp": tcp_states},
    "processes": {
        "count": proc_count, "zombies": zombies,
        "top_cpu": top_cpu, "top_mem": top_mem
    },
    "services": services,
    "security": {"ssh_failures": ssh_fails, "sudo_failures": sudo_fails, "last_logins": logins},
    "time": {"ntp_offset_ms": ntp_offset},
    "docker": {
        "available": docker_available,
        "containers_running": containers_running,
        "containers_total": containers_total,
        "unhealthy": unhealthy,
        "restarting": restarting,
        "containers": json.loads(_CONTAINER_JSON),
    },
    "temperature": temp_zones,
}

json.dump(data, sys.stdout, indent=2)
