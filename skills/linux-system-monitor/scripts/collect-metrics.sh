#!/usr/bin/env bash
# collect-metrics.sh — Gather system metrics from a Linux host and emit JSON to stdout.
set -euo pipefail

REMOTE=""
IDENTITY=""
LOCAL_MODE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --remote)   REMOTE="$2";    shift 2 ;;
    --identity) IDENTITY="$2";  shift 2 ;;
    --local)   LOCAL_MODE="1"; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

SSH_CMD_ARRAY=()
if [[ -n "$REMOTE" && -z "$LOCAL_MODE" ]]; then
  SSH_CMD_ARRAY=(ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new)
  [[ -n "$IDENTITY" ]] && SSH_CMD_ARRAY+=(-i "$IDENTITY")
  SSH_CMD_ARRAY+=("$REMOTE")
fi

run_cmd() {
  local cmd="$*"
  if [[ ${#SSH_CMD_ARRAY[@]} -gt 0 ]]; then
    "${SSH_CMD_ARRAY[@]}" "$cmd" 2>/dev/null || true
  else
    bash -c "$cmd" 2>/dev/null || true
  fi
}

# ---- Collect raw data ----

HOSTNAME_RAW=$(run_cmd "hostname")
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
NPROC=$(run_cmd "nproc")
UPTIME_S=$(run_cmd "cat /proc/uptime | awk '{print int(\$1)}'")

# CPU: aggregate line from /proc/stat
CPU_LINE=$(run_cmd "head -1 /proc/stat")
IFS=' ' read -r _ cpu_user cpu_nice cpu_sys cpu_idle cpu_iowait cpu_irq cpu_softirq cpu_steal _ <<< "$CPU_LINE"

# Load average
LOADAVG=$(run_cmd "cat /proc/loadavg")
IFS=' ' read -r load1 load5 load15 _ <<< "$LOADAVG"

# Context switches and interrupts
CTX=$(run_cmd "awk '{print \$2}' /proc/stat | head -1")
INTR=$(run_cmd "awk '{print \$2}' /proc/stat | tail -1")

# Memory
mem_total=$(run_cmd "awk '/^MemTotal:/ {print int(\$2)*1024}' /proc/meminfo")
mem_free=$(run_cmd "awk '/^MemFree:/ {print int(\$2)*1024}' /proc/meminfo")
mem_avail=$(run_cmd "awk '/^MemAvailable:/ {print int(\$2)*1024}' /proc/meminfo")
mem_buffers=$(run_cmd "awk '/^Buffers:/ {print int(\$2)*1024}' /proc/meminfo")
mem_cached=$(run_cmd "awk '/^Cached:/ {print int(\$2)*1024}' /proc/meminfo")
swap_total=$(run_cmd "awk '/^SwapTotal:/ {print int(\$2)*1024}' /proc/meminfo")
swap_free=$(run_cmd "awk '/^SwapFree:/ {print int(\$2)*1024}' /proc/meminfo")

# Disk and network via Python helpers
DISK_JSON=$(run_cmd "df -B1 -x tmpfs -x devtmpfs -x squashfs -x overlay 2>/dev/null | tail -n+2" | python3 "$SCRIPT_DIR/encode-disks.py")
NET_JSON=$(run_cmd "python3 $SCRIPT_DIR/encode-net.py")

# TCP states
TCP_JSON=$(run_cmd "cat /proc/net/tcp /proc/net/tcp6 2>/dev/null" | python3 "$SCRIPT_DIR/encode-tcp.py")

# Process counts
PROC_COUNT=$(run_cmd "ls /proc/ | grep -c '^[0-9]' 2>/dev/null || echo 0")
ZOMBIES=$(run_cmd "find /proc -maxdepth 2 -name status -exec grep -l '^State:.*Z' {} \; 2>/dev/null | wc -l")

# Top CPU/MEM processes
TOP_CPU_JSON=$(run_cmd "ps aux --sort=-%cpu 2>/dev/null | awk 'NR>=2 && NR<=5 {print \$2\"|\"\$3\"|\"\$4\"|\"\$11}'" | python3 "$SCRIPT_DIR/encode-containers.py")
TOP_MEM_JSON=$(run_cmd "ps aux --sort=-%mem 2>/dev/null | awk 'NR>=2 && NR<=5 {print \$2\"|\"\$3\"|\"\$4\"|\"\$11}'" | python3 "$SCRIPT_DIR/encode-containers.py")

# Services
SVC_JSON=$(run_cmd "python3 $SCRIPT_DIR/encode-services.py")

# Security
SSH_FAILS=$(run_cmd "journalctl -u ssh -u sshd --since '1 hour ago' --no-pager 2>/dev/null | grep -ci 'Failed password' || echo 0")
SUDO_FAILS=$(run_cmd "grep -c 'incorrect password attempt' /var/log/auth.log 2>/dev/null || echo 0")
LAST_LOGINS_JSON=$(run_cmd "last -n 3 2>/dev/null" | python3 "$SCRIPT_DIR/encode-logins.py")

# NTP
NTP_OFFSET=$(run_cmd "python3 $SCRIPT_DIR/encode-ntp.py")

# Temperature
TEMP_JSON=$(run_cmd "cat /sys/class/thermal/thermal_zone*/temp 2>/dev/null" | python3 "$SCRIPT_DIR/encode-temp.py")

# Docker
DOCKER_AVAILABLE="false"
DOCKER_RUNNING="0"
DOCKER_TOTAL="0"
DOCKER_UNHEALTHY="0"
DOCKER_RESTARTING="0"
DOCKER_CONTAINERS_JSON="[]"
_DOCKER_BIN=$(run_cmd "command -v docker 2>/dev/null" || echo "")
if [[ -n "$_DOCKER_BIN" ]]; then
  _DOCKER_VER=$(run_cmd "docker info --format '{{.ServerVersion}}' 2>/dev/null" || echo "")
  if [[ -n "$_DOCKER_VER" ]]; then
    DOCKER_AVAILABLE="true"
    DOCKER_RUNNING=$(run_cmd "docker ps -q 2>/dev/null | wc -l")
    DOCKER_TOTAL=$(run_cmd "docker ps -aq 2>/dev/null | wc -l")
    DOCKER_UNHEALTHY=$(run_cmd "docker ps -a --format '{{.Names}} {{.Status}}' 2>/dev/null | grep -ci 'unhealthy' || echo 0")
    DOCKER_RESTARTING=$(run_cmd "docker ps -a --format '{{.Names}} {{.Status}}' 2>/dev/null | grep -ci 'Restarting' || echo 0")
    DOCKER_CONTAINERS_JSON=$(run_cmd "docker ps --format '{{.Names}}|{{.Status}}|{{.Health}}|{{.CPUPerc}}|{{.MemPerc}}' 2>/dev/null" | python3 "$SCRIPT_DIR/encode-containers.py")
  fi
fi

KERNEL=$(run_cmd "uname -r")
ARCH=$(run_cmd "uname -m")

# ---- Emit JSON ----
# All complex JSON is triple-quoted as Python strings to avoid bash expanding {chars}
python3 << PYEOF

import json, sys

# CPU percentages from bash variables
try:
    vals = [$cpu_user, $cpu_nice, $cpu_sys, $cpu_idle, $cpu_iowait, $cpu_irq, $cpu_softirq, $cpu_steal]
    total = sum(int(v) for v in vals)
    _CPU_PCT = [round(int(vals[i]) / total * 100, 1) for i in [0, 2, 3, 4]]
except:
    _CPU_PCT = [0.0, 0.0, 0.0, 0.0]
_CTX = $\{CTX:-0\}
_INTR = $\{INTR:-0\}

data = \{
    'hostname': '$HOSTNAME_RAW',
    'timestamp': '$TIMESTAMP',
    'kernel': '$KERNEL',
    'arch': '$ARCH',
    'nproc': $NPROC,
    'uptime_seconds': $UPTIME_S,
    'cpu': \{
        'user_pct': _CPU_PCT[0],
        'system_pct': _CPU_PCT[1],
        'idle_pct': _CPU_PCT[2],
        'iowait_pct': _CPU_PCT[3],
        'ctx_switches': _CTX,
        'interrupts': _INTR
    \},
    'load': \{'1m': $load1, '5m': $load5, '15m': $load15\},
    'memory': \{
        'total': $mem_total, 'free': $mem_free, 'available': $mem_avail,
        'buffers': $mem_buffers, 'cached': $mem_cached,
        'swap_total': $swap_total, 'swap_free': $swap_free
    \},
    'disk': $DISK_JSON,
    'network': $NET_JSON,
    'tcp': $TCP_JSON,
    'processes': \{
        'count': $PROC_COUNT, 'zombies': $ZOMBIES,
        'top_cpu': $TOP_CPU_JSON, 'top_mem': $TOP_MEM_JSON
    \},
    'services': $SVC_JSON,
    'security': \{
        'ssh_failures': $SSH_FAILS, 'sudo_failures': $SUDO_FAILS,
        'last_logins': $LAST_LOGINS_JSON
    \},
    'time': \{'ntp_offset_ms': $NTP_OFFSET\},
    'docker': \{
        'available': $DOCKER_AVAILABLE,
        'containers_running': $DOCKER_RUNNING,
        'containers_total': $DOCKER_TOTAL,
        'unhealthy': $DOCKER_UNHEALTHY,
        'restarting': $DOCKER_RESTARTING,
        'containers': $DOCKER_CONTAINERS_JSON
    \},
    'temperature': $TEMP_JSON
\}

sys.stdout.write(json.dumps(data, indent=2))
PYEOF
