# Heartbeat (heartbeat-4h) — silent maintenance checklist

This file is the authoritative checklist for the `heartbeat-4h` automation
(job id `abf05994-45dc-4dba-b410-eeb78af88448`, cron `0 */4 * * *`, tz
Australia/Sydney, isolated session, model `ollama/minimax-m3.1-flash:cloud`).

Run each step below. Be silent unless something is actually wrong.

## CRITICAL — command form rules

The host exec approval layer is `security=allowlist, ask=on-miss,
askFallback=deny`, and headless scheduled runs **cannot** wait for an
interactive approval prompt. Three command shapes are therefore **denied
outright**, and the agent then stalls until the job's 600s timeout:

| Denied shape | Example | Use instead |
|---|---|---|
| `cd <dir> && ...` | `cd ~/.openclaw/workspace && git status` | `git -C /home/keith/.openclaw/workspace status` |
| command substitution in a path | `cat .../$(date +%F).md` | `date +%F` as its own call, then the `read` tool |
| chained `&&` commands | `a && b && c` | one command per exec call |

A denied exec is **not** a transient error to retry — switch to the safe form
immediately. Never wait on an approval that cannot arrive.

## 1. Memory maintenance

1. `exec`: `date +%Y-%m-%d`
2. `exec`: `date -d yesterday +%Y-%m-%d`
3. Use the **`read` tool** (not `cat`) on:
   - `/home/keith/.openclaw/workspace/memory/<today>.md`
   - `/home/keith/.openclaw/workspace/memory/<yesterday>.md`
   Skip any file that does not exist.
4. If either file contains significant new insights, append a distilled entry to
   `/home/keith/.openclaw/workspace/MEMORY.md` using the **`edit` tool**.
   Otherwise do nothing.

## 2. Git workspace status

1. `exec`: `git -C /home/keith/.openclaw/workspace status --short -- . ':!codex' ':!skills/aix-system-monitor' ':!state'`
2. `exec`: `git -C /home/keith/.openclaw/workspace stash list`

Report only if there are uncommitted changes. **Do NOT auto-commit** — the
separate `Daily workspace git commit & push` automation owns committing, and it
must remain the only writer of `Auto-commit YYYY-MM-DD HH:MM` commits.

## 3. Gateway health

1. `exec`: `systemctl --user is-active openclaw-gateway`
2. If the output is exactly `active`, the gateway is healthy — report nothing.
3. If it is anything else (`inactive`, `failed`, `activating`), retry as two
   separate exec calls: `sleep 10`, then
   `systemctl --user is-active openclaw-gateway`.
4. Report a problem only if the retry is also not `active`, stating
   `Gateway service is <status>` using the literal systemctl output.

## Response rules

- All checks pass → reply with exactly `HEARTBEAT_OK` and nothing else.
- A problem exists → reply with a single short sentence naming it.
- Never explain reasoning, methodology, or tool-call results.
- Never narrate what was done — only what is wrong, if anything.
