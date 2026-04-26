# VAX/VMS Cluster Rebuild Runbook

## Goal

Rebuild the existing 2-node OpenVMS VAXcluster on SIMH with the same functional model:

- **FUSION** = primary node, boot server, DECnet node, MSCP disk server
- **RISE** = secondary node, satellite booting from **FUSION** over DECnet/MOP
- **RISE local disk** retained for **PAGEFILE/SWAPFILE**
- Optional shared data disks served from **FUSION**
- Optional shadowing later, after the base cluster is stable

## What the current working system looks like

### Confirmed current behaviour

#### FUSION
- OpenVMS VAX **V7.3**
- DECnet node/address: **FUSION / 12.106**
- TCP/IP address: **192.168.1.137**
- Cluster member with **RISE**
- System disk: **FUSION$DUA0:** volume **OVMSVAXSYS**
- Additional mounted disks:
  - **FUSION$DUA1:** volume **SYSVAX2**
  - **FUSION$DUA2:** volume **DATA1**
  - **FUSION$DUA3:** CD-ROM volume **VAXVMS073**
- `FUSION$DUA0:` is **served to cluster via MSCP Server**

#### RISE
- OpenVMS VAX **V7.3**
- Cluster member with **FUSION**
- Boot/root configuration:
  - `SYS$SYSDEVICE = FUSION$DUA0:`
  - `SYS$SPECIFIC = FUSION$DUA0:[SYS10.]`
- Therefore **RISE is booting from FUSION's served system disk**
- Local disk:
  - **RISE$DUA0:** volume **RISE_12395**
- Active paging files on RISE:
  - `DISK$RISE_12395:[SYSEXE]PAGEFILE.SYS;1`
  - `DISK$RISE_12395:[SYSEXE]SWAPFILE.SYS;1`

### Captured reference files
- `/home/keith/.openclaw/workspace/fusion_capture_2026-04-15.txt`
- `/home/keith/.openclaw/workspace/rise_capture_via_fusion_2026-04-15.txt`
- `/home/keith/.openclaw/workspace/FUSION_LIC1.COM`

## SIMH intent

### FUSION SIMH role
- Local bootable system disk on `rq0`
- Optional extra disks on `rq1`, `rq2`
- CD-ROM on `rq3`
- Ethernet on `xq`
- Stable MAC address

### RISE SIMH role
- Ethernet on `xq`
- Local disk on `rq0` for page/swap
- No requirement for local system root
- Stable MAC address

## Recommended rebuild order

1. Preserve copies of current SIMH configs and disk images
2. Build **FUSION** first as a healthy standalone VMS node
3. Apply licences
4. Configure DECnet on FUSION
5. Enable cluster/MSCP serving on FUSION
6. Create RISE satellite root on FUSION system disk
7. Configure FUSION as satellite boot server for RISE
8. Build/attach RISE local disk for page/swap
9. Boot RISE over network from FUSION
10. Move RISE page/swap to local disk
11. Validate cluster membership and storage layout
12. Add optional served shared data disks
13. Add optional shadowing only after the base cluster is proven

## Phase 1: Prepare host-side assets

On the SIMH host:

- Keep the backup/snapshot you already made
- Duplicate the existing directories before experimenting
- Keep original `vax.ini` files unchanged until the replacement boot path is proven

Suggested host-side layout:

- `~/FUSION/new/`
- `~/RISE/new/`

## Phase 2: Define target SIMH configs

### FUSION target pattern

Use a config equivalent to:

```ini
attach nvr ./data/nvram.bin
set cpu 64m
set cpu idle

set rq0 ra92
set rq1 ra92
set rq2 ra92
set rq3 cdrom

attach rq0 ./data/d0.dsk       ; system disk
attach rq1 ./data/d1.dsk       ; optional shared/system work disk
attach rq2 ./data/d2.dsk       ; optional shared data disk
attach -r rq3 ./data/os.iso

set rl disable
set ts disable

set xq mac=08-00-2B-AA-BB-02
attach xq tap:tap0

boot cpu
```

### RISE target pattern

Use a config equivalent to:

```ini
attach nvr ./data/nvram.bin
set cpu 64m
set cpu idle

set rq0 ra92                   ; local page/swap disk
set rq3 cdrom

attach rq0 ./data/d0.dsk

set rl disable
set ts disable

set xq mac=08-00-2B-AA-BB-03
attach xq tap:tap1

boot cpu
```

### Notes
- `tap0` and `tap1` are acceptable because you confirmed they are on the same bridge
- Do **not** dual-attach the same writable disk image to both VAX instances
- Shared cluster-visible storage should be **served from FUSION via MSCP**, not shared at the host file level

## Phase 3: Rebuild FUSION as standalone first

Boot the installer and build FUSION as a normal standalone VMS V7.3 system.

### Target node identity
- Node name: `FUSION`
- DECnet address: `12.106`
- TCP/IP address: `192.168.1.137`

### After base install
Confirm:

```text
SHOW SYSTEM
SHOW DEVICE
SHOW NETWORK
MC NCP SHOW EXECUTOR
```

Apply licences from the retrieved licence command file:

```text
@SYS$SYSROOT:[SYSMGR]LIC1.COM
```

If you place the saved copy back onto the rebuilt machine, keep it in `SYS$SYSROOT:[SYSMGR]` or similar admin storage.

## Phase 4: Configure DECnet on FUSION

Ensure DECnet Phase IV matches the current node identity.

Target:

- Node: `FUSION`
- Address: `12.106`

Validate with:

```text
SHOW NETWORK
MC NCP SHOW EXECUTOR CHARACTERISTICS
```

## Phase 5: Enable cluster and MSCP serving on FUSION

Target behaviour on FUSION:

- member of VAXcluster
- serves system disk to satellites
- serves additional disks clusterwide

Current captured values were:

```text
VAXCLUSTER     = 2
MSCP_LOAD      = 1
MSCP_SERVE_ALL = 2
```

Use the cluster configuration procedure rather than hand-editing parameters where possible:

```text
@SYS$MANAGER:CLUSTER_CONFIG.COM
```

Then verify:

```text
MC SYSGEN SHOW VAXCLUSTER
MC SYSGEN SHOW MSCP_LOAD
MC SYSGEN SHOW MSCP_SERVE_ALL
SHOW DEVICE/FULL
```

## Phase 6: Prepare the served system disk layout for RISE

The working cluster uses:

- FUSION root on `FUSION$DUA0:[SYS0.]`
- RISE root on `FUSION$DUA0:[SYS10.]`

That is the model to reproduce.

Use `CLUSTER_CONFIG.COM` on **FUSION** to:

- add a satellite node named `RISE`
- create the satellite root `[SYS10.]` on `FUSION$DUA0:`
- update cluster startup files
- update MOP/satellite boot information

After this, the target on RISE should eventually be:

```text
SYS$SYSDEVICE = FUSION$DUA0:
SYS$SPECIFIC  = FUSION$DUA0:[SYS10.]
```

## Phase 7: Configure FUSION as boot server for RISE

FUSION must provide the network boot path for RISE.

Requirements:

- DECnet/MOP functioning on the shared Ethernet
- RISE node defined correctly
- RISE hardware address associated with the satellite boot definition
- boot server aware of the served system disk/root

Use the cluster/satellite configuration procedure first. If manual DECnet tuning is required, verify with:

```text
MC NCP SHOW KNOWN NODES
MC NCP SHOW EXECUTOR CHARACTERISTICS
```

Key point: the working environment already proves that **SET HOST RISE** and satellite booting are viable on this LAN, so preserve that model rather than redesigning it.

## Phase 8: Build RISE local disk for paging and swap

RISE should keep a local disk specifically for page/swap.

Current working model:

- local disk: `RISE$DUA0:`
- volume label: `RISE_12395`
- page/swap live on that local disk, not on the served root

### Target result on RISE

```text
SHOW MEMORY/FILES
```

should report something like:

```text
DISK$RISE_xxxxx:[SYSEXE]PAGEFILE.SYS
DISK$RISE_xxxxx:[SYSEXE]SWAPFILE.SYS
```

### Likely procedure on RISE

1. Initialise and mount the local disk
2. Create page and swap files there
3. Point the system to use them
4. Reboot and verify with `SHOW MEMORY/FILES`

Useful files and procedures to inspect:

```text
SYS$MANAGER:SYPAGSWPFILES.COM
SHOW MEMORY/FILES
SHOW DEVICE/FULL
```

## Phase 9: Boot RISE as a satellite

On the rebuilt RISE instance:

- boot with Ethernet available
- use the cluster/satellite boot path from FUSION
- confirm login on RISE

The decisive checks on RISE are:

```text
SHOW LOGICAL SYS$SYSDEVICE
SHOW LOGICAL SYS$SPECIFIC
SHOW MEMORY/FILES
SHOW CLUSTER
SHOW DEVICE/FULL
```

Success criteria:

```text
SYS$SYSDEVICE = FUSION$DUA0:
SYS$SPECIFIC  = FUSION$DUA0:[SYS10.]
```

and page/swap on local `RISE$DUA0:`.

## Phase 10: Recreate shared disks

Current FUSION disk set suggests this pattern:

- `FUSION$DUA1:` = secondary/system work disk (`SYSVAX2`)
- `FUSION$DUA2:` = shared data disk (`DATA1`)

Recommended approach:

- attach shared disks to **FUSION only**
- mount them on FUSION
- serve them clusterwide via MSCP
- access them from RISE as cluster-served devices

Do not try to emulate “shared storage” by attaching one host file to both VAXes at once.

## Phase 11: Validation checklist

### On FUSION

```text
SHOW CLUSTER
SHOW DEVICE/FULL
SHOW NETWORK
MC NCP SHOW EXECUTOR CHARACTERISTICS
MC SYSGEN SHOW VAXCLUSTER
MC SYSGEN SHOW MSCP_LOAD
MC SYSGEN SHOW MSCP_SERVE_ALL
```

Expected:
- FUSION and RISE both present as `MEMBER`
- `FUSION$DUA0:` served via MSCP
- additional shared disks mounted and visible as intended

### On RISE

```text
SHOW CLUSTER
SHOW LOGICAL SYS$SYSDEVICE
SHOW LOGICAL SYS$SPECIFIC
SHOW MEMORY/FILES
SHOW DEVICE/FULL
```

Expected:
- `SYS$SYSDEVICE = FUSION$DUA0:`
- `SYS$SPECIFIC = FUSION$DUA0:[SYS10.]`
- page/swap on `DISK$RISE_xxxxx:` local disk

## Phase 12: Quorum and votes

Captured current values on FUSION were:

```text
EXPECTED_VOTES = 1
VOTES          = 1
```

That is unusual for a 2-node cluster, though it may be deliberate in this lab.

Recommendation:
- preserve the current behaviour for the first rebuild
- revisit votes/quorum only after the replacement cluster is stable

Do **not** try to optimise quorum early. Reproduce first, improve second.

## Phase 13: Optional shadowing later

If you want a more complete clustered storage model later:

- use extra disks on **FUSION**
- build shadow sets there
- serve the resulting virtual unit to the cluster

That is the safe path.

Avoid these until the base rebuild is complete:
- dual-mounting one SIMH disk image read/write on both nodes
- changing both satellite boot and storage architecture at the same time
- mixing shadowing work into the initial rebuild

## Minimal success definition

The rebuild is successful when all of the following are true:

1. FUSION boots standalone and is licensed
2. FUSION has DECnet `12.106`
3. FUSION serves `FUSION$DUA0:` via MSCP
4. RISE boots from FUSION over DECnet/MOP
5. RISE shows:
   - `SYS$SYSDEVICE = FUSION$DUA0:`
   - `SYS$SPECIFIC = FUSION$DUA0:[SYS10.]`
6. RISE uses local `RISE$DUA0:` for page/swap
7. Both nodes appear as cluster members
8. Shared data disks can be served from FUSION and accessed from RISE

## Suggested working method

Use this order exactly:

1. FUSION standalone install
2. licence application
3. DECnet on FUSION
4. cluster enablement on FUSION
5. create RISE satellite root on FUSION
6. configure RISE local page/swap disk
7. boot RISE as satellite
8. validate cluster
9. add shared data disks
10. add shadowing only if still desired

## Practical warning

The current cluster is already architecturally sensible.

The replacement should preserve these three design choices:

- **served system disk on FUSION**
- **satellite root for RISE on FUSION**
- **local page/swap disk on RISE**

Those are the parts worth keeping.
