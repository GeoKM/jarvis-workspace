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

## Promoted From Short-Term Memory (2026-07-30)

<!-- openclaw-memory-promotion:memory:memory/2026-07-24.md:11:12 -->
- AIX Midday Monitor — 12:00 AEST: | titan-aix71 | ❌ No route to host | | 43p | ❌ No route to host | [score=0.818 recalls=0 avg=0.620 source=memory/2026-07-24.md:11-12]
<!-- openclaw-memory-promotion:memory:memory/2026-07-24.md:17:20 -->
- AIX Midday Monitor — 12:00 AEST: Persei-NIM: 2026-05-28; Celestia: 2026-05-28; Titan-AIX71: 2026-05-21; 43p: 2026-05-13 [score=0.818 recalls=0 avg=0.620 source=memory/2026-07-24.md:17-20]

## Promoted From Short-Term Memory (2026-07-31)

<!-- openclaw-memory-promotion:memory:memory/2026-07-24.md:46:48 -->
- Files Modified on Plexus: `/etc/fstab` — NFS entries added (with `_netdev` and systemd ordering options, though the systemd service is what actually does the mounting); `/etc/systemd/system/nfs-mount-after-dhcp.service` — custom service; `ifupdown-wait-online.service` — enabled (ineffective on its own but kept enabled) [score=0.818 recalls=0 avg=0.620 source=memory/2026-07-24.md:46-48]
<!-- openclaw-memory-promotion:memory:memory/2026-07-24.md:43:43 -->
- Key Lesson: On Debian with ifupdown + dhcpcd, `network-online.target` and `ifupdown-wait-online.service` are fundamentally unreliable for NFS mounts — they report "online" before DHCP assigns an IP. The only reliable approach is to poll for actual IP-level reachability to the NFS server before attempting the mount. [score=0.818 recalls=0 avg=0.620 source=memory/2026-07-24.md:43-43]
<!-- openclaw-memory-promotion:memory:memory/2026-07-24.md:37:40 -->
- NFS Auto-Mount on Boot — Three Attempts: **Attempt 1:** Added NFS entries to `/etc/fstab` with `rw,hard,tcp` options. Failed on reboot — `mount.nfs: Network is unreachable`; **Attempt 2:** Added `_netdev` to fstab options. Failed — same error. `_netdev` tells systemd "needs network" but `network-online.target` fires before DHCP lease is acquired; **Attempt 3:** Added `x-systemd.requires=network-online.target` + `x-systemd.after=network-online.target`. Also enabled `ifupdown-wait-online.service`. Failed — `ifupdown-wait-online.service` completes the moment it starts *soliciting* a DHCP lease, not when the lease is actually obtained.... [score=0.818 recalls=0 avg=0.620 source=memory/2026-07-24.md:37-40]
<!-- openclaw-memory-promotion:memory:memory/2026-07-24.md:51:53 -->
- Plexus Details: VM 109 on proxima5, Debian 13 Trixie, 192.168.1.241; NFS mounts from poly (192.168.1.8): `/Data/MP3_Library`, `/Data/VIDEO`; sudoers: NOPASSWD allowlist only — `sudo install` trick used for root file writes [score=0.818 recalls=0 avg=0.620 source=memory/2026-07-24.md:51-53]

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
