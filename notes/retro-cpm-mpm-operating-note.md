# Retro CP/M and MP/M Operating Note

## Scope

Working note for the Retro Computing Telegram topic covering Keith's virtual
Digital Research environments on Dockyards.

Host:
- `dockyards.can.barnabasmusic.com`

Systems:
- `3003` — ZPM3 (`Z3PLUS` / CP/M Plus with Z-System)
- `3002` — MP/M II

Access:
- `telnet dockyards.can.barnabasmusic.com 3003`
- `telnet dockyards.can.barnabasmusic.com 3002`

---

## ZPM3

### Console / shell behaviour

- Live prompt observed as `A0:COMMANDS>>`
- Uses named directories heavily
- Supplied manual reviewed: `Z3PLUS The Z-System for CP/M-Plus User’s Manual`
- `ZSHOW` / `SHOW` is the preferred read-only inspection tool

### ZPM3 path model

Observed in `ZSHOW`:
- symbolic path: `$0 A0 B0 J1 J2`
- DU form: `A0 A0 B0 J1 J2`
- DIR form: `COMMANDS COMMANDS WORK WS F80`

System file names / environment data observed:
- shell variable file: `SH.VAR`
- system file names 1-4 undefined
- console width `80`, total lines `24`, text lines `22`
- LST width `80`, total lines `66`, text lines `58`, formfeed `YES`
- `DU OK = YES`
- `Max DU = P15`
- `Speed = 4 MHz`
- `Quiet = NO`
- drive map `A..P`

### ZPM3 named directories

- `A0` = `COMMANDS`
- `B0` = `WORK`
- `J1` = `WS`
- `J2` = `F80`
- `J3` = `TP1`
- `J4` = `TP3`
- `J5` = `SCALC`
- `J6` = `BASIC`
- `J7` = `MULTIPLN`
- `J8` = `DBASEII`
- `K0` = `GAMES`
- `K1` = `ZORK`

### ZPM3 navigation notes

- `DIR` does **not** accept named directory or DU targets as an argument on this build
  - e.g. `DIR WS:` and `DIR J1:` returned `ERROR: Illegal command tail.`
- Reliable pattern:
  1. change into a named area, e.g. `WS:` or `TP1:`
  2. run `DIR`
- `DIRS` appears to be interactive on this build rather than a simple one-shot listing command

### ZPM3 application areas surveyed

#### `WS` (`J1`)
- WordStar suite present
- notable files included:
  - `WS.COM`, `WS.OVR`
  - `WSHELP.OVR`, `WSMSGS.OVR`
  - `WSCHANGE.COM`, `WSCHANGE.OVR`, `WSCHHELP.OVR`
  - `WSPRINT.OVR`
  - `WSU.COM`
  - `SPELSTAR.DCT`, `SPELSTAR.OVR`
  - `WSREADME.TXT`

#### `F80` (`J2`)
- FORTRAN-80 toolchain present
- notable files included:
  - `F80.COM`, `F80C.COM`
  - `F80LIB.FOR`, `F80LIB.REL`
  - `FORLIB.REL`, `OBSLIB.REL`
  - `TEST.FOR`, `TEST.COM`, `TESTBAK.FOR`, `TESTBAK.COM`
  - `MENU.CMD`

#### `TP1` (`J3`)
- Turbo Pascal area
- notable files included:
  - `TURBO.COM`, `TURBO.OVR`, `TURBOMSG.OVR`
  - `TP.LBR`
  - `TINST.COM`, `TINST.DTA`
  - `TLIST.COM`
  - `HELLO.PAS`, `HELLO.COM`
  - `MC.PAS`, `MC.HLP`, `MCDEMO.MCS`, `MC-MODxx.INC`
  - `MENU.CMD`, `MENU.COM`

#### `TP3` (`J4`)
- Later Turbo Pascal area
- notable files included:
  - `TP3.LBR`
  - `TURBO.COM`, `TURBO.OVR`, `TURBO.MSG`
  - `TINST.COM`, `TINST.DTA`, `TINST.MSG`
  - `HELLO.PAS`, `HELLO.COM`
  - `CMDLIN.PAS`, `LISTER.PAS`
  - `MC.COM`, `MC.PAS`, `MC.HLP`, `MCDEMO.MCS`

#### `SCALC` (`J5`)
- Spreadsheet / calculation area
- notable files included:
  - `SC2.COM`, `SC2.OVR`, `SC2.HLP`
  - `SDI.COM`, `SDI.OVR`
  - `INSTALL.COM`, `INSTALL.DAT`, `INSTALL.OVR`
  - `.CAL` sheets such as `BUDGET.CAL`, `CHECKS.CAL`, `RULE-78.CAL`, `TEN.CAL`, `TENMIN.CAL`

#### `BASIC` (`J6`)
- Rich BASIC language area
- notable files included:
  - `MBASIC.COM`, `MBASIC45.COM`, `MBASIC51.COM`, `MBASIC52.COM`
  - `CBASIC.COM`, `CBASE2.COM`
  - `BASCOM.COM`, `BASCOM.HLP`, `BASCOM2.HLP`
  - `BRUN.COM`, `CRUN.COM`, `CRUN2.COM`
  - `CB80.COM` and overlays
  - `BASLIB.REL`, `OBSLIB.REL`
  - numerous sample/game/demo programs including `ELIZA.BAS`, `STARTREK.BAS`, `WUMPUS4K.BAS`, `LANDER4K.BAS`, `BLACKJAK.BAS`, `ROCKET.BAS`

#### `DBASEII` (`J8`)
- dBase II environment plus application data
- notable files included:
  - `DBASE.COM`, `DBASEOVR.COM`, `DBASEMSG.TXT`
  - `CB-*` chequebook-style command/data files
  - `IN-*` inventory-style command/data files
  - `LB-*`, `SP-*`
  - data/index/report forms present: `.DBF`, `.NDX`, `.FRM`, `.MEM`

#### `ZORK` (`K1`)
- Infocom trilogy present
- files observed:
  - `ZORK1.COM`, `ZORK1.DAT`, `ZORK1.SAV`
  - `ZORK2.COM`, `ZORK2.DAT`
  - `ZORK3.COM`, `ZORK3.DAT`

---

## MP/M II

### Console behaviour

- Primary prompt observed as `0A>`
- Prompt reflects user/drive context and was also seen as `1A>`, `2A>`, `0B>`, `2D>`, etc.
- Environment is much plainer than ZPM3, no named-directory layer

### MP/M II navigation model

- Explore manually by:
  1. selecting a drive, e.g. `A:` / `B:` / `C:`
  2. switching user area, e.g. `USER 0`, `USER 1`, `USER 2`
  3. running `DIR`
- Keith advised that `SDIR` can be used to show system files, especially on `0A:`
- Commands like `USER`, `DIR`, and `STAT` appear to be transient `.PRL` programs on this build

### MP/M II findings so far

#### Baseline command behaviour
- `DIR` in `A0` returned:
  - `Directory for User 0:`
  - `File not found.`
  - `System Files Exist`
- `HELP` returned `HELP?`
- `USER` reported the active user correctly
- `STAT` on `A:` reported free space

#### Survey results

##### Drive A
- `A0`:
  - no ordinary visible files
  - reports `System Files Exist`
- `A1`:
  - `File not found`
- `A2`:
  - `File not found`

##### Drive B
- `B0`:
  - `File not found`
- `B1`:
  - `File not found`
- `B2`:
  - `File not found`

##### Drives C and D
- Access attempts triggered BDOS errors rather than simple empty-directory results
- observed errors included:
  - `Bdos Err On C: Bad Sector`
  - `Bdos Err On D: Bad Sector`
- transient commands failed while trying to load files such as:
  - `USER.PRL`
  - `DIR.PRL`
  - `STAT.PRL`
- Interpretation: `C:` and `D:` are not valid/healthy online work volumes in the present configuration, or are mapped to absent/bad images

##### Additional drives
- Later probe output suggested similar BDOS trouble reaching at least `H:`
- Extended survey beyond `D:` was not yet completed cleanly enough to treat as authoritative

### Working interpretation of MP/M II state

- `A:` is the only clearly usable drive seen so far, and mainly as a system area
- `B:` is reachable but appears empty in users `0..2`
- `C:` and `D:` are erroring at the BDOS/transient-command level
- further probing should be done conservatively, one drive at a time

### Recommended future read-only method for MP/M II

1. `A:`
2. `USER 0`
3. `SDIR`
4. then test one additional drive at a time
5. for each drive, try `USER 0`, `USER 1`, `USER 2`, then `DIR`
6. stop and note BDOS errors rather than pushing deeper automatically
