#!/usr/bin/env bash
# run-aix-monitor.sh — Orchestrate AIX system monitoring for one or all AIX hosts.
# Reads hosts from ~/lab-docs/monitoring/aix-hosts.d/hosts.yaml
#
# Usage:
#   ./run-aix-monitor.sh --host <name>   Run for a specific host
#   ./run-aix-monitor.sh --all           Run for all hosts in inventory
#   ./run-aix-monitor.sh --list          List configured hosts and exit

set -euo pipefail

# Hard timeout to prevent hanging against unreachable hosts.
# Cron's own timeout is ~120s; we cut off at 100s to leave clean exit room.
TIMEOUT_SECS=100

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INVENTORY="$HOME/lab-docs/monitoring/aix-hosts.d/hosts.yaml"
SCRIPT_REMOTE="/tmp/collect-aix-metrics.py"
SNAPSHOT_ROOT="$HOME/lab-docs/monitoring/snapshots-aix"

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
    --list)  LIST_ONLY=true;   shift ;;
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
  echo "Configured AIX hosts:"
  echo "$HOSTS_JSON" | python3 -c "
import json, sys
for h in json.load(sys.stdin):
    print(f\"  {h['name']:<20}  user={h.get('user','keith')}@{h.get('host','')}\")
"
}

if [[ "$LIST_ONLY" == true ]]; then
  list_hosts
  exit 0
fi

# ---- Helper: resolve host config ----
get_host_config() {
  local name="$1"
  echo "$HOSTS_JSON" | python3 -c "
import json, sys
hosts = json.load(sys.stdin)
for h in hosts:
    if h['name'] == '$name':
        print(json.dumps(h))
        break
" 2>/dev/null || echo "{}"
}

# ---- Helper: build SSH options for a host ----
get_ssh_opts() {
  local config="$1"
  local identity=$(echo "$config" | python3 -c "import json,sys; print(json.load(sys.stdin).get('identity','~/.ssh/id_jt_ed25519'))")
  local ssh_config_name=$(echo "$config" | python3 -c "import json,sys; print(json.load(sys.stdin).get('ssh_config_name',''))")

  if [[ -n "$ssh_config_name" && "$ssh_config_name" == "43p" ]]; then
    echo "-o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=off -o ServerAliveInterval=15 -o ServerAliveCountMax=3 -o KexAlgorithms=+diffie-hellman-group14-sha1 -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa -i $identity"
  elif [[ -n "$ssh_config_name" ]]; then
    echo "-o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=off -o ServerAliveInterval=15 -o ServerAliveCountMax=3 -F $HOME/.ssh/config"
  else
    echo "-o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=off -o ServerAliveInterval=15 -o ServerAliveCountMax=3 -i $identity"
  fi
}

# ---- Helper: detect remote Python path ----
detect_remote_python() {
  local config="$1"
  local user=$(echo "$config" | python3 -c "import json,sys; print(json.load(sys.stdin).get('user','keith'))")
  local host=$(echo "$config" | python3 -c "import json,sys; print(json.load(sys.stdin).get('host',''))")

  # Check if inventory specifies explicit python_path
  local python_path=$(echo "$config" | python3 -c "import json,sys; print(json.load(sys.stdin).get('python_path',''))")
  if [[ -n "$python_path" ]]; then
    echo "$python_path"
    return
  fi

  # Build SSH opts for this host and test python3
  local ssh_opts
  ssh_opts=$(get_ssh_opts "$config")

  local remote_python="/opt/freeware/bin/python3"
  local py_test=$(ssh $ssh_opts "${user}@${host}" "/opt/freeware/bin/python3 --version 2>&1 | head -1" 2>&1 || echo "")
  if [[ -n "$py_test" && "$$py_test" != *"not found"* && "$py_test" != *"No such"* && "$py_test" != *"cannot"* ]]; then
    remote_python="/opt/freeware/bin/python3"
  else
    local py2_test=$(ssh $ssh_opts "${user}@${host}" "/opt/freeware/bin/python --version 2>&1 | head -1" 2>&1 || echo "")
    if [[ -n "$py2_test" && "$py2_test" != *"not found"* && "$py2_test" != *"No such"* && "$py2_test" != *"cannot"* ]]; then
      remote_python="/opt/freeware/bin/python"
    fi
  fi
  echo "$remote_python"
}

# ---- Helper: collect metrics from one AIX host ----
collect_aix_host() {
  local name="$1"
  local host="$2"
  local user="$3"
  local identity="$4"
  local remote_python="$5"
  local ssh_config_name="${6:-}"

  local SSH_OPTS
  SSH_OPTS=$(get_ssh_opts "$(get_host_config "$name")")

  local snapshot_dir="$SNAPSHOT_ROOT/$name"
  mkdir -p "$snapshot_dir"

  local ts=$(date -u +"%Y%m%dT%H%M%SZ")
  local out_file="$snapshot_dir/${name}-${ts}.json"
  local temp_marker="$snapshot_dir/collector.state"

  echo "[AIX] Collecting $name ($host) ..."

  # Step 1: scp collector script to remote
  local scp_exit=0
  scp $SSH_OPTS "$SCRIPT_DIR/collect-aix-metrics.py" \
      "${user}@${host}:${SCRIPT_REMOTE}" 2>&1 || scp_exit=$?

  echo "running" > "$temp_marker"

  if [[ $scp_exit -ne 0 ]]; then
    echo "[AIX] SCP failed for $name (exit $scp_exit)"
    echo "SCP failed" > "$temp_marker"
    sleep 2
    return 0  # don't abort the monitoring loop
  fi

  # Step 2: run collector on AIX
  local ssh_output=""
  local ssh_exit=0
  ssh_output=$(ssh $SSH_OPTS -o ConnectTimeout=60 "${user}@${host}" \
                   "$remote_python $SCRIPT_REMOTE" 2>&1) || ssh_exit=$?

  # Step 3: clean up remote script
  ssh $SSH_OPTS -o ConnectTimeout=10 "${user}@${host}" \
      "rm -f $SCRIPT_REMOTE" 2>/dev/null || true

  if [[ $ssh_exit -ne 0 ]]; then
    echo "[AIX] SSH failed for $name (exit $ssh_exit): $ssh_output"
    echo "SSH failed" > "$temp_marker"
    sleep 2
    return 0  # don't abort the monitoring loop
  fi

  if [[ -z "$ssh_output" ]]; then
    echo "[AIX] Empty output from $name collector"
    echo "Empty output" > "$temp_marker"
    return 0  # don't abort the monitoring loop
  fi

  if ! echo "$ssh_output" | python3 -c "import json,sys; json.load(sys.stdin)" 2>/dev/null; then
    echo "[AIX] Invalid JSON from $name"
    echo "$ssh_output" > "$out_file.failed"
    echo "Invalid JSON" > "$temp_marker"
    return 0  # don't abort the monitoring loop
  fi

  echo "$ssh_output" > "$out_file"
  echo "complete" > "$temp_marker"
  echo "[AIX] Snapshot saved: $out_file"
  echo "$out_file"
}

# ---- Main: run for requested host(s) ----
run_host() {
  local name="$1"
  local config=$(get_host_config "$name")

  if [[ -z "$config" || "$config" == "{}" ]]; then
    echo "ERROR: Host '$name' not found in inventory" >&2
    return 1
  fi

  local host=$(echo "$config" | python3 -c "import json,sys; print(json.load(sys.stdin).get('host',''))")
  local user=$(echo "$config" | python3 -c "import json,sys; print(json.load(sys.stdin).get('user','keith'))")
  local identity=$(echo "$config" | python3 -c "import json,sys; print(json.load(sys.stdin).get('identity','~/.ssh/id_jt_ed25519'))")
  local ssh_config_name=$(echo "$config" | python3 -c "import json,sys; print(json.load(sys.stdin).get('ssh_config_name',''))")

  local remote_python=$(detect_remote_python "$config")
  echo "[AIX] $name: using python at $remote_python"

  collect_aix_host "$name" "$host" "$user" "$identity" "$remote_python" "$ssh_config_name"
}

# ---- Entry point: timeout wrapper for monitoring runs ----
if [[ "$RUN_ALL" == true || -n "$TARGET_HOST" ]]; then
  # If __TIMEOUT_CHILD is already set, we've been re-executed under timeout — run directly.
  if [[ "${__TIMEOUT_CHILD:-}" == "1" ]]; then
    # Re-executed under timeout — run monitoring directly.
    for h in $(echo "$HOSTS_JSON" | python3 -c "import json,sys; [print(h['name']) for h in json.load(sys.stdin)]"); do
      run_host "$h" || echo "[AIX] FAILED: $h"
    done
    echo "[AIX] Done."
  else
    # First invocation: re-execute under timeout with marker env var.
    exec env __TIMEOUT_CHILD=1 timeout "$TIMEOUT_SECS" "$0" --all "$@"
  fi
else
  usage
fi
