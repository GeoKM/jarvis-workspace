# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### Proxmox

- proxmox → `jarvis@proxima.can.barnabasmusic.com` (`192.168.1.93`), port 22, key-based SSH
- SSH identity file → `~/.ssh/id_jt_ed25519`
- SSH execution model → `ssh ... "sudo <proxmox-command>"`
- primary API endpoint → `https://proxima.can.barnabasmusic.com:8006/api2/json`
- auth model → API token preferred, SSH+sudo fallback

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
