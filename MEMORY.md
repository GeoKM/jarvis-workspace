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

## Promoted From Short-Term Memory (2026-05-16)

<!-- openclaw-memory-promotion:memory:memory/2026-05-11.md:2:2 -->
- - 22:23 Telegram Retro Computing Fun topic delivery issue: Topic 1 and Topic 86 both successfully replied after resetting topic 1 session and adding explicit group/topic systemPrompt workaround forcing Telegram `message` tool sends for group -1003981232995 topics 1 and 86. Config backups: openclaw.json.bak-20260511-221112 and openclaw.json.bak-20260511-221911. Diagnostics flags telegram.http/telegram.payload remain enabled. [score=0.865 recalls=0 avg=0.620 source=memory/2026-05-11.md:2-2]
<!-- openclaw-memory-promotion:memory:memory/2026-05-11.md:4:4 -->
- - 22:35 Created daily cron job `3f39e26c-f206-494d-b0f6-45c9109f68ce` to track OpenClaw GitHub issue #80647 at 09:00 Australia/Sydney and announce meaningful changes/fix status. [score=0.847 recalls=0 avg=0.620 source=memory/2026-05-11.md:4-4]

## Promoted From Short-Term Memory (2026-05-17)

<!-- openclaw-memory-promotion:memory:memory/2026-05-12.md:4:5 -->
- Keith created a new Telegram forum topic for discussing the SIMH VAXcluster. Topic ID and config noted in MEMORY.md. [score=0.854 recalls=0 avg=0.620 source=memory/2026-05-12.md:4-4]

## Promoted From Short-Term Memory (2026-05-31)

<!-- openclaw-memory-promotion:memory:memory/2026-05-06.md:1:6 -->
- # 2026-05-06 - In Telegram group "Retro Computing" topic "VAX VMS", Keith scheduled `SYS$MANAGER:BURST_PULL_NODEDB_WEEKLY.COM` on VMS node FUSION via batch queue `BURST_BATCH` for first run at 10-MAY-2026 03:00:00.00. - Keith asked to be reminded after the Sunday 10-MAY-2026 run so we can review the log and confirm the self-resubmit worked. - By early 7-MAY-2026, Keith had created and started batch queue `BURST_BATCH`, submitted the weekly job successfully, migrated `NETNODE_REMOTE.DAT` to `SYS$COMMON:[SYSEXE]` so FUSION and RISE share the same permanent DECnet node database, and successfully ran `SET KNOWN NODES ALL` on both nodes after enabling `OPER`, `NETMBX`, and `TMPMBX` for the process. [score=0.850 recalls=3 avg=0.573 source=memory/2026-05-06.md:1-6]

## Promoted From Short-Term Memory (2026-06-12)

<!-- openclaw-memory-promotion:memory:memory/2026-06-09.md:12:12 -->
- Network topology note: Hebei (current host) is not on the 10.0.0.0/24 AIX network. Monitoring should run from a host with access to that segment, or a VPN/bridge needs to be in place. [score=0.815 recalls=0 avg=0.620 source=memory/2026-06-09.md:12-12]
<!-- openclaw-memory-promotion:memory:memory/2026-06-09.md:4:4 -->
- All AIX hosts unreachable from Hebei — no route to 10.0.0.0/24 network segment. [score=0.815 recalls=0 avg=0.620 source=memory/2026-06-09.md:4-4]
<!-- openclaw-memory-promotion:memory:memory/2026-06-09.md:6:6 -->
- Monitored hosts: [score=0.815 recalls=0 avg=0.620 source=memory/2026-06-09.md:6-6]

## Promoted From Short-Term Memory (2026-06-18)

<!-- openclaw-memory-promotion:memory:memory/2026-06-09.md:7:10 -->
- AIX Midday Monitoring (12:00 AEST): Persei-NIM (persei-nim.can.barnabasmusic.com) — ❌ No route; Celestia (celestia.can.barnabasmusic.com) — ❌ No route; Titan-AIX71 (titan-aix71.can.barnabasmusic.com) — ❌ No route; 43p (43p.can.barnabasmusic.com) — ❌ No route [score=1.000 recalls=0 avg=0.620 source=memory/2026-06-09.md:7-10]
<!-- openclaw-memory-promotion:memory:memory/2026-05-30.md:13:13 -->
- AIX Midday Monitoring (12:01 AEST): No snapshot written for this run (hosts unavailable) [score=0.894 recalls=0 avg=0.620 source=memory/2026-05-30.md:13-13]
<!-- openclaw-memory-promotion:memory:memory/2026-05-30.md:5:8 -->
- AIX Midday Monitoring (12:01 AEST): All AIX hosts unreachable: Persei-NIM, Celestia, Titan-AIX71, 43p; Error: "No route to host" — network/path issue from Hebei to AIX subnet; Last successful collections:; Persei-NIM: 2026-05-28 [score=0.894 recalls=0 avg=0.620 source=memory/2026-05-30.md:5-8]
<!-- openclaw-memory-promotion:memory:memory/2026-05-30.md:9:12 -->
- AIX Midday Monitoring (12:01 AEST): Celestia: 2026-05-28; Titan-AIX71: 2026-05-21; 43p: 2026-05-13; Monitoring script: `~/.openclaw/workspace/skills/aix-system-monitor/scripts/run-aix-monitor.sh` [score=0.894 recalls=0 avg=0.620 source=memory/2026-05-30.md:9-12]

## Promoted From Short-Term Memory (2026-06-22)

<!-- openclaw-memory-promotion:memory:memory/2026-06-18-2311.md:16:19 -->
- Conversation Summary: user: @JarvisKMT_bot Please share the Cluster details with @HermesKMT_bot , remember you need to explicitly @mention each other in this Telegram topic if you want you other agent buddy's to see you messages. assistant: Posted with explicit @mentions for both of them. user: Oh My God.... Its not rocket science. How is it that you guys keep mixing up your bot names. Kerri You are @kerriKMT_bot Hermes You are @HermesKMT_bot (It just so happens that you are both instances of the Hermes Agent Framework) Jarvis is @JarvisKMT_bot and in OpenClaw Agent Framework. [score=0.866 recalls=0 avg=0.620 source=memory/2026-06-18-2311.md:16-19]
<!-- openclaw-memory-promotion:memory:memory/2026-06-18-2311.md:20:23 -->
- Conversation Summary: assistant: Apologies for the confusion — noted for future reference. I'll be more careful with bot handle etiquette going forward. user: OK @JarvisKMT_bot Please send the Cluster details to JarvisKMT_bot, remember to @mention him by name. assistant: Clarified back to Keith — that one didn't quite add up! user: @JarvisKMT_bot Yes Direct it to HermesKMT_bot [score=0.866 recalls=0 avg=0.620 source=memory/2026-06-18-2311.md:20-23]
<!-- openclaw-memory-promotion:memory:memory/2026-06-18-2311.md:24:26 -->
- Conversation Summary: assistant: Sent to @HermesKMT_bot. user: OK all @HermesKMT_bot @JarvisKMT_bot @kerriKMT_bot You should be able to find the VAX VMS full documentation that Jarvis previously created in my Obsidian vault using your Obsidian skills. assistant: Posted for both agents. The VAX Cluster Rebuild project notes are all in **CentralVault** under `Projects/VAX Cluster Rebuild/` — index at `index.md`. [score=0.866 recalls=0 avg=0.620 source=memory/2026-06-18-2311.md:24-26]
<!-- openclaw-memory-promotion:memory:memory/2026-06-18-2311.md:12:15 -->
- Conversation Summary: user: @JarvisKMT_bot you should already have a great document in your workspace that you previously created to describe the Cluster environment. assistant: Posted. I've also logged this new topic setup to today's memory file. What would you like to explore first in the cluster? user: @JarvisKMT_bot can you share that detail with @HermesKMT_bot and @kerriKMT_bot assistant: Sent. They're not registered as sub-agents I can message directly, so I've posted the context into the same topic for them to pick up. [score=0.837 recalls=0 avg=0.620 source=memory/2026-06-18-2311.md:12-15]
<!-- openclaw-memory-promotion:memory:memory/2026-06-18-2311.md:3:5 -->
- Session: 2026-06-18 23:11:06 GMT+10: **Session Key**: agent:main:telegram:group:-1003981232995:topic:332; **Session ID**: 530f2420-0006-424b-b877-07af6ec73148; **Source**: telegram [score=0.837 recalls=0 avg=0.620 source=memory/2026-06-18-2311.md:3-5]
<!-- openclaw-memory-promotion:memory:memory/2026-06-19-2219.md:30:30 -->
- Conversation Summary: <https://github.com/openclaw/openclaw/issues/80647#issuecomment-4420719837> [score=0.815 recalls=0 avg=0.620 source=memory/2026-06-19-2219.md:30-30]
<!-- openclaw-memory-promotion:memory:memory/2026-06-19-2219.md:45:48 -->
- Conversation Summary: **Issue:** OpenClaw #80647; **Schedule:** every day at **09:00 Australia/Sydney**; **Job ID:** `3f39e26c-f206-494d-b0f6-45c9109f68ce`; **Behaviour:** report only meaningful changes — closure, maintainer response, linked PR, merged fix, release note, or requested follow-up. [score=0.815 recalls=0 avg=0.620 source=memory/2026-06-19-2219.md:45-48]
<!-- openclaw-memory-promotion:memory:memory/2026-06-19-2219.md:69:69 -->
- Conversation Summary: …but it was emitted as normal final text, not via the Telegram `message` tool, so it stayed invisible. Same upstream bug class again. [score=0.815 recalls=0 avg=0.620 source=memory/2026-06-19-2219.md:69-69]
<!-- openclaw-memory-promotion:memory:memory/2026-06-18-2311.md:9:9 -->
- Conversation Summary: assistant: [score=0.807 recalls=0 avg=0.620 source=memory/2026-06-18-2311.md:9-9]
