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

## Promoted From Short-Term Memory (2026-06-23)

<!-- openclaw-memory-promotion:memory:memory/2026-06-19-2219.md:67:67 -->
- Conversation Summary: > “Hey Keith — Jarvis checking in…” [score=0.869 recalls=0 avg=0.620 source=memory/2026-06-19-2219.md:67-67]
<!-- openclaw-memory-promotion:memory:memory/2026-06-19-2219.md:13:14 -->
- Conversation Summary: Failed to log in to github.com account GeoKM The token in default is invalid. [score=0.837 recalls=0 avg=0.620 source=memory/2026-06-19-2219.md:13-14]
<!-- openclaw-memory-promotion:memory:memory/2026-06-19-2219.md:17:17 -->
- Conversation Summary: So I **can’t file the issue yet** until GitHub auth is refreshed. [score=0.837 recalls=0 avg=0.620 source=memory/2026-06-19-2219.md:17-17]
<!-- openclaw-memory-promotion:memory:memory/2026-06-19-2219.md:22:22 -->
- Conversation Summary: gh auth login -h github.com [score=0.837 recalls=0 avg=0.620 source=memory/2026-06-19-2219.md:22-22]
<!-- openclaw-memory-promotion:memory:memory/2026-06-19-2219.md:25:28 -->
- Conversation Summary: Then tell me when it’s done, and I’ll create the upstream OpenClaw issue immediately. user: [Mon 2026-05-11 22:33 GMT+10] OK Done. I also had brew update gh. assistant: There is already an open upstream issue that matches this almost exactly: **#80647**. Rather than create a duplicate, I’ll add our fresh 2026.5.7 reproduction as a comment with the Topic 1 vs Topic 86 evidence and workaround result. assistant: Reported upstream as a comment on the existing matching issue: [score=0.837 recalls=0 avg=0.620 source=memory/2026-06-19-2219.md:25-28]
<!-- openclaw-memory-promotion:memory:memory/2026-06-19-2219.md:3:5 -->
- Session: 2026-06-19 22:19:12 GMT+10: **Session Key**: agent:main:main; **Session ID**: be66393e-7732-4025-8547-a58cd1ffabc4; **Source**: webchat [score=0.837 recalls=0 avg=0.620 source=memory/2026-06-19-2219.md:3-5]
<!-- openclaw-memory-promotion:memory:memory/2026-06-19-2219.md:32:32 -->
- Conversation Summary: I did not create a duplicate issue because #80647 already describes the same underlying fault: Telegram forum/group sessions silently completing with normal final text when visible replies require the `message` tool. [score=0.837 recalls=0 avg=0.620 source=memory/2026-06-19-2219.md:32-32]
<!-- openclaw-memory-promotion:memory:memory/2026-06-19-2219.md:34:34 -->
- Conversation Summary: I added our fresh `2026.5.7` reproduction, including: [score=0.837 recalls=0 avg=0.620 source=memory/2026-06-19-2219.md:34-34]
<!-- openclaw-memory-promotion:memory:memory/2026-06-19-2219.md:36:39 -->
- Conversation Summary: Topic 1 final-text failure; Topic 86 explicit `message` tool success; Session reset + topic-level prompt workaround; Recommendation for runtime diagnostics/guarding. [score=0.837 recalls=0 avg=0.620 source=memory/2026-06-19-2219.md:36-39]
<!-- openclaw-memory-promotion:memory:memory/2026-06-19-2219.md:40:41 -->
- Conversation Summary: user: [Mon 2026-05-11 22:35 GMT+10] OK we should track that bug Daily to find out when it is fixed. assistant: Done. [score=0.837 recalls=0 avg=0.620 source=memory/2026-06-19-2219.md:40-41]

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
