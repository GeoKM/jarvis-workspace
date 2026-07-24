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
- Root SSH also works: `root@proxima.can.barnabasmusic.com` (and all proxima2-5 nodes)
- SSH identity file → `~/.ssh/id_jt_ed25519`
- SSH execution model → `ssh ... "sudo <proxmox-command>"` (jarvis) or direct as root
- primary API endpoint → `https://proxima.can.barnabasmusic.com:8006/api2/json`
- auth model → API token preferred, SSH+sudo fallback

### XavierNV
- xaviernv → `keith@xaviernv.can.barnabasmusic.com` (`192.168.1.115`), port 22
- SSH identity file → `~/.ssh/id_jt_ed25519`
- OS: Ubuntu 20.04 (Focal), NVIDIA Jetson Xavier (aarch64, Tegra kernel 5.10)
- Also reachable via Tailscale: `xaviernv.tail4d3f85.ts.net` (100.107.211.73)

### Plexus
- plexus → `keith@plexus.can.barnabasmusic.com` (`192.168.1.241`), port 22
- SSH identity file → `~/.ssh/id_jt_ed25519`
- OS: Debian 13 (Trixie), kernel 6.12.96+deb13-amd64
- Proxmox VM 109 on proxima5
- Role: Plex Media Server
- NFS mounts from poly (192.168.1.8): `/Data/MP3_Library`, `/Data/VIDEO`
- NFS auto-mount: `nfs-mount-after-dhcp.service` (waits for DHCP lease before `mount -a -t nfs`)
- sudoers: NOPASSWD allowlist only (no general NOPASSWD) — use `sudo install` trick for root file writes

### Retrobench
- retrobench → `keith@retrobench.can.barnabasmusic.com` (`192.168.1.218`), port 22
- SSH identity file → `~/.ssh/id_jt_ed25519`
- OS: Debian 12 (Bookworm), liquorix kernel

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
