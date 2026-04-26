# VAX Cluster Rebuild Checklist

## Objective

Recreate:
- **FUSION** as primary node, DECnet node, boot server, MSCP disk server
- **RISE** as satellite booting from `FUSION$DUA0:[SYS10.]`
- **RISE local disk** for page/swap

## Known good target state

### FUSION
- OpenVMS VAX V7.3
- DECnet: `FUSION` / `12.106`
- TCP/IP: `192.168.1.137`
- System disk: `FUSION$DUA0:` label `OVMSVAXSYS`
- Shared disks:
  - `FUSION$DUA1:` label `SYSVAX2`
  - `FUSION$DUA2:` label `DATA1`

### RISE
- OpenVMS VAX V7.3
- `SYS$SYSDEVICE = FUSION$DUA0:`
- `SYS$SPECIFIC = FUSION$DUA0:[SYS10.]`
- Page/swap on local disk `RISE$DUA0:` label `RISE_12395`

## Files captured from the current system

- `/home/keith/.openclaw/workspace/fusion_capture_2026-04-15.txt`
- `/home/keith/.openclaw/workspace/rise_capture_via_fusion_2026-04-15.txt`
- `/home/keith/.openclaw/workspace/FUSION_LIC1.COM`

## Host-side prep

- [ ] Keep current backups/snapshot intact
- [ ] Clone existing SIMH directories before changes
- [ ] Keep original `vax.ini` files unchanged until the new build works

## SIMH config targets

### FUSION
- [ ] `rq0` = system disk
- [ ] `rq1` = optional shared/system work disk
- [ ] `rq2` = optional shared data disk
- [ ] `rq3` = CD-ROM
- [ ] `xq` attached to bridged LAN
- [ ] MAC retained/stable

### RISE
- [ ] `rq0` = local page/swap disk
- [ ] `xq` attached to bridged LAN
- [ ] MAC retained/stable
- [ ] no dependence on a local system root

## Build sequence

### 1. Rebuild FUSION standalone
- [ ] Install OpenVMS VAX V7.3 on FUSION
- [ ] Confirm standalone boot works
- [ ] Set node name to `FUSION`
- [ ] Configure DECnet address `12.106`
- [ ] Configure TCP/IP `192.168.1.137`
- [ ] Apply licences using `FUSION_LIC1.COM`

Validation:
```text
SHOW NETWORK
MC NCP SHOW EXECUTOR
SHOW DEVICE
```

### 2. Enable cluster/MSCP on FUSION
- [ ] Run `@SYS$MANAGER:CLUSTER_CONFIG.COM`
- [ ] Enable VAXcluster mode
- [ ] Enable MSCP serving
- [ ] Ensure system disk is served clusterwide

Validation:
```text
MC SYSGEN SHOW VAXCLUSTER
MC SYSGEN SHOW MSCP_LOAD
MC SYSGEN SHOW MSCP_SERVE_ALL
SHOW DEVICE/FULL
```

Expected on FUSION:
- [ ] `FUSION$DUA0:` served via MSCP

### 3. Create RISE satellite root on FUSION
- [ ] Add satellite node `RISE`
- [ ] Create root `[SYS10.]` on `FUSION$DUA0:`
- [ ] Update startup and boot-server config

Target result:
```text
RISE -> SYS$SYSDEVICE = FUSION$DUA0:
RISE -> SYS$SPECIFIC  = FUSION$DUA0:[SYS10.]
```

### 4. Prepare RISE local disk
- [ ] Initialise/mount `RISE$DUA0:`
- [ ] Label disk `RISE_12395` or chosen replacement label
- [ ] Create local `PAGEFILE.SYS`
- [ ] Create local `SWAPFILE.SYS`
- [ ] Configure RISE to use local page/swap files

Validation on RISE:
```text
SHOW MEMORY/FILES
```

Expected:
- [ ] Page/swap files shown on local `DISK$RISE_xxxxx:`

### 5. Boot RISE as satellite
- [ ] Boot RISE over Ethernet from FUSION
- [ ] Log in on RISE
- [ ] Confirm cluster membership

Validation on RISE:
```text
SHOW CLUSTER
SHOW LOGICAL SYS$SYSDEVICE
SHOW LOGICAL SYS$SPECIFIC
SHOW MEMORY/FILES
SHOW DEVICE/FULL
```

Expected:
- [ ] `SYS$SYSDEVICE = FUSION$DUA0:`
- [ ] `SYS$SPECIFIC = FUSION$DUA0:[SYS10.]`
- [ ] page/swap on local `RISE$DUA0:`

### 6. Recreate shared data disks
- [ ] Attach shared disks to FUSION only
- [ ] Mount them on FUSION
- [ ] Serve them via MSCP
- [ ] Verify access from RISE

Suggested mapping:
- [ ] `FUSION$DUA1:` = `SYSVAX2`
- [ ] `FUSION$DUA2:` = `DATA1`

## Final validation

### On FUSION
```text
SHOW CLUSTER
SHOW DEVICE/FULL
SHOW NETWORK
MC NCP SHOW EXECUTOR CHARACTERISTICS
```

- [ ] FUSION and RISE both show as `MEMBER`
- [ ] FUSION system disk served via MSCP

### On RISE
```text
SHOW CLUSTER
SHOW LOGICAL SYS$SYSDEVICE
SHOW LOGICAL SYS$SPECIFIC
SHOW MEMORY/FILES
```

- [ ] RISE root is `[SYS10.]` on FUSION system disk
- [ ] RISE page/swap is on local disk

## Do not do during the first rebuild

- [ ] Do not dual-attach the same writable SIMH disk image to both nodes
- [ ] Do not change quorum/votes early unless necessary
- [ ] Do not introduce shadowing until the base cluster works

## Optional later work

- [ ] Add served shared data volumes
- [ ] Add shadow sets on FUSION
- [ ] Review quorum/vote settings once stable
