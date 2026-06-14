#!/opt/freeware/bin/python
# -*- coding: utf-8 -*-
"""Collect system metrics from AIX (5.1 through 7.x) and emit JSON to stdout.
Supports AIX 5.1 through 7.x (some metrics unavailable on AIX 5.1).
Compatible with Python 2.7 and Python 3.x.
"""

import subprocess
import json
import re

def run(cmd):
    try:
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        # Decode bytes to string if needed (Python 3 on some AIX hosts returns bytes)
        if isinstance(out, bytes):
            out = out.decode('utf-8', errors='replace')
        return out.strip()
    except Exception as e:
        return str(e)

def int_or_0(s):
    try:
        return int(float(s.strip().replace(',', '')))
    except:
        return 0

def float_or_0(s):
    try:
        return float(s.strip().replace(',', ''))
    except:
        return 0.0

# ---- Detect AIX version ----
raw_uname = run("uname -a")
parts = raw_uname.split()
AixVer = int(parts[2]) if len(parts) > 2 else 5  # 5, 6, or 7

# ---- Timestamp ----
timestamp = run("date -u +'%Y-%m-%dT%H:%M:%SZ'")

# ---- Hostname ----
hostname = parts[1] if len(parts) > 1 else run("hostname -s")
os_version = parts[2] if len(parts) > 2 else ""
os_release = parts[3] if len(parts) > 3 else ""

# ---- Kernel/level ----
if AixVer >= 7:
    kernel = run("oslevel -s 2>/dev/null || oslevel 2>/dev/null | head -1")
else:
    kernel = run("oslevel 2>/dev/null | head -1")

arch = run("uname -m")

# ---- Uptime ----
uptime_s = 0
uptime_raw = run("uptime")
m = re.search(r'up\s+(\d+):(\d+)', uptime_raw)
if m:
    uptime_s = int(m.group(1)) * 3600 + int(m.group(2)) * 60
else:
    m = re.search(r'up\s+(\d+)\s+day', uptime_raw)
    if m:
        uptime_s = int(m.group(1)) * 86400
        m2 = re.search(r'up\s+\d+\s+day[s]?[,\s]+(\d+):(\d+)', uptime_raw)
        if m2:
            uptime_s += int(m2.group(1)) * 3600 + int(m2.group(2)) * 60
    else:
        m = re.search(r'up\s+(\d+)\s+hr', uptime_raw)
        if m:
            uptime_s = int(m.group(1)) * 3600
            m2 = re.search(r'up\s+\d+\s+hr[s]?[,\s]+(\d+)\s+min', uptime_raw)
            if m2:
                uptime_s += int(m2.group(1)) * 60
        else:
            m = re.search(r'up\s+(\d+)\s+min', uptime_raw)
            if m:
                uptime_s = int(m.group(1)) * 60

# ---- CPU via vmstat ----
# Extract lcpu (logical CPUs) from vmstat config line for CPU% normalisation
# AIX vmstat CPU% columns are per-CPU; divide by lcpu to get system-wide 0-100%
vmstat_raw = run("vmstat 1 2")
aix_lcpu = 1
for line in vmstat_raw.split('\n'):
    if 'lcpu=' in line:
        m = re.search(r'lcpu=(\d+)', line)
        if m:
            aix_lcpu = int(m.group(1))
        break
# Fallback: count physical processors via lsdev
if aix_lcpu <= 1:
    try:
        nproc_out = run("lsdev -C | grep -c '^proc' || echo 1")
        nproc_phys = max(1, int(nproc_out.strip()))
        # Estimate lcpu from physical procs (SMT factor ~4 on POWER7)
        aix_lcpu = max(aix_lcpu, nproc_phys * 4)
    except:
        pass

vmstat_lines = [l for l in vmstat_raw.split('\n')
                if l.strip()
                and 'kthr' not in l.lower()
                and 'cpu' not in l.lower()
                and 'System configuration' not in l
                and l.strip().split()[0].isdigit()]
cpu_pct = {"user_pct": 0.0, "system_pct": 0.0, "idle_pct": 0.0, "iowait_pct": 0.0, "n_proc": 1}
if vmstat_lines:
    fields = vmstat_lines[-1].split()
    us_idx = sy_idx = id_idx = wa_idx = -1
    for i, f in enumerate(fields):
        if f == 'us' and i + 4 < len(fields):
            us_idx, sy_idx, id_idx, wa_idx = i, i+1, i+2, i+3
            break
    if us_idx < 0:
        if AixVer >= 7 and len(fields) >= 18:
            us_idx, sy_idx, id_idx, wa_idx = 13, 14, 15, 16
        elif len(fields) >= 16:
            us_idx, sy_idx, id_idx, wa_idx = 12, 13, 14, 15
    if us_idx >= 0 and id_idx < len(fields):
        # AIX vmstat CPU% is per-logical-CPU; normalise to system-wide (0-100)
        def norm(v):
            return round(min(100.0, float_or_0(v) / float(aix_lcpu)), 1)
        cpu_pct = {
            "user_pct": norm(fields[us_idx]),
            "system_pct": norm(fields[sy_idx]),
            "idle_pct": norm(fields[id_idx]),
            "iowait_pct": norm(fields[wa_idx]),
            "n_proc": aix_lcpu
        }
        if AixVer < 7:
            pass

# ---- Memory ----
mem = {"total_kb": 0, "used_kb": 0, "free_kb": 0, "pin_kb": 0, "virtual_kb": 0}
if AixVer >= 6:
    for line in run("svmon -G").split('\n'):
        if line.startswith('memory'):
            fields = line.split()
            if len(fields) >= 6:
                page_kb = 4
                mem = {
                    "total_kb": int_or_0(fields[1]) * page_kb,
                    "used_kb": int_or_0(fields[2]) * page_kb,
                    "free_kb": int_or_0(fields[3]) * page_kb,
                    "pin_kb": int_or_0(fields[4]) * page_kb,
                    "virtual_kb": int_or_0(fields[5]) * page_kb,
                }
            break
else:
    # AIX 5.1: estimate from vmstat avm and fre (in 4KB pages)
    vmstat_data = run("vmstat 1 2")
    for line in vmstat_data.split('\n'):
        fields = line.split()
        if len(fields) >= 4 and fields[0].isdigit():
            page_kb = 4
            avm = int_or_0(fields[2])
            fre = int_or_0(fields[3])
            mem = {
                "total_kb": (avm + fre) * page_kb,
                "used_kb": avm * page_kb,
                "free_kb": fre * page_kb,
                "pin_kb": 0,
                "virtual_kb": 0,
            }
            break

# ---- Paging via lsps -a (AIX 5.1+) ----
# Note: lsps -a output is fixed-width columns, not space-delimited.
# Parse by finding non-whitespace tokens and using their positions as boundaries.
import re as _re
paging = []
lsps_raw = run("lsps -a 2>/dev/null")
if lsps_raw and 'not found' not in lsps_raw.lower() and 'not a valid flag' not in lsps_raw.lower():
    lines = lsps_raw.split('\n')
    if len(lines) >= 2:
        data = lines[1]
        tokens = [(m.start(), m.end(), m.group()) for m in _re.finditer(r'\S+', data)]
        def fld(idx):
            return tokens[idx][2] if idx < len(tokens) else ''
        def size_to_mb(s):
            s = s.strip()
            if not s: return 0
            # Handle 2-char units (MB, GB, KB) and 1-char (M, G, K)
            if len(s) >= 2 and s[-2:].upper() in ('MB','GB','KB','MG','MK'):
                num = s[:-2]
                unit = s[-2:].upper()
            else:
                num = s[:-1] if s[-1] in 'MmGgKk' else s
                unit = s[-1].upper() if s[-1] in 'MmGgKk' else ''
            try:
                v = int(float(num))
            except:
                return 0
            if unit == 'GB' or unit == 'G': return v * 1024
            if unit == 'KB' or unit == 'K': return v // 1024
            return v  # MB
        if len(tokens) >= 5:
            paging.append({
                "vg": fld(2),
                "type": fld(1),
                "size_mb": size_to_mb(fld(3)),
                "used_pct": int_or_0(fld(4)),
                "active": fld(5),
            })


# ---- Filesystems via df -k ----
filesystems = []
df_raw = run("df -k 2>/dev/null")
if '1K-blocks' in df_raw or 'Available' in df_raw:
    # AIX 5.1 style: filesystem 1K-blocks used available use% mount
    for line in df_raw.split('\n'):
        stripped = line.lstrip()
        if not stripped or 'Filesystem' in stripped or stripped.startswith('-'):
            continue
        parts = line.split()
        if len(parts) < 6:
            continue
        mount = parts[-1]
        if mount in ('/proc', 'none', '-', '/dev'):
            continue
        use_pct = int_or_0(parts[-2].replace('%', ''))
        free_kb = int_or_0(parts[-3]) * 1024
        used_kb = int_or_0(parts[-4]) * 1024
        total_kb = int_or_0(parts[-5]) * 1024
        filesystems.append({
            "mount": mount,
            "total_kb": total_kb,
            "used_kb": used_kb,
            "free_kb": free_kb,
            "use_pct": use_pct,
        })
else:
    # AIX 7.x style: filesystem 1024-blocks free %used iused %iused mount
    for line in df_raw.split('\n'):
        stripped = line.lstrip()
        if not stripped or 'Filesystem' in stripped or stripped.startswith('-'):
            continue
        parts = line.split()
        if len(parts) < 6:
            continue
        mount = parts[-1]
        if mount in ('/proc', 'none', '-', '/dev'):
            continue
        use_pct = int_or_0(parts[-2].replace('%', ''))
        free_kb = int_or_0(parts[-4])
        total_kb = int_or_0(parts[-6])
        used_kb = total_kb - free_kb
        filesystems.append({
            "mount": mount,
            "total_kb": total_kb,
            "used_kb": used_kb,
            "free_kb": free_kb,
            "use_pct": use_pct,
        })

# ---- Network interfaces via netstat -in ----
interfaces = []
seen = set()
for line in run("netstat -in 2>/dev/null").split('\n')[2:]:
    if not line.strip() or 'Kernel' in line:
        continue
    fields = line.split()
    if len(fields) >= 5:
        name = fields[0].rstrip('*')
        mtu = fields[1]
        addr = fields[3]
        pkts_in = int_or_0(fields[4])
        pkts_out = int_or_0(fields[7]) if len(fields) > 7 else 0
        if name and name not in seen:
            seen.add(name)
            interfaces.append({
                "name": name,
                "mtu": mtu,
                "address": addr,
                "pkts_in": pkts_in,
                "pkts_out": pkts_out,
            })

# ---- LPAR via lparstat (AIX 6+ only) ----
lpar = {}
if AixVer >= 6:
    lparstat_raw = run("lparstat 1 1 2>/dev/null")
    if lparstat_raw and 'not found' not in lparstat_raw.lower():
        lines = lparstat_raw.split('\n')
        if len(lines) >= 3:
            data = lines[-1].split()
            for i, f in enumerate(data):
                if f == 'ent' and i + 1 < len(data):
                    lpar = {"entitled_proc_units": int_or_0(data[i + 1])}
                    break

# ---- System errors via errpt ----
alerts = []
errpt_raw = run("errpt -aj 2>/dev/null")
if not errpt_raw or 'not a valid flag' in errpt_raw.lower() or 'not found' in errpt_raw.lower():
    errpt_raw = run("errpt 2>/dev/null")
    for line in errpt_raw.split('\n'):
        if not line.strip() or 'IDENTIFIER' in line:
            continue
        fields = line.split(None, 4)
        if len(fields) >= 5:
            alerts.append({
                'id': fields[0],
                'timestamp': fields[1],
                'type': fields[2],
                'class': fields[3],
                'resource': fields[4] if len(fields) > 4 else '',
            })
else:
    current = {}
    for line in errpt_raw.split('\n'):
        line = line.strip()
        if not line:
            if current:
                alerts.append(current)
                current = {}
            continue
        parts = line.split(None, 1)
        if not parts:
            continue
        key = parts[0]
        val = len(parts) > 1 and parts[1] or ''
        if key == 'IDENTIFIER':
            if current:
                alerts.append(current)
            current = {'id': val}
        elif key in ('TIMESTAMP', 'TYPE', 'CLASS', 'RESOURCE_NAME', 'DESCRIPTION'):
            current[key.lower()] = val
    if current:
        alerts.append(current)

alerts = alerts[-20:]

severity_counts = {"P": 0, "I": 0, "O": 0}
for a in alerts:
    sev = a.get('type', '')
    if sev in severity_counts:
        severity_counts[sev] += 1

# ---- System attributes via lsattr ----
sys0_attrs = {}
for line in run("lsattr -El sys0 2>/dev/null").split('\n'):
    fields = line.split()
    if len(fields) >= 2:
        sys0_attrs[fields[0]] = fields[1]

autorestart = sys0_attrs.get('autorestart', 'unknown')
cpuguard = sys0_attrs.get('cpuguard', 'unknown')

# ---- Active users ----
who_raw = run("who 2>/dev/null")
unique_users = sorted(set([l.split()[0] for l in who_raw.split('\n') if l]))

# ---- Disk I/O via iostat (AIX 6+ only) ----
disk_stats = []
if AixVer >= 6:
    seen_disks = set()
    for line in run("iostat 1 2 2>/dev/null").split('\n'):
        fields = line.split()
        if len(fields) >= 5 and fields[0] not in ('tty', 'disks:', 'Disks:', 'System', ''):
            disk = fields[0]
            try:
                busy = float_or_0(fields[1])
                tps = float_or_0(fields[2])
                rkb = float_or_0(fields[3])
                wkb = float_or_0(fields[4])
                if disk and disk not in seen_disks:
                    seen_disks.add(disk)
                    disk_stats.append({
                        "disk": disk,
                        "busy_pct": round(busy, 1),
                        "tps": round(tps, 1),
                        "read_kb_s": round(rkb, 1),
                        "write_kb_s": round(wkb, 1),
                    })
            except (ValueError, IndexError):
                continue
    disk_stats = sorted(disk_stats, key=lambda d: d['busy_pct'], reverse=True)[:5]

# ---- Health summary ----
summary_severity = "green"
if severity_counts['P'] > 0:
    summary_severity = "red"
elif cpu_pct['idle_pct'] < 20:
    summary_severity = "orange"
elif any(fs['use_pct'] > 90 for fs in filesystems):
    summary_severity = "orange"

# ---- Assemble ----
output = {
    "timestamp": timestamp,
    "hostname": hostname,
    "os": "AIX " + os_version + "." + os_release,
    "kernel": kernel,
    "arch": arch,
    "uptime_s": uptime_s,
    "cpu": cpu_pct,
    "memory": mem,
    "paging": paging,
    "disk_io": disk_stats,
    "filesystems": filesystems,
    "network_interfaces": interfaces,
    "lpar": lpar,
    "alerts": alerts,
    "alert_counts": severity_counts,
    "system_attrs": {
        "autorestart": autorestart,
        "cpuguard": cpuguard,
    },
    "active_users": unique_users,
    "summary_severity": summary_severity,
}

print(json.dumps(output, indent=2))