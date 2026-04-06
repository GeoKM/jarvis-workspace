---
name: linux-system-monitor
description: >
  Run periodic Linux system monitoring across multiple hosts via SSH, collecting
  CPU, memory, disk, network, process, service, and security metrics as JSON
  snapshots. Use when: (1) Keith asks to check the status of Hebei or XavierNV,
  (2) a periodic monitoring run is triggered via cron or heartbeat, (3) a
  host appears slow or unwell and diagnostic data is needed, (4) adding a new
  host to the monitoring rotation. Trigger phrases: "check hebei", "check xavier",
  "run monitor", "system status", "host diagnostics", "monitoring snapshot".
---

# Linux System Monitor

Collects and analyses system metrics from Linux hosts over SSH (or locally for
Hebei) using only standard system tools. No agents required.

## Host Inventory

Hosts are defined in `~/lab-docs/monitoring/hosts.d/hosts.yaml`. Each entry
specifies the SSH target and connection style. The first entry is the default
when no host is specified.

```yaml
hosts:
  - name: hebei
    ssh: false          # localhost — no SSH needed
  - name: xaviernv
    ssh: true
    host: 192.168.1.40  # IP or hostname — adjust as needed
    user: keith
```

To add a new host, append an entry to `hosts.d/hosts.yaml`.

## Snapshot Storage

All JSON snapshots live under `~/lab-docs/monitoring/snapshots/<hostname>/`:

```
~/lab-docs/monitoring/
├── snapshots/
│   └── <hostname>/
│       └── <hostname>-<YYYYMMDD-HHMMSS>.json
├── hosts.d/
│   ├── hosts.yaml        # inventory (can be git-tracked)
│   └── <hostname>.yaml   # per-host threshold overrides
└── alerts/
    └── <hostname>-<date>.log
```

## Scripts

- **`scripts/collect-metrics.sh`** — Connects to a host (or runs locally) and
  emits raw JSON to stdout. Reads `hosts.d/hosts.yaml` for connection details.
  No elevated privileges required; reads from `/proc`, `sysfs`, and standard
  CLI tools (`free`, `df`, `ss`, etc.).

- **`scripts/parse-report.py`** — Reads a snapshot JSON file, applies
  per-host thresholds from `hosts.d/<hostname>.yaml` (or defaults), and
  emits a human-readable digest to stdout. Writes an annotated snapshot and
  any triggered alerts to the output directories.

- **`scripts/run-monitor.sh`** — Orchestrates the full pipeline. Runs
  `collect-metrics.sh`, pipes output to `parse-report.py`, writes snapshots
  to disk, and prints a digest. Supports `--host <name>` to target a specific
  host, or `--all` to run against every host in `hosts.yaml` sequentially.

## Running

```bash
# Check a specific host
./scripts/run-monitor.sh --host hebei
./scripts/run-monitor.sh --host xaviernv

# Run against all configured hosts
./scripts/run-monitor.sh --all

# Run collect + parse manually
./scripts/collect-metrics.sh hebei | python3 scripts/parse-report.py hebei
```

## Adding a New Host

1. Add the host to `~/lab-docs/monitoring/hosts.d/hosts.yaml`
2. Optionally create `~/lab-docs/monitoring/hosts.d/<hostname>.yaml` with
   threshold overrides (see `references/thresholds.md` for available keys)
3. Verify SSH works: `ssh keith@<host>` (SSH agent should have the key)
4. Run `./scripts/run-monitor.sh --host <hostname>` to confirm it works

## Reference Files

- `references/metrics-explained.md` — What each metric means, normal ranges,
  and failure-mode indicators for each category
- `references/thresholds.md` — Full list of configurable thresholds, their
  defaults, and examples of per-host overrides
