# PULSE — RSX-11M-PLUS 4.6 System Profile

## Summary

PULSE is a DEC RSX-11M-PLUS 4.6 system running under SIMH as a PDP-11/70 emulation instance on the host **Simul**. It is a HECnet/DECnet node and is currently known as:

- Node name: **PULSE**
- DECnet node: **12.103**
- Host platform: **SIMH PDP-11/70 emulation**
- Host machine: **Simul**

This note captures the environment information established during the initial network bring-up and subsequent verification session.

## Operating System

- OS: **RSX-11M-PLUS V4.6**
- Base level: **BL87**
- System name shown at login: **PULSE**
- Login banner sourced from: `LB:[1,2]LOGIN.TXT`

Observed login banner:

- `RSX-11M-PLUS V4.6   BL87    [1,54] System    PULSE`

## Access Method

Interactive access confirmed via:

- **TELNET** to `pulse`

Observed behaviour:

- Connection presents `Welcome to PULSE, an RSX-11M-PLUS system!`
- Login sequence uses:
  - `HEL SYSTEM`
  - password prompt
- Successful login runs:
  - `@LB:[1,2]SYSLOGIN.CMD`

A terminal-type related message was observed during automated login:

- `SET -- Inquire cannot determine terminal type`

This suggests `SYSLOGIN.CMD` or a called procedure attempts terminal-type discovery that does not fully suit a raw scripted telnet session.

## DECnet / HECnet

Confirmed DECnet identity:

- Executor node: **12.103 (PULSE)**

Known nodes confirmed during setup and preserved across reboot:

- `1.13 (MIM)`
- `12.106 (FUSION)`
- `12.107 (RISE)`
- `12.1022 (BURST)`

These names were successfully applied using `NCP SET NODE ... NAME ...` and were later verified after boot, confirming persistence through startup procedures.

### Important DECnet note

On this RSX build, `NCP` accepted:

- `SET NODE <addr> NAME <name>`

But did **not** accept:

- `DEFINE NODE ...`
- `DEFINE KNOWN NODE ...`

So this environment appears to rely on **startup command files** for persistent node naming rather than a VMS-style permanent NCP database update model.

## TCP/IP Environment

PULSE is using **Johnny Billquist’s BQTCP/IP package** associated with the `rsx11bq` environment.

Configuration was performed via:

- `@LB:[IP]IPCONFIG`

Startup/bring-up appears to use:

- `@LB:[IP]IPAPPL`
- with related procedures present:
  - `LB:[IP]PREAPPL.CMD`
  - `LB:[IP]POSTAPPL.CMD`

### Generated TCP/IP configuration

The generated configuration file is:

- `LB:[1,2]IPPARAM.CMD`

Observed values:

- Hostname: `PULSE`
- Domain: `can.barnabasmusic.com`
- DNS server: `192.168.1.1`
- NTP server: `pool.ntp.org`
- Primary interface IP: `192.168.1.139`
- Netmask: `255.255.255.0`
- Default router: `192.168.1.1`
- Broadcast interface index: `0`
- Log directory: `LB:[IPLOG]`

### Interfaces

`IFCONFIG SHOW ALL` showed:

- `IF0` — running, `PULSE.local/24`, broadcast `192.168.1.255`, MTU `1500`, ACP `ETHACP`, line `UNA-0`
- `IF1` — running loopback, `127.0.0.1/8`, broadcast `127.255.255.255`, MTU `8128`

This indicates:

- physical network on `UNA-0`
- ACP in use: `ETHACP`
- loopback correctly enabled

### Verified network services

Confirmed working during testing:

- `PING` to `192.168.1.1`
- `TELNET`
- `FTP`

Observed ping target response:

- `unifi.can.barnabasmusic.com (192.168.1.1)`

## TCP/IP package contents observed in `LB:[IP]`

Notable files/tasks present include:

- `ETHACP.TSK`
- `SLIPACP.TSK`
- `DLXACP.TSK`
- `IFCONFIG.TSK`
- `PING.TSK`
- `TRACERT.TSK`
- `NETSTAT.TSK`
- `TELNETD.TSK`
- `INETD.TSK`
- `DNS.TSK`
- `DHCP.TSK`
- `FTP.TSK`
- `FTPD.TSK`
- `MAILD.TSK`
- `WWW.TSK`
- `IRC.TSK`
- `RWHOD.TSK`
- `IPGEN.CMD`
- `IPINS.CMD`
- `IPAPPL.CMD`
- `IPCONFIG.CMD`
- `README.DOC`

This suggests a comparatively full BQTCP/IP environment, including client and server components.

## Important local fixes discovered

### `IPCONFIG.CMD` defects

During initial configuration, `LB:[IP]IPCONFIG.CMD` was found to contain at least two defects that affected interactive setup.

#### 1. String prompt default handling bug

A `.ASKS` line in `.qstr` used an invalid default-specification form and required correction so string defaults were quoted properly.

#### 2. Missing quote in `.qyn`

A line building `qvar` was missing a closing quote.

A backup copy was created during repair:

- `LB:[IP]IPCONFIG.BAK`

This should be retained for reference.

## Startup and persistence observations

Based on the live session:

- system login invokes `@LB:[1,2]SYSLOGIN.CMD`
- node naming persisted across reboot
- TCP/IP configuration persisted to `LB:[1,2]IPPARAM.CMD`
- startup customisation for DECnet naming was likely placed in a system startup command file, most plausibly `LB:[1,2]STARTUP.CMD`

This should be verified directly on-console when convenient.

## Audit limitations

This note is based on:

- directly observed TELNET access behaviour
- live outputs shared during the session
- confirmed command results from PULSE during bring-up and post-boot testing

The automated audit from this Linux host was partially constrained by RSX terminal handling under scripted TELNET sessions. In particular, the login-time command procedure emitted terminal-type related behaviour that interfered with longer unattended command capture. So this note is accurate on the major system characteristics already established, but it is **not yet a full exhaustive dump** of tasks, partitions, memory pools, or all startup procedures.

## Recommended next audit pass

For a deeper read-only survey, gather these interactively from a normal terminal session on PULSE:

- `SHOW SYSTEM`
- `SHOW MEMORY`
- `SHOW TASKS`
- `SHOW PARTITIONS`
- `SHOW POOL`
- `SHOW USERS`
- `SHOW DEVICES`
- `NCP SHOW EXECUTOR CHARACTERISTICS`
- `PIP TI:=LB:[1,2]STARTUP.CMD`
- `PIP TI:=LB:[1,2]SYSLOGIN.CMD`
- `PIP TI:=LB:[IP]README.DOC`

That would allow this profile to be expanded into a more complete operating manual for PULSE.
