# Threshold Configuration

Thresholds define the boundaries between OK / WARNING / CRITICAL for each metric.
They are applied by `parse-report.py` when analysing a snapshot.

## Defaults

Defaults are defined in `scripts/threshold-defaults.yaml`. They apply to all hosts
unless overridden in a per-host config.

## Per-Host Overrides

Create `~/lab-docs/monitoring/hosts.d/<hostname>.yaml` to override defaults for a
specific host. Only include the keys you want to change.

## Threshold Keys

All keys are optional. Omitted keys fall back to the default.

```yaml
cpu:
  idle_warn: 30.0        # % CPU idle below which WARNING fires
  idle_crit: 10.0        # % CPU idle below which CRITICAL fires
  load_warn: null        # load threshold multiplier over nproc (null = disabled)
  load_crit: null
  ctx_warn: 500000        # context switches/sec above which WARNING fires

memory:
  avail_warn: 10          # % of total memory below which WARNING fires
  avail_crit: 5           # % of total memory below which CRITICAL fires
  swap_warn: 1073741824   # swap used (bytes) above which WARNING fires

disk:
  # Per-mount thresholds. Key = sanitised mount point (slashes → underscores)
  _:
    free_pct_warn: 10     # % free below which WARNING fires
    free_pct_crit: 5      # % free below which CRITICAL fires
  _home:
    free_pct_warn: 15     # stricter threshold for /home

network:
  errs_warn: 0            # interface errors above which WARNING fires
  drops_warn: 0           # interface drops above which WARNING fires
  timewait_warn: 5000     # TCP TIME_WAIT connections above which WARNING fires
  conn_max: 10000         # total TCP connections above which WARNING fires

processes:
  zombie_warn: 1          # zombie processes above which WARNING fires
  conn_warn: 500          # total process count above which WARNING fires

services:
  # Map of service-name: expected-state
  # Any service not in desired state triggers CRITICAL
  desired:
    ssh: active
    systemd-journald: active
    ntp: active

security:
  ssh_failures_warn: 50   # failed SSH auths above which WARNING fires
  sudo_failures_warn: 10  # failed sudo attempts above which WARNING fires

temp:
  warn: 80                # °C above which WARNING fires
  crit: 90                # °C above which CRITICAL fires
```

## Example Per-Host Override

File: `~/lab-docs/monitoring/hosts.d/xaviernv.yaml`

```yaml
# XavierNV is an ARM SBC with limited RAM — stricter memory threshold
memory:
  avail_warn: 20
  avail_crit: 10

# XavierNV runs cooler — relax thermal threshold
temp:
  warn: 85
  crit: 95

# XavierNV is on LAN — SSH failures less concerning
security:
  ssh_failures_warn: 200
```

## Applying Thresholds

Thresholds are applied automatically by `parse-report.py`. You do not pass a
threshold file explicitly — the script reads `hosts.d/<hostname>.yaml` if it exists,
merges it over the defaults, and applies the result.

## Retrieving Defaults

To see the full defaults without reading the YAML file directly:

```bash
python3 -c "import yaml; print(yaml.dump(yaml.safe_load(open('scripts/threshold-defaults.yaml'))))"
```
