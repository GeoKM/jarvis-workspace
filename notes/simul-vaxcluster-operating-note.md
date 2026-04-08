# Simul VAXcluster Operating Note

Last updated: 2026-04-07

## Systems
- **Host:** `Simul` (`192.168.1.236`)
- **Router/Gateway:** `BURST` — DECnet `12.1022` via `pydecnet`
- **Cluster nodes:**
  - `FUSION` — DECnet `12.106`, IP `192.168.1.137`, MAC `08-00-2B-AA-BB-02`
  - `RISE` — DECnet `12.107`, IP `192.168.1.138`, MAC `08-00-2B-AA-BB-03`

## Roles
- **FUSION:** primary VMS cluster node, richer storage layout
- **RISE:** secondary/satellite VMS cluster node, leaner local storage
- **BURST:** critical local DECnet/HECNET gateway and router

## Key directories on Simul
```bash
~/src/pydecnet/pydecnet/
~/src/simh/BIN/
~/FUSION/X/
~/RISE/X/
```

## Host network layout
- `br0` = host bridge, IP `192.168.1.236`
- `ens18` = physical NIC
- `tap0` = FUSION
- `tap1` = RISE
- `tap2` = spare
- `tap3` = BURST / pydecnet

TAP interfaces are persistent via `/etc/network/interfaces`.

### Live bridge membership
- `br0` bridges: `ens18 tap0 tap1 tap2 tap3`
- Host IP lives on `br0`, not on the TAP interfaces

## Startup order
```bash
cd ~/src/pydecnet/pydecnet/
sudo pydecnet pydecnet.conf samples/http.conf
```

```bash
cd ~/FUSION/X
/home/keith/src/simh/BIN/vax ./vax.ini
```

```bash
cd ~/RISE/X
/home/keith/src/simh/BIN/vax ./vax.ini
```

**Order matters:**
1. `BURST`
2. `FUSION`
3. `RISE`

## Shutdown order
1. shut down `RISE`
2. shut down `FUSION`
3. stop `BURST`

## pydecnet / BURST configuration baseline
From `~/pydecnet.conf`:
- node identity: `12.1022 BURST`
- routing type: `l1router`
- Ethernet circuit: `ETH-0 Ethernet tap:tap3 --mop`
- GRE uplink: `GRE-0 GRE 103.46.213.236 --source=192.168.1.236`
- web monitor: `http://simul.can.barnabasmusic.com:8000`

## SIMH configuration summary

### FUSION (`~/FUSION/X/vax.ini`)
- `64M` RAM
- persistent NVRAM: `./data/nvram.bin`
- `rq0` = `./data/d0.dsk`
- `rq1` = `./data/d0-1.dsk`
- `rq2` = `./data/d1.dsk`
- `rq3` = `./data/os.iso` (read-only CD)
- Ethernet on `tap0`
- MAC `08-00-2B-AA-BB-02`

### RISE (`~/RISE/X/vax.ini`)
- `64M` RAM
- persistent NVRAM: `./data/nvram.bin`
- `rq0` = `./data/d0.dsk`
- only one active disk attachment
- Ethernet on `tap1`
- MAC `08-00-2B-AA-BB-03`

## OpenVMS / cluster baseline
Observed on 2026-04-08 local VMS time:

### Cluster membership
- `FUSION` — `MEMBER`
- `RISE` — `MEMBER`

Confirmed from both nodes via `SHOW CLUSTER`.

### DECnet executor identity
- `FUSION` executor = `12.106 (FUSION)`
- `RISE` executor = `12.107 (RISE)`

### FUSION storage baseline
- `FUSION$DUA0:` → `OVMSVAXSYS`
- `FUSION$DUA1:` → `SYSVAX2`
- `FUSION$DUA2:` → `DATA1`
- `FUSION$DUA3:` → `VAXVMS073` (write-locked CD)

### RISE storage baseline
- `RISE$DUA0:` → `RISE_12395`
- `FUSION$DUA1:` → remote mount
- `FUSION$DUA2:` → remote mount
- `FUSION$DUA3:` → remote mount

Interpretation:
- `FUSION` is the richer storage/administrative node
- `RISE` has its own local system volume and clustered visibility to FUSION volumes

## DECnet visibility notes
From `FUSION`:
- `MCR NCP SHOW NODE BURST` shows node `12.1022 (BURST)` via `QNA-0`
- `MCR NCP SHOW NODE RISE` shows node `12.107 (RISE)` via `QNA-0`, next node `12.1022 (BURST)`

Operational implication:
- `BURST` is central to local DECnet pathing and should be treated as foundational infrastructure.

## Expected healthy state

### On Simul
```bash
ip -brief link show
ip -brief addr show
ps -ef | grep -i '[p]ydecnet'
ps -ef | grep '/home/keith/src/simh/BIN/vax' | grep -v grep
ss -ltnp | grep ':8000'
```

Healthy indicators:
- `br0`, `tap0`, `tap1`, `tap3` are **UP**
- `pydecnet` is running
- two SIMH `vax` processes are running
- port `8000` is listening

### On OpenVMS
```text
SHOW CLUSTER
SHOW DEVICE
MCR NCP SHOW EXECUTOR
MCR NCP SHOW NODE BURST
MCR NCP SHOW NODE FUSION
MCR NCP SHOW NODE RISE
```

Healthy indicators:
- both `FUSION` and `RISE` show as `MEMBER`
- `FUSION` executor = `12.106`
- `RISE` executor = `12.107`

## First-response troubleshooting

### If RISE fails to join
1. confirm `BURST` is running
2. confirm `FUSION` is already up
3. confirm `tap1` is UP
4. check on VMS:
```text
SHOW CLUSTER
MCR NCP SHOW EXECUTOR
MCR NCP SHOW NODE BURST
```

### If DECnet is unhealthy
1. check `pydecnet` on Simul
2. verify `tap3` and `br0`
3. on VMS:
```text
MCR NCP SHOW EXECUTOR
MCR NCP SHOW NODE BURST
```

### If both VAXen seem isolated
Check Linux first:
```bash
ip link show br0
ip link show tap0
ip link show tap1
ip link show tap3
systemctl status networking --no-pager
```

## Key operational truth
This environment depends on the full chain being intact:

**Linux bridge/TAP -> BURST/pydecnet -> DECnet path -> OpenVMS cluster**

If one layer misbehaves, the upper layers will usually follow.
