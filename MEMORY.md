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

## Promoted From Short-Term Memory (2026-07-28)

<!-- openclaw-memory-promotion:memory:memory/2026-07-24-1534.md:58:61 -->
- ⚠️ Warnings: | Host | Issue | |------|-------| | **hebei** | high swap (1.1GiB) | | **arya** | disk full 8% (_export_LibraryPool_Archive) | [score=0.836 recalls=0 avg=0.620 source=memory/2026-07-24-1534.md:58-61]
<!-- openclaw-memory-promotion:memory:memory/2026-07-22.md:10:10 -->
- Host Status Summary: ⬛ UNREACHABLE: 1 (cbm) [score=0.808 recalls=0 avg=0.620 source=memory/2026-07-22.md:10-10]
<!-- openclaw-memory-promotion:memory:memory/2026-07-22.md:25:27 -->
- ⬛ Unreachable: | Host | Error | |------|-------| | cbm | No route to host | [score=0.808 recalls=0 avg=0.620 source=memory/2026-07-22.md:25-27]

## Promoted From Short-Term Memory (2026-07-29)

<!-- openclaw-memory-promotion:memory:memory/2026-07-24-1534.md:52:55 -->
- 🔴 CRITICAL Alerts: | **proxima2** | 3 security packages + high swap (2.2GiB) | | **proxima3** | 3 security packages + disk full 8% (_PX3_Data0_subvol-101-disk-0) | | **proxima4** | 3 security packages + high swap (1.5GiB) | | **proxima5** | 3 security packages | [score=0.803 recalls=0 avg=0.620 source=memory/2026-07-24-1534.md:52-55]
<!-- openclaw-memory-promotion:memory:memory/2026-07-24-1534.md:48:51 -->
- 🔴 CRITICAL Alerts: | Host | Issue | |------|-------| | **xaviernv** | 12 security packages | | **proxima** | 3 security packages + high swap (2.4GiB) | [score=0.803 recalls=0 avg=0.620 source=memory/2026-07-24-1534.md:48-51]
<!-- openclaw-memory-promotion:memory:memory/2026-07-24.md:5:5 -->
- AIX Midday Monitor — 12:00 AEST: All 4 AIX hosts returned **No route to host** — consistent with known network topology issue. [score=0.803 recalls=0 avg=0.620 source=memory/2026-07-24.md:5-5]
<!-- openclaw-memory-promotion:memory:memory/2026-07-24.md:14:14 -->
- AIX Midday Monitor — 12:00 AEST: **Network topology:** Hebei (current host, where cron runs) is not on the 10.0.0.0/24 AIX network segment. This is a long-standing issue — first observed ~2026-06-09 and recurring since. Monitoring script runs from Hebei but cannot reach the AIX subnet. [score=0.803 recalls=0 avg=0.620 source=memory/2026-07-24.md:14-14]
<!-- openclaw-memory-promotion:memory:memory/2026-07-24.md:7:10 -->
- AIX Midday Monitor — 12:00 AEST: | Host | Status | |------|--------| | persei-nim | ❌ No route to host | | celestia | ❌ No route to host | [score=0.803 recalls=0 avg=0.620 source=memory/2026-07-24.md:7-10]
<!-- openclaw-memory-promotion:memory:memory/2026-07-24.md:22:22 -->
- AIX Midday Monitor — 12:00 AEST: **Options to restore monitoring:** [score=0.803 recalls=0 avg=0.620 source=memory/2026-07-24.md:22-22]
<!-- openclaw-memory-promotion:memory:memory/2026-07-24.md:16:16 -->
- AIX Midday Monitor — 12:00 AEST: **Last known successful collections** (from memory/2026-05-30): [score=0.803 recalls=0 avg=0.620 source=memory/2026-07-24.md:16-16]
<!-- openclaw-memory-promotion:memory:memory/2026-07-24.md:27:27 -->
- AIX Midday Monitor — 12:00 AEST: **Note:** This is a known persistent issue — not a new failure. No action required unless the user explicitly requests network remediation. [score=0.803 recalls=0 avg=0.620 source=memory/2026-07-24.md:27-27]
<!-- openclaw-memory-promotion:memory:memory/2026-07-24.md:23:25 -->
- AIX Midday Monitor — 12:00 AEST: Run the monitoring script from a host with access to 10.0.0.0/24 (e.g., proxima node on that segment, or a VPN/bridge); Set up routing between Hebei and the AIX subnet; Use SSH tunnel / jump host [score=0.803 recalls=0 avg=0.620 source=memory/2026-07-24.md:23-25]
<!-- openclaw-memory-promotion:memory:memory/2026-07-24.md:32:34 -->
- Monitoring Integration: Added `plexus` to `~/lab-docs/monitoring/hosts.d/hosts.yaml`; Test snapshot successful — Debian 13 Trixie, kernel 6.12.96, 4 cores, Plex Media Server running; Dashboard picks it up automatically (reads hosts.yaml dynamically) [score=0.803 recalls=0 avg=0.620 source=memory/2026-07-24.md:32-34]

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
