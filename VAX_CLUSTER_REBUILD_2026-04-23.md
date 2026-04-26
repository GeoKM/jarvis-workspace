# OpenVMS VAXcluster Rebuild — 23 April 2026

## What was built

A 2-node OpenVMS VAXcluster in SIMH, rebuilt from a base install:

| Node | Role |
|------|------|
| **FUSION** | Primary node, DECnet `12.106`, TCP/IP `192.168.1.137`, boot server, MSCP disk server |
| **RISE** | Satellite, booting root from FUSION, page/swap on local disk |

## Disk layout on FUSION

| Device | Volume | Role |
|--------|--------|------|
| `FUSION$DUA0:` | `OVMSVAXSYS` | System disk (served to cluster via MSCP) |
| `FUSION$DUA1:` | `SYSVAX2` | Cluster/common services disk |
| `FUSION$DUA2:` | `DATA1` | User/data disk |
| `FUSION$DUA3:` | `VAXVMS073` | OpenVMS V7.3 CD-ROM |

RISE local disk:
| Device | Volume | Role |
|--------|--------|------|
| `RISE$DUA0:` | `RISE_12395` | Local page/swap |

---

## Phase 1 — Extra disks on FUSION

Before enabling clustering, set up the two extra disks:

```text
INITIALIZE FUSION$DUA1: SYSVAX2
INITIALIZE FUSION$DUA2: DATA1

MOUNT/SYSTEM FUSION$DUA1:
MOUNT/SYSTEM FUSION$DUA2:

CREATE/DIRECTORY SYSVAX2:[VMSCOMMON]
CREATE/DIRECTORY SYSVAX2:[TOOLS]
CREATE/DIRECTORY SYSVAX2:[BATCH]
CREATE/DIRECTORY SYSVAX2:[PRINT]
CREATE/DIRECTORY SYSVAX2:[CLUSTER]

CREATE/DIRECTORY DATA1:[USERS]
CREATE/DIRECTORY DATA1:[PROJECTS]
CREATE/DIRECTORY DATA1:[PUBLIC]
CREATE/DIRECTORY DATA1:[BACKUPS]
```

Optional logical names (add to `SYS$MANAGER:SYLOGICALS.COM`):

```text
DEFINE/SYSTEM/EXEC SYSVAX2  SYSVAX2:[000000]
DEFINE/SYSTEM/EXEC DATA1    DATA1:[000000]
DEFINE/SYSTEM/EXEC USERDISK DATA1:[USERS]
```

---

## Phase 2 — Enable VAXcluster on FUSION

Run the cluster configuration procedure:

```text
@SYS$MANAGER:CLUSTER_CONFIG.COM
```

Answers given:

| Prompt | Answer |
|--------|--------|
| Use LANACP rather than DECnet for boot serving? | `YES` |
| Main menu choice | `1` (Add a voting member) |
| LAN used for cluster communications? | `Y` |
| Cluster group number | `123` |
| FUSION will be a boot server? | `Y` |
| ALLOCLASS | `0` |
| Quorum disk? | `N` |
| Run AUTOGEN now? | `Y` |

After AUTOGEN completes and FUSION reboots, verify:

```text
MC SYSGEN SHOW VAXCLUSTER
MC SYSGEN SHOW MSCP_LOAD
MC SYSGEN SHOW MSCP_SERVE_ALL
SHOW CLUSTER
SHOW DEVICE/FULL FUSION$DUA0
```

Expected results:
- `VAXCLUSTER = 2`
- `MSCP_LOAD = 1`
- `FUSION` shows as `MEMBER` in `SHOW CLUSTER`
- `FUSION$DUA0:` shows `served to cluster via MSCP Server`

---

## Phase 3 — Fix LANACP / MOP boot serving

If `CLUSTER_CONFIG.COM` warns that no LAN adapters are configured for downline loading:

```text
MCR LANCP SET DEVICE XQA0/MOPDLL=ENABLE
MCR LANCP DEFINE DEVICE XQA0/MOPDLL=ENABLE
MCR LANCP SHOW DEVICE XQA0

@SYS$STARTUP:LAN$STARTUP
```

Then re-run `@SYS$MANAGER:CLUSTER_CONFIG.COM` and go back to the Add Node path.

---

## Phase 4 — Add RISE as a satellite

From the main menu of `CLUSTER_CONFIG.COM`:

```text
@SYS$MANAGER:CLUSTER_CONFIG.COM
```

Then choose `1` (Add a VAX node to the cluster).

Answers given:

| Prompt | Answer |
|--------|--------|
| Continue? | `Y` |
| Satellite? | `Y` |
| SCS node name | `RISE` |
| SCSSYSTEMID | `12395` |
| DECnet? | `Y` |
| LAN adapter hardware address | `08-00-2B-AA-BB-03` |
| System root device | `[default DISK$OVMSVAXSYS:]` — press Return |
| System root name | `[SYS10]` — press Return |
| Conversational bootstrap? | `N` |
| Workstation software? | `1` (None) |
| Disk server? | `N` |
| Pagefile size | `[Return for AUTOGEN sizing]` |
| Temporary pagefile size | `10000` |
| Swap file size | `[Return for AUTOGEN sizing]` |
| Temporary swap file size | `8000` |
| Local disk for paging/swap? | `Y` |
| RFxx disks? | `N` |

The procedure then waits for RISE to boot. Boot RISE from its console:

```text
>>> BOOT XQA0
```

When prompted for the local paging/swapping disk, choose:

```text
RISE$DUA0:
```

AUTOGEN runs and reboots RISE automatically. Wait for the completion message.

---

## Phase 5 — Verify the cluster

### On FUSION

```text
SHOW CLUSTER
SHOW DEVICE/FULL FUSION$DUA0
```

Expected:
- FUSION and RISE both show as `MEMBER`
- `FUSION$DUA0:` is `shareable, served to cluster via MSCP Server`
- Volume mounted on both nodes

### On RISE

```text
SHOW CLUSTER
SHOW LOGICAL SYS$SYSDEVICE
SHOW LOGICAL SYS$SPECIFIC
SHOW MEMORY/FILES
SHOW DEVICE/FULL RISE$DUA0
```

Expected:
- `SYS$SYSDEVICE = FUSION$DUA0:`
- `SYS$SPECIFIC = FUSION$DUA0:[SYS10.]`
- Pagefile and swapfile on `DISK$RISE_12395:[SYSEXE]`
- `RISE$DUA0:` mounted, label `RISE_12395`

---

## Phase 6 — Optional logical name persistence

Add to `SYS$MANAGER:SYLOGICALS.COM` on FUSION so disks mount on every boot:

```text
MOUNT/SYSTEM FUSION$DUA1:
MOUNT/SYSTEM FUSION$DUA2:
DEFINE/SYSTEM/EXEC SYSVAX2  SYSVAX2:[000000]
DEFINE/SYSTEM/EXEC DATA1    DATA1:[000000]
DEFINE/SYSTEM/EXEC USERDISK DATA1:[USERS]
```

---

## Cluster shutdown

To shut down the entire cluster cleanly, from FUSION:

```text
@SYS$SYSTEM:SHUTDOWN
```

Then select the option to shut down the whole cluster (not just the local node).

---

## SIMH notes

- FUSION `xq` MAC: `08-00-2B-AA-BB-02`
- RISE `xq` MAC: `08-00-2B-AA-BB-03`
- Both on same bridged TAP interface
- `set cpu noidle` required in SIMH config to avoid timer crash during install
- Do NOT dual-attach the same writable disk image to both VAX instances — use MSCP serving from FUSION instead

---

## Reference documents

- Full runbook: `VAX_CLUSTER_REBUILD_RUNBOOK.md`
- Step checklist: `VAX_CLUSTER_REBUILD_CHECKLIST.md`
- Pre-rebuild captures: `fusion_capture_2026-04-15.txt`, `rise_capture_via_fusion_2026-04-15.txt`
- Licence procedure: `FUSION_LIC1.COM`