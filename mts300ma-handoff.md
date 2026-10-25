# Handoff: Meross MTS300MA local-control hack

## Goal
Get the Meross MTS300MA thermostat under fully local Home Assistant control by replacing the Wi-Fi side only. Keep the stock SinOne MCU firmware, which runs the touch UI, display, sensor, and relay staging. The approach is to sniff and decode the UART protocol between the Wi-Fi module and the MCU, then either:
- flash OpenBeken onto the existing module (if its chip is supported) and write a driver, or
- swap in an ESP32-C3 module and use an ESPHome custom UART climate component (TuyaMCU-style).

Rewriting the MCU firmware is out of scope. The SinOne flash is likely read-protected, and there's no public datasheet.

Install target: a barn with a condensing furnace. A new multi-conductor thermostat run (with C) will be pulled, so C-wire power isn't a constraint.

## Hardware: confirmed
| Item | Detail |
|---|---|
| Device | Meross MTS300MA (Matter-over-Wi-Fi, US) |
| Wi-Fi module | Meross-branded, 16-pin castellated (8 per side), PCB antenna, RF shield. Label `MWA6EBV1-MTS300MA-US9`. Chip under the shield is **unknown**. |
| MCU | SinOne (SOC) **SC95R605P**, LQFP48, date code 2520. No public datasheet found. The "R" doesn't match SinOne's public naming, where "F" = Flash MCU, so it's probably non-catalog or customer-specific. Likely a 1T 8051 with touch-key sensing. Programmed via SinOne SC LINK (2-wire JTAG). |
| Power section | Buck converter with a "220" inductor; 2× 100µF/63V caps (likely the rectified 24V input) and a 220µF/25V cap (likely the buck output). Runs off R–C. |
| Board-to-backplate | Two rows of 6 pins connecting to the wiring terminals |

## 4-pin header next to the MCU
Pin 1 is the far-left pin in the photo orientation, with the MCU below the header.

| Pin | Finding | Status |
|---|---|---|
| 1 | GND. Continuity to the Wi-Fi module's RF shield. | Confirmed |
| 2 | Power rail. Continuity to caps in the power section. **Voltage not yet measured** (3.3V vs 5V unknown). | Partly confirmed |
| 3 | Traces to MCU only (no continuity to the module) | Confirmed |
| 4 | Traces to MCU only (no continuity to the module) | Confirmed |

Conclusion: this is almost certainly the **SC LINK debug/programming port**, not the module↔MCU UART. Don't send serial data into it.

## Hypotheses (unconfirmed)
- The 7 white 4-pin parts marked "1.2P" are probably PhotoMOS/opto-MOSFET SSRs, one per output terminal. The yellow rectangular block near the top is unidentified. It's **unknown whether the MCU or the module drives the relays**. The plan assumes the MCU does. If the module does, the plan changes.
- Possible pin-compatible reference for the MCU: the SinOne SC95F8617 LQFP48 datasheet, which is public. Use it as a guide only and verify every pin.

## Wi-Fi module: confirmed via FCC filing
Found FCC internal/external photos (AGC report AGC00970231205AP02) for this module. Saved in [reference/](reference/).

- **Chip: Realtek RTL8720F**, confirmed by marking visible in [reference/fcc-internal-photos.png](reference/fcc-internal-photos.png). OpenBeken-supported — the ESP32-C3 swap fallback likely isn't needed.
- **Module: Meross `MR3E_MWA6E_Rev1.0`** (silkscreened on the module in [reference/meross-mwa6e-module-pinout.png](reference/meross-mwa6e-module-pinout.png)), sold under part family `BSLBWR01`. 16 castellated pins, 8/side, 3.3V supply, 300mA max.
- **Full pin definition** (from the module datasheet page, same image):

  | Pin | Function | | Pin | Function |
  |---|---|---|---|---|
  | 1 | LOG_TX | | 16 | UTX0 |
  | 2 | LOG_RX | | 15 | URX0 |
  | 3 | EN | | 14 | GPIO20 (PWM0) |
  | 4 | GPIO17 | | 13 | GPIO19 (PWM7) |
  | 5 | GPIO2 (PWM2) | | 12 | GPIO18 |
  | 6 | GPIO3 (PWM3) | | 11 | GPIO12 / NC |
  | 7 | GPIO4 (PWM4) | | 10 | GPIO0 |
  | 8 | 3V3 | | 9 | GND |

  **Two separate UARTs exist on this module**: pins 1/2 are `LOG_TX`/`LOG_RX` — the module's own debug/boot-log UART (115200 baud, per Realtek convention). Pins 15/16 are `URX0`/`UTX0` — a distinct UART0, the much stronger candidate for the module↔MCU link. These are different physical nets; don't conflate them.

## Hypotheses (unconfirmed)
- The module↔MCU UART is most likely on module pins 15/16 (URX0/UTX0). Need to locate these physically on the castellated edge (standard orientation: pin 1 is adjacent to the antenna, per the datasheet diagram) and probe there directly.

## Protocol: confirmed
Cold-boot capture on module pins 15/16 (`URX0`/`UTX0`) shows real, correctly-framed traffic — see [decoded/05_cold_boot_frames.md](decoded/05_cold_boot_frames.md), decoded from [captures/05_cold_boot_uart0_pins15_16.sr](captures/05_cold_boot_uart0_pins15_16.sr) (not committed, see `.gitignore`).

- **Baud/framing**: 9600 8N1.
- **Frame grammar**: `55 AA | version | command | len_hi len_lo | payload[len] | checksum`. Checksum = sum of all preceding bytes in the frame, mod 256 — verified correct on every captured frame.
- **This is standard TuyaMCU protocol**, as the doc predicted.
- `URX0` (MCU → module, cmd `0x06`): at boot, the MCU dumps its entire datapoint (DP) table one frame at a time, dp_id ascending from 0x01 to 0x55. Payload grammar per DP: `dp_id | dp_type | dp_len_hi dp_len_lo | dp_data`. Observed dp_types: `01`=bool, `02`=value (4-byte int), `04`=enum (1-byte).
- `UTX0` (module → MCU, cmd `0x07`): module acks each DP report, echoing the same dp_id/type/value back.
- **Promising DP values already visible in the boot dump** (unconfirmed meaning — need to correlate against the capture checklist, e.g. setpoint changes):
  - dp 0x02 = 760, dp 0x03 = 640, dp 0x06 = 700, dp 0x07 = 690 — all plausible as temperatures in tenths of a degree (76.0° / 64.0° / 70.0° / 69.0°). Good candidates for current temp and heat/cool setpoints.
  - dp 0x01, 0x04, 0x05 = enum 0 — good candidates for mode/fan-mode fields.
- **Next step**: repeat the doc's capture checklist (setpoint up/down from touchscreen and app, mode change, fan change, temperature change) on these same two pins, and diff against this boot dump to map dp_id → meaning.

## Ruled out
- **Two round test pads above the Wi-Fi module**: metered out to module pins 4 (GPIO17) and 5 (GPIO2/PWM2) — general-purpose GPIOs, not UART. Explains the three all-zero captures; nothing wrong with the capture setup, just the wrong net. Not worth probing further unless GPIO toggling becomes relevant later (e.g. a reset or mode-select line).

## Bench setup
- **Power:** 24VDC on **R (+)** and **C (−)** from a current-limited supply (100–200 mA). If it doesn't boot, swap polarity; the input may be a half-wave diode.
- Running on DC may trigger wiring-detection errors or missing AC zero-cross behavior. That doesn't matter for sniffing. If it gets in the way, use a 24VAC transformer instead.
- **Don't backpower.** When the board runs from 24V, connect only GND and signal lines from the analyzer or adapter, never VDD.
- Measure header pin 2 to GND with power on before connecting any 3.3V-only tool.

## Current step (in progress)
The logic analyzer is going on the MCU first, then the Wi-Fi chip.

### Find the UART lines
1. Check continuity from each module pad to the MCU pins. Two lines shared between them = the UART candidates.
2. Check whether the two test pads above the module tie into those lines.
3. With power on, TX idles firmly high because it's driven. RX is often weakly pulled up or floating; a 10k to GND barely moves TX.

### Captures to take (label each with what was done)
1. Cold boot / power-cycle, including the startup handshake
2. Idle, 2–5 minutes (heartbeats or polling)
3. Setpoint up and down from the **touchscreen**
4. Setpoint up and down from the **app**
5. Mode change: off / heat / cool / auto
6. Fan mode change
7. Temperature or humidity changing (breathe on the sensor) to find status reports
8. Wi-Fi provisioning or reset, if practical
9. Separately: the module's own debug UART (if found) at 115200 baud for its boot log. Look for a `chip set :` line.

### Decoding
- Use the analyzer's autobaud. Otherwise try 9600, then 115200. Assume 8N1 to start.
- Look for a fixed header, a length byte, a command/type byte, a payload, and a checksum (sum or XOR). Compare against the TuyaMCU framing (`55 AA ...`), since many vendors copy it.
- Compare touchscreen-initiated and app-initiated changes. That separates MCU→module status reports from module→MCU commands.

## Firmware dump plan (in progress)
Decided to skip app-based captures (no provisioning wanted) and go straight for a full flash dump of the Wi-Fi module, per the decision tree below — RTL8720 flash on these Tuya/Meross-style modules is typically unencrypted.

On RTL8720CF (AmebaZ2), the flashing/ISP port is the **same UART as the debug log** (internally "UART2"), not `URX0`/`UTX0`. Mapping onto the confirmed Meross module pinout:

| Function | SoC pin | Module pin |
|---|---|---|
| Flashing UART, adapter TX → here | RX2 / PA15 | Pin 2 (`LOG_RX`) |
| Flashing UART, adapter RX ← here | TX2 / PA16 | Pin 1 (`LOG_TX`) |
| Download-mode strap — pull to **3.3V**, not GND | GPIO0 / PA00 | Pin 10 (`GPIO0`) |
| Reset / chip-enable — ground briefly to reset | CEN | Pin 3 (`EN`) — likely, unconfirmed |
| Must NOT be grounded while flashing | PA13 / RX0 | Pin 15 (`URX0`) — leave disconnected |

Procedure: hold pin 10 at 3.3V, then briefly ground pin 3 (or power-cycle), chip should print "Open Download Mode on UART" on the LOG UART. Then use `ltchiptool` to dump flash over pins 1/2.

**Caution**: flashing draws more current and is more sensitive to supply droop than passive sniffing. The bench supply's 100-200mA current limit (set for safe sniffing) may need to be raised temporarily for a successful dump — a sagging 3.3V rail is the most common flashing failure per LibreTiny's docs.

Source: [LibreTiny RTL8720CF/CM docs](https://docs.libretiny.eu/docs/platform/realtek-ambz2/).

## Firmware identified: boot banner captured
Got the chip to boot fully to application firmware while listening on LOG_TX/LOG_RX (pins 1/2) with `ltchiptool`'s ROM download-mode handshake in progress. At the time this looked like a tight race (ROM falling through to app boot before a command could be sent) — that theory was wrong. The actual cause: GPIO0 had been unjumpered from 3.3V during an earlier debug-console test and never reconnected, so the chip was just doing a normal boot the whole time (no download-mode strap asserted at all). Once GPIO0 was reconnected, download mode held reliably with no race. That "failure" run did give us a useful full boot log while it lasted:

```
chip set : rtl8720cm
hw_ver   : 9.0.0
fw_ver   : 9.1.16
compiler : gcc 10.3.0
compile time : 2025/11/20-11:31:42
curr_fw_idx : 2
matter md5  : 9c3a623c86216a9f4fc98889092f3361
model : mts300
mac   : c4:e7:ae:27:3f:5a
Enter INTERACTIVE MODE
Login:
```

- **Chip confirmed as RTL8720CM** (not CF as assumed — same AmebaZ2 family, `ltchiptool`'s `realtek-ambz2` target still applies).
- **Meross left an interactive debug console in production firmware**, reachable over the same LOG UART (pins 1/2) on every normal boot — no GPIO0 strap needed. Prompts `Login:`. Untried: what credentials it accepts, if any.
- This is a new, possibly easier path than the ROM-level flash dump: if the login is open or has known/default credentials, it may give direct shell/flash access. Decided to prioritize the flash dump first since credentials are likely recoverable from the dump itself.
- `ltchiptool`'s `dump_words()`/`dump_bytes()` in `.venv-ltchiptool/` have a local patch (not upstream): skip any response line that doesn't parse as a hex address instead of crashing. This was a real, independent bug — leftover boot-banner text or the device's own echo of the sent command (e.g. `DW 40000038 4` echoed back) could land as the first "response" line and crash the parser. Worth upstreaming.

## Decision tree after decoding
- Protocol decoded and the module chip is OpenBeken-supported → back up the module flash (Meross firmware isn't encrypted), flash OpenBeken, and write the driver.
- Protocol decoded but the chip isn't supported → desolder the module, fit an ESP32-C3 module, and use an ESPHome custom UART component exposing a `climate` entity.
- Protocol not decodable → fall back to stock Matter control through HA's Matter integration, blocking the device's internet access at the firewall.

## Full flash dump obtained
`captures/flash_dump.bin` (gitignored, 4MB) — a clean, complete dump via `ltchiptool flash read`, confirmed `ltchiptool flash file` detects it as `Realtek AmebaZ2 Flash Image (Type.VALID)`. Took ~30 min at 115200 baud; tried bumping to 460800/921600 to speed it up, both failed differently (921600 gave garbled repeating noise — real baud mismatch; 460800 got a clean timeout waiting for the `ucfg` baud-switch command's ack) — this ROM build doesn't seem to support the baud-switch command reliably. Stuck with 115200.

### Debug console credentials (partial)
`strings`-mining the dump around the `Login:`/`Passwd:` text found the real prompt sequence is `\r\nUser:` then `\r\nPasswd:` (not `Login:`/`Password:` as assumed during the live attempt — that mismatch is likely why the earlier interactive test got no response). The string `admin` sits immediately before `\r\nUser:` in the binary, a strong candidate for the hardcoded default username. No adjacent password string found yet — might be derived (e.g. from MAC/serial) rather than a plain compiled-in literal; would need disassembly around the `admin` string's cross-reference to confirm. Untried: actually logging in with `admin` against the corrected `User:`/`Passwd:` prompts.

Also found in the same binary region: a large CLI command table (`hw`, `fw`, `network info`, `flash operation`, `matter data`, `upg_mcu`, `e2p` (looks like EEPROM/config read-write), `crash`, `nvdm iterm clear`, `backup`, and more) — this is a substantial debug shell, worth getting into if the login works.

Also found an embedded HTTP config server page (SSID/password/UUID/MAC/factory-mode form, firmware upload field named `meross_mt7682_image`) — the MT7682 reference in the upload field name is likely vestigial/shared code from an older hardware revision, not evidence this unit uses that chip (chip is confirmed RTL8720CM from the boot banner).

## OpenBeken flashing plan
Found a close parallel project — [ardamaks/wbr3-flash](https://github.com/ardamaks/wbr3-flash), OpenBeken on a Tuya RTL8720CF floor-heating thermostat. Confirms our protocol decode independently: **TuyaMCU v3 at 9600 baud on UART0**, matching our captured `ver=03` frames exactly. Their example dpID mapping (1=heating on/off, 16=target temp x10, 24=room temp x10) is a good starting reference for mapping our own captured dp_ids, though needs verifying against our own device's actual behavior, not assumed from a different product.

Key difference from that project: their WBR3 is RTL8720CF with 2MB flash; ours is confirmed RTL8720CM with **4MB** flash (from the dump size). Board profile: `generic-rtl8720cm-4mb-1712k` (LibreTiny). Partition layout (Tuya default, matches our dual-firmware boot banner showing `curr_fw_idx: 2`):
- Boot: 0x004000 (32 KiB)
- OTA1: 0x010000 (1.7 MiB)
- OTA2: 0x1BC000 (1.7 MiB)
- LibreTiny KVS (settings storage): 0x3F8000 (32 KiB)

Downloaded prebuilt firmware: [openbeken/OpenRTL87X0C_1.18.318.bin](openbeken/OpenRTL87X0C_1.18.318.bin) (OpenBeken 1.18.318, latest as of 2026-10-24), confirmed valid via `ltchiptool flash file`. Flash command (same pattern as the read we already proved works):
```
.venv-ltchiptool/bin/ltchiptool flash write -d /dev/ttyUSB0 openbeken/OpenRTL87X0C_1.18.318.bin
```

**Security note**: `captures/flash_dump.bin` (our stock backup) contains Wi-Fi credentials and Tuya keys per the wbr3-flash project's warning. It's gitignored and must never be committed or shared.

**Write risk**: a power loss during the ~1 second bootloader-write window can brick the chip, requiring UART recovery (per wbr3-flash's notes). Make sure the supply is stable before writing. We have a full stock backup, so worst case is a recovery flash, not a dead board.

**Done**: `flash write` succeeded (2026-10-24). First attempt failed mid-transfer at XMODEM block 48 — the chip reset unexpectedly, leaking its own boot banner text into the XMODEM channel instead of ACK bytes (classic symptom, matches the wbr3-flash project's warning about power-loss-during-write). Immediate retry succeeded cleanly in 92.8s, full hash verification passed (`hash check: start=0X0, count=0XCC444` = 836,676 bytes = exact file size), exit code 0.

Confirmed booting on real hardware — full clean boot log:
```
Initializing WIFI ...OpenRTL87X0C, version 1.18.318
...
Info:MAIN:Using SSID []
Info:MAIN:Using Pass []
...
Info:MQTT:MQTT_RegisterCallback called for bT homeassistant/ subT homeassistant/+
...
Info:MAIN:Boot complete
```
No Wi-Fi configured yet, so it correctly fell back to its setup AP (visible and confirmed from a phone). `lfs is absent` / `failed to get file autoexec.bat` — expected on first boot, no config filesystem yet.

### Remaining steps
1. ~~Configure Wi-Fi via the setup AP~~ — done (2026-10-24). Device is on the local network at **192.168.30.186**, hostname `OpenRTL87X0C_AE273F5A`, short name `rtl87x0CAE273F5A`.
2. ~~Map real dp_id meanings before writing the TuyaMCU config.~~ **DONE — see [decoded/mts300ma_dp_map.md](decoded/mts300ma_dp_map.md).** The complete, authoritative dp_id→name→type→range table was extracted directly from the stock firmware dump (DP definition table at flash offset `0x14e168`), using Meross's own symbol names, and cross-checked against live captured values (every `value` DP is the quantity ×10). No touchscreen-guessing needed. Key: 0x01 mode, 0x02 coolTemp, 0x03 heatTemp, 0x07 currentTemp, 0x08 currentHumi, 0x0B-0x0E relay states, 0x19 tempUnit (1=°F here), 0x04/0x1C fan. Still worth a quick live correlation of the `mode` enum (0x01) values (off/heat/cool/auto) against the touchscreen.
3. Write the `autoexec.bat` config (via the HTTP API, see below) mapping confirmed dp_ids to OpenBeken channels: `startDriver TuyaMCU`, `tuyaMcu_setBaudRate 9600` (our device, not the 115200 seen in generic examples), `setChannelType`/`linkTuyaMCUOutputToChannel` per confirmed dp_id.
4. No dedicated "climate" entity pattern found in OpenBeken's docs — likely need individual number/select/sensor channels exposed to Home Assistant (MQTT discovery already registers `homeassistant/+` topics) combined with an HA-side generic thermostat helper, or check if newer OBK versions added native climate support. Needs research once dp_ids are confirmed.
5. ~~Clear the "St" setup state.~~ **SOLVED (2026-10-24).** "St" = `systemSetOk` (dp 0x64) == 0. Writing `systemSetOk=1` from OBK over the MCU protocol clears it — confirmed on hardware, the display left "St" and the MCU stopped its continuous full-table setup broadcast and began behaving as a normal running thermostat. Command used: `tuyaMcu_sendState 100 1 1`. The unconfigured baseline accepted the write with the default config block as-is (systemClass=0, coolLvNum=1, heatLvNum=1, fanLvNum=3, obSet=0), so for the bench/barn setup no custom wiring block was needed — just the commit flag. **This proves the full goal: new-in-box → OBK flashed → configured thermostat, entirely from OBK, no Meross app.** For installs needing specific HVAC config (multi-stage, heat pump/OB, aux), write the relevant system DPs *before* 0x64; defaults suit a simple single-stage conventional system. Reversible via `systemReset` (dp 0x65).
6. ~~Test actual thermostat control end-to-end.~~ **DONE.** OBK↔MCU is fully bidirectional: writing channel 3 (heatTemp) to 680 was accepted by the MCU and echoed back; mode writes engage the correct relays (mode=1 heat → heatState/fanState on). Setpoints persist in MCU NVDM across reboots.
7. ~~Persist config.~~ **DONE.** `autoexec.bat` (startup command) saved and verified to survive an OBK restart — driver auto-loads, channels auto-populate, MQTT reconnects, all unattended.

### Device-side: COMPLETE
Dual-setpoint thermostat (heat dp3 + cool dp2, band-controlled in auto). Fully local, self-sufficient, no Meross app/cloud. Persisted `autoexec.bat`:
```
startDriver TuyaMCU
tuyaMcu_setBaudRate 9600
tuyaMcu_defWiFiState 4
linkTuyaMCUOutputToChannel 1 4 1     # mode   enum  0=off 1=heat 2=cool 3=auto
linkTuyaMCUOutputToChannel 2 2 2     # coolTemp  val /10 (F)
linkTuyaMCUOutputToChannel 3 2 3     # heatTemp  val /10 (F)
linkTuyaMCUOutputToChannel 7 2 7     # currentTemp val /10 (F) [read]
linkTuyaMCUOutputToChannel 8 2 8     # currentHumi val /10 (%) [read]
linkTuyaMCUOutputToChannel 11 4 11   # coolState enum [read]
linkTuyaMCUOutputToChannel 12 4 12   # heatState enum [read]
linkTuyaMCUOutputToChannel 13 4 13   # fanState  enum [read]
linkTuyaMCUOutputToChannel 16 2 16   # insideTempCalib val/10 F, signed +-4.5 (= app's temp calibration)
linkTuyaMCUOutputToChannel 17 2 17   # insideHumiCalib val/10 %, signed
```
Temp/humidity calibration (the app's calibration feature) = dp 0x10/0x11, writable signed offsets (±4.5°, confirmed accepting negative values).
MQTT: broker 192.168.1.25:1883, base/client topic `rtl87x0CAE273F5A`, group `rtl87x0c`, user `homeassistant`. Channel state on `rtl87x0CAE273F5A/<ch>/get`, command on `rtl87x0CAE273F5A/<ch>/set`. Device name set to "ShopThermostat". Device IP 192.168.30.186.

### Home Assistant climate entity — two ready options in [homeassistant/](homeassistant/)
Dual-setpoint → HA `heat_cool` with temp_low=heat(dp3)/temp_high=cool(dp2), ÷10 scaling in templates. OBK's built-in auto-discovery only makes simple per-channel entities, NOT a unified climate, so use one of:
- [homeassistant/climate.yaml](homeassistant/climate.yaml) — paste into `configuration.yaml` under `mqtt:`, restart HA.
- [homeassistant/mqtt_discovery_climate.md](homeassistant/mqtt_discovery_climate.md) — publish one retained discovery message (via HA Developer Tools → `mqtt.publish`); HA auto-creates `climate.shop_thermostat`, no YAML/restart. (Preferred — user asked for discovery.)

Then layer Nest-like features (Scheduler HACS, presence/home-away automations, or Versatile Thermostat `over_climate` wrapping this entity). Leave the device's own schedule (dp5) off so HA is the single source of truth.

### Driving OpenBeken over HTTP (no GUI needed)
Confirmed OpenBeken exposes everything needed via plain HTTP, so this can be scripted/driven by Claude directly:
- `GET http://192.168.30.186/cmd_tool?cmd=<command>` — run any console command (form param `cmd`)
- `GET http://192.168.30.186/startup_command?startup_cmd=1&data=<script>` — set the `autoexec.bat`-equivalent startup script (form param `data`, textarea)
- `GET http://192.168.30.186/index?state=1` — live state poll (used by the web UI's auto-refresh)
- `GET http://192.168.30.186/cfg` — lists all config sub-pages (`cfg_pins`, `cfg_wifi`, `cfg_mqtt`, `ha_cfg`, `ota`, etc.)

## Open questions
- Header pin 2 voltage
- ~~Which module pads carry the UART to the MCU; baud and framing~~ — confirmed: module pins 15/16 (URX0/UTX0), TuyaMCU framing, 9600 8N1
- ~~Wi-Fi module chipset~~ — confirmed Realtek RTL8720CM via boot banner (FCC filing read it as RTL8720F, close but imprecise)
- ~~Does grounding pin 3 (EN) actually reset the chip~~ — confirmed yes, reliably reproduces the ROM boot banner
- ~~What each dp_id means~~ — SOLVED, full map in [decoded/mts300ma_dp_map.md](decoded/mts300ma_dp_map.md) from firmware symbols + live cross-check. (Only the `mode` enum value→label mapping still wants a quick live confirm.)
- The system-config DP values matching the user's actual HVAC wiring (to clear "St" — see Remaining steps #5)
- Whether `admin` is really the debug console username, and what the password is
- What drives the SSRs (MCU or module)
- What the yellow component near the top edge is
