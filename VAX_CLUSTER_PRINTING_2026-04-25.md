# OpenVMS VAXcluster Printing / Spooling Notes — 25 April 2026

## Final working print path

```text
FUSION / RISE
  -> OpenVMS queue HL2445
  -> LPD to Simul (192.168.1.236)
  -> CUPS queue brother2445br
  -> Brother HL-L2445DW
```

This was verified working from **both FUSION and RISE**.

---

## Why this design was needed

Direct LPD printing from OpenVMS to the Brother printer was unreliable:

- `BINARY_P1` accepted jobs but produced no useful output
- `TEXT_P1` produced blank pages
- even when transport worked, modern printer-side handling of VMS text jobs was inconsistent

Using **Simul as an LPD-to-CUPS bridge** solved the problem cleanly.

---

## OpenVMS side

### Queue name

- Execution queue: `HL2445`

### Final OpenVMS LPD target

- Remote host (`rm`): `192.168.1.236`  
- Remote printer (`rp`): `brother2445br`

### Confirmed `TCPIP$PRINTCAP.DAT` entry shape

```text
HL2445|hl2445|LASER:\
 :lf=/SYS$SPECIFIC/TCPIP$LPD/HL2445.LOG:\
 :lp=HL2445:\
 :rm=192.168.1.236:\
 :rp=brother2445br:\
 :sd=/SYS$SPECIFIC/TCPIP$LPD/HL2445:
```

### Recommended queue defaults

```text
SET QUEUE HL2445 /DEFAULT=(NOFEED,NOFLAG,FORM=DEFAULT)
```

### Test command

```text
PRINT/QUEUE=HL2445 TESTPRINT.TXT
```

This was confirmed to print successfully from:
- **FUSION**
- **RISE**

---

## Simul side

### Working CUPS queue

A driverless CUPS queue was tested first, but VMS-fed jobs arrived as `unknown` and were canceled by the printer.

The working queue was a **brlaser** queue:

```bash
sudo lpadmin -p brother2445br -E \
  -v socket://192.168.1.74 \
  -m drv:///brlaser.drv/brl2360d.ppd
```

This queue successfully printed both:
- direct Linux test jobs
- OpenVMS jobs relayed through LPD

### LPD bridge on Simul

`cups-lpd` was exposed via systemd socket activation.

#### `/etc/systemd/system/cups-lpd.socket`

```ini
[Unit]
Description=CUPS LPD mini-server socket

[Socket]
ListenStream=515
Accept=yes
NoDelay=true

[Install]
WantedBy=sockets.target
```

#### `/etc/systemd/system/cups-lpd@.service`

```ini
[Unit]
Description=CUPS LPD mini-server
After=cups.service
Requires=cups.service

[Service]
ExecStart=/usr/lib/cups/daemon/cups-lpd -n
StandardInput=socket
StandardOutput=socket
StandardError=journal
User=lp
Group=lp
```

### Reload / enable

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now cups-lpd.socket
sudo systemctl restart cups-lpd.socket
```

---

## Diagnostics that proved useful

### On OpenVMS

Check queue state:

```text
SHOW QUEUE/FULL HL2445
```

Check the LPD log:

```text
TYPE SYS$SPECIFIC:[TCPIP$LPD]HL2445.LOG
```

If a queue process wedges, restarting the queue manager clears it:

```text
STOP/QUEUE/MANAGER/ABORT
START/QUEUE/MANAGER
```

Or kill the specific symbiont process if needed:

```text
SHOW SYSTEM
STOP/ID=pid
```

### On Simul

Check CUPS-LPD activity:

```bash
sudo journalctl -u cups-lpd.socket -u 'cups-lpd@*' -n 50 --no-pager
```

Check CUPS job state:

```bash
lpstat -W all -o brother2445br
lpstat -t
```

Check CUPS error log:

```bash
sudo tail -n 50 /var/log/cups/error_log
```

---

## Key lesson learned

For this environment, the reliable solution is:

- **do not print directly from OpenVMS to the Brother printer**
- instead, **print from OpenVMS to Simul via LPD**
- let **CUPS + brlaser** handle the modern printer protocol details

This gives a stable cluster-wide print service with minimal OpenVMS-side complexity.
