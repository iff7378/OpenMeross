# ltchiptool quick reference (RTL8720CF / AmebaZ2)

Installed in a local venv: `.venv-ltchiptool/` (gitignored). All commands below assume you're in the repo root.

## Setup reminder: entering download mode
1. GND common between CH340 and board.
2. CH340 TX -> module pin 2 (LOG_RX). CH340 RX -> module pin 1 (LOG_TX).
3. Jumper pin 10 (GPIO0) to 3.3V (pin 8) -- **pull to 3.3V, not GND** (opposite of ESP chips).
4. Keep pin 15 (URX0) disconnected / not grounded while flashing.
5. With GPIO0 held at 3.3V, apply power OR briefly ground pin 3 (EN) to reset.
6. Success looks like "Open Download Mode on UART" -- if the tool times out instead, the chip is booting normally instead of into the ROM download handler (see open question in the handoff doc about whether EN actually resets the chip).

## Check port permissions
If you get a permission error on `/dev/ttyUSB0`:
```bash
sudo chmod 666 /dev/ttyUSB0
```

## Get chip info (sync test -- do this first)
```bash
.venv-ltchiptool/bin/ltchiptool -v flash info realtek-ambz2 -d /dev/ttyUSB0 -t 30
```
Start this command *before* triggering the reset/power-on, so the tool is already listening when the chip comes out of reset.

## Dump the entire flash
```bash
.venv-ltchiptool/bin/ltchiptool flash read realtek-ambz2 captures/flash_dump.bin -d /dev/ttyUSB0
```
Same timing rule: have the chip already in download mode (or start the command, then reset) before this begins.

## Dump a specific region
```bash
.venv-ltchiptool/bin/ltchiptool flash read realtek-ambz2 captures/flash_partial.bin -d /dev/ttyUSB0 -s 0x0 -l 0x100000
```
`-s` = start offset (hex/dec), `-l` = length in bytes.

## After a successful dump
```bash
.venv-ltchiptool/bin/ltchiptool flash file captures/flash_dump.bin
```
Identifies partitions/file type in the dump. Useful before trying `flash split`.

## Notes
- Baud is auto-chosen by the tool; no need to specify unless it has trouble.
- `-v` adds verbose/debug output, useful for diagnosing sync failures.
- A sagging 3.3V rail is a common cause of failed dumps -- the current-limited bench supply (100-200mA, set for safe passive sniffing) may need to be raised for flashing.
