# MEMORY.md — Long-Term Memory

## Operating Procedures

### Secrets Management

**Critical rule:** Before modifying any secrets file or openclaw config, create a backup.

Files requiring backup before modification:
- `~/.config/openclaw/openclaw.env` — OpenClaw secrets (API keys, tokens)
- `~/.openclaw/openclaw.json` — OpenClaw configuration

Backup procedure:
```bash
cp ~/.config/openclaw/openclaw.env ~/.config/openclaw/openclaw.env.bak-$(date +%Y%m%d%H%M%S)
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak-$(date +%Y%m%d%H%M%S)
```

After any modification to either file, validate and reload:
```bash
openclaw config validate && systemctl --user restart openclaw-gateway
```

Additional safeguard learned on 2026-04-05:
- Before editing `~/.config/openclaw/openclaw.env`, read the entire file first.
- Do not use fragile single-anchor targeted replacements for secrets files.
- Prefer append-only changes or a full verified rewrite that preserves all existing entries.
- Do not surface raw secret values in normal conversational responses.

### Environment Injection

Secrets are injected via three mechanisms:
- **Gateway service:** `~/.config/systemd/user/openclaw-gateway.service.d/env-file.conf` → `EnvironmentFile=`
- **Desktop/GUI apps:** `~/.config/environment.d/openclaw.conf` (loaded by systemd --user)
- **SSH/login shells:** `~/.profile` sources `~/.config/openclaw/openclaw.env`

If the TUI or CLI cannot resolve `OPENCLAW_GATEWAY_TOKEN` after a fresh login, the shell may not have sourced `~/.profile`. Run `exec bash -l` to force a login shell.

## System Architecture

### OpenClaw Gateway
- Service: `openclaw-gateway.service` (systemd --user)
- Config: `~/.openclaw/openclaw.json`
- Secrets: `~/.config/openclaw/openclaw.env` (mode 600)
- Port: 18789 (loopback)
- Auth: token-based

### Secrets (as of 2026-04-04)
| Variable | Purpose |
|---|---|
| `OPENCLAW_GATEWAY_TOKEN` | Gateway authentication |
| `OPENCLAW_TELEGRAM_TOKEN` | Telegram bot |
| `OPENCLAW_BRAVE_KEY` | Brave Search API |
| `OPENCLAW_PERPLEXITY_KEY` | Perplexity web search API |
| `OPENCLAW_GOOGLE_PLACES_KEY` | Google Places API |
| `OPENCLAW_WHISPER_KEY` | OpenAI Whisper API |
| `OPENCLAW_ELEVENLABS_KEY` | ElevenLabs TTS |

### Tailscale Serve

- Enabled: `tailscale serve --bg https+insecure://localhost:18789`
- Serve hostname: `https://hebei.tail4d3f85.ts.net/`
- Gateway config: `gateway.tailscale.mode: "serve"`
- Control UI allowed origins: `https://hebei.tail4d3f85.ts.net`
- Note: serve must be `https+insecure` (not plain `http`) to properly terminate TLS for the gateway

## Git Workspace Identity

- User: Jarvis KMT <xvr-jarvis@linux-mail.com>

## Heartbeat Cron

- Job: `heartbeat-4h` — fires every 4 hours (00:00, 04:00, 08:00, 12:00, 16:00, 20:00 AEDT)
- Session: isolated (fires independently of main session)
- Checks: Memory file maintenance → MEMORY.md, Git workspace status, Gateway health
- Silent unless there is a problem — reports via webchat only on issues
- As of 2026-04-06, the cron payload still specifies `ollama/gemma4:latest`, but the gateway reports that model is not allowed and falls back to the agent default model. Treat the configured model line as stale until the cron job is updated.

## Important Paths
- Workspace: `~/.openclaw/workspace/`
- OpenClaw config: `~/.openclaw/openclaw.json`
- Secrets: `~/.config/openclaw/openclaw.env`
- Systemd user services: `~/.config/systemd/user/`

## Git Remote

- https://github.com/GeoKM/jarvis-workspace

## Model Preferences (updated 2026-04-05)

- Default: `openai-codex/gpt-5.4`
- Fallback 1: `ollama/minimax-m2.7:cloud`
- Fallback 2: `openrouter/auto`

## linux-system-monitor Skill

**Skill dir:** `~/.openclaw/workspace/skills/linux-system-monitor/`
**Storage:** `~/lab-docs/monitoring/`

### What it does

SSH-less local + SSH-based remote Linux system monitoring. Collects CPU, memory,
disk, network, TCP, processes, services, security, NTP, and temperature metrics
as JSON snapshots. Applies threshold rules and emits a digest to Telegram via
cron. Prunes snapshots older than 30 days on each run.

### Key scripts

- `collect-metrics.sh` — collects metrics, emits JSON (runs locally or over SSH)
- `parse-report.py` — applies thresholds, writes snapshot + alert log, prints digest
- `run-monitor.sh` — orchestrator; reads `hosts.d/hosts.yaml`, loops all hosts

### Inventory

`~/lab-docs/monitoring/hosts.d/hosts.yaml`:
- `hebei` — local, no SSH
- `xaviernv` — SSH `keith@xaviernv.can.barnabasmusic.com`, key `~/.ssh/id_jt_ed25519`
- `retrobench` — SSH `keith@retrobench.can.barnabasmusic.com`, key `~/.ssh/id_jt_ed25519`
- `simul` — SSH `keith@simul.can.barnabasmusic.com`, key `~/.ssh/id_jt_ed25519`

### Cron job

```
ID:  69bd6692-073a-4f8d-94e5-d7ad151763aa
Name: linux-system-monitor
Cron: 0 12 * * *  (midday Australia/Sydney)
Delivers: Telegram (announce mode)
```

### Important bash + SSH lessons

- **Scalar SSH var pitfall:** Storing `SSH_CMD="ssh ... user@host"` then executing
  `"$SSH_CMD arg"` treats the whole string as a filename → "No such file or directory".
  **Fix:** use a bash array: `SSH_CMD=(ssh -o ... user@host)` and call `"${SSH_CMD[@]}"`.
- `bash -s --local` — use `--` so `--local` is a script arg, not a bash flag.
- `set -e` + pipeline → PIPESTATUS trap; use `|| true` on pipeline chains.
- `while read` loops run in a subshell — `return` exits the subshell, not the parent.
  Use `for` loops instead.
- Every `run_cmd` call needs `|| true` to survive `set -e` on legitimate non-zero exits.
- `journalctl -u a -u b` is invalid — run two separate invocations.
- `grep -c` returns exit 1 when count is 0 — always wrap: `grep -c ... || echo 0`.
- skill-creator `init_skill.py` preflight rejects multi-line shell heredocs — write
  scripts directly with the `write` tool instead.

## Dockyards added to linux-system-monitor (2026-04-06)

- `dockyards.can.barnabasmusic.com` — SSH `keith@dockyards...`, key `~/.ssh/id_jt_ed25519`
- Proxmox VM, 4 cores, 2GB RAM, 217h uptime
- Per-host threshold override: `network.drops_warn=2M`, `errs_warn=100`
- Has overcommit memory quirk: MemAvailable in /proc/meminfo reports virtual address space
  (8TB) not physical RAM; parse-report.py caps avail% at 100 to handle this
- Scientific notation overflow on long-running hosts: uptime*1000 and MemAvailable*1024 produce
  e.g. `2.14748e+09` which bash arithmetic can't parse. Fix: awk `sprintf("%.0f", ...)` for all
  memory/swap field multiplications in collect-metrics.sh

## Simul added to linux-system-monitor (2026-04-06)

- `simul.can.barnabasmusic.com` — SSH `keith@simul...`, key `~/.ssh/id_jt_ed25519`
- Debian 6.1, 4 cores, 217h uptime (~9 days)
- Runs DEC emulator (VAX) and DECnet — `vax` ~12% CPU, `pydecnet` ~5% MEM
- Per-host override: `network.drops_warn=2M` (same as Dockyards)
