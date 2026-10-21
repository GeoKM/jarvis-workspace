---
**[Learning from 2026-04-09 MP/M II Reconnaissance]**
MP/M II uses a manual drive/user-area model, distinct from modern filesystem abstractions.
1. Drive A: reported 'System Files Exist' when queried via `SDIR`.
2. Drives C:/D: trigger BDOS bad-sector errors with common commands (`USER`, `DIR`, `STAT`).
3. **Actionable Insight**: prioritise `SDIR` on specific drives (e.g. `0A:`) to map core system files,
   respecting the vintage architecture's procedural nature.
---

**[Learning from 2026-04-24 VAXcluster Rebuild Audit]**
A read-only audit confirmed the rebuilt OpenVMS VAXcluster topology, current reference state:
FUSION = primary boot/MSCP server, DECnet 12.106, TCP/IP 192.168.1.137; RISE = satellite, DECnet
12.107, TCP/IP 192.168.1.138; shared root `FUSION$DUA0:[SYS10.]`, local page/swap on `RISE$DUA0:`.
Canonical notes: `FUSION_ENVIRONMENT_2026-04-24.md`, `RISE_ENVIRONMENT_2026-04-24.md`.
---

**[Learning from 2026-07-06 KASM Workspaces Upgrade 1.18.1 → 1.19.0]**
KASM Workspaces lives in LXC 102 on proxima2 (Debian Trixie, Docker 29.6.1). Upgrade: Proxmox
snapshot `pct snapshot 102 <name>` (no dots/hyphens) → DB backup
`/opt/kasm/current/bin/utils/db_backup --path /opt/kasm/current --backup-file /opt/kasm/backups/<name>.tar -v`
(needs `chmod 777` on the backups dir) → `curl -O
https://kasm-static-content.s3.amazonaws.com/kasm_release_<version>.tar.gz`, extract, `bash
upgrade.sh --proxy-port 443 -b --ignore-dep-failures` (the ignore flag is needed for LXC —
Wireguard/v4l2loopback unavailable) → `docker restart kasm_guac` if unhealthy (API race on
simultaneous startup) → prune old infra images but keep workspace images. Access chain: Hebei →
SSH root@proxima → SSH proxima2 → `pct exec 102 -- bash -c "..."`. Current: 1.19.0 at
`/opt/kasm/1.19.0`, symlink `/opt/kasm/current`. Non-KASM containers in the same LXC (hbbs, hbbr
/RustDesk, portainer_agent) are unaffected. Rollback: Proxmox snapshot or repoint the `current`
symlink.

---

---

**[Learning from 2026-10-10 Proxima4 NIC Fault]**
Proxima4 (Turion II Neo N40L) has intermittent NIC failures where the interface "just disappears,"
taking down the host and all VMs/LXCs on it (including LXC 103 Hebei — the OpenClaw gateway).
Recovery currently requires a physical power cycle. Symptom from the gateway: simultaneous
timeouts on `ollama/minimax-m3:cloud` (primary) and `openai/gpt-5.6-terra` (fallback) during cron
wake tasks. Candidates: NIC driver/firmware, power management (ASPM / runtime PM), hardware
degradation. Worth tracking failure frequency and a remote recovery path (IPMI/iLO).

---

## Security Incident — DDoS Botnet on VM 109 (Plexus) — 2026-10-20

**Status: RESOLVED — host deleted 2026-10-20 ~22:00.** Containment was by **destroying the VM**,
not cleaning it: the `plex` account had a nologin shell, `sudo` needed a password (so processes
could not be killed or the crontab stripped remotely), and no firewall tooling (ufw/nft/iptables)
was installed. Keith removed VM 109 outright; the host is unreachable and no C2 survives with it.
Found by the `proxmox-health-3d` cron while investigating a 95% CPU reading on Proxima5.

**Verification at removal:** `.gb` (pid 699029) ran since 04:52:40 with an ESTABLISHED TLS session to
`45.56.82.212:443`; `.uf_guard` (721948) and the UDP flooder (768627, 800 threads →
`152.53.168.44`) were live. DNS for `plexus.can.barnabasmusic.com` still resolves to 192.168.1.241
— stale record to clean up. **Proxima5 crashed during the removal** (4/5 nodes, still quorate);
cause not established. **Plexus was rebuilt the next day as LXC 109 on Proxima5 — see "Plexus
Rebuild & Hardening (2026-10-21)" below; the Oct 20 Plex account token still needs rotating.**
Host: VM 109 "Plexus" (Proxmox, Proxima5, 192.168.1.241, Debian 13, Plex 1.43.3.10828-00f62d37d);
compromised user `plex` (uid 999, `/usr/sbin/nologin`).

**Chain of compromise** (full forensics: `memory/2026-10-20.md`): a malicious Plex "codec" plugin
(`.../Codecs/4987be2-…-linux-x86_64/zz75920.so`, mtime 2026-10-20 16:58) ran a **reverse shell**
to `202.78.167.55:10570` (`script -qc` used because `plex` has a nologin shell, so a PTY is
required). `202.78.167.55:8765` served the payloads (`/go_beacon_amd64`|`_arm64`). Payload 1 =
`/tmp/.gb` (5.7 MB Go "go_beacon", C2 `45.56.82.212:443` TLS, args
`la_au599433 tk_la_au512_3211ea`); payload 2 = `/tmp/.uf` (UDP flooder, 800 threads, 65000-byte
packets, 300 s bursts → `152.53.168.44` on 22,80,443,3000,8080,8084); watchdog `/tmp/.uf_guard`
re-materialises `.uf` from an embedded base64 blob every 5 s; persistence via the `plex` crontab.

**Detection signature worth remembering:** Proxmox reported VM 109 at only 3.7% CPU while the
*node* sat at 95%. **VM 109 has no QEMU guest agent**, so guest-internal load is invisible to the
Proxmox API — the node/CPU gap was the only clue. Inside the guest: load average 238–294,
`python3` at 350% CPU. For any node pegged well above its guest-reported CPU, check the guest
directly rather than trusting the Proxmox resource view.

**Blast radius (verified clean):** every other reachable host scanned for payloads and processes
— proxima, proxima2-5, dockyards, kasm, arya, tg-b, simul, xaviernv, retrobench clean. NFS
shares from 192.168.1.8 have no plex-owned files written since 2026-10-17. No SSH key planted, no
systemd user units, no failed SSH logins in 7 days — access was via the Plex plugin, not brute
force. 707 `*.jpg` in /tmp are benign Plex thumbnails.

**Open items for Keith:** (1) ~~kill 699029 / 765066 / 721948 + clear the crontab~~ — CLOSED by
destroying VM 109; (2) ~~delete `/tmp/.gb`, `/tmp/.uf*`, `zz75920.so`, upgrade Plex~~ — CLOSED with
the host; Plex 1.43.3.10828-00f62d37d is the affected version to avoid on rebuild; (3) rotate the
Plex token and block 202.78.167.55 / 45.56.82.212 — OPEN, for the replacement host (no firewall
tooling on the old one); (4) cluster has **zero backup jobs**, so VM 109 had no restore point —
OPEN, worth fixing separately; (5) ~~dead `test` zfspool~~ — CLOSED 22:20 (`pvesm remove test`).

**Post-recovery verification (22:10–22:20):** 0 matching sockets for `45.56.82.212`,
`202.78.167.55`, or `152.53.168.44` on **all five** Proxmox nodes. Cluster 5/5 quorate, Ceph
HEALTH_OK, 5 MONs, 5 OSDs up/in. VM 109 absent from `/cluster/resources` and from every node's
`qemu-server/` dir.

**### Proxmox cluster — standing caveats (2026-10-20 23:46 health report)

- **The bundled health script under-reported ZFS faults — now patched** (`846534a`, pushed).
  `cluster_status_report.sh` read `pvesh /nodes/<node>/disks/zfs`, whose payload has **no `cap`
  field** (rendered `cap n/a`), and its attention heuristic checked only `health != ONLINE` — never
  `zpool status` error text or vdev counters, so a pool with a **live checksum error read as
  "healthy"** (PX3_Data0 on proxima3 = "unrecoverable error" while the script said no issues).
  Fix: real `cap` via `zpool list -H -o …,cap,…` with a >= 85% flag; `zpool status -x` error-text
  parsing; **per-node** pool collection (it previously read every node's pools from one host —
  `keith` has NOPASSWD sudo for `zpool` there, `jarvis` does not; override with
  `OPENCLAW_PROXMOX_NODE_SSH_USER`); >= 80% node-memory threshold. **Always cross-check
  `zpool status` + `zpool list -o cap` directly.** <!-- project: github.com/GeoKM/jarvis-workspace -->
- **PX3_Data0 (proxima3)** — raidz1 × 3 × 4 TB, 9.44 T, **91% used** (808 G free). Subvol
  `subvol-101-disk-0` = 5.76 T of a 7.10 T refquota, 410 G available. Capacity 90% Apr–May → 92%
  late Sep → 94% on 2026-10-03, then **flat since 2026-10-04** — static, not runaway. Live vdev
  **CKSUM=16 on /dev/sdc** (`ata-ST4000DM004-2CV104_ZTT2F1L6-part2`), `Reallocated_Sector_Ct=816`,
  `Command_Timeout=1`; sdb/sdd clean. Pool ONLINE, "No known data errors", 2026-10-11 scrub
  repaired 1M with 0 errors. **Never previously recorded** — needs a long SMART test + fresh
  scrub to clear.
- **Thin memory headroom** — proxima4 77.8% (12.4/15.9 G, 3.2 G swap, kvm/VM 103 Hebei at
  9.2 G RSS); proxima 70.3% (5.6/7.9 G, 2.9 G swap, ceph-osd 1.6 G). Stable, but proxima has only
  7.9 G total and no failure margin.
- **Zero backup jobs cluster-wide** (still open) — no restore point exists for any guest.
- `sudo pvesm status` is **not** in the NOPASSWD allowlist on the Proxmox nodes; `zpool list`,
  `zpool status`, `smartctl`, `qm`, `pct`, `pvesh` are. Read storage status via the API.
- Dead `storage/proxima/test` zfspool (no `test` pool on any node) removed 2026-10-20 22:20 —
  use the bare storage ID (`pvesm remove test`); `pvesm remove proxima/test` fails with
  *"storage ID contains illegal characters"*. `HA resources: 0` cluster-wide. VM 105 (HMC) and
  VM 106 (ArosOne) on Proxima5 are intentionally stopped.

---

## Plexus Rebuild & Hardening (2026-10-21) <!-- project: github.com/GeoKM/jarvis-workspace -->

Plexus was **rebuilt as LXC 109 (unprivileged) on Proxima5** — 192.168.1.241/24, Debian 13.6 trixie,
2 CPU / 4 GB + 512 MB swap, `onboot=1`; rootfs `CephPool0:vm-109-disk-0` (32 G), data
`DATA5:subvol-109-disk-0` → `/Data` (500 G, a PVE-managed ZFS **subvol** so it shows in the GUI).
Plex **1.43.5.11029-6bf8af3f0** — safely past the compromised 1.43.3.10828. DNS
`plexus.can.barnabasmusic.com` → .241 was already correct. **Still open for Keith:** claim the
server (`claimed="0"`) and **rotate the Plex account token** (the Oct 20 token must be revoked under
plex.tv account settings — it cannot be rotated from the server side), then add libraries at
`/Data/{MP3_Library,VIDEO,GALLERY}`.

**Build gotchas:**
- **ZFS pools are node-local, not cluster-shared like Ceph** — `DATA5` lives on Proxima5, so an LXC
  on proxima4 cannot bind-mount it; building on Proxima5 removes the problem entirely.
- **Plex's apt repo and CDN return 403 from this network** (Cloudflare/S3 `AccessDenied`, cf-ray
  SYD) on every host, container and header set — including `plex.gpg`, `dists/*/InRelease` and
  direct `.deb` paths. Workaround: the `plex-media-server-new/<version>/debian/*.deb` path is not
  blocked; get the URL from `https://plex.tv/pms/downloads/5.json` (`api/downloads/1.json` 404s).
- **poly (192.168.1.8) NFS speaks only `vers=3`** (`vers=4` → "Protocol not supported"). An
  **unprivileged LXC cannot mount NFS at all** ("Operation not permitted") — mount on the Proxmox
  host and bind-mount into the container.
- `pct create` needs **root@pam** for bind-mount mp points (the API token is `privsep=1` → "Permission
  check failed"); container templates live on `cephfs:vztmpl/...`, not `local:`. An LXC `mp0` on a
  zfspool creates a **subvol**, not a zvol (`ZFSPoolPlugin` supports `subvol`; `ZFSPlugin` does not).
- **No `lxc-agent` exists in PVE 9** — LXC reports CPU/mem to the Proxmox GUI via cgroups with no
  guest agent at all (measured 34% CPU under load). The Oct 20 blind spot was specific to the old
  QEMU VM lacking a QEMU guest agent; the LXC switch closes it by design.
- `pve-container` installs are slow: dpkg blocks in `jbd2_log_wait_commit` — OSD 5 on proxima4 is
  HDD class (62–128 ms commit) vs 0–5 ms on the SSD OSDs; expect a ~13 min tail.
- Proxmox API returned a **transient 401** mid-session; 3 consecutive retries returned 200.

**Plex remote access was broken by the Let's Encrypt YR2 chain, not by Plex.** Plex 1.43.5 is issued
by the new **YR2** intermediate → **ISRG Root YR** (root generated 2025-09-03, not yet in any major
trust store), so Plex's AWS reachability probes abort with `tlsv1 alert unknown ca` and the server
reports "Mapped - Not Published (Not Reachable)". Fix: replace Plex's served chain (`Cache/ca.crt`,
backup `Cache/ca.crt.bak.*`) with **YR2 + Root YR cross-signed by ISRG Root X1**
(`https://letsencrypt.org/certs/gen-y/root-yr-by-x1.pem`; the flat `isrgrootyr.pem` path 404s).
Result: chain serves 3 certs, `curl` → 200 "SSL certificate verify ok", Plex log shows
`connectivity="1"` and `mapping state set to 'Mapped'`, zero `unknown ca` errors. Key traps: the
**container's own** trust store is irrelevant (the *remote* checker validates the chain Plex
**serves**); a grep for the root subject in `ca-certificates.crt` is unreliable (base64 DER) — use
`openssl crl2pkcs7 -nocrl -certfile <bundle> | openssl pkcs7 -print_certs -noout`; testing TLS
from a host whose store you just modified is contaminated.

**In-container nftables firewall** (Keith-approved; the Proxmox node firewall is cluster-wide and
was rejected). `/etc/nftables.conf` in CT 109: input policy drop, forward drop, output accept;
allow loopback, `ct state established,related`, ICMP (PMTU on the 32400 forward), SSH 22 from LAN,
Plex 32400 from anywhere (Plex's checkers connect from AWS IPs, not the router's public IP, so the
source cannot be pinned), Plex discovery UDP 1901/32410/32412/32413/32414 LAN-only, IPv6 ULA +
link-local. **Port 111 (rpcbind) is blocked and not needed** — the container is not an NFS client:
the three poly exports are mounted in the **Proxima5 host netns** and bind-mounted in (the
container's `rpcinfo -p` registers only program 100000; there are no `mount.nfs`/`statd`/`lockd`
processes in it). Verified after apply and after `pct reboot 109`. The container has its own
network namespace, so `nft` inside it cannot touch the host ruleset. Escape hatch: `pct exec 109 --
bash` from the Proxmox host bypasses the container firewall; rollback = restore
`nftables.conf.bak.*`.

**Post-rebuild IOC sweep against the exact Oct 20 indicators: CLEAN.** No `/tmp/.gb`, `.uf`,
`.uf_guard`, `.uf_go`, `.uf.pid`; 0 filesystem hits for `.gb`/`.uf`/`zz75920.so`/`go_beacon*`; 0
sockets or files for the C2/flood IPs `45.56.82.212`, `202.78.167.55`, `152.53.168.44`; 0 beacon
args in processes; 0 reverse-shell patterns (`script -qc`, `nc -e`, `sh -i`, `/dev/tcp`); 0
miners/crawlers; `Plug-ins/` empty; `Codecs/` holds no `.so` files; `dpkg -V plexmediaserver`
clean; only stock cron/systemd units; no `/etc/ld.so.preload`; `authorized_keys` = keith's key
only; accounts root + keith (+ `plex` uid 999, nologin, no sudo); load 0.29–0.35 vs 238–294 on the
old host; no unexpected internet inbound; 0 hits cluster-wide on all 5 Proxmox nodes; plex.tv shows
exactly one server resource and no ghost entry from the destroyed VM.

---

## CBM unattended-upgrades rollout (2026-10-21) — no reboot <!-- project: github.com/GeoKM/jarvis-workspace -->

Keith authorised `unattended-upgrades` on CBM (192.168.1.19; the old
`cbm.can.barnabasmusic.com` → 192.168.1.241 DNS record is stale — DNS now points to .19). Debian
13.7 trixie, kernel 6.12.111+deb13-amd64. `unattended-upgrades` 2.12 installed, effective gate
`Q='1'`, explicit `Automatic-Reboot "false"` in `/etc/apt/apt.conf.d/51unattended-upgrades-config`
(plus `Update-Package-Lists "1"`, `AutocleanInterval "7"`, `Remove-Unused-Kernel-Packages "true"`,
`Remove-Unused-Dependencies "false"`, `Remove-New-Unused-Dependencies "true"`). The 17-package
security backlog was applied with the house tooling (`sudo -n /usr/local/sbin/raff-apply-updates`,
then `raff-apply-full-upgrade` for the held-back kernel) → **0 pending upgrades**, `dpkg --audit`
clean, `apt-daily-upgrade.timer` enabled. Kernel **6.12.113-1 installed but not active** (running
6.12.111) → `/var/run/reboot-required.pkgs` is set.

**Reboot deliberately NOT performed.** CBM is a physical machine with **no IPMI/BMC**
(`/dev/ipmi*` absent) and **no confirmed Wake-on-LAN** path — a failed reboot would need a physical
power cycle. `Automatic-Reboot "false"` is set explicitly for exactly this reason; the new kernel
activates at the next manual reboot. `linux-image-6.1.0-23-amd64` and
`linux-image-6.12.111+deb13-amd64` were `apt-mark manual` so unattended kernel cleanup cannot
auto-remove CBM's GRUB fallbacks (6.1.0-23 backs the MS-DOS/Windows chainload entries, which are
intact and UUID-based).

**CBM sudo gotchas:** keith has a **NOPASSWD allowlist**, not blanket root — `apt`, `apt-get`,
`apt-cache`, `apt-mark`, `dpkg`, `dpkg-query`, `install`, `systemctl`, `journalctl`, `ls`, `cat`,
`tail`, `df`, `du`, `findmnt`, `smartctl`, `mdadm`, `zpool`/`zfs`, `pvs`/`vgs`/`lvs` + the `raff-*`
scripts. **`tee` and `sed` are NOT in it** — use `sudo install` as the write mechanism for
`/etc/apt/apt.conf.d/`. `sudo -n true` is rejected, so don't probe sudo with `true`; `sudo -n
apt-get …` works. sudo 1.9.16p2 is too old for inline `VAR=value` env passing (needs 1.9.21+), so
`sudo -n DEBIAN_FRONTEND=noninteractive …` and `sudo -n env …` are both rejected. `wazuh-agent` is
**not** installed on CBM (pre-existing; `wazuh.list` is still in apt sources).

**Fleet unattended-upgrade gate status (18:26):** cbm `1`/0 ✅ · dockyards `1`/0 · kasm `1`/0 ·
arya `1`/0 · tg-b `1`/0 · pidp11 `1`/**225 backlog** · xaviernv `1`/1 · **retrobench `0`** (disabled
by local `02periodic` + `51unattended-upgrades-config` overrides) · **simul UNSET** (no
`20auto-upgrades`; `enable_auto_updates: false`) · hebei unreachable by SSH key from this path.
retrobench and simul still have upgrades **disabled** and need a decision; pidp11's 225-package
backlog is the largest outstanding item.

---

## OpenClaw 2026.10.2 — Model, Config & Plugin Gotchas (2026-10-20)

Durable traps hit while switching the default model and running `doctor`/`security audit` on hebei.

**Model selection (default is now `ollama/minimax-m3.1-flash:cloud`)**
- **Two independent allow lists.** `agents.defaults.modelPolicy.allow` is not enough — the gateway enforces `agents.entries.*.modelPolicy.allow` and rejects with *"Model override … is not allowed for agent main"*. Update both.
- **Per-agent override shadows the global default.** `openclaw models set` writes only `agents.defaults`; `agents.entries.main.model.primary` wins for the `main` agent. Set it with `openclaw config set agents.entries.main.model.primary <model>` (no `--agent` flag for `models set`).
- **Bracket-string config set is rejected** ("Invalid path bracket string") — use index form: `openclaw config set 'path[4]' 'value'`.
- **Cloud-route models are absent from the local catalog** (`ollama list`/`/api/tags`) yet `ollama show` resolves them and they run; `models set` warns but still saves.
- **Probe via `openclaw infer model run --gateway --model <m> --prompt "Reply with exactly: PROVIDER-PROOF-OK"`.** `openclaw agent --agent main --model …` is blocked ("Gateway agent from agent exec would lose inter-session attribution"). Fallback: `openai/gpt-5.6-terra`.

**Config / security audit** <!-- project: github.com/GeoKM/jarvis-workspace -->
- **`plugins.allow` is an EXCLUSIVE allowlist** — plugin ids not in it are disabled at activation. A minimal list (e.g. `["codex"]`) would disable ollama/telegram/memory-core and break the gateway. Set it to the exact set of currently-enabled ids (44 here: 42 bundled + `codex` + `perplexity`); disabled bundled plugins deliberately excluded.
- **The non-secret API-key marker exemption is path-specific** — `isNonSecretApiKeyMarker` applies only to `models.providers.*.apiKey`, not `memory.search.remote.apiKey`. The only clean fix there is `openclaw config unset memory.search.remote.apiKey` (no SecretRef migration — nothing to protect). Local ollama on 127.0.0.1:11434 needs no auth header.
- **Startup migrations pending** requires `openclaw doctor --fix` (mutating — needs owner approval).
- **Gateway memory pressure** (RSS 2.4–2.8 GiB vs 2.21 GiB threshold, 17–19 workers) with recurring "slow SQLite transaction" / "SQLite lock wait failed"; session DB 134M, agent dir 618M → gateway restart + session pruning. **Compaction failures** on minimax-m3.1-flash:cloud: "summary output budget (6553 tokens) exhausted" → guard cancels. Root cause: 6553 = 8192 × 0.8 from the model's `maxTokens`, consumed by the summariser's reasoning before any visible text; the cloud model is absent from the local catalog so there is no per-model `maxTokens` to raise. Fix applied: `agents.defaults.compaction.thinkingLevel: "off"` (compaction-only; hot-reloads, no restart). Next lever: a dedicated higher-`maxTokens` model via `agents.defaults.compaction.model`. <!-- project: github.com/GeoKM/jarvis-workspace -->
- **"Dead-lettered delivery queue" is a false alarm**: the 13 `status='failed'` rows in `delivery_queue_entries` are legacy **tombstones** (payload NULL, `recovery_state='completed_permanent'`, single-timestamp rows), not undelivered messages — no live backlog, alerting chain intact. No CLI deletes them, so `openclaw health` keeps warning until removed by hand. <!-- project: github.com/GeoKM/jarvis-workspace -->
- **Invalid skills are silently skipped** (no YAML frontmatter → "Skipping invalid skill" on every load; the AIX cron still worked because it runs a `command` payload, not the skill). Fix = add `name` + `description` frontmatter.

**Skill authoring / Workshop** <!-- project: github.com/GeoKM/jarvis-workspace -->
- **Workshop publication standard is 10,000 chars.** `os-upgrade-lab-hosts` SKILL.md 26,768 → short procedure (8,855 chars) + 8 reference files. **One source per meaning** — the reference must point back, not restate. **Never write "see X above"** — name the file/section instead. **The frontmatter description is the routing surface** — rewrite it whenever the branches change.
- The `read` tool refuses a skill file already served whole in context ("Skill instructions were already served whole earlier…") — use `exec sed -n` to re-read. `progress_card` rejects numeric strings: `limit`/`plan` need real integers and `plan` must be an array.

**Workspace git hygiene** <!-- project: github.com/GeoKM/jarvis-workspace -->
- 158 stray `collect-metrics.py.bak.*` / `*.broken-fragment.*` files (~924K) + `__pycache__` were untracked; `.gitignore` now excludes `__pycache__/`, `*.py[co]`, `*.bak.*`, `*.broken-fragment.*` (files left on disk, later trashed via `gio trash`).
- A **fragmented** collector is ~1331 bytes; a working one is 11,063+. `ast.unparse()` round-trips split semicolon-chained statements — literal-text grep counts do not prove call counts.
- **GitHub auth (current path)**: `GH_TOKEN` (classic `ghp_` PAT) in `~/.config/openclaw/openclaw.env` — the OpenClaw process and exec children inherit it and `gh auth git-credential get` honours it with **no keyring entry**. A stale `users: GeoKM: {}` in `~/.config/gh/hosts.yml` **shadows** the env token and makes `gh auth status` exit 1; that file must contain only `git_protocol: https`. Push to `GeoKM/jarvis-workspace` (public, default branch master) works. The earlier OAuth-keyring path died when gnome-keyring's `login` collection locked (unlocking needs the login password via a desktop session — `openclaw secrets request` cannot deliver it to Telegram). <!-- project: github.com/GeoKM/jarvis-workspace -->

## Unattended-Upgrades Rollout — No Reboots (2026-10-20)

Scope approved by Keith: non-Proxmox-cluster hosts only (proxima, proxima2-5 stay manual). manifold and Helios excluded. ArosOne ignored. cbm deferred (powered off). **No reboots anywhere.**

- **hebei (gateway, Ubuntu 24.04 noble)** — full config. Custom `20auto-upgrades` with `APT::Periodic::{Update-Package-Lists,Download-Upgradeable-Packages,Unattended-Upgrade,AutocleanInterval,Unattended-Upgrade-Delay}` plus `Unattended-Upgrade::Automatic-Reboot "false"` uncommented. Backup `/var/backups/openclaw-unattended-upgrades/20261020-132427/`.
- **All others (9 hosts)** — "K path": plain `apt-get install -y unattended-upgrades`, stock conffiles left alone; `Automatic-Reboot` stays commented (package default = false). The postinst enables the service + timers.
- Host notes: xaviernv = Ubuntu 20.04 focal aarch64 (Jetson), sudo needs a password for file writes; simul = Debian 13 trixie (QEMU VM), `update-notifier-common` has no trixie candidate → replaced by `apt-config-auto-update`; retrobench = Debian 12 bookworm, liquorix 6.12.7-2, u-u 2.9.1+nmu3 already present; LXC/Pi hosts (dockyards, kasm, tg-b, arya, plexus, pidp11) run host/vendor kernels so apt will not replace them; tg-b is Ubuntu 26.04 resolute. **No kernel-blacklist file was written anywhere** — `keith` has no sudoers NOPASSWD for `/etc/apt/apt.conf.d` writes.
- **Caveat:** a kernel package *can* enter the upgrade queue on hebei/xaviernv/simul/retrobench. `Automatic-Reboot` is false everywhere, so it installs but does not reboot — it then shows as a `reboot_required` CRITICAL in the Lab Monitor digest until manually rebooted.
- Rollback (anywhere except hebei): `apt-get purge unattended-upgrades`.

## reboot_required Flag in linux-system-monitor (2026-10-20) <!-- project: github.com/GeoKM/jarvis-workspace -->

- `scripts/collect-metrics.py` computes `reboot_required` (needed/pkgs/reasons/kernel_age_h) from `/var/run/reboot-required{,.pkgs,.reason}` and emits it in the JSON snapshot; `scripts/parse-report.py` adds `check_reboot()` (CRITICAL when needed, else OK with running-kernel age), called once in `main()` after `check_docker`.
- Both branches verified on hebei: OK (`Reboot OK (running kernel 849.4h)`) and CRITICAL via a synthetic `/var/run/reboot-required` (header flipped, package list rendered, `[CRITICAL] reboot_required = True`); the synthetic flag was removed afterwards.
- Lesson: `collect-metrics.py` had been truncated to a 41-line fragment in an earlier session and was restored from `collect-metrics.py.bak.20261019-212104` (297-line working version). **Resolved 2026-10-20 21:40**: 158 stray `*.bak.*` / `*.broken-fragment.*` files (~924K) plus `__pycache__/` were trashed via `gio trash` (recoverable in `~/.local/share/Trash/files/`); the dir went 1.1M → 104K, all 13 real scripts intact. <!-- project: github.com/GeoKM/jarvis-workspace -->

---

## System Upgrades (2026-09-30)

### CBM: Debian 12 (Bookworm) → Debian 13 (Trixie)
CBM (`cbm.can.barnabasmusic.com`, `192.168.1.241`) — Pentium 4 3.00GHz, 3.3GiB RAM, x86_64
- Debian 13.7 Trixie, kernel 6.12.111+deb13-amd64 (old 6.1.0-23 remains as GRUB fallback)
- Full-upgrade: 806 upgraded, 164 new, 50 removed (~28 min). Pre: cleared 7 old kernels, 151M apt
  archives, 81.4M journal, apt cache → /home/apt-cache (var only 1.3G free). Post: dpkg
  --configure -a, apt-get -f install, autoremove --purge (~70 obsolete pkgs).
- FS: DOS (/dev/sdb1 vfat), WIN (/dev/sdb5 vfat), WIN2K (/dev/sdc1 ntfs) remounted. LVM: CBM-vg
  root 7.2G, var 2.7G, home 25G, tmp 531M, swap; / 4.1G free (42%), /var 1.1G (59%)
- sudo needs password (keith) and blocks env vars (DEBIAN_FRONTEND) → use dpkg --configure -a
- Wazuh agent installed (wazuh.list in sources.list.d)

### TG-B: Ubuntu 24.04 LTS (Noble) → Ubuntu 26.04.1 LTS (Resolute)
TG-B (`tg-b.can.barnabasmusic.com`, `192.168.1.187`) — LXC 107 on proxima3, Turion II Neo N40L, 7.8G
- Ubuntu 26.04.1, kernel 7.0.14-17-pve (Proxmox host kernel — not upgraded); 197 pkgs; RAM
  temporarily 512→2048MiB for the upgrade, then restored
- Python 3.12→3.14, OpenSSH 9.6→10.2, OpenSSL 3.0→3.5, curl 8.5→8.18, systemd→259.5,
  libc 2.39→2.43, sudo 1.9.15→1.9.17
- sudoers fix: removed `Defaults:keith !requiretty` from /etc/sudoers.d/90-keith (requiretty
  removed in sudo 1.9.17). Twingate → deb822 (`twingate.sources`); Ubuntu sources moved to
  /etc/apt/sources.list.d/ubuntu.sources. do-release-upgrade has no --dry-run/--sandbox
- sudo needs password; blocks env vars (same as CBM)

### Proxmox Container Map (reference):
Updated 2026-10-21 (post-rebuild). VM 109 **Plexus** was deleted 2026-10-20 after the compromise,
then rebuilt as an **LXC on Proxima5** (192.168.1.241).

| VMID | Name | Node | Type | Memory | Status |
|------|------|------|------|--------|--------|
| 100 | Dockyards | proxima | LXC | 2048 MiB | running |
| 101 | Arya | proxima3 | LXC | 1024 MiB | running |
| 102 | KASM | proxima2 | LXC | 4096 MiB | running |
| 103 | Hebei | proxima4 | QEMU | 9024 MiB | running |
| 104 | Pegasus | Proxima5 | LXC | 4096 MiB | stopped (never deleted — just not started after the Proxima5 crash) |
| 105 | HMC | Proxima5 | QEMU | 4096 MiB | stopped (intentional) |
| 106 | ArosOne | Proxima5 | QEMU | 2048 MiB | stopped (intentional) |
| 107 | tg-b | proxima3 | LXC | 512 MiB | running |
| 108 | Simul | proxima | LXC | 2048 MiB | running |
| 109 | Plexus | Proxima5 | LXC | 4096 MiB | running (rebuilt 2026-10-21, .241) |

## Promoted From Short-Term Memory (Condensed 2026-10-20)

Auto-promoted Aug–Sep 2026 monitoring snapshots, distilled. Raw entries live in `memory/2026-08-*.md` … `memory/2026-09-*.md`; the promotion blocks used to be re-pushed verbatim every cycle and pushed MEMORY.md past the 20,000-char bootstrap cap.

- **Recurring fleet state (Aug–Sep 2026; mostly resolved/superseded):** security updates unapplied to proxima–proxima5 (22 pkgs each) and retrobench; swap pressure on proxima (2.2–3.0GiB), proxima2 (2.9–3.0GiB), proxima4, plexus (2.0–2.6GiB); disk at 92% on arya (`_export_LibraryPool_Archive`) and proxima3 (`_PX3_Data0_subvol-101-disk-0`). **Resolved by 2026-09-04:** hebei cleared its update backlog (24 → 0); proxima3 swap alert cleared (disk still 92%).
- **Standing remediation track:** apply security updates to the Proxmox cluster + retrobench; prune arya and proxima3 storage; investigate swap.
- **AIX midday monitor cron fix (2026-08-05):** payload changed from `agentTurn` → `command` (`bash .../run-aix-monitor.sh --all`), `sessionTarget: "isolated"`, `delivery.mode: "announce"` with `--best-effort-deliver`. <!-- project: github.com/GeoKM/jarvis-workspace -->
- **Stale note (2026-10-21):** "xaviernv / cbm / Helios unreachable since 2026-08-13" no longer holds — xaviernv was reachable again by 2026-10-20; only cbm and Helios remain long-standing down, and VM 109 (plexus) has been removed.
