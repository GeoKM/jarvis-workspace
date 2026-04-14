#!/usr/bin/env bash
# run-monitor.sh — Orchestrate the full monitoring pipeline for one or all hosts.
# Reads hosts from ~/lab-docs/monitoring/hosts.d/hosts.yaml
#
# Usage:
#   ./run-monitor.sh --host <name>   Run for a specific host
#   ./run-monitor.sh --all           Run for all hosts in inventory
#   ./run-monitor.sh --list          List configured hosts and exit

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INVENTORY="$HOME/lab-docs/monitoring/hosts.d/hosts.yaml"
RETENTION_DAYS=30

usage() {
  echo "Usage: $0 --host <name>   Run for a specific host"
  echo "       $0 --all            Run for all hosts in inventory"
  echo "       $0 --list           List hosts and exit"
  exit 1
}

# ---- Argument parsing ----
TARGET_HOST=""
RUN_ALL=false
LIST_ONLY=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --host)  TARGET_HOST="$2"; shift 2 ;;
    --all)   RUN_ALL=true;    shift ;;
    --list)  LIST_ONLY=true;  shift ;;
    *)       usage ;;
  esac
done

# ---- Load inventory ----
if [[ ! -f "$INVENTORY" ]]; then
  echo "ERROR: Inventory not found: $INVENTORY" >&2
  exit 1
fi

HOSTS_JSON=$(python3 -c "
import yaml, json, sys
data = yaml.safe_load(open('$INVENTORY'))
hosts = data.get('hosts', [])
print(json.dumps(hosts))
" 2>/dev/null) || { echo "ERROR: Failed to parse $INVENTORY" >&2; exit 1; }

list_hosts() {
  echo "Configured hosts:"
  echo "$HOSTS_JSON" | python3 -c "
import json, sys
for h in json.load(sys.stdin):
    ssh = 'SSH' if h.get('ssh') else 'local'
    print(f\"  {h['name']:<20} ({ssh})  user={h.get('user','keith')}  host={h.get('host','')}\")
"
}

if [[ "$LIST_ONLY" == true ]]; then
  list_hosts
  exit 0
fi

if [[ "$RUN_ALL" == false && -z "$TARGET_HOST" ]]; then
  echo "ERROR: specify --host <name> or --all" >&2
  usage
fi

# ---- Retention: prune snapshots older than RETENTION_DAYS ----
prune_old_snapshots() {
  local host="$1"
  local snap_dir="$HOME/lab-docs/monitoring/snapshots/$host"
  [[ ! -d "$snap_dir" ]] && return 0
  local cutoff
  cutoff=$(date -d "$RETENTION_DAYS days ago" -u +%Y%m%d 2>/dev/null || date -v-${RETENTION_DAYS}d -u +%Y%m%d 2>/dev/null) || return 0
  local removed=0
  for f in "$snap_dir"/*.json; do
    [[ -f "$f" ]] || continue
    # Extract YYYYMMDD from filename: hostname-YYYYMMDD-HHMMSSZ.json
    local fname
    fname=$(basename "$f")
    local file_date="${fname##*-}"
    file_date="${file_date:0:8}"
    if [[ "$file_date" =~ ^[0-9]{8}$ && "$file_date" -lt "$cutoff" ]]; then
      rm -f "$f"
      removed=$((removed + 1))
    fi
  done
  [[ $removed -gt 0 ]] && echo "  Pruned $removed old snapshot(s) for $host"
}

# ---- Write an unavailable marker snapshot ----
write_unavailable_marker() {
  local hname="$1"
  local err_msg="$2"
  local snap_dir="$HOME/lab-docs/monitoring/snapshots/$hname"
  local ts
  ts=$(date -u +%Y-%m-%dT%H%M%SZ)
  local snap_file="$snap_dir/${hname}-${ts//[:-]/}.json"
  mkdir -p "$snap_dir"
  # Extract last successful snapshot to preserve its status
  local last_snap
  last_snap=$(ls -t "$snap_dir"/*.json 2>/dev/null | head -1)
  local last_status="green"
  if [[ -n "$last_snap" ]]; then
    last_status=$(python3 -c "
    import json, sys
    d=json.load(open('$last_snap'))
    print(d.get('_summary_severity','OK').lower())
    " 2>/dev/null || true
  fi
  local err_short
  err_short=$(head -1 <<< "$err_msg" | tr -d '\n')
  local marker
  marker=$(python3 -c "
import json, sys
d={
    'hostname': '$hname',
    'timestamp': '$ts',
    'unavailable': True,
    'error': '''$err_msg''',
    'last_known_status': '$last_status',
    'last_checked_at': '$ts'
}
print(json.dumps(d, indent=2))
" 2>/dev/null)
  echo "$marker" > "$snap_file"
  echo "  Unavailable marker written: ${snap_file##*/}"
}

# ---- Helper: run for one host ----
run_host() {
  local hname="$1"
  local ssh_required="$2"
  local ssh_host="$3"
  local ssh_user="$4"
  local ssh_identity="$5"

  echo ""
  echo "============================================================"
  echo "  Collecting metrics from: $hname"
  echo "============================================================"

  if [[ "$ssh_required" == "true" ]]; then
    # Build SSH command array (avoid scalar+eval pitfall)
    local -a SSH_CMD=(ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new)
    if [[ -n "$ssh_identity" ]]; then
      local id_path="${ssh_identity/#\~/$HOME}"
      SSH_CMD+=(-i "$id_path")
    fi
    SSH_CMD+=("${ssh_user}@${ssh_host}")

    # Capture metrics from remote host via SSH
    # We pipe the Python script over SSH and execute it remotely
    METRICS=$(mktemp)
    "${SSH_CMD[@]}" "python3 -" < "$SCRIPT_DIR/collect-metrics.py" > "$METRICS" 2>&1
    SSH_EXIT=$?

    if [[ $SSH_EXIT -ne 0 ]]; then
      echo ""
      echo "============================================================"
      echo "  Host UNREACHABLE: $hname  (SSH exit code: $SSH_EXIT)"
      echo "  Error output:"
      sed 's/^/    /' "$METRICS"
      echo "  Writing unavailable marker and moving to next host..."
      echo ""
      write_unavailable_marker "$hname" "$METRICS"
      rm -f "$METRICS"
      # Still prune old snapshots for unreachable host
      prune_old_snapshots "$hname"
      return 0
    fi

    python3 "$SCRIPT_DIR/parse-report.py" "$hname" < "$METRICS"
    rm -f "$METRICS"
  else
    # Local execution — always exit 0 from parse-report so pipeline status is predictable
    python3 "$SCRIPT_DIR/collect-metrics.py" 2>/dev/null \
      | python3 "$SCRIPT_DIR/parse-report.py" "$hname" || true
  fi

  # Prune old snapshots for this host
  prune_old_snapshots "$hname"

  # Always return 0 so the --all loop continues even if one host has issues
  return 0
}

# ---- Resolve host details from inventory ----
resolve_host() {
  local hname="$1"
  local details
  details=$(echo "$HOSTS_JSON" | python3 -c "
import json, sys
for h in json.load(sys.stdin):
    if h['name'] == '$hname':
        print(json.dumps(h)); break
" 2>/dev/null)
  [[ -z "$details" ]] && { echo "ERROR: Host '$hname' not found in inventory." >&2; list_hosts >&2; exit 1; }
  echo "$details"
}

# ---- Main ----
ALL_HOSTS=$(python3 -c "
import yaml, json, sys
data = yaml.safe_load(open('$INVENTORY'))
for h in data.get('hosts', []):
    print(h['name'])
" 2>/dev/null) || true

if [[ "$RUN_ALL" == true ]]; then
  for hname in $ALL_HOSTS; do
    details=$(resolve_host "$hname")
    run_host "$hname" \
      "$(echo "$details" | python3 -c 'import json,sys; print("true" if json.load(sys.stdin).get("ssh") else "false")')" \
      "$(echo "$details" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("host",""))')" \
      "$(echo "$details" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("user","keith"))')" \
      "$(echo "$details" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("identity",""))')" \
      || true
  done
elif [[ -n "$TARGET_HOST" ]]; then
  details=$(resolve_host "$TARGET_HOST")
  run_host "$TARGET_HOST" \
    "$(echo "$details" | python3 -c 'import json,sys; print("true" if json.load(sys.stdin).get("ssh") else "false")')" \
    "$(echo "$details" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("host",""))')" \
    "$(echo "$details" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("user","keith"))')" \
    "$(echo "$details" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("identity",""))')" \
    || true
fi

echo ""
echo "Done."
