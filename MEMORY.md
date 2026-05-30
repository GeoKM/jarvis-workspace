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

## Promoted From Short-Term Memory (2026-05-07)

<!-- openclaw-memory-promotion:memory:memory/2026-04-21.md:32:42 -->
- - **4 AIX** hosts: Persei-NIM (AIX 5L TL5), Celestia (AIX 7.2 TL5), Titan-AIX71 (AIX 7.1 TL5), 43p (AIX 5.1) - All producing valid snapshots; dashboard displaying correctly after memory/LCPU fixes ## Key File Paths (reference) - AIX collector: `~/.openclaw/workspace/skills/aix-system-monitor/scripts/collect-aix-metrics.py` - AIX orchestrator: `~/.openclaw/workspace/skills/aix-system-monitor/scripts/run-aix-monitor.sh` - Linux collector: `~/.openclaw/workspace/skills/linux-system-monitor/scripts/collect-metrics.py` - AIX hosts inventory: `~/lab-docs/monitoring/aix-hosts.d/hosts.yaml` - AIX snapshots: `~/lab-docs/monitoring/snapshots-aix/<hostname>/` - Dashboard server: `~/Projects/lab-monitor-dashboard/server.py` [score=0.811 recalls=5 avg=0.398 source=memory/2026-04-21.md:32-42]

---
**[Telegram Retro Computing Fun Topic Workaround — 2026-05-11]**
If Keith says he has added a new Topic area in Telegram group `Retro Computing Fun` (`-1003981232995`), add that topic ID under `channels.telegram.groups["-1003981232995"].topics` in `~/.openclaw/openclaw.json` with the `TELEGRAM_FORUM_TOPIC_DELIVERY_WORKAROUND` systemPrompt that forces replies through the Telegram `message` tool (`action="send"`, `channel="telegram"`, `target="-1003981232995"`, `replyTo` = triggering Telegram `message_id`). Create a timestamped config backup first. Restart/reload the gateway afterwards. If the topic already has an existing session, reset `agent:main:telegram:group:-1003981232995:topic:<topicId>` so the prompt is picked up. Existing working examples: topics `1` and `86`.
---
---
**[Telegram Agent Chat Group Workaround — 2026-05-11]**
Telegram group `Agent Chat and Support Group for BMS` has id `-1003882117886` and session key `agent:main:telegram:group:-1003882117886`. It needs the same visible-reply workaround class as Retro Computing Fun: configure `channels.telegram.groups["-1003882117886"].systemPrompt` to force replies through the Telegram `message` tool (`action="send"`, `channel="telegram"`, `target="-1003882117886"`, `replyTo` = triggering Telegram `message_id` when available). Create a timestamped `~/.openclaw/openclaw.json` backup before edits, restart/reload gateway, and reset the group session if the prompt was added after the session existed.
---


## Promoted From Short-Term Memory (2026-05-16)

<!-- openclaw-memory-promotion:memory:memory/2026-05-11.md:2:2 -->
- - 22:23 Telegram Retro Computing Fun topic delivery issue: Topic 1 and Topic 86 both successfully replied after resetting topic 1 session and adding explicit group/topic systemPrompt workaround forcing Telegram `message` tool sends for group -1003981232995 topics 1 and 86. Config backups: openclaw.json.bak-20260511-221112 and openclaw.json.bak-20260511-221911. Diagnostics flags telegram.http/telegram.payload remain enabled. [score=0.865 recalls=0 avg=0.620 source=memory/2026-05-11.md:2-2]
<!-- openclaw-memory-promotion:memory:memory/2026-05-11.md:4:4 -->
- - 22:35 Created daily cron job `3f39e26c-f206-494d-b0f6-45c9109f68ce` to track OpenClaw GitHub issue #80647 at 09:00 Australia/Sydney and announce meaningful changes/fix status. [score=0.847 recalls=0 avg=0.620 source=memory/2026-05-11.md:4-4]

## Promoted From Short-Term Memory (2026-05-17)

<!-- openclaw-memory-promotion:memory:memory/2026-05-12.md:4:5 -->
- Keith created a new Telegram forum topic for discussing the SIMH VAXcluster. Topic ID and config noted in MEMORY.md. [score=0.854 recalls=0 avg=0.620 source=memory/2026-05-12.md:4-4]
