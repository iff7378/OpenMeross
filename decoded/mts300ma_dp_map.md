# MTS300MA TuyaMCU datapoint map (authoritative)

Extracted from the stock Meross firmware dump (`captures/flash_dump.bin`), DP definition table at flash offset `0x14e168`, 0x48-byte stride, little-endian records `0607 | dpId | type | len | max | min`. Names are Meross's own, from the adjacent symbol table. Cross-checked against live values captured over the running UART: every `value`-type DP is the real quantity x10 (e.g. currentTemp 0x07 = 710 = 71.0, coolTemp 0x02 = 760 = 76.0 F). `tempUnit` (0x19) = 1 here, so temps are transmitted in F x10.

Protocol: TuyaMCU v3, 9600 8N1, frame `55 AA | ver | cmd | len16 | payload | sum8`. MCU->module uses cmd `0x07` (status report); module->MCU uses cmd `0x06` (control/set). OpenBeken parses the 0x07 reports correctly (confirmed live).

| dpId | dec | name | type | max | min | meaning |
|---|---|---|---|---|---|---|
| 0x01 | 1 | mode | enum | 4 | 0 | operating mode (enum 0-4) |
| 0x02 | 2 | coolTemp | value | 350 | 50 | cool setpoint, unit=tempUnit, x10 |
| 0x03 | 3 | heatTemp | value | 350 | 50 | heat setpoint, unit=tempUnit, x10 |
| 0x04 | 4 | fanSpeedMode | enum | 3 | 0 | fan speed (enum 0-3) |
| 0x05 | 5 | schedule | enum | 1 | 0 | schedule on/off |
| 0x06 | 6 | humiSet | value | 1000 | 0 | humidity setpoint %x10 |
| 0x07 | 7 | currentTemp | value | 500 | 0 | CURRENT TEMP, x10 (room) |
| 0x08 | 8 | currentHumi | value | 1000 | 0 | current humidity %x10 |
| 0x09 | 9 | outTemp | value | 500 | -340 | outdoor temp x10 |
| 0x0A | 10 | outHumi | value | 1000 | 0 | outdoor humidity %x10 |
| 0x0B | 11 | coolState | enum | 1 | 0 | cool relay active |
| 0x0C | 12 | heatState | enum | 1 | 0 | heat relay active |
| 0x0D | 13 | fanState | enum | 3 | 0 | fan relay active |
| 0x0E | 14 | auxState | enum | 1 | 0 | aux/emergency heat active |
| 0x0F | 15 | dryHumState | enum | 2 | 0 | dry/dehumidify state |
| 0x10 | 16 | insideTempCalib | value | 45 | -45 | inside temp calibration offset |
| 0x11 | 17 | insideHumiCalib | value | 990 | -990 | inside humidity calib |
| 0x13 | 19 | childLock | raw | 1 | 0 | child lock |
| 0x14 | 20 | fault | bitmap | 255 | 0 | fault bitmap |
| 0x15 | 21 | maxBrightness | value | 8 | 1 | max display brightness |
| 0x16 | 22 | minBrightness | value | 8 | 0 | min display brightness |
| 0x17 | 23 | sensor | enum | 255 | 0 | external sensor sel |
| 0x18 | 24 | wifiFault | enum | 9 | 0 | wifi fault code |
| 0x19 | 25 | tempUnit | enum | 1 | 0 | temp unit 0=C 1=F |
| 0x1A | 26 | simpleDis | enum | 1 | 0 | simple display |
| 0x1B | 27 | fanCycleTime | value | 59 | 1 | fan cycle time |
| 0x1C | 28 | fanMode | enum | 2 | 1 | fan mode (enum 1-2) |
| 0x1D | 29 | cloudTemp | value | -170 | 1200 | cloud/weather temp |
| 0x1E | 30 | changeWifi | raw | 1 | 0 | change wifi trigger |
| 0x28 | 40 | coolHeatGap | value | 50 | 10 |  |
| 0x29 | 41 | heatLv1TempDiff | value | 50 | 5 |  |
| 0x2A | 42 | heatLv2TempDiff | value | 50 | 5 |  |
| 0x2B | 43 | heatLv3TempDiff | value | 75 | 5 |  |
| 0x2C | 44 | heatMinWorkTime | value | 20 | 1 |  |
| 0x2D | 45 | heatLv23StopWay | raw | 1 | 0 |  |
| 0x2E | 46 | heatClass | enum | 1 | 0 |  |
| 0x32 | 50 | compMinStartTime | value | 30 | 1 |  |
| 0x33 | 51 | compMinStopTime | value | 30 | 2 |  |
| 0x34 | 52 | compStartTemp | value | 180 | -400 |  |
| 0x35 | 53 | coolLv1TempDiff | value | 50 | 10 |  |
| 0x36 | 54 | coolLv2TempDiff | value | 25 | 5 |  |
| 0x37 | 55 | compLv2StopWay | raw | 1 | 0 |  |
| 0x38 | 56 | compClass | enum | 1 | 0 |  |
| 0x39 | 57 | compTempEnable | raw | 1 | 0 |  |
| 0x3C | 60 | auxStopTemp | value | 260 | -170 |  |
| 0x3D | 61 | auxLv1TempDiff | value | 50 | 5 |  |
| 0x3E | 62 | auxLv2TempDiff | value | 50 | 5 |  |
| 0x3F | 63 | auxLv3TempDiff | value | 75 | 5 |  |
| 0x40 | 64 | auxStopWay | raw | 1 | 0 |  |
| 0x41 | 65 | auxWorkWay | raw | 1 | 0 |  |
| 0x42 | 66 | auxMinWorkTime | value | 30 | 1 |  |
| 0x43 | 67 | auxOutLimitOn | raw | 1 | 0 |  |
| 0x46 | 70 | fanHeatDSTime | value | 600 | 0 |  |
| 0x47 | 71 | fanCoolDSTime | value | 600 | 0 |  |
| 0x48 | 72 | filterNotifyTime | value | 2000 | 0 |  |
| 0x49 | 73 | filterWorkTime | value | 65535 | 0 |  |
| 0x50 | 80 | dryOnlyHeat | raw | 1 | 0 |  |
| 0x51 | 81 | dryOpenFan | raw | 1 | 0 |  |
| 0x52 | 82 | dryAlwaysOn | raw | 1 | 0 |  |
| 0x53 | 83 | dryDeadZone | value | 1000 | 10 |  |
| 0x54 | 84 | humDeadZone | value | 1000 | 10 |  |
| 0x55 | 85 | humOpen | raw | 1 | 0 |  |
| 0x56 | 86 | dryOpen | raw | 1 | 0 |  |
| 0x5A | 90 | systemClass | enum | 3 | 0 | systemClass (HVAC type) |
| 0x5B | 91 | coolLvNum | value | 2 | 0 | cool stages |
| 0x5C | 92 | heatLvNum | value | 3 | 0 | heat stages |
| 0x5D | 93 | fanLvNum | value | 3 | 0 | fan levels |
| 0x5E | 94 | dryHumClass | enum | 3 | 0 |  |
| 0x5F | 95 | obSet | raw | 1 | 0 |  |
| 0x64 | 100 | systemSetOk | raw | 1 | 0 | systemSetOk - commit system config |
| 0x65 | 101 | systemReset | raw | 1 | 0 | systemReset |

## Core climate DPs (for OpenBeken / HA)
- **0x01 mode** enum: operating mode. **Confirmed on hardware: 0=off, 1=heat, 2=cool, 3=auto** (4 = no-op). Matches manual's Heat/Cool/Auto/Off.
- **0x02 coolTemp** value /10: cool setpoint (writable).
- **0x03 heatTemp** value /10: heat setpoint (writable).
- **0x07 currentTemp** value /10: measured room temperature (read-only).
- **0x08 currentHumi** value /10: measured humidity (read-only).
- **0x0B/0x0C/0x0D/0x0E coolState/heatState/fanState/auxState** enum: live relay/stage status (read-only).
- **0x19 tempUnit** enum: 0=C, 1=F.
- **0x1C fanMode / 0x04 fanSpeedMode** enum: fan control.

## System type (systemClass 0x5A) — from manual wiring table
The manual's wiring table lists exactly 4 system types, matching `systemClass` enum 0-3 (unverified individually, but ordering is the strong default):
- 0 = **Conventional** (gas/electric furnace + AC) — this unit's committed default; correct for the barn condensing furnace
- 1 = Heat Pump (with/without aux)
- 2 = 2-Pipe Fan Coil
- 3 = 4-Pipe Fan Coil

Capacity per manual: up to 2-stage cool, 3-stage heat, 3-speed fan, + humidifier/dehumidifier (matches coolLvNum≤2 / heatLvNum≤3 / fanLvNum≤3 ranges). Terminals: R, Rc, Rh, C, G, Y, Y2, W/AUX, W2, O/B, E.

## The 'St' (setup) display state
Per Meross FAQ, 'St' means the device has not completed initial configuration. This is NOT wifi/cloud pairing - it is the HVAC *system configuration* (wiring/system type) that the Meross app's setup wizard normally writes. The relevant DPs are the system block: **0x5A systemClass** (HVAC type), **0x5B/0x5C/0x5D** cool/heat/fan stage counts, the wire/aux config DPs (0x2E heatClass, 0x38 compClass, 0x5E dryHumClass, 0x5F obSet, etc.), and finally **0x64 systemSetOk** to commit. Until this config is written and committed, the MCU stays in setup mode and ignores normal setpoint input. Replicating app setup = writing this system block over cmd 0x06 then 0x64=1. Needs the user's actual HVAC wiring to choose correct values.
