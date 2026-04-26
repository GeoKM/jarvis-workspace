# FUSION Environment Description — 2026-04-24

## Scope
Read-only live audit performed over Telnet on **24-APR-2026** after the cluster rebuild.

## System Identity
- Node name: **FUSION**
- OpenVMS version: **OpenVMS VAX V7.3**
- Cluster role: **boot server / primary cluster member / MSCP server**
- Cluster membership at audit time:
  - **FUSION** — MEMBER
  - **RISE** — MEMBER
- Cluster view source: `SHOW CLUSTER`
- System ID shown by `SHOW CLUSTER`: **12394**

## Network Identity
### DECnet
- Executor node: **12.106 (FUSION)**
- DECnet type: **nonrouting Phase IV**
- Incoming proxy: **Enabled**
- Outgoing proxy: **Enabled**

### TCP/IP
- Product: **Compaq TCP/IP Services for OpenVMS VAX V5.1**
- Hostname: **FUSION.can.barnabasmusic.com**
- IPv4 address: **192.168.1.137/24**
- Default route: **0.0.0.0 -> 192.168.1.1**
- Name service domain: **can.barnabasmusic.com**
- DNS servers reported: **SHANGHAI**, **DNS.GOOGLE**

### Ethernet
- Interface: **QE0**
- Ethernet address: **AA-00-04-00-6A-30**
- Interface flags: **UP BRDCST RUN MCAST SMPX**

## Storage Layout
### System disk
- Device: **FUSION$DUA0:**
- Volume label: **OVMSVAXSYS**
- Mounted: **system**
- Served to cluster: **Yes, via MSCP Server**
- Also mounted on: **RISE**
- Free blocks at audit time: **2250603**

### Shared auxiliary disks
- **FUSION$DUA1:** label **SYSVAX2**
  - Mounted system-wide
  - Served via MSCP Server
  - Also mounted on **RISE**
  - Free blocks: **2940564**
- **FUSION$DUA2:** label **DATA1**
  - Mounted system-wide
  - Served via MSCP Server
  - Also mounted on **RISE**
  - Free blocks: **2885409**

### Optical device
- **FUSION$DUA3:** device type **RRD40**
- Online at audit time

## System Root and Paging/Swap
- `SYS$SYSDEVICE` = **FUSION$DUA0:**
- `SYS$SPECIFIC` = **FUSION$DUA0:[SYS0.]**
- Paging/swapping reported by `SHOW MEMORY/FILES`:
  - `DISK$OVMSVAXSYS:[SYS0.SYSEXE]SWAPFILE.SYS`
  - `DISK$OVMSVAXSYS:[SYS0.SYSEXE]PAGEFILE.SYS`
- Totals reported:
  - Swapfile: **45000** pages
  - Pagefile: **122000** pages

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
- **SYSTEM** on **FUSION**

## DECnet Known Nodes
- `MC NCP SHOW KNOWN NODES` showed a large imported **volatile** known-node database.
- Entries included, among many others:
  - **12.107 (RISE)**
  - **12.1022 (BURST)**
- This confirms the imported known-node set was present on FUSION during the audit.

## Summary
FUSION is operating as the primary node of the rebuilt two-node VAXcluster. It is serving the shared system and data disks through MSCP, providing the cluster boot/root environment used by RISE, and is configured with working DECnet and TCP/IP identities consistent with the rebuilt target design.
