---
summary: "Diagnosis of OpenClaw's stale SQLite snapshot accumulation and state-DB contention on Hebei, and the verified remediation."
tags: [openclaw, sqlite, snapshots, doctor, disk, troubleshooting]
---

# Stale SQLite snapshots and state-DB contention (Hebei)

## Symptom

`~/.cache/openclaw/` accumulated read-only snapshot directories (peak 185 MB
across 4 dirs), with the Gateway logging:

```
SQLite read-only snapshot cleanup failed. Check directory permissions and available storage before retrying.
  subsystem=infra/sqlite-snapshot  path=~/.cache/openclaw/openclaw-sqlite-readonly-v2-<id>  operation=rm
```

Doctor lint also produced spurious errors when run concurrently with other CLI
reads: *"Shared-state read scope is closing or closed"* and *"auth profile store
unreadable"*.

## Root causes (three distinct ones)

1. **Retired snapshots whose `rm` failed.** Each snapshot is a private copy of
   the state DB staged under `~/.cache/openclaw/`. Cleanup is an `rm -rf` after
   the reader retires. On local ext4 this normally succeeds; it failed only
   under peak load (2 failures total, both at 17:22). A failed cleanup leaves
   the directory on disk with a `.seal` marker, and it is **not** retried
   automatically.
2. **Deleted-but-open file descriptors.** The Gateway keeps long-lived
   read-only snapshot FDs. When the snapshot directory is removed while the FD
   is still open, the space stays consumed (unlink-while-open) even though the
   path is gone. Measured: 4 FDs / 69 MiB held invisible in `du`. **Only a
   process restart releases this.**
3. **Doctor lint running concurrently with other CLI reads.** The lint forks
   read-only snapshot workers; concurrent CLI reads on the same state DB make
   those workers' scopes close early. This produced the misleading
   "read scope is closing" / "auth profile store unreadable" errors.

## What was NOT a problem

- **No DB bloat.** `PRAGMA freelist_count` = 0 on the 236 MB agent DB; the
  state DB had only 152 free pages (~623 KB). VACUUM/reclamation had nothing
  to reclaim.
- **No sustained contention.** Under deliberate load (6 concurrent
  `secrets audit` reads + `health`), all reads succeeded cleanly. Doctor lint
  run against that same concurrent load returned **zero findings**.
- The earlier "state database is busy" errors were all from running
  `openclaw secrets apply` against a live Gateway — that command is
  offline-only by design, not a contention defect.

## Verified remediation

1. Re-verify no process holds the directory (`/proc/<pid>/fd` readlink scan),
   then remove it — the docs explicitly sanction this: *"If a reported temporary
   directory remains after OpenClaw exits, remove it once no process holds its
   files open."* `gio trash` keeps it recoverable.
2. Restart the Gateway to release deleted-but-open snapshot FDs. The runtime
   `gateway` restart action **defers while an agent run is active** (the run
   blocks it), so use `systemctl --user restart openclaw-gateway.service` from
   a shell outside the Gateway's own process tree.
3. Run `doctor --lint` **in isolation** — never concurrently with other CLI
   reads — or the scope-closing errors are measurement artifacts, not faults.

## Result

- Snapshot cache: 812 MB peak → **16 KB**, zero snapshot directories.
- Deleted-but-open FDs: 69 MiB → 65.9 MiB steady baseline (4 FDs), stable
  over a 5-minute watch — a fixed per-process baseline, not a leak.
- `doctor --lint --all`: 74 checks, all findings resolved except one
  informational codex plugin deprecation notice (Oct 2026 API retirement).
- `health --json`: `ok: true`, `degradedSecretOwners: null`.

## Also fixed along the way

`core/doctor/legacy-cron-store` flagged *"1 tool-bearing automation require
explicit scheduled authority reauthorization"*. The flagged job was
**`heartbeat-main`** (`16a7498a-…`, an `agentTurn` job with no `toolsAllow`
and no owner), not the AIX command job. Fix: `openclaw automations edit
<id> --tools <list>`, which stamps `scheduledToolPolicy: {version:1,mode:"trusted"}`.
The list should match the in-family sibling (`heartbeat-4h`): `read, edit,
write, apply_patch, exec, process, cron, memory_search, memory_get,
session_status, web_search, web_fetch, view_image`.

Note `toolsAllow` is only consulted for `agentTurn`/`script` payloads
(`cronJobUsesToolRuntime`); a `command` payload ignores it.

## Operational notes

- `doctor --lint --all` takes 4-5 minutes. Run it as a **detached systemd
  transient unit** (`systemd-run --user --unit=<name> --collect`) so a Gateway
  restart does not kill the run and lose its output.
- `openclaw plugins registry --refresh` and `openclaw models auth` /
  `secrets apply` are **offline-only** and refuse to run while the Gateway
  holds state ownership. Stop the unit first, run the command, start it again.
- `openclaw backup create` can fail on a huge workspace file (a 1.3 GB
  `workspace/memory/.dreams/session-corpus/*.txt` entry aborted the
  traversal). Use `--no-include-workspace`, or copy the SQLite files directly
  as a rollback point.
