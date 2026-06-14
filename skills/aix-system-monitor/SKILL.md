# AIX System Monitor Skill

Monitor AIX systems using AIX-native commands. Produces JSON snapshots
in the same format as the Linux `linux-system-monitor` skill so the dashboard
can display both without modification.

## Overview

- **Hosts**: Persei-NIM, Celestia, Titan-AIX71 (AIX 7.1)
- **Collection**: Remote SSH with `collect-aix-metrics.py` via Python3 on AIX
- **Snapshot storage**: `~/lab-docs/monitoring/snapshots-aix/<hostname>/`
- **Schedule**: Daily midday (see cron setup below)
- **Output format**: Same JSON schema as Linux snapshots

## AIX Collector

**Script**: `scripts/collect-aix-metrics.py` (runs on AIX via SSH)

### AIX-Specific Commands Used

| Metric | Command | Notes |
|---|---|---|
| Hostname | `uname -a` (field 1) | |
| OS version | `uname -a` fields 2,3 | |
| Kernel | `oslevel -s` | TL/SP level |
| Uptime | `uptime` (regex parsed) | Handles H:MM and "n hr" formats |
| CPU | `vmstat 1 2` | Last non-header line; fields us/sy/id/wa |
| Memory | `svmon -G` | 4KB page multiply |
| Paging | `lsps -a` | |
| Filesystems | `df -k` | 1024-byte blocks; used = total - free |
| Network | `netstat -in` | IPv4 addresses, skip duplicate lo0 |
| LPAR | `lparstat 1 1` | entitled_proc_units |
| Errors | `errpt -aj` | Last 20 entries; P=permanent, I=info |
| System attrs | `lsattr -El sys0` | autorestart, cpuguard |
| Active users | `who` | unique sorted |
| Disk I/O | `iostat 1 2` | Top 5 by busy% |

### AIX Python Path

```
/opt/freeware/bin/python3
```

Note: `python3` alone is NOT in PATH on AIX — must use the full path.

### Alert / Severity Logic

- `summary_severity: red` → P (permanent) errors present
- `summary_severity: orange` → CPU idle < 20% OR any FS > 90% used
- `summary_severity: green` → all clear

## Host Inventory

File: `~/lab-docs/monitoring/aix-hosts.d/hosts.yaml`

```yaml
hosts:
  - name: Persei-NIM
    ssh: true
    host: Persei-NIM.can.barnabasmusic.com
    user: keith
    identity: /home/keith/.ssh/id_jt_ed25519

  - name: Celestia
    ssh: true
    host: Celestia.can.barnabasmusic.com
    user: keith
    identity: /home/keith/.ssh/id_jt_ed25519

  - name: Titan-AIX71
    ssh: true
    host: Titan-AIX71.can.barnabasmusic.com
    user: keith
    identity: /home/keith/.ssh/id_jt_ed25519
```

## Snapshot Naming

```
<hostname>-<YYYYMMDD>T<HHMMSS>Z.json
```

## Dashboard Integration

The same `server.py` (lab-monitor-dashboard) serves AIX snapshots alongside
Linux snapshots. Both use the same JSON schema.

To make AIX hosts appear in the dashboard alongside Linux hosts, update
`server.py` to look in both:
- Linux: `~/lab-docs/monitoring/snapshots/<hostname>/`
- AIX:   `~/lab-docs/monitoring/snapshots-aix/<hostname>/`

Currently the server only looks at the Linux path. Either add a second
scan root, or add AIX hosts to the Linux host file and run a shared collector.

## Cron Setup

Add to crontab for midday AIX monitoring:

```
0 12 * * *  ~/.openclaw/workspace/skills/aix-system-monitor/scripts/run-aix-monitor.sh
```

The run script:
1. Reads `~/lab-docs/monitoring/aix-hosts.d/hosts.yaml`
2. For each host: scp `collect-aix-metrics.py`, run via SSH, save snapshot
3. Writes `unavailable` markers for unreachable hosts
4. Cleans up the remote temp file after each run

## Manual Test

```bash
# Quick test of collector on each host
for host in Persei-NIM.can.barnabasmusic.com Celestia.can.barnabasmusic.com Titan-AIX71.can.barnabasmusic.com; do
  echo "=== $host ==="
  scp -o BatchMode=yes -o ConnectTimeout=15 -i ~/.ssh/id_jt_ed25519 \
    ~/.openclaw/workspace/skills/aix-system-monitor/scripts/collect-aix-metrics.py \
    keith@$host:/tmp/collect-aix-metrics.py
  ssh -o BatchMode=yes -o ConnectTimeout=15 -i ~/.ssh/id_jt_ed25519 \
    keith@$host "/opt/freeware/bin/python3 /tmp/collect-aix-metrics.py"
  ssh -o BatchMode=yes -o ConnectTimeout=15 -i ~/.ssh/id_jt_ed25519 \
    keith@$host "rm -f /tmp/collect-aix-metrics.py"
done
```