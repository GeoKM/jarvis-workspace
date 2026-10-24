# VAXcluster health monitor — run instructions

Target: OpenVMS VAXcluster (FUSION 192.168.1.137, RISE 192.168.1.138), OpenVMS VAX V7.3.

## Step 1 — run the health check

```bash
cd /home/keith/.openclaw/workspace/scripts && python3 vms_cluster_health.py
```

It takes roughly 8–12 minutes (telnet sessions to two VAXen, two binary-file
captures, and a UAF read per node for the password expiry check). Use a generous
exec timeout (900000 ms) and poll the session if it has not finished. Exit code
0 = healthy, 1 = fault detected.

The script prints a JSON report with:
- `healthy` (bool) and `errors` (list of current faults)
- per node: `ping`, `telnet`, `uptime`, `cluster_procs`, `interconnect`, `mounts`
- `auth`: group number + hash per node, and `auth_match`
- `password_expiry`: per node — `days_remaining`, `expired`, `login_fails`,
  `raw_pwdchange`, `raw_expires`
- `password_warnings`: list of non-fatal credential warnings
- `opcom`: recent cluster membership events, `current_bad` (unresolved) vs
  `historical_bad_count` (already-resolved, informational only)

## Step 2 — decide

- **`healthy: true`** → do NOT post anything to Telegram. This is a quiet run.
  Record the run in the daily memory file only if something changed.

- **`healthy: false`** → post ONE message to the Telegram group topic
  `-1003981232995`, thread/topic `332`, using the `message` tool with
  `action="send"`, `channel="telegram"`, `target="-1003981232995"`,
  `replyTo="332"`. Keep it brief and factual:
  - what failed (node, interconnect, mount, auth mismatch, OPCOM event)
  - the relevant evidence (device status, error counts, log lines)
  - a suggested next step

  If the script itself fails to run (exception, timeout, malformed output),
  treat that as a fault and report it — an unreachable cluster is a legitimate
  alert, and a broken monitor is also worth surfacing.

- **`password_warnings` non-empty but `healthy: true`** → still a quiet run
  (no Telegram message) UNLESS the password has already expired. The script
  escalates an expired password into `errors`, so an expiry that actually
  breaks the monitor's own login will arrive via the `healthy: false` path.
  A near-expiry warning is advisory only — mention it only if you are already
  posting for another reason.

## Important context (do not re-derive this)

- **`SHOW CLUSTER` is NOT a valid health signal on this image.** It returns
  `%SYSTEM-F-NOPRIV` because `SHOW.EXE` (287 blocks, the only SHOW utility
  present) has no cluster action compiled in. There is no `SHOW_CLUSTER.EXE`
  anywhere in SYSEXE. Do not report this as a fault and do not try to fix it.
- The working health signals are: `SHOW DEVICE DUA0:` (cluster disk mounts),
  `SHOW DEVICE MUA1:`/`MUA2:`/`MUA3:` (interconnect controllers),
  `SHOW SYSTEM` (cluster server processes + uptime), and the OPCOM operator log.
- The cluster authorisation file is `SYS$COMMON:[SYSEXE]CLUSTER_AUTHORIZE.DAT`
  and must be captured with `vms_binfile.py` (fixed settle), never with the
  `$`-prompt waiter — the file is 512 bytes of mostly NUL, so prompt detection
  truncates the capture and yields a false "nodes differ" result.
- The low byte of the group number is 0x7b == 123 == the ASCII `{` character,
  so the `{` byte in the capture IS data. Do not skip it.
- Known historical event: RISE's SIMH crashed 22-OCT-2026 10:08, FUSION
  ejected it at 10:09, RISE rejoined 23-OCT-2026 22:22 as csid 00010003 and
  reached ACTIVE state. The monitor treats events before the last good
  (recovery) event as historical, not current faults.
- SYSTEM password expires around 2-NOV-2026 (changed 3-OCT-2026, 30-day
  lifetime). The monitor now reads the UAF record on each node and reports
  `days_remaining`; it warns at 14 days and escalates to a fault once expired
  (an expired password breaks the monitor's own login). If authentication
  starts failing, check this first — report it as a credential expiry, not a
  cluster fault.
