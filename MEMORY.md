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

## Promoted From Short-Term Memory (2026-08-08)

<!-- openclaw-memory-promotion:memory:memory/2026-08-03.md:6:9 -->
- AIX Midday Monitoring Alert (12:00 AEST): Persei-NIM: DOWN (no route to host); Celestia: DOWN (no route to host); Titan-AIX71: DOWN (no route to host); 43p: DOWN (no route to host) [score=0.803 recalls=0 avg=0.620 source=memory/2026-08-03.md:6-9]
<!-- openclaw-memory-promotion:memory:memory/2026-08-03.md:11:11 -->
- AIX Midday Monitoring Alert (12:00 AEST): Likely network infrastructure issue rather than individual host failures given the simultaneous nature. No user action taken at this time — monitoring will continue. [score=0.803 recalls=0 avg=0.620 source=memory/2026-08-03.md:11-11]
<!-- openclaw-memory-promotion:memory:memory/2026-08-03.md:5:5 -->
- AIX Midday Monitoring Alert (12:00 AEST): All 4 AIX hosts reported unreachable simultaneously: [score=0.803 recalls=0 avg=0.620 source=memory/2026-08-03.md:5-5]

## Promoted From Short-Term Memory (2026-08-09)

<!-- openclaw-memory-promotion:memory:memory/2026-08-02.md:30:32 -->
- AIX Monitor Cron Routing Fix: Changed delivery mode to `none` (`--no-deliver`); Updated the agent prompt to explicitly use `message action=send channel=telegram target=7174833131` to deliver results directly; This bypasses the broken announce mechanism entirely [score=0.815 recalls=0 avg=0.620 source=memory/2026-08-02.md:30-32]
<!-- openclaw-memory-promotion:memory:memory/2026-08-02.md:42:42 -->
- AIX Midday Monitor Cron — Second Fix (2026-08-05): The fix above did NOT work. The root cause: the cron was still using `sessionTarget: "isolated"` with an `agentTurn` payload. Even with delivery mode `none`, the isolated session has no Telegram access. [score=0.815 recalls=0 avg=0.620 source=memory/2026-08-02.md:42-42]
<!-- openclaw-memory-promotion:memory:memory/2026-08-02.md:36:36 -->
- AIX Monitor Cron Routing Fix: **Status:** ✅ Fixed — next run at 12:00 AEST tomorrow will deliver directly to Telegram. [score=0.815 recalls=0 avg=0.620 source=memory/2026-08-02.md:36-36]

## Promoted From Short-Term Memory (2026-08-10)

<!-- openclaw-memory-promotion:memory:memory/2026-08-02.md:49:49 -->
- AIX Midday Monitor Cron — Second Fix (2026-08-05): Command payloads run on the gateway host directly, and their stdout is what gets announced to Telegram [score=0.851 recalls=0 avg=0.620 source=memory/2026-08-02.md:49-49]
<!-- openclaw-memory-promotion:memory:memory/2026-08-02.md:44:44 -->
- AIX Midday Monitor Cron — Second Fix (2026-08-05): **Second fix applied (2026-08-05 12:15 AEST):** [score=0.851 recalls=0 avg=0.620 source=memory/2026-08-02.md:44-44]
<!-- openclaw-memory-promotion:memory:memory/2026-08-02.md:51:51 -->
- AIX Midday Monitor Cron — Second Fix (2026-08-05): **Key lesson:** `sessionTarget: "main"` with `systemEvent` payload is the only way to run an agent in the main session and have it use tools like `message`. An `isolated` agentTurn session cannot use the message tool. Command payloads are the correct approach for script-runner cron jobs that need announce delivery. [score=0.851 recalls=0 avg=0.620 source=memory/2026-08-02.md:51-51]
<!-- openclaw-memory-promotion:memory:memory/2026-08-02.md:34:34 -->
- AIX Monitor Cron Routing Fix: The jobs file at `~/.openclaw/cron/jobs.json.migrated` was also updated (for when the system next migrates/loads), but the live gateway config is in-memory — the `openclaw cron edit` command is what took effect. [score=0.804 recalls=0 avg=0.620 source=memory/2026-08-02.md:34-34]

## Promoted From Short-Term Memory (2026-08-14)

<!-- openclaw-memory-promotion:memory:memory/2026-07-01.md:29:55 -->
- Proxima3 PX3_Data0: 8.7TB allocated, 945GB free (88% used) ⚠️ - Proxima4 AI0: 32% fragmentation ### Security Updates — Proxmox nodes - All 5 Proxmox nodes share same packages: 37 upgradable total - 3 security-specific: libhttp-daemon-perl, libssh2-1t64, python3-urllib3 (confirmed on proxima) - NOT 3 per-node — monitoring likely aggregated across cluster rep - **xaviernv and retrobench NOT on Proxmox — separate SSH access needed** ### Disk Alerts - arya: _export_LibraryPool_Archive at 92.1% — separate host, not Proxmox - Proxima3 PX3_Data0: confirmed ~88% used — ZFS pool near capacity - All other Proxmox node disks healthy (10-46%)... [score=0.869 recalls=4 avg=0.695 source=memory/2026-07-01.md:29-55]
<!-- openclaw-memory-promotion:memory:memory/2026-08-10.md:13:14 -->
- ⚠️ Warnings: **arya**: LibraryPool_Archive 92% used; **plexus**: high swap (1.6GiB) [score=0.816 recalls=0 avg=0.620 source=memory/2026-08-10.md:13-14]

## Promoted From Short-Term Memory (2026-08-15)

<!-- openclaw-memory-promotion:memory:memory/2026-08-10.md:17:17 -->
- ⬛ Unreachable: xaviernv, cbm, helios — No route to host [score=0.835 recalls=0 avg=0.620 source=memory/2026-08-10.md:17-17]
<!-- openclaw-memory-promotion:memory:memory/2026-08-10.md:8:10 -->
- 🔴 CRITICAL: **retrobench**: 23 security packages pending; **proxima–5**: 2 security packages each + high swap (proxima2 worst: 2.7GiB); **proxima3**: also disk 92% used (8% free) [score=0.835 recalls=0 avg=0.620 source=memory/2026-08-10.md:8-10]
<!-- openclaw-memory-promotion:memory:memory/2026-08-10.md:5:5 -->
- System Monitoring Snapshot (12:03 AEST): Received from cron session. Critical issues: [score=0.803 recalls=0 avg=0.620 source=memory/2026-08-10.md:5-5]
<!-- openclaw-memory-promotion:memory:memory/2026-08-10.md:20:23 -->
- Action Items (from monitoring): Security updates — retrobench (23), proxima cluster (2 each); Memory pressure — proxima2 (2.7GiB swap) worst; Disk cleanup — arya, proxima3 both at 92%; Host connectivity — xaviernv, cbm, helios need physical check [score=0.803 recalls=0 avg=0.620 source=memory/2026-08-10.md:20-23]
<!-- openclaw-memory-promotion:memory:memory/2026-08-10.md:26:27 -->
- Notes: Telegram reply to cron session failed (no target chat ID available); Monitoring data captured here for reference [score=0.803 recalls=0 avg=0.620 source=memory/2026-08-10.md:26-27]
