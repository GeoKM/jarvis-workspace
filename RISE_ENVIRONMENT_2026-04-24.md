# RISE Environment Description — 2026-04-24

## Scope
Read-only live audit performed over Telnet on **24-APR-2026** after the cluster rebuild.

## System Identity
- Node name: **RISE**
- OpenVMS version: **OpenVMS VAX V7.3**
- Cluster role: **satellite / secondary cluster member**
- Cluster membership at audit time:
  - **RISE** — MEMBER
  - **FUSION** — MEMBER
- Cluster view source: `SHOW CLUSTER`
- System ID shown by `SHOW CLUSTER`: **12395**

## Network Identity
### DECnet
- Executor node: **12.107 (RISE)**
- DECnet type: **nonrouting Phase IV**
- Incoming proxy: **Enabled**
- Outgoing proxy: **Enabled**

### TCP/IP
- Product: **Compaq TCP/IP Services for OpenVMS VAX V5.1**
- Hostname: **RISE.can.barnabasmusic.com**
- IPv4 address: **192.168.1.138/24**
- Default route: **0.0.0.0 -> 192.168.1.1**
- Name service domain: **can.barnabasmusic.com**
- DNS servers reported: **SHANGHAI**, **DNS.GOOGLE**

### Ethernet
- Interface: **QE0**
- Ethernet address: **AA-00-04-00-6B-30**
- Interface flags: **UP BRDCST RUN MCAST SMPX**

## Cluster Boot and Root Model
- `SYS$SYSDEVICE` = **FUSION$DUA0:**
- `SYS$SPECIFIC` = **FUSION$DUA0:[SYS10.]**
- This confirms RISE is booted from the shared system disk hosted by FUSION.

## Local Paging/Swap Disk
### Local satellite disk
- Device: **RISE$DUA0:**
- Volume label: **RISE_12395**
- Mounted system-wide on RISE
- Available to cluster
- Free blocks at audit time: **2768076**

### Paging/swapping reported by `SHOW MEMORY/FILES`
- `DISK$RISE_12395:[SYSEXE]SWAPFILE.SYS;1`
- `DISK$RISE_12395:[SYSEXE]PAGEFILE.SYS;1`
- Totals reported:
  - Swapfile: **46496** pages
  - Pagefile: **125992** pages

## Shared Cluster-Visible Disks Seen from RISE
RISE had the following FUSION-hosted volumes mounted and available through the cluster:
- **FUSION$DUA0:** label **OVMSVAXSYS**
  - Host name shown: **FUSION**
  - Free blocks: **2250603**
- **FUSION$DUA1:** label **SYSVAX2**
  - Host name shown: **FUSION**
  - Free blocks: **2940564**
- **FUSION$DUA2:** label **DATA1**
  - Host name shown: **FUSION**
  - Free blocks: **2885412**

## TCP/IP Services Enabled at Audit Time
Enabled services reported by `TCPIP SHOW SERVICES`:
- FTP
- LOCKD
- MOUNTD
- NFS
- NTP
- PORTMAPPER
- REXEC
- RLOGIN
- RSH
- SNMP
- STATD
- TELNET

Disabled services explicitly shown:
- ESNMP
- LPD
- SMTP

## Users Visible at Audit Time
`SHOW USERS` reported:
- **KEITH** on **FUSION**
- **SYSTEM** on **RISE**

## Notes from Audit
- The expected shared-root satellite model is intact.
- RISE is using its own local page and swap files on `RISE$DUA0:`.
- The node-specific TCP/IP identity is active and separate from FUSION.
- A test attempt to query specific known-node entries with `MC NCP SHOW KNOWN NODES FUSION/RISE` used incorrect syntax and was not relied upon; DECnet executor characteristics were captured successfully.

## Summary
RISE is operating as the rebuilt satellite node exactly in the intended pattern: boot/root from **FUSION$DUA0:[SYS10.]**, local page/swap on **RISE$DUA0:**, cluster membership active, and its own independent DECnet and TCP/IP node identity functioning normally.
