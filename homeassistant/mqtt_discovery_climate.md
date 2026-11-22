# HA integration via MQTT discovery (current setup)

Reproduce with `python3 homeassistant/setup_ha.py` (device-side + sensors, no broker
creds) then publish the climate JSON it prints, once, retained.

## What exists in HA (one unified "Shop Thermostat" device)
- **Climate** `climate.shop_thermostat` — HEAT-ONLY (modes off/heat, single setpoint =
  heatTemp dp3, current temp dp7, humidity dp8, action from heatState dp12).
- **Sensors** (plottable history): `Shop_Temperature` (dp7), `Shop_Humidity` (dp8),
  `Shop_Heat_Setpoint` (dp3).
- **Diagnostics** (IP/RSSI/SSID/build/uptime) — from OBK's own built-in auto-discovery.
All grouped under device identifier `ShopThermostat`.

## How each piece is published
- **Sensors** are published by **OBK itself** over its HTTP command API (`publish <topic>
  <payload> 1`, retained). OBK can't auto-make a climate, but it can publish arbitrary
  retained discovery for the sensors. `setup_ha.py` does this.
- **Climate** is published **once** as a retained message by you (it then persists across
  reboots / HA restarts). It is NOT published by OBK because the JSON exceeds OBK's
  command buffer (see Gotchas). `setup_ha.py` prints the exact HA `mqtt.publish` payload.

## Gotchas discovered (important)
- **OBK `publish` has a ~512-byte command-buffer limit.** Payloads up to ~444 land; ~544+
  are silently dropped. Sensors fit; a full climate does not. Keep OBK-published payloads
  compact and **space-free** (OBK splits the command on spaces — a space in any value,
  even the `name`, truncates the payload).
- **OBK must have Flag 19** ("[MQTT] Always publish channels used by TuyaMCU") or channel
  values never reach MQTT and everything reads "Unknown". Also Flags 2/7/10. All are in
  the device autoexec.
- **HA rejects temperature sensors with unit `"F"`** — it requires `"°F"` (with the degree
  sign). Plain `F`/`C` is silently discarded for `device_class: temperature`.

## Device is configured HEAT-ONLY
The MCU system config was corrected this session from the OBK-bringup defaults
(coolLvNum=1) to the real setup: `coolLvNum=0, heatLvNum=1, fanLvNum=1`, re-committed with
`systemSetOk`. The physical display now cycles only Heat/Off. See
`decoded/mts300ma_dp_map.md` for the exact DP writes. Re-run with `setup_ha.py --reconfig`.

## To remove / re-do
Publish an empty retained payload to a config topic to delete that entity. To change the
climate, re-publish its topic (`homeassistant/climate/shop_thermostat/config`) retained.
