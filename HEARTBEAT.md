# HEARTBEAT.md — Periodic Maintenance Checklist

Run these checks silently. Reply HEARTBEAT_OK only if everything is normal.
Message the user only if there is a problem.

## Tasks

1. **Memory file maintenance**
   - Read memory/YYYY-MM-DD.md for today and yesterday
   - If new significant events/decisions are logged, distill key points into MEMORY.md
   - Keep MEMORY.md curated — add new insights, remove outdated info

2. **Git workspace sync & status**
   - cd ~/.openclaw/workspace && git status --short
   - If there are uncommitted changes, do NOT auto-commit (user reviews first)
   - If there are stashes, note them silently
   - If repo is clean, do nothing

3. **Gateway health check**
   - Run: systemctl --user status openclaw-gateway
   - If not "active (running)", there is a problem
   - If gateway process is running but memory search is broken, there may be a problem
   - Report only actual problems

## Response Rules
- All checks pass → reply HEARTBEAT_OK
- Something needs attention → reply with the specific issue
- Never reply with full diagnostic output unless there's a problem
