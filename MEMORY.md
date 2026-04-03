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

### Secrets (as of 2026-04-03)
| Variable | Purpose |
|---|---|
| `OPENCLAW_GATEWAY_TOKEN` | Gateway authentication |
| `OPENCLAW_TELEGRAM_TOKEN` | Telegram bot |
| `OPENCLAW_BRAVE_KEY` | Brave Search API |
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
- Model: `ollama/gemma4:latest` (Tesla V100, 32GB VRAM)
- Session: isolated (fires independently of main session)
- Checks: Memory file maintenance → MEMORY.md, Git workspace status, Gateway health
- Silent unless there is a problem — reports via webchat only on issues

## Important Paths
- Workspace: `~/.openclaw/workspace/`
- OpenClaw config: `~/.openclaw/openclaw.json`
- Secrets: `~/.config/openclaw/openclaw.env`
- Systemd user services: `~/.config/systemd/user/`
