# Standardised Monitoring Report Format

**This template is mandatory.** Every daily monitoring report (Linux and AIX) must follow this exact layout. Do not deviate, improvise, or "improve" — produce this structure verbatim, populating it with the data from the script output.

---

## Linux System Monitor Report

```
📊 **System Monitoring Snapshot** — <YYYY-MM-DD HH:MM> <TZ>

### Hosts: <N> total | 🟢 OK: <n> | ⚠️ WARNING: <n> | 🔴 CRITICAL: <n> | ⬛ UNREACHABLE: <n>

### 🔴 CRITICAL Alerts
| Host | Issue |
|------|-------|
| **<host>** | <concise issue summary> |

### ⚠️ Warnings
| Host | Issue |
|------|-------|
| **<host>** | <concise issue summary> |

### ⬛ Unreachable
| Host | Error |
|------|-------|
| **<host>** | <error message> |

### 🟢 Nominal
<comma-separated list of OK hosts> — all clear

### Action Items
1. **<category>** — <specific hosts and what needs doing>
2. **<category>** — <specific hosts and what needs doing>
...
```

### Rules for Linux Report

1. **Header line**: Always `📊 **System Monitoring Snapshot** — <date/time> <tz>`
2. **Summary line**: Always `Hosts: <N> total | 🟢 OK: <n> | ⚠️ WARNING: <n> | 🔴 CRITICAL: <n> | ⬛ UNREACHABLE: <n>`
3. **Sections order**: CRITICAL → Warnings → Unreachable → Nominal → Action Items
4. **Tables**: Use Markdown tables with `| Host | Issue |` columns (or `| Host | Error |` for Unreachable)
5. **Issue text**: Concise, human-readable. Combine multiple issues per host into one cell, separated by ` + `. Example: `1 security pkg + high swap (2.9GiB)`
6. **Nominal section**: Single line, comma-separated host names in lowercase, followed by `— all clear`
7. **Action Items**: Numbered list, each starting with a **bold category**, then specific hosts and action
8. **If a section has no entries**: Omit the section entirely (e.g., no CRITICAL section if nothing is critical)
9. **Do NOT include**: Raw script output, per-host detailed breakdowns, snapshot file paths, or internal diagnostics
10. **Do NOT include**: Section dividers (`---`) between sections

---

## AIX System Monitor Report

```
**AIX Midday Monitor — <Day> <DD> <Mon> <YYYY> <HH:MM> <TZ>**

<One of the following two formats:>

**IF ALL HOSTS REACHABLE:**
| Host | Status | Load | Memory | Disk | Notes |
|------|--------|------|--------|------|-------|
| <host> | ✅ OK / ⚠️ WARN / 🔴 CRIT | <load> | <mem%> | <disk> | <notes> |

**Summary:** <N> hosts | <n> OK | <n> WARN | <n> CRIT

**IF ALL HOSTS UNREACHABLE:**
All <N> AIX hosts returned **<error type>** — <likely cause>:

| Host | Status |
|------|--------|
| **<host>** | ❌ <error> |

<single sentence likely cause explanation>

**IF MIXED (some reachable, some not):**
Use the full table format above, with ❌ for unreachable hosts in the Status column.
```

### Rules for AIX Report

1. **Header**: Always `**AIX Midday Monitor — <Day> <DD> <Mon> <YYYY> <HH:MM> <TZ>**`
2. **All unreachable**: Use the simplified two-column table format with a single-sentence cause
3. **All reachable**: Use the full six-column table with Load, Memory, Disk, Notes
4. **Mixed**: Full table, unreachable hosts get ❌ in Status
5. **Summary line**: Always present after table(s), format: `**Summary:** <N> hosts | <n> OK | <n> WARN | <n> CRIT`
6. **Do NOT include**: Raw script output, SCP/SSH diagnostics, snapshot paths, or "[AIX] Collecting..." lines
7. **Do NOT include**: Section dividers (`---`)

---

## General Rules (Both Reports)

1. **Never** include raw script stdout/stderr, debug lines, or internal diagnostics
2. **Never** include snapshot file paths or collection metadata
3. **Always** use the exact emoji indicators: 🟢 ⚠️ 🔴 ⬛ ❌ ✅
4. **Always** use **bold** for host names in table rows
5. **Always** use Markdown tables (Telegram rich text supports them)
6. **Keep** issue descriptions concise — one line per host
7. **Combine** multiple issues for the same host with ` + ` separator
8. **Sort** hosts within each section: CRITICAL first (by severity), then WARNING, then UNREACHABLE, then OK
9. **Action Items** (Linux only): Numbered, prioritised by severity, each with a bold category label