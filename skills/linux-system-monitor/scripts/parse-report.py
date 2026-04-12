#!/usr/bin/env python3
"""
parse-report.py — Apply thresholds to a metrics JSON snapshot and emit a digest.
Reads:
  - snapshot JSON on stdin
  - ~/lab-docs/monitoring/hosts.d/<hostname>.yaml for per-host thresholds (optional)
  - skills/linux-system-monitor/scripts/threshold-defaults.yaml for defaults
Writes:
  - ~/lab-docs/monitoring/snapshots/<hostname>/<hostname>-<ts>.json  (annotated snapshot)
  - ~/lab-docs/monitoring/alerts/<hostname>-<date>.log  (new alerts only)
Prints a human-readable digest to stdout.
"""

import sys, json, yaml
from datetime import datetime, date, timezone
from pathlib import Path

SKILL_SCRIPTS = Path(__file__).parent
DEFAULTS_FILE = SKILL_SCRIPTS / "threshold-defaults.yaml"
LAB_DOCS = Path.home() / "lab-docs" / "monitoring"


def load_thresholds(hostname: str) -> dict:
    defaults = yaml.safe_load(DEFAULTS_FILE.read_text())
    host_override = LAB_DOCS / "hosts.d" / f"{hostname}.yaml"
    if host_override.exists():
        override = yaml.safe_load(host_override.read_text())
        for top_key, top_val in override.items():
            if top_key in defaults and isinstance(top_val, dict):
                for sub_key, sub_val in top_val.items():
                    if isinstance(sub_val, dict) and sub_key in defaults[top_key]:
                        defaults[top_key][sub_key].update(sub_val)
                    else:
                        defaults[top_key][sub_key] = sub_val
            else:
                defaults[top_key] = top_val
    return defaults


def pct_used(total: int, avail: int) -> float:
    if total == 0:
        return 0.0
    return round(100 * (total - avail) / total, 1)


def level(severity: str) -> str:
    return {"warning": "⚠ WARNING", "critical": "🚨 CRITICAL", "ok": "✅ OK"}.get(severity, severity)


def check_cpu(data: dict, t: dict) -> tuple:
    alerts, lines = [], []
    idle = data.get("cpu", {}).get("idle_pct", 100.0)
    load1 = data.get("load", {}).get("1m", 0)
    nproc = data.get("nproc", 1)
    severity = "ok"
    if idle < t["cpu"]["idle_crit"]:
        severity = "critical"
    elif idle < t["cpu"]["idle_warn"]:
        severity = "warning"
    if severity != "ok":
        alerts.append({"metric": "cpu.idle_pct", "severity": severity, "value": idle})
    lines.append(f"  CPU    idle={idle}%  load_1m={load1}  (nproc={nproc})  [{level(severity)}]")
    return alerts, lines


def check_memory(data: dict, t: dict) -> tuple:
    alerts, lines = [], []
    mem = data.get("memory", {})
    total = mem.get("total", 1)
    avail = mem.get("available", 0)
    avail_pct = 0.0 if total == 0 else min(round(100 * avail / total, 1), 100.0)
    swap_used = mem.get("swap_used", 0)
    severity = "ok"
    if avail_pct < t["memory"]["avail_crit"]:
        severity = "critical"
    elif avail_pct < t["memory"]["avail_warn"]:
        severity = "warning"
    if severity != "ok":
        alerts.append({"metric": "memory.available_pct", "severity": severity, "value": avail_pct})
    swap_sev = "ok"
    if swap_used > t["memory"]["swap_warn"]:
        swap_sev = "warning"
        alerts.append({"metric": "memory.swap_used", "severity": "warning", "value": swap_used})
    mem_sev = severity if severity != "ok" else swap_sev
    lines.append(f"  Memory avail={avail_pct}%  swap={_bytes(swap_used)}  [{level(mem_sev)}]")
    return alerts, lines


def check_disk(data: dict, t: dict) -> tuple:
    alerts, lines = [], []
    disk_defaults = t.get("disk", {}).get("_", {})
    for vol in data.get("disk", []):
        mount = vol.get("mount", "_")
        override_key = f"_{mount.replace('_', '__')}"
        overrides = t.get("disk", {}).get(override_key, {})
        warn = overrides.get("free_pct_warn", disk_defaults.get("free_pct_warn", 10))
        crit = overrides.get("free_pct_crit", disk_defaults.get("free_pct_crit", 5))
        total = int(vol.get("total", 0))
        avail = int(vol.get("avail", 0))
        raw_mount = vol.get("raw_mount", mount)
        used_pct = 0.0 if total == 0 else pct_used(total, avail)
        free_pct = round(100 * avail / total, 1) if total else 0
        severity = "ok"
        if free_pct < crit:
            severity = "critical"
        elif free_pct < warn:
            severity = "warning"
        if severity != "ok":
            alerts.append({"metric": f"disk.{mount}.free_pct", "severity": severity, "value": free_pct})
        lines.append(f"  Disk   {raw_mount:<30} {used_pct}% used  {free_pct}% free  [{level(severity)}]")
    return alerts, lines


def check_network(data: dict, t: dict) -> tuple:
    alerts, lines = [], []
    net = data.get("network", {})
    tcp = net.get("tcp", {})
    rx_errs = net.get("rx_errs", 0)
    tx_errs = net.get("tx_errs", 0)
    rx_drop = net.get("rx_drop", 0)
    tx_drop = net.get("tx_drop", 0)
    tw = tcp.get("time_wait", 0)
    est = tcp.get("established", 0)
    sev = "ok"
    if rx_errs > t["network"]["errs_warn"] or tx_errs > t["network"]["errs_warn"]:
        sev = "warning"
        alerts.append({"metric": "network.errors", "severity": "warning", "value": rx_errs + tx_errs})
    if rx_drop > t["network"]["drops_warn"] or tx_drop > t["network"]["drops_warn"]:
        sev = "warning"
        alerts.append({"metric": "network.drops", "severity": "warning", "value": rx_drop + tx_drop})
    if tw > t["network"]["timewait_warn"]:
        sev = "warning"
        alerts.append({"metric": "network.tcp.time_wait", "severity": "warning", "value": tw})
    if est + tw > t["network"]["conn_max"]:
        sev = "warning"
        alerts.append({"metric": "network.tcp.conn_total", "severity": "warning", "value": est + tw})
    lines.append(f"  Net    rx_err={rx_errs}  tx_err={tx_errs}  rx_drop={rx_drop}  tx_drop={tx_drop}  TCP: est={est}  tw={tw}  [{level(sev)}]")
    return alerts, lines


def check_processes(data: dict, t: dict) -> tuple:
    alerts, lines = [], []
    proc = data.get("processes", {})
    zombies = proc.get("zombies", 0)
    count = proc.get("count", 0)
    sev = "ok"
    if zombies >= t["processes"]["zombie_warn"]:
        sev = "warning"
        alerts.append({"metric": "processes.zombies", "severity": "warning", "value": zombies})
    if count > t["processes"]["proc_warn"]:
        sev = "warning"
        alerts.append({"metric": "processes.count", "severity": "warning", "value": count})
    lines.append(f"  Procs  total={count}  zombies={zombies}  [{level(sev)}]")
    return alerts, lines


def check_services(data: dict, t: dict) -> tuple:
    alerts, lines = [], []
    desired = t.get("services", {}).get("desired", {})
    actual = data.get("services", {})
    sev = "ok"
    for svc, expected in desired.items():
        actual_state = actual.get(svc, "unknown")
        if actual_state.lower() != expected.lower():
            sev = "critical"
            alerts.append({"metric": f"service.{svc}", "severity": "critical", "value": actual_state, "expected": expected})
            lines.append(f"  Svc    {svc:<30} {actual_state} (expected: {expected})  [{level('critical')}]")
    if sev == "ok":
        lines.append(f"  Svc    all critical services active  [{level('ok')}]")
    return alerts, lines


def check_security(data: dict, t: dict) -> tuple:
    alerts, lines = [], []
    sec = data.get("security", {})
    ssh_fails = sec.get("ssh_failures", 0)
    sudo_fails = sec.get("sudo_failures", 0)
    sev = "ok"
    if ssh_fails >= t.get("security", {}).get("ssh_failures_warn", 50):
        sev = "warning"
        alerts.append({"metric": "security.ssh_failures", "severity": "warning", "value": ssh_fails})
    if sudo_fails >= t.get("security", {}).get("sudo_failures_warn", 10):
        sev = "warning"
        alerts.append({"metric": "security.sudo_failures", "severity": "warning", "value": sudo_fails})
    logins = sec.get("last_logins", [])
    last = logins[0] if logins else {}
    last_login_str = f"{last.get('user','?')} from {last.get('from','?')}" if last else "none"
    lines.append(f"  Security  ssh_fails={ssh_fails}  sudo_fails={sudo_fails}  last_login={last_login_str}  [{level(sev)}]")
    return alerts, lines


def check_docker(data: dict, t: dict) -> tuple:
    alerts, lines = [], []
    docker = data.get("docker", {})
    avail_val = docker.get("available", False)
    if not avail_val or str(avail_val).lower() in ("false", "no", "0"):
        lines.append(f"  Docker  not available  [✅ OK]")
        return alerts, lines

    running = docker.get("containers_running", 0)
    total = docker.get("containers_total", 0)
    unhealthy = docker.get("unhealthy", 0)
    restarting = docker.get("restarting", 0)

    sev = "ok"
    if int(unhealthy) > 0:
        sev = "warning"
        alerts.append({"metric": "docker.unhealthy", "severity": "warning", "value": unhealthy})
    if int(restarting) > 0:
        sev = "warning"
        alerts.append({"metric": "docker.restarting", "severity": "warning", "value": restarting})

    containers = docker.get("containers", [])
    top_cpu = sorted(containers, key=lambda c: float(c.get("cpu", "0%").rstrip("%")), reverse=True)[:3]
    top_mem = sorted(containers, key=lambda c: float(c.get("mem", "0%").rstrip("%")), reverse=True)[:3]
    cpu_top = ", ".join(f"{c['cpu']} {c['name']}" for c in top_cpu) if top_cpu else "none"
    mem_top = ", ".join(f"{c['mem']} {c['name']}" for c in top_mem) if top_mem else "none"

    if int(running) == 0:
        docker_sev = "OK"
    elif sev != "ok":
        docker_sev = "⚠ WARNING"
    else:
        docker_sev = "✅ OK"
    lines.append(f"  Docker  running={running}/{total}  unhealthy={unhealthy}  restarting={restarting}  [{docker_sev}]")
    lines.append(f"  Top CPU: {cpu_top}")
    lines.append(f"  Top MEM: {mem_top}")
    return alerts, lines


def check_packages(data: dict, t: dict) -> tuple:
    alerts, lines = [], []
    pkg = data.get("packages", {})
    manager = pkg.get("manager", "unknown")
    total = pkg.get("total", 0)
    security = pkg.get("security", 0)
    if manager == "unknown":
        lines.append(f"  Pkgs   package manager not detected  [✅ OK]")
        return alerts, lines
    sev = "ok"
    pkg_thresh = t.get("packages", {"warn": 50, "security_warn": 1})
    if security >= pkg_thresh.get("security_warn", 1):
        sev = "critical"
        alerts.append({"metric": "packages.security", "severity": "critical", "value": security})
    elif total >= pkg_thresh.get("warn", 50):
        sev = "warning"
        alerts.append({"metric": "packages.total", "severity": "warning", "value": total})
    lines.append(f"  Pkgs   {total} upgradable ({security} security)  [{level(sev)}]")
    return alerts, lines


def check_temp(data: dict, t: dict) -> tuple:
    alerts, lines = [], []
    temps = data.get("temperature", {})
    if not temps:
        return [], []
    worst = max(temps.values())
    sev = "ok"
    if worst >= t["temp"]["crit"]:
        sev = "critical"
        alerts.append({"metric": "temperature.max", "severity": "critical", "value": worst})
    elif worst >= t["temp"]["warn"]:
        sev = "warning"
        alerts.append({"metric": "temperature.max", "severity": "warning", "value": worst})
    lines.append(f"  Temp   max={worst}C  zones={temps}  [{level(sev)}]")
    return alerts, lines


def _bytes(b: int) -> str:
    for unit in ["B", "KiB", "MiB", "GiB", "TiB"]:
        if abs(b) < 1024:
            return f"{b:.1f}{unit}"
        b /= 1024
    return f"{b:.1f}PiB"


def main():
    hostname = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON: {e}", file=sys.stderr)
        sys.exit(1)

    ts = data.get("timestamp", datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'))
    nproc = data.get("nproc", 1)
    uptime_h = round(data.get("uptime_seconds", 0) / 3600, 1)
    kernel = data.get("kernel", "?")
    arch = data.get("arch", "?")
    thresholds = load_thresholds(hostname)

    all_alerts = []
    lines = []

    a, l = check_cpu(data, thresholds); all_alerts.extend(a); lines.extend(l)
    a, l = check_memory(data, thresholds); all_alerts.extend(a); lines.extend(l)
    a, l = check_disk(data, thresholds); all_alerts.extend(a); lines.extend(l)
    a, l = check_network(data, thresholds); all_alerts.extend(a); lines.extend(l)
    a, l = check_processes(data, thresholds); all_alerts.extend(a); lines.extend(l)
    a, l = check_services(data, thresholds); all_alerts.extend(a); lines.extend(l)
    a, l = check_security(data, thresholds); all_alerts.extend(a); lines.extend(l)
    a, l = check_packages(data, thresholds); all_alerts.extend(a); lines.extend(l)
    a, l = check_temp(data, thresholds); all_alerts.extend(a); lines.extend(l)
    a, l = check_docker(data, thresholds); all_alerts.extend(a); lines.extend(l)

    top_cpu = data.get("processes", {}).get("top_cpu", [])
    top_mem = data.get("processes", {}).get("top_mem", [])
    cpu_top = ", ".join(f"{p['cpu']}% {p['cmd']}" for p in top_cpu[:3]) if top_cpu else "none"
    mem_top = ", ".join(f"{p['mem']}% {p['cmd']}" for p in top_mem[:3]) if top_mem else "none"
    lines.append(f"  Top CPU: {cpu_top}")
    lines.append(f"  Top MEM: {mem_top}")

    if any(a["severity"] == "critical" for a in all_alerts):
        summary_sev = "CRITICAL"
    elif any(a["severity"] == "warning" for a in all_alerts):
        summary_sev = "WARNING"
    else:
        summary_sev = "OK"

    sep = "=" * 60
    print(f"\n{sep}")
    print(f"  {hostname.upper()}  |  {ts}  |  {summary_sev}")
    print(f"  {kernel}  ({arch})  |  {nproc} cores  |  uptime={uptime_h}h")
    print(sep)
    for line in lines:
        print(line)
    print(sep)
    if all_alerts:
        print(f"  {len(all_alerts)} alert(s)")
        for a in all_alerts:
            print(f"    [{a['severity'].upper()}] {a['metric']} = {a['value']}")
    else:
        print(f"  No alerts — all metrics nominal")
    print()

    # Write snapshot
    out_dir = LAB_DOCS / "snapshots" / hostname
    out_dir.mkdir(parents=True, exist_ok=True)
    ts_safe = ts.replace(":", "").replace("-", "").replace("T", "-")
    snap_file = out_dir / f"{hostname}-{ts_safe}.json"
    enriched = dict(data)
    enriched["_alerts"] = all_alerts
    enriched["_summary_severity"] = summary_sev
    enriched["_checked_at"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    snap_file.write_text(json.dumps(enriched, indent=2))
    print(f"  Snapshot saved: {snap_file.relative_to(LAB_DOCS)}")

    # Append alerts to daily log
    if all_alerts:
        alert_log = LAB_DOCS / "alerts" / f"{hostname}-{date.today().isoformat()}.log"
        alert_log.parent.mkdir(parents=True, exist_ok=True)
        with open(alert_log, "a") as f:
            f.write(f"\n[{ts}] {hostname.upper()} {summary_sev}\n")
            for a in all_alerts:
                f.write(f"  [{a['severity'].upper()}] {a['metric']} = {a['value']}\n")


    # Snapshot written successfully even if alerts were found — always exit 0
    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise  # pass through sys.exit(0) from main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
