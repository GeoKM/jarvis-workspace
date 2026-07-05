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

## Promoted From Short-Term Memory (2026-06-24)

<!-- openclaw-memory-promotion:memory:memory/2026-06-19-2219.md:54:56 -->
- Conversation Summary: assistant: I’ll inspect the new Telegram group session and routing config. This may be a separate group allowlist/mention-policy issue rather than the forum-topic delivery bug. assistant: The group was received correctly; the problem is the same delivery-policy class, but for a **plain Telegram group** rather than a forum topic. I can see my generated greeting in the transcript, but it was normal final text, so it did not visibly post. I’ll add the same message-tool workaround for this new group and reset that session so it takes effect. assistant: I found it. [score=0.900 recalls=0 avg=0.620 source=memory/2026-06-19-2219.md:54-56]
<!-- openclaw-memory-promotion:memory:memory/2026-06-19-2219.md:60:63 -->
- Conversation Summary: Group: `Agent Chat and Support Group for BMS`; ID: `-1003882117886`; Session: `agent:main:telegram:group:-1003882117886`; Your invite message was seen with `was_mentioned: true`. [score=0.900 recalls=0 avg=0.620 source=memory/2026-06-19-2219.md:60-63]
<!-- openclaw-memory-promotion:memory:memory/2026-06-19-2219.md:65:65 -->
- Conversation Summary: I also found my generated reply in the transcript: [score=0.900 recalls=0 avg=0.620 source=memory/2026-06-19-2219.md:65-65]
<!-- openclaw-memory-promotion:memory:memory/2026-06-19-2219.md:43:43 -->
- Conversation Summary: I’ve created a daily tracker: [score=0.868 recalls=0 avg=0.620 source=memory/2026-06-19-2219.md:43-43]
<!-- openclaw-memory-promotion:memory:memory/2026-06-19-2219.md:50:53 -->
- Conversation Summary: I also logged it into today’s memory. user: [Mon 2026-05-11 22:36 GMT+10] Thanks Mate assistant: Anytime, Keith. We have the workaround in place, upstream notified, and a daily watch set. Quite a tidy result, despite Telegram’s best efforts. user: [Mon 2026-05-11 23:00 GMT+10] I just added a new Telegram chat group for all of my Agents to chat about general subjects. You did not reply to the invite. It is session telegram:g-agent-chat-and-support-group-for-bms [score=0.868 recalls=0 avg=0.620 source=memory/2026-06-19-2219.md:50-53]
<!-- openclaw-memory-promotion:memory:memory/2026-06-19-2219.md:58:58 -->
- Conversation Summary: The new group was received correctly: [score=0.868 recalls=0 avg=0.620 source=memory/2026-06-19-2219.md:58-58]
<!-- openclaw-memory-promotion:memory:memory/2026-06-19-2219.md:9:10 -->
- Conversation Summary: assistant: I have the GitHub skill loaded. I’ll verify `gh` authentication and then file a concise upstream issue with the evidence we’ve gathered. assistant: GitHub CLI is installed, but authentication is currently broken: [score=0.860 recalls=0 avg=0.620 source=memory/2026-06-19-2219.md:9-10]
<!-- openclaw-memory-promotion:memory:memory/2026-06-19-2219.md:19:19 -->
- Conversation Summary: Please run: [score=0.858 recalls=0 avg=0.620 source=memory/2026-06-19-2219.md:19-19]

## Promoted From Short-Term Memory (2026-06-27)

<!-- openclaw-memory-promotion:memory:memory/2026-06-24.md:4:4 -->
- Monitoring Report Format Standardisation (12:40): Keith requested consistent output formatting for the daily Linux and AIX monitoring reports, which previously varied based on model output. [score=0.815 recalls=0 avg=0.620 source=memory/2026-06-24.md:4-4]
<!-- openclaw-memory-promotion:memory:memory/2026-06-24.md:6:6 -->
- Monitoring Report Format Standardisation (12:40): **Actions taken:** [score=0.815 recalls=0 avg=0.620 source=memory/2026-06-24.md:6-6]
<!-- openclaw-memory-promotion:memory:memory/2026-06-24.md:7:10 -->
- Monitoring Report Format Standardisation (12:40): Created `skills/linux-system-monitor/references/report-format-template.md` — a mandatory report format template covering both Linux and AIX report layouts; Updated `linux-system-monitor` cron job prompt to require reading and following the template verbatim; Updated `AIX midday monitoring` cron job prompt to require reading and following the AIX section of the template; Template defines: exact header format, section ordering (CRITICAL → Warnings → Unreachable → Nominal → Action Items), table columns, emoji indicators, issue combining rules, and explicit "do NOT include" rules for... [score=0.815 recalls=0 avg=0.620 source=memory/2026-06-24.md:7-10]

## Promoted From Short-Term Memory (2026-06-28)

<!-- openclaw-memory-promotion:memory:memory/2026-06-24.md:12:12 -->
- Monitoring Report Format Standardisation (12:40): Template location: `~/.openclaw/workspace/skills/linux-system-monitor/references/report-format-template.md` [score=0.869 recalls=0 avg=0.620 source=memory/2026-06-24.md:12-12]

## Promoted From Short-Term Memory (2026-07-04)

<!-- openclaw-memory-promotion:memory:memory/2026-07-01.md:24:27 -->
- Cluster: Proxima-One (live check): 5 nodes, all online, quorum OK; 4 VMs (3 running, 1 stopped: Aros2 on proxima3); 5 LXCs all running; Ceph: HEALTH_WARN — 1 OSD experiencing slow operations [score=0.815 recalls=0 avg=0.620 source=memory/2026-07-01.md:24-27]
<!-- openclaw-memory-promotion:memory:memory/2026-07-01.md:28:30 -->
- Cluster: Proxima-One (live check): ZFS: All pools ONLINE; Proxima3 PX3_Data0: 8.7TB allocated, 945GB free (88% used) ⚠️; Proxima4 AI0: 32% fragmentation [score=0.815 recalls=0 avg=0.620 source=memory/2026-07-01.md:28-30]
<!-- openclaw-memory-promotion:memory:memory/2026-07-01.md:39:41 -->
- Disk Alerts: arya: _export_LibraryPool_Archive at 92.1% — separate host, not Proxmox; Proxima3 PX3_Data0: confirmed ~88% used — ZFS pool near capacity; All other Proxmox node disks healthy (10-46%) [score=0.815 recalls=0 avg=0.620 source=memory/2026-07-01.md:39-41]

## Promoted From Short-Term Memory (2026-07-05)

<!-- openclaw-memory-promotion:memory:memory/2026-07-01.md:11:14 -->
- Key Issues: **Security packages** — 9 hosts need updates (xaviernv worst: 20, retrobench: 15); **Swap pressure** — hebei (1.4Gi), proxima (3.1Gi), proxima2 (2.7Gi), proxima4 (1.9Gi); **Disk space** — arya (_export_LibraryPool_Archive 92.1%), proxima3 (_PX3_Data0_subvol-101-disk-0 92.1%); **Network** — cbm (192.168.1.19), Helios (192.168.1.58) unreachable [score=0.869 recalls=0 avg=0.620 source=memory/2026-07-01.md:11-14]
<!-- openclaw-memory-promotion:memory:memory/2026-07-01.md:17:19 -->
- Notes: SSH key access not configured from this session to remote hosts; Monitoring agent has credentials — snapshot came from there; CBM/Helios confirmed unreachable via ping [score=0.869 recalls=0 avg=0.620 source=memory/2026-07-01.md:17-19]
<!-- openclaw-memory-promotion:memory:memory/2026-07-01.md:5:8 -->
- Host Status Summary: 🟢 OK (5): dockyards, simul, tg-b, manifold, pidp11; ⚠️ WARNING (2): arya (disk 92.1%), hebei (swap 1.4Gi); 🔴 CRITICAL (9): xaviernv, retrobench, proxima, proxima2, proxima3, proxima4, proxima5, kasm (security packages), hebei (high swap noted); ⬛ UNREACHABLE: cbm, Helios (no route) [score=0.869 recalls=0 avg=0.620 source=memory/2026-07-01.md:5-8]
<!-- openclaw-memory-promotion:memory:memory/2026-07-01.md:33:36 -->
- Security Updates — Proxmox nodes: All 5 Proxmox nodes share same packages: 37 upgradable total; 3 security-specific: libhttp-daemon-perl, libssh2-1t64, python3-urllib3 (confirmed on proxima); NOT 3 per-node — monitoring likely aggregated across cluster rep; **xaviernv and retrobench NOT on Proxmox — separate SSH access needed** [score=0.837 recalls=0 avg=0.620 source=memory/2026-07-01.md:33-36]
<!-- openclaw-memory-promotion:memory:memory/2026-07-01.md:44:45 -->
- Swap Alerts: Hebei (VM on Proxima4): 87.5% memory allocated — swap pressure expected; Proxima VMs are consuming high memory (Hebei VM: 3.5GB, HMC: 3.9GB) [score=0.837 recalls=0 avg=0.620 source=memory/2026-07-01.md:44-45]
<!-- openclaw-memory-promotion:memory:memory/2026-07-01.md:48:49 -->
- Unreachable: cbm (192.168.1.19): genuinely off-network; Helios (192.168.1.58): genuinely off-network [score=0.837 recalls=0 avg=0.620 source=memory/2026-07-01.md:48-49]
<!-- openclaw-memory-promotion:memory:memory/2026-07-01.md:52:54 -->
- SSH Access Gap: This session has no key-based SSH to xaviernv, retrobench, kasm, arya, hebei, cbm, Helios; Proxmox cluster accessible via jarvis@proxima + id_jt_ed25519; Monitoring agent likely uses different credentials [score=0.837 recalls=0 avg=0.620 source=memory/2026-07-01.md:52-54]
