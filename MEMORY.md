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

## Promoted From Short-Term Memory (2026-07-22)

<!-- openclaw-memory-promotion:memory:memory/2026-07-18.md:15:17 -->
- GitHub CLI PAT Configuration (22:36–22:42 AEST): First PAT revoked by Keith after second was configured; **PAT expiry: 90 days — expires approximately 2026-10-16**; Security note: full token values were visible in Telegram chat context metadata [score=0.836 recalls=0 avg=0.620 source=memory/2026-07-18.md:15-17]
<!-- openclaw-memory-promotion:memory:memory/2026-07-18.md:11:14 -->
- GitHub CLI PAT Configuration (22:36–22:42 AEST): First PAT (`ghp_IX…Wp6c`) configured — missing `read:org` scope, `gh auth login --with-token` failed validation; Second PAT (`ghp_uI…ohBz`) configured — full scopes: `repo`, `delete_repo`, `notifications`, `read:org`, `audit_log`; Account: GeoKM (Keith Matthews); Token stored at `~/.config/gh/hosts.yml` (permissions 600) [score=0.836 recalls=0 avg=0.620 source=memory/2026-07-18.md:11-14]
<!-- openclaw-memory-promotion:memory:memory/2026-07-18.md:4:7 -->
- Proxmox Cluster Security Updates (22:19 AEST): Applied `apt update && apt upgrade -y` to all 5 nodes (proxima, proxima2-5) in parallel; All nodes completed successfully — Samba/GnuPG libs, pve-ha-manager, pve-manager triggers, postfix restarted; No reboot performed (per Keith's instruction — manual reboot later); Remaining upgradable (kernel, held back): `proxmox-kernel-6.17` → 6.17.13-18, `proxmox-kernel-7.0` → 7.0.14-5 on all nodes [score=0.815 recalls=0 avg=0.620 source=memory/2026-07-18.md:4-7]

## Promoted From Short-Term Memory (2026-07-23)

<!-- openclaw-memory-promotion:memory:memory/2026-07-18.md:8:8 -->
- Proxmox Cluster Security Updates (22:19 AEST): Config: used `--force-confdef --force-confold` to preserve existing config files [score=0.803 recalls=0 avg=0.620 source=memory/2026-07-18.md:8-8]

## Promoted From Short-Term Memory (2026-07-26)

<!-- openclaw-memory-promotion:memory:memory/2026-07-22.md:19:22 -->
- ⚠️ WARNING — Disk Space: | Host | Mount | Usage | |------|-------|-------| | arya | /export/LibraryPool_Archive | 5.7T/6.2T = 92% (506G free) | | hebei | swap | 1.2GiB — likely transient | [score=0.818 recalls=0 avg=0.620 source=memory/2026-07-22.md:19-22]

## Promoted From Short-Term Memory (2026-07-27)

<!-- openclaw-memory-promotion:memory:memory/2026-07-22.md:6:9 -->
- Host Status Summary: Total: 9 hosts; 🟢 OK: 4 (dockyards, simul, kasm, tg-b); ⚠️ WARNING: 2 (hebei, arya); 🔴 CRITICAL: 2 (xaviernv, retrobench) [score=0.803 recalls=0 avg=0.620 source=memory/2026-07-22.md:6-9]
<!-- openclaw-memory-promotion:memory:memory/2026-07-22.md:37:37 -->
- Events: 12:00 — Scheduled monitoring snapshot via cron. cbm still unreachable since first report. hebei swap elevated. [score=0.803 recalls=0 avg=0.620 source=memory/2026-07-22.md:37-37]
<!-- openclaw-memory-promotion:memory:memory/2026-07-22.md:13:16 -->
- 🔴 CRITICAL — Security Packages: | Host | Packages | Notes | |------|----------|-------| | retrobench | 3 | libnss3 (x2), google-chrome-stable | | xaviernv | 8 | Ubuntu 20.04 ESM packages (accountsservice, libarchive13, snapd, wget, etc.) | [score=0.803 recalls=0 avg=0.620 source=memory/2026-07-22.md:13-16]
<!-- openclaw-memory-promotion:memory:memory/2026-07-22.md:30:33 -->
- Action Items: **retrobench** — 3 security packages: libnss3 x2 + google-chrome-stable → apply; **xaviernv** — 8 security packages (ESM/Ubuntu 20.04 arm64) → needs sudo password or root SSH; **arya** — 506G free on 6.2T dataset → identify large deletable files, archival?; **cbm** — unreachable since last check → hardware/power/ping check [score=0.803 recalls=0 avg=0.620 source=memory/2026-07-22.md:30-33]
<!-- openclaw-memory-promotion:memory:memory/2026-07-22.md:34:34 -->
- Action Items: **hebei** — swap 1.2GiB → likely OK, monitor [score=0.803 recalls=0 avg=0.620 source=memory/2026-07-22.md:34-34]

## Promoted From Short-Term Memory (2026-07-28)

<!-- openclaw-memory-promotion:memory:memory/2026-07-24-1534.md:58:61 -->
- ⚠️ Warnings: | Host | Issue | |------|-------| | **hebei** | high swap (1.1GiB) | | **arya** | disk full 8% (_export_LibraryPool_Archive) | [score=0.836 recalls=0 avg=0.620 source=memory/2026-07-24-1534.md:58-61]
<!-- openclaw-memory-promotion:memory:memory/2026-07-22.md:10:10 -->
- Host Status Summary: ⬛ UNREACHABLE: 1 (cbm) [score=0.808 recalls=0 avg=0.620 source=memory/2026-07-22.md:10-10]
<!-- openclaw-memory-promotion:memory:memory/2026-07-22.md:25:27 -->
- ⬛ Unreachable: | Host | Error | |------|-------| | cbm | No route to host | [score=0.808 recalls=0 avg=0.620 source=memory/2026-07-22.md:25-27]
