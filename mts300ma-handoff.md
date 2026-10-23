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

## Decision tree after decoding
- Protocol decoded and the module chip is OpenBeken-supported → back up the module flash (Meross firmware isn't encrypted), flash OpenBeken, and write the driver.
- Protocol decoded but the chip isn't supported → desolder the module, fit an ESP32-C3 module, and use an ESPHome custom UART component exposing a `climate` entity.
- Protocol not decodable → fall back to stock Matter control through HA's Matter integration, blocking the device's internet access at the firewall.

## Open questions
- Header pin 2 voltage
- ~~Which module pads carry the UART to the MCU; baud and framing~~ — confirmed: module pins 15/16 (URX0/UTX0), TuyaMCU framing, 9600 8N1
- ~~Wi-Fi module chipset~~ — confirmed Realtek RTL8720F via FCC filing
- What each dp_id means (temperature scale/units, mode encoding, etc.) — in progress, see Protocol section
- What drives the SSRs (MCU or module)
- What the yellow component near the top edge is
