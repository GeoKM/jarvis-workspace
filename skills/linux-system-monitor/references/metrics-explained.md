# Metrics Explained

This guide explains what each metric measures, what healthy looks like, and what
to investigate when a value looks wrong.

---

## CPU

### `cpu.user` / `cpu.system` / `cpu.idle` (%)

Percentage of CPU time spent in user-space, kernel-space, and idle.

- **Healthy**: `idle` ≥ 70% under normal load, `user` dominates `system`
- **Warning**: `idle` < 30% sustained — system is under load
- **Critical**: `idle` < 10% sustained, or `system` > `user` (kernel churn)
- **Drill-down**: `top -bn1`, `vmstat 1 5`

### `load.1` / `load.5` / `load.15`

Average number of runnable processes across 1, 5, and 15 minute windows.

- **Healthy**: < `nproc` (number of CPU cores)
- **Warning**: > `nproc` sustained for > 5 min
- **Critical**: > 2× `nproc`
- **Note**: Load includes processes blocked on I/O. High load + idle CPU = disk bottleneck.

### `ctx.switches` (per second)

Context switches. Kernel switches between threads.

- **Healthy**: < 100,000/s
- **Warning**: > 500,000/s — may indicate heavy threading or interrupt storm
- **Drill-down**: `vmstat 1`, look at `in` (interrupts) and `cs` (context switches)

### `intr` (per second)

Hardware interrupts serviced.

- **Healthy**: < 10,000/s on typical server/desktop
- **Warning**: Sudden spike — check `cat /proc/interrupts` for offending device

---

## Memory

### `mem.total` / `mem.used` / `mem.free` / `mem.available` (bytes)

Physical memory breakdown.

- **Healthy**: `available` ≥ 20% of `total`
- **Warning**: `available` < 10% of `total`
- **Critical**: OOM killer active (`dmesg | grep -i oom`)
- **Note**: `free` alone is misleading — Linux caches aggressively. Use `available`.

### `mem.swap.used` / `mem.swap.total` (bytes)

Swap file/pool in use.

- **Healthy**: 0 or minimal (a few MB)
- **Warning**: > 1 GB used on a system with > 4 GB RAM — indicates memory pressure
- **Critical**: Swap continuously growing — system is thrashing
- **Drill-down**: `smem`, `cat /proc/meminfo | grep -E 'SwapCached|SwapFree'`

---

## Disk

### `disk.<mount>.total` / `disk.<mount>.used` / `disk.<mount>.avail` (bytes)

Filesystem space. `<mount>` is sanitised (slashes → underscores).

- **Healthy**: ≥ 20% free on system volumes, ≥ 10% on data volumes
- **Warning**: < 10% free on any volume
- **Critical**: < 5% free — risk of processes failing to write

### `disk.<mount>.inodes_total` / `disk.<mount>.inodes_used`

Inode counts (files/directories).

- **Healthy**: < 80% inode usage
- **Critical**: inode exhaustion causes "No space left on device" even with free bytes

### `io.read_bytes` / `io.write_bytes` (bytes/sec)

Block device I/O throughput (aggregated across all devices).

- **Healthy**: Variable, depends on workload
- **Warning**: Sustained > 100 MB/s on spinning disks (normal on SSD)
- **Drill-down**: `iostat -xz 1 5`, check `await` and `%util` per device

### `io.r_await` / `io.w_await` (ms)

Average read/write latency per I/O operation.

- **Healthy**: < 10 ms for SSDs, < 20 ms for spinning disks
- **Warning**: > 50 ms — I/O queue building up
- **Critical**: > 500 ms — severe bottleneck, likely HW issue

---

## Network

### `net.rx_bytes` / `net.tx_bytes` (bytes/sec)

Aggregate network receive/transmit throughput.

- **Healthy**: Well below interface link speed
- **Warning**: > 80% of link speed sustained
- **Critical**: Interface errors or drops > 0

### `net.rx_errs` / `net.tx_errs` / `net.rx_drop` / `net.tx_drop` (count)

Interface error and drop counts. Cumulative since boot.

- **Healthy**: All zero or near-zero
- **Warning**: Any value > 0 on a normally-operating interface
- **Critical**: Errors growing per snapshot interval

### `net.conn.tcp.established` / `net.conn.tcp.timewait` / `net.conn.tcp.synrecv`

TCP connection states.

- **Healthy**: Established count normal for workload, TIME_WAIT < 1000
- **Warning**: TIME_WAIT > 5000 — connection reuse issues (often HTTP keepalive related)
- **Critical**: Many connections in `CLOSE_WAIT` — application not closing sockets

---

## Processes

### `proc.count` (total process count)

Number of running processes/threads.

- **Healthy**: Stable, no runaway growth
- **Warning**: Rapid growth over short period — possible fork bomb or exploit
- **Drill-down**: `ps aux --sort=-%cpu | head -20`

### `proc.zombies`

Zombie process count.

- **Healthy**: 0
- **Warning**: > 0 — parent process is not reaping children
- **Critical**: > 5 — investigate parent processes

### `proc.top_cpu` / `proc.top_mem`

Top 5 processes by CPU% and memory usage.

- **Healthy**: Varied, expected processes dominate
- **Note**: Included for quick triage — snapshot also has full process list

---

## Services

### `service.<name>.state`

State of a named systemd service.

- Values: `active`, `inactive`, `failed`, `unknown`
- **Critical**: Any expected service in `failed` state

Service list monitored (configured in `hosts.d/<hostname>.yaml`):
- `ssh` — OpenSSH server
- `systemd-journald` — syslog
- `ntp` / `chrony` — time sync
- `firewalld` / `ufw` — firewall
- Custom services as needed

---

## Security

### `security.ssh_failures` (count since boot)

Failed SSH authentication attempts.

- **Healthy**: 0–10 on an internet-facing machine (port scans are constant)
- **Warning**: > 50 — possible brute-force attack in progress
- **Critical**: > 500 — active compromise attempt; check `journalctl -u ssh | grep Failed`
- **Note**: Should be evaluated relative to exposure (internet-facing vs. LAN-only)

### `security.sudo_failures` (count since boot)

Failed `sudo` attempts.

- **Healthy**: 0 or very few
- **Warning**: Any unexpected count
- **Critical**: Many failures in short window — possible privilege escalation attempt

### `security.last_logins` (last 5)

Recent successful logins (user, tty, source IP, timestamp).

---

## Time

### `time.ntp_offset` (ms)

NTP time offset. Only present if `ntpstat` or `chronyc sources` succeeds.

- **Healthy**: < 100 ms
- **Warning**: 100–500 ms
- **Critical**: > 500 ms — clock drift risk; check NTP service

### `time.tz`

System timezone string (e.g., `AEST-10`).

---

## Temperature (optional)

### `temp.cpu` / `temp.core_N` (°C)

CPU core temperatures, if `sensors` is available.

- **Healthy**: < 80°C under load
- **Warning**: 80–90°C sustained — thermal throttling
- **Critical**: > 90°C — CPU will throttle; possible cooling failure
