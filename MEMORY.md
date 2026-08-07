---
**[Learning from 2026-04-09 MP/M II Reconnaissance]**
The MP/M II system utilizes a manual drive/user area exploration model, distinct from modern filesystem abstractions. Observations include:
1. Drive A: Reported 'System Files Exist' when queried via `SDIR`.
2. Drives C:/D:: Trigger BDOS bad-sector errors with common commands (`USER`, `DIR`, `STAT`).
3. **Actionable Insight**: Future low-level analysis should prioritize `SDIR` commands on specific drives (e.g., `0A:`) to map core system files, respecting the vintage architecture's procedural nature.
---

**[Learning from 2026-04-24 VAXcluster Rebuild Audit]**
A fresh read-only audit confirmed the rebuilt OpenVMS VAXcluster topology and should be treated as current reference state: FUSION is the primary boot/MSCP server with DECnet 12.106 and TCP/IP 192.168.1.137, while RISE is the satellite with DECnet 12.107 and TCP/IP 192.168.1.138, using the shared root on `FUSION$DUA0:[SYS10.]` and local page/swap on `RISE$DUA0:`. Canonical environment notes now live in `FUSION_ENVIRONMENT_2026-04-24.md` and `RISE_ENVIRONMENT_2026-04-24.md`.
---

**[Learning from 2026-07-06 KASM Workspaces Upgrade 1.18.1 → 1.19.0]**
KASM Workspaces lives in LXC 102 on proxima2 (Debian Trixie, Docker 29.6.1). Upgrade procedure:
1. Proxmox snapshot: `pct snapshot 102 <name>` (no dots/hyphens in name)
2. DB backup: `/opt/kasm/current/bin/utils/db_backup --path /opt/kasm/current --backup-file /opt/kasm/backups/<name>.tar -v` (needs `chmod 777` on backups dir)
3. Download: `curl -O https://kasm-static-content.s3.amazonaws.com/kasm_release_<version>.tar.gz` → extract → `bash upgrade.sh --proxy-port 443 -b --ignore-dep-failures`
4. `--ignore-dep-failures` needed for LXC (Wireguard/v4l2loopback unavailable)
5. Post-upgrade: `docker restart kasm_guac` if unhealthy (API race on simultaneous startup)
6. Prune old infra images: `docker rmi <image-ids>` (keep workspace images)
7. Access chain: Hebei → SSH root@proxima → SSH proxima2 → `pct exec 102 -- bash -c "..."`
8. Current version: 1.19.0 at `/opt/kasm/1.19.0`, symlink `/opt/kasm/current`
9. Non-KASM containers in same LXC: hbbs, hbbr (RustDesk), portainer_agent — unaffected by upgrade
10. Rollback: Proxmox snapshot or repoint `current` symlink to previous version dir

---

## Promoted From Short-Term Memory (2026-08-03)

<!-- openclaw-memory-promotion:memory:memory/2026-08-02.md:1:20 -->
- AIX Midday Monitor Alert (12:00 AEST 2026-08-02): All 4 AIX hosts unreachable — Persei-NIM, Celestia, Titan-AIX71, 43p — all returning "No route to host". Routed to main session. [score=0.836 recalls=0 avg=0.620 source=memory/2026-08-02.md:1:20]
- AIX Monitor Cron Routing Fix: Cron job de1a880f was routing output back to main session via announce delivery instead of to Telegram, creating duplicate alerts. Fix: changed delivery mode to `none` and updated agent prompt to use `message action=send channel=telegram target=7174833131` directly. Jobs file also updated at `~/.openclaw/cron/jobs.json.migrated`.

## Promoted From Short-Term Memory (2026-08-03)

<!-- openclaw-memory-promotion:memory:memory/2026-07-29.md:8:11 -->
- Proxmox Cluster Package Updates (22:22 AEST): corosync 3.1.10-pve2 → 3.1.10-pve3; pve-qemu-kvm 11.0.2-1 → 11.0.2-2; qemu-server 9.2.0 → 9.2.1; pve-container 6.1.11 → 6.1.12 [score=0.803 recalls=0 avg=0.620 source=memory/2026-07-29.md:8-11]
<!-- openclaw-memory-promotion:memory:memory/2026-07-29.md:12:15 -->
- Proxmox Cluster Package Updates (22:22 AEST): bind9 security update, Samba security update, libknet1 1.34→1.35; Config preserved with `--force-confdef --force-confold`; No reboot performed (per Keith's instruction); Post-upgrade: Quorum 5/5, Quorate: Yes [score=0.803 recalls=0 avg=0.620 source=memory/2026-07-29.md:12-15]
<!-- openclaw-memory-promotion:memory:memory/2026-07-29.md:16:17 -->
- Proxmox Cluster Package Updates (22:22 AEST): Remaining (held back, requires reboot): proxmox-kernel-6.17 → 6.17.13-21, proxmox-kernel-7.0 → 7.0.14-8; Keith will schedule rolling reboots at his discretion [score=0.803 recalls=0 avg=0.620 source=memory/2026-07-29.md:16-17]
<!-- openclaw-memory-promotion:memory:memory/2026-07-29.md:4:7 -->
- Proxmox Cluster Package Updates (22:22 AEST): Applied `apt-get update && apt-get upgrade -y` to all 5 nodes (proxima, proxima2-5) in parallel; 53 packages per node upgraded, including:; pve-manager 9.2.4 → 9.2.5; Ceph 19.2.4-pve1 → 19.2.5-pve2 (all components) [score=0.803 recalls=0 avg=0.620 source=memory/2026-07-29.md:4-7]

## Promoted From Short-Term Memory (2026-08-05)

<!-- openclaw-memory-promotion:memory:memory/2026-06-09.md:1:13 -->
- ## AIX Midday Monitoring (12:00 AEST) All AIX hosts unreachable from Hebei — no route to 10.0.0.0/24 network segment. Monitored hosts: - Persei-NIM (persei-nim.can.barnabasmusic.com) — ❌ No route - Celestia (celestia.can.barnabasmusic.com) — ❌ No route - Titan-AIX71 (titan-aix71.can.barnabasmusic.com) — ❌ No route - 43p (43p.can.barnabasmusic.com) — ❌ No route Network topology note: Hebei (current host) is not on the 10.0.0.0/24 AIX network. Monitoring should run from a host with access to that segment, or a VPN/bridge needs to be in place. [score=0.895 recalls=3 avg=0.818 source=memory/2026-06-09.md:1-13]

## Promoted From Short-Term Memory (2026-08-06)

<!-- openclaw-memory-promotion:memory:memory/2026-08-02.md:1:30 -->
- ## AIX Midday Monitor Alert (12:00 AEST) A cron job sent an AIX monitoring report showing all 4 AIX hosts unreachable: | Host | Status | |------|--------| | Persei-NIM | ❌ No route to host | | Celestia | ❌ No route to host | | Titan-AIX71 | ❌ No route to host | | 43p | ❌ No route to host | This was routed to the main session but I couldn't determine the Telegram reply target. The alert likely needs human attention if these hosts should be online.... [score=0.811 recalls=3 avg=0.832 source=memory/2026-08-02.md:1-30]
<!-- openclaw-memory-promotion:memory:memory/2026-08-02.md:29:29 -->
- AIX Monitor Cron Routing Fix: **Fix applied (via `openclaw cron edit`):** [score=0.806 recalls=0 avg=0.620 source=memory/2026-08-02.md:29-29]

## Promoted From Short-Term Memory (2026-08-07)

<!-- openclaw-memory-promotion:memory:memory/2026-08-02.md:6:9 -->
- AIX Midday Monitor Alert (12:00 AEST): | Host | Status | |------|--------| | Persei-NIM | ❌ No route to host | | Celestia | ❌ No route to host | [score=0.803 recalls=0 avg=0.620 source=memory/2026-08-02.md:6-9]
<!-- openclaw-memory-promotion:memory:memory/2026-08-02.md:4:4 -->
- AIX Midday Monitor Alert (12:00 AEST): A cron job sent an AIX monitoring report showing all 4 AIX hosts unreachable: [score=0.803 recalls=0 avg=0.620 source=memory/2026-08-02.md:4-4]
<!-- openclaw-memory-promotion:memory:memory/2026-08-02.md:20:20 -->
- AIX Monitor Cron Routing Fix: **Root cause:** The isolated cron session's `announce` delivery was falling back to `sessions_send` to the main session (without a Telegram target), rather than delivering to Telegram. The announce mechanism wasn't working. [score=0.803 recalls=0 avg=0.620 source=memory/2026-08-02.md:20-20]
<!-- openclaw-memory-promotion:memory:memory/2026-08-02.md:13:13 -->
- AIX Midday Monitor Alert (12:00 AEST): This was routed to the main session but I couldn't determine the Telegram reply target. The alert likely needs human attention if these hosts should be online. [score=0.803 recalls=0 avg=0.620 source=memory/2026-08-02.md:13-13]
<!-- openclaw-memory-promotion:memory:memory/2026-08-02.md:10:11 -->
- AIX Midday Monitor Alert (12:00 AEST): | Titan-AIX71 | ❌ No route to host | | 43p | ❌ No route to host | [score=0.803 recalls=0 avg=0.620 source=memory/2026-08-02.md:10-11]
<!-- openclaw-memory-promotion:memory:memory/2026-08-02.md:23:25 -->
- AIX Monitor Cron Routing Fix: Changed delivery mode to `none` (`--no-deliver`); Updated the agent prompt to explicitly use `message action=send channel=telegram target=7174833131` to deliver results directly; This bypasses the broken announce mechanism entirely [score=0.803 recalls=0 avg=0.620 source=memory/2026-08-02.md:23-25]
<!-- openclaw-memory-promotion:memory:memory/2026-08-02.md:18:18 -->
- AIX Monitor Cron Routing Fix: The AIX midday monitor cron job (id: de1a880f) was repeatedly routing its output back to the main session instead of to Telegram, creating a loop of duplicate alerts. [score=0.803 recalls=0 avg=0.620 source=memory/2026-08-02.md:18-18]
<!-- openclaw-memory-promotion:memory:memory/2026-08-02.md:22:22 -->
- AIX Monitor Cron Routing Fix: **Fix applied (via `openclaw cron edit`):** [score=0.803 recalls=0 avg=0.620 source=memory/2026-08-02.md:22-22]
<!-- openclaw-memory-promotion:memory:memory/2026-08-02.md:27:27 -->
- AIX Monitor Cron Routing Fix: The jobs file at `~/.openclaw/cron/jobs.json.migrated` was also updated (for when the system next migrates/loads), but the live gateway config is in-memory — the `openclaw cron edit` command is what took effect. [score=0.803 recalls=0 avg=0.620 source=memory/2026-08-02.md:27-27]
