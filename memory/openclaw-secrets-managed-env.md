---
summary: "Why OpenClaw's openrouter:default auth profile stayed degraded despite the key being present in the Gateway's process env, and the verified end-state of the fix on Hebei."
tags: [openclaw, secrets, secretref, systemd, env, troubleshooting]
---

# OpenClaw degraded secret: managed env keys need a runtime source

**Symptom (Hebei, 2026-11-19):** `openclaw status` reported
`Degraded secrets: 1 degraded · cold account:[".../openclaw-agent.sqlite","openrouter:default"]: secret reference was not found`,
and `openclaw secrets audit` showed
`REF_UNRESOLVED profiles.openrouter:default.key → env:default:OPENROUTER_API_KEY (Environment variable "OPENROUTER_API_KEY" is missing or empty)`.

**The trap:** the key *was* in the Gateway's environment. `/proc/<gateway-pid>/environ`
showed `OPENROUTER_API_KEY=sk-or-v1-…`, because the systemd unit loads
`EnvironmentFile=/home/keith/.openclaw/gateway.systemd.env`. Verifying the process env
therefore looks like a false positive.

**Actual root cause:** `OPENROUTER_API_KEY` was listed in the service's
`OPENCLAW_SERVICE_MANAGED_ENV_KEYS`. Managed keys are values OpenClaw expects to
regenerate from a runtime source it owns — config `env.vars`, `~/.openclaw/.env`, or a
SecretRef — **not** from the supervisor's `EnvironmentFile`. During bootstrap,
`clearMissingManagedServiceEnvKeys` (dist/pre-bootstrap-*.mjs) deletes managed keys from
`process.env` when they are absent from the dotenv/config sources. So the value present
in the supervisor env was stripped before SecretRef resolution ran, and
`env:default:OPENROUTER_API_KEY` resolved against an empty environment.

Docs confirm the rule: "Doctor detects managed `.env`/SecretRef-backed service environment
values that older installs embedded inline and rewrites the service metadata so those
values load from the runtime source instead of the supervisor definition."

## Verified end-state (Hebei, 2026-11-19)

Final state after the full migration:

- **Protected store** — `openclaw secrets store set OPENROUTER_API_KEY --kind secret
  --allow-host api.openrouter.ai` → write-only team store entry.
- **Agent store** (`agents/main/agent/openclaw-agent.sqlite`) — both
  `openrouter:default` and `openrouter:manual` are
  `ref(store:teamstore:OPENROUTER_API_KEY)`. No plaintext credential rows.
- **Shared native store** (`state/openclaw.sqlite`) — the stale
  `openrouter:default` env-ref row was removed; it still holds only the
  OpenAI OAuth profile.
- **Runtime `.env`** (`~/.openclaw/.env`, mode 0600) — retains only
  `OPENCLAW_PERPLEXITY_KEY`, which the perplexity plugin's
  `webSearch.apiKey` still refs as `env:default:OPENCLAW_PERPLEXITY_KEY`.

Final verification: `openclaw secrets audit` → `plaintextCount: 0,
unresolvedRefCount: 0`; `openclaw health --json` → `ok: true`,
`degradedSecretOwners: null`; `openclaw doctor --lint --json` → `ok: true`,
43 checks, **zero findings**. The only remaining audit entries are
`LEGACY_RESIDUE` (archived June `.bak` auth sources and the OpenAI OAuth
profile) — out of scope for static SecretRef migration.

**Pre-existing quirk on this host:** `OPENCLAW_PERPLEXITY_KEY` and
`OPENROUTER_API_KEY` carry the *identical* value (`sk-or-v1-…`). The
perplexity key therefore remains the one plaintext copy of that value, and it
is still required by the perplexity plugin's env ref.

**Note on residual plaintext bytes:** grepping the raw SQLite files still
matches the key string. Those hits are the protected store entry itself
(store values are stored unencrypted by design, DB file mode 0600) and
session-transcript text from the debugging session — not credential rows.
The live `auth_profile_store` rows contain only SecretRefs.

## Operational constraints learned

- `openclaw secrets apply` writing auth-profile targets requires **exclusive offline
  state ownership**. With the Gateway running it fails with "OpenClaw state database is
  busy at …/state/openclaw.sqlite" and refuses to run online. Sequence:
  stop the gateway systemd unit → apply → start it again → `openclaw secrets reload`.
- Apply **preflight validates every active ref**, not just the plan's targets. If another
  ref (e.g. perplexity `webSearch.apiKey`) cannot resolve, the whole apply aborts with
  `WEB_SEARCH_KEY_UNRESOLVED_NO_FALLBACK`. Export the managed env keys into the
  applying shell before running it — source `~/.openclaw/.env` at the top of the script.
- `openclaw models auth logout <id>` removes a profile from **every owner store**, and
  removes the `auth.profiles.<id>` entry from `openclaw.json`. Re-add that mapping
  afterwards with `openclaw config patch --stdin` if the profile is still needed.
- A **shared-store** row cannot be repointed at a `store` SecretRef by `secrets apply`;
  plans resolve auth-profile targets against the *agent* store only. To clear a stale
  shared-store row, log the profile out (which removes it from all owner stores) and
  re-create it in the agent store via the plan. Sequence matters: log out first, then
  apply, then restore the `auth.profiles` config entry.
- A script that stops the Gateway **must not run as a Gateway child** — it is killed
  mid-run. Run it as a detached systemd transient unit
  (`systemd-run --user --unit=<name> --collect /bin/bash <script>`). systemd user units
  get a minimal PATH and no supervisor env, so export PATH and the managed env keys
  explicitly inside the script.
- `openclaw backup create` can fail on a huge workspace file (a 1.3 GB
  `workspace/memory/.dreams/session-corpus/*.txt` entry aborted the traversal). Use
  `--no-include-workspace` or copy the SQLite files directly as a rollback point.
- `openclaw doctor --lint` takes 3-5 minutes; run it in isolation. Concurrent CLI reads
  produce spurious "Shared-state read scope is closing or closed" and "auth profile store
  unreadable" errors that vanish on an isolated re-run.
