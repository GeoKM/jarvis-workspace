---
summary: "How the OpenClaw update-recovery cleanup and the dead-lettered outbound delivery receipts on Hebei were retired, with the exact commands and the constraints each path imposes."
tags: [openclaw, update-cleanup, delivery-queue, secrets, disk, maintenance]
---

# Retiring update recovery copies and dead-lettered delivery receipts

## Update recovery cleanup (item 4)

**Scope confirmed by dry run:** 6 candidates / 509 MB, versus 2130 protected
entries / 1.2 GB. The candidates were:

- 4 × `*.pre-startup-migration-*.bak` (agent + state SQLite originals, 220 MB
  largest) — producer-verified originals from the 2026-11-18 migration
- 1 × 2-byte `legacy-store.sessions.json.imported-*` stub
- 1 × unsealed update capture `~/.openclaw.update-captures/0d3a0974-…` (254 MB)

**Procedure:**

```bash
openclaw update cleanup --dry-run          # inspect candidates vs protected
openclaw backup create --no-include-workspace   # safety net FIRST
openclaw update cleanup --yes               # needs the Gateway STOPPED
```

`update cleanup --yes` refuses to run against a live Gateway
("Stop the Gateway first (openclaw gateway stop), then retry") — it mutates
recovery metadata and needs exclusive state ownership.

**Result:** candidates 0 bytes; the unsealed capture and the 4 migration
originals were retired. The three `doctor-*` retained-doctor-captures
(800 MB) remain **protected** — they are deliberate pre-repair evidence, and
`update cleanup` will not remove them without `--include-unmanifested`.

Two items report **blocked** (2 bytes each, "destination database ownership
cannot be verified") — negligible and not worth chasing.

## Dead-lettered outbound deliveries

**Symptom:** `openclaw status --deep` showed
`Delivery queue │ WARN │ dead-lettered entries — outbound: 13; oldest 94d ago`,
and `health --json` reported `deliveryQueues.failed: [{queueName:"outbound",
count:13}]`.

**What they actually are** (table `delivery_queue_entries` in
`state/openclaw.sqlite`): all 13 had `status='failed'` **and**
`recovery_state='completed_permanent'` with a NULL `retention_id_prefix`.
They were payload-stripped terminal receipts — no `channel`, `target`,
`session_key`, `entry_kind`, or `last_error` — dated 2026-08-17 (1 row) and
2026-08-27 (12 rows within 8 seconds). **Not** pending messages: pending
count was 0.

**Why no shipped sweep clears them:** the tombstone sweep
(`pruneDeliveryQueueTombstoneAges`) deletes only
`status IN ('completed','failed') AND recovery_state='completed_bounded'` with
a namespace past its own retention window, or `status='completed'` rows
older than 30 days whose recovery_state is neither permanent nor bounded.
A `failed` + `completed_permanent` row matches neither branch, so it is
never pruned.

**Decisive evidence that the product treats these as disposable:** OpenClaw's
own global backup *"remove[s] every delivery queue row before compaction,
including pending work, failed ownership fences, and completion receipts or
records used to prevent duplicate sends"* — the sanitised backup archive
contained **0** `delivery_queue_entries` rows.

**Removal (direct, offline, targeted):**

```bash
systemctl --user stop openclaw-gateway.service
sqlite3 ~/.openclaw/state/openclaw.sqlite \
  "DELETE FROM delivery_queue_entries
    WHERE status='failed' AND recovery_state='completed_permanent'
      AND retention_id_prefix IS NULL AND id IN (...13 exact ids...);"
systemctl --user start openclaw-gateway.service
```

Result: `deliveryQueues: null`, the Delivery queue WARN line gone, DB
`integrity_check` ok, `cron_jobs` and `cron_run_receipts` untouched.

**Operational gotchas hit on the way:**

- `sqlite3` on this host is at `/home/linuxbrew/.linuxbrew/bin/sqlite3` — a
  systemd transient unit's default PATH will NOT find it. Export PATH
  explicitly or use the absolute path.
- A systemd transient unit does inherit the calling shell's PATH only via
  `systemd-run --setenv=PATH=...` or an export inside the script.
- `openclaw --help` lists no delivery-queue maintenance command; there is no
  supported CLI surface for this table beyond the automatic sweeps.
- The external-sqlite guard refuses to open databases under the active
  OpenClaw state directory: copy to `/tmp` and inspect the copy, or run the
  write with the Gateway stopped.

## Retained artefacts

- `/home/keith/2026-11-19T22-54-39.414+11-00-openclaw-backup.tar.gz` (468 MB) —
  verified backup taken before the irreversible cleanup; `integrity_check` ok on
  the restored state DB, and it contains the live config (including the
  `teamstore` secret provider) and all agent DBs.
- `~/.openclaw.update-captures` still holds 764 MB of protected doctor
  captures.
