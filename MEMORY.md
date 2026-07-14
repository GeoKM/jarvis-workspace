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

## Promoted From Short-Term Memory (2026-07-09)

<!-- openclaw-memory-promotion:memory:memory/2026-07-06.md:19:19 -->
- KASM Workspaces Upgrade 1.18.1 → 1.19.0 (14:20–14:50): **Post-upgrade issue resolved:** [score=0.815 recalls=0 avg=0.620 source=memory/2026-07-06.md:19-19]
<!-- openclaw-memory-promotion:memory:memory/2026-07-06.md:23:23 -->
- KASM Workspaces Upgrade 1.18.1 → 1.19.0 (14:20–14:50): **Final state:** [score=0.815 recalls=0 avg=0.620 source=memory/2026-07-06.md:23-23]
<!-- openclaw-memory-promotion:memory:memory/2026-07-06.md:4:4 -->
- KASM Workspaces Upgrade 1.18.1 → 1.19.0 (14:20–14:50): **Host:** LXC 102 (KASM) on proxima2, Debian Trixie, Docker 29.6.1 [score=0.815 recalls=0 avg=0.620 source=memory/2026-07-06.md:4-4]

## Promoted From Short-Term Memory (2026-07-10)

<!-- openclaw-memory-promotion:memory:memory/2026-07-06.md:24:27 -->
- KASM Workspaces Upgrade 1.18.1 → 1.19.0 (14:20–14:50): `/opt/kasm/current` → `/opt/kasm/1.19.0`; API healthcheck: `{"ok": true}`; Disk: 53G/157G used (36%), 97G free; Workspace images (1.18.0-rolling-weekly) retained — still valid for existing sessions [score=0.869 recalls=0 avg=0.620 source=memory/2026-07-06.md:24-27]
<!-- openclaw-memory-promotion:memory:memory/2026-07-06.md:30:30 -->
- KASM Workspaces Upgrade 1.18.1 → 1.19.0 (14:20–14:50): **Rollback path:** Proxmox snapshot `Pre_1_19_0_upgrade` on LXC 102 [score=0.869 recalls=0 avg=0.620 source=memory/2026-07-06.md:30-30]
<!-- openclaw-memory-promotion:memory:memory/2026-07-06.md:6:6 -->
- KASM Workspaces Upgrade 1.18.1 → 1.19.0 (14:20–14:50): **Steps completed:** [score=0.869 recalls=0 avg=0.620 source=memory/2026-07-06.md:6-6]
<!-- openclaw-memory-promotion:memory:memory/2026-07-06.md:11:14 -->
- KASM Workspaces Upgrade 1.18.1 → 1.19.0 (14:20–14:50): Ran `upgrade.sh --proxy-port 443 -b --ignore-dep-failures`; Wireguard dependency failed (package unavailable for Trixie/LXC) — ignored, reduced egress functionality only; v4l2loopback DKMS also failed (no kernel headers for PVE host) — webcam support disabled; All other dependencies installed successfully [score=0.837 recalls=0 avg=0.620 source=memory/2026-07-06.md:11-14]
<!-- openclaw-memory-promotion:memory:memory/2026-07-06.md:15:17 -->
- KASM Workspaces Upgrade 1.18.1 → 1.19.0 (14:20–14:50): Database migrated from 1.18.1 → 1.19.0 (new volume `kasm_db_1.19.0`); All 8 KASM containers running 1.19.0-rolling images, all healthy; Pruned 8 old 1.18.1 infrastructure images, reclaimed ~2 GB [score=0.837 recalls=0 avg=0.620 source=memory/2026-07-06.md:15-17]
<!-- openclaw-memory-promotion:memory:memory/2026-07-06.md:20:21 -->
- KASM Workspaces Upgrade 1.18.1 → 1.19.0 (14:20–14:50): `kasm_guac` container initially unhealthy — failed to register with API during simultaneous startup (502 error); Fixed by `docker restart kasm_guac` — container registered successfully on second boot [score=0.837 recalls=0 avg=0.620 source=memory/2026-07-06.md:20-21]
<!-- openclaw-memory-promotion:memory:memory/2026-07-06.md:28:28 -->
- KASM Workspaces Upgrade 1.18.1 → 1.19.0 (14:20–14:50): Old 1.18.1 install directory retained at `/opt/kasm/1.18.1` for rollback [score=0.837 recalls=0 avg=0.620 source=memory/2026-07-06.md:28-28]
<!-- openclaw-memory-promotion:memory:memory/2026-07-06.md:7:10 -->
- KASM Workspaces Upgrade 1.18.1 → 1.19.0 (14:20–14:50): Proxmox snapshot: `Pre_1_19_0_upgrade` created on LXC 102; Database backup: `/opt/kasm/backups/kasm_backup_pre_1.19.0.tar` and `/opt/kasm/backups/kasm_db_backup.tar` (auto-created by upgrade script); Downloaded `kasm_release_1.19.0.tar.gz` from S3 (~10.5 MB, dated June 13 2026); Stopped KASM services via `/opt/kasm/bin/stop` [score=0.837 recalls=0 avg=0.620 source=memory/2026-07-06.md:7-10]

## Promoted From Short-Term Memory (2026-07-13)

<!-- openclaw-memory-promotion:memory:memory/2026-07-10.md:23:23 -->
- Proxmox Cluster Report (22:46 AEST): **No HA resources or backup jobs configured.** [score=0.815 recalls=0 avg=0.620 source=memory/2026-07-10.md:23-23]
<!-- openclaw-memory-promotion:memory:memory/2026-07-10.md:5:5 -->
- Proxmox Cluster Report (22:46 AEST): **Cluster:** Proxima-One | Quorum: ✅ YES | Nodes: 5/5 online [score=0.815 recalls=0 avg=0.620 source=memory/2026-07-10.md:5-5]
<!-- openclaw-memory-promotion:memory:memory/2026-07-10.md:7:7 -->
- Proxmox Cluster Report (22:46 AEST): **Ceph ⚠️ HEALTH_WARN:** [score=0.815 recalls=0 avg=0.620 source=memory/2026-07-10.md:7-7]

## Promoted From Short-Term Memory (2026-07-14)

<!-- openclaw-memory-promotion:memory:memory/2026-07-10.md:15:15 -->
- Proxmox Cluster Report (22:46 AEST): **ZFS Pools:** All ONLINE ✅ [score=0.869 recalls=0 avg=0.620 source=memory/2026-07-10.md:15-15]
<!-- openclaw-memory-promotion:memory:memory/2026-07-10.md:21:21 -->
- Proxmox Cluster Report (22:46 AEST): **Top I/O:** lxc 102 (KASM) on proxima2 — 4.1 TB written [score=0.869 recalls=0 avg=0.620 source=memory/2026-07-10.md:21-21]
<!-- openclaw-memory-promotion:memory:memory/2026-07-10.md:8:10 -->
- Proxmox Cluster Report (22:46 AEST): MONS: 5, OSDs: 6 up/6 in; Warning: daemons running older version of ceph; Action: `ceph versions` on any mon node to identify mixed-version daemons [score=0.869 recalls=0 avg=0.620 source=memory/2026-07-10.md:8-10]
<!-- openclaw-memory-promotion:memory:memory/2026-07-10.md:13:13 -->
- Proxmox Cluster Report (22:46 AEST): qemu 106 (Aros2) on proxima3 — stopped; verify if intentional [score=0.837 recalls=0 avg=0.620 source=memory/2026-07-10.md:13-13]
<!-- openclaw-memory-promotion:memory:memory/2026-07-10.md:18:19 -->
- Proxmox Cluster Report (22:46 AEST): proxima4: 86.6% (highest); proxima: 78.0% [score=0.837 recalls=0 avg=0.620 source=memory/2026-07-10.md:18-19]
<!-- openclaw-memory-promotion:memory:memory/2026-07-10.md:12:12 -->
- Proxmox Cluster Report (22:46 AEST): **Guests:** [score=0.827 recalls=0 avg=0.620 source=memory/2026-07-10.md:12-12]
<!-- openclaw-memory-promotion:memory:memory/2026-07-10.md:17:17 -->
- Proxmox Cluster Report (22:46 AEST): **Memory pressure:** [score=0.827 recalls=0 avg=0.620 source=memory/2026-07-10.md:17-17]
