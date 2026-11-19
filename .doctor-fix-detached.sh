#!/bin/bash
# Run `openclaw doctor --fix` from OUTSIDE the gateway process tree.
#
# Why: the doctor refuses to run from inside the gateway's own process tree,
# because the repair needs to stop/restart the very gateway that owns it.
#
# The gateway drains gracefully on SIGTERM, which stalls while it waits for
# in-flight turns (including the one that launched this script). So: give it
# a short grace period, then force-stop it. The doctor then runs against the
# same state/config with no gateway owning it, and we restart afterwards.
LOG=/home/keith/.openclaw/workspace/.doctor-fix.log
: > "$LOG"
{
  echo "=== doctor --fix started $(date -Is) ==="
  echo "--- requesting gateway stop (10s grace) ---"
  systemctl --user stop --no-block openclaw-gateway
  for i in $(seq 1 10); do
    state=$(systemctl --user show openclaw-gateway -p ActiveState --value 2>/dev/null)
    echo "    t=${i}s ActiveState=${state}"
    [ "$state" = "active" ] && break
    sleep 1
  done
  if [ "$(systemctl --user show openclaw-gateway -p ActiveState --value 2>/dev/null)" != "inactive" ]; then
    echo "--- forcing gateway stop ---"
    systemctl --user kill --signal=SIGKILL openclaw-gateway 2>&1
    sleep 2
    systemctl --user stop openclaw-gateway 2>&1
  fi
  echo "--- gateway state: $(systemctl --user show openclaw-gateway -p ActiveState --value 2>/dev/null) ---"
  echo "--- running doctor --fix ---"
  openclaw doctor --fix --non-interactive --yes
  echo "--- doctor exit code: $? ---"
  echo "--- restarting gateway ---"
  systemctl --user start openclaw-gateway
  sleep 3
  echo "--- gateway restarted $(date -Is), state=$(systemctl --user is-active openclaw-gateway) ---"
} >> "$LOG" 2>&1
echo "WRAPPER_EXIT=$?" >> "$LOG"
