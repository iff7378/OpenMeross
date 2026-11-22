#!/usr/bin/env python3
"""Reproduce the MTS300MA -> OpenBeken -> Home Assistant setup.

Everything OpenBeken can do itself (device config + the 3 sensor discovery
messages) is pushed over OBK's HTTP command API -- no broker creds needed.
The climate entity's discovery JSON is too large for OBK's ~512-byte command
buffer, so this script only PRINTS it; publish it once as a retained message
(HA Developer Tools -> Actions -> mqtt.publish, or mosquitto_pub). Once
retained on the broker it persists across reboots / HA restarts.

Usage:
  python3 homeassistant/setup_ha.py [device_ip]      # default 192.168.30.186
  python3 homeassistant/setup_ha.py --reconfig       # also re-apply heat-only HVAC config
"""
import sys, json, urllib.request, urllib.parse

IP = next((a for a in sys.argv[1:] if not a.startswith("-")), "192.168.30.186")
RECONFIG = "--reconfig" in sys.argv
BASE = "rtl87x0CAE273F5A"                 # OBK MQTT client/base topic
DEV_ID = "ShopThermostat"                  # OBK device identifier (merges climate+sensors+diag)

def obk(cmd):
    url = f"http://{IP}/cmd_tool?cmd=" + urllib.parse.quote(cmd)
    urllib.request.urlopen(url, timeout=6).read()

# --- optional: re-apply heat-only HVAC system config (single-stage heat, G fan, no cooling) ---
if RECONFIG:
    for c in ["tuyaMcu_sendState 91 4 0",   # coolLvNum = 0 (no cooling)
              "tuyaMcu_sendState 92 4 1",    # heatLvNum = 1 (single-stage W)
              "tuyaMcu_sendState 93 4 1",    # fanLvNum  = 1 (G fan)
              "tuyaMcu_sendState 100 1 1"]:  # systemSetOk commit
        obk(c); print("reconfig:", c)

# --- sensors: OBK self-publishes these (compact, space-free, retained) ---
def sensor(obj, name, ch, unit, dev_cla):
    topic = f"homeassistant/sensor/shoptherm_{obj}/config"
    p = ('{"name":"%s","uniq_id":"shoptherm_%s","stat_t":"%s/%d/get",'
         '"val_tpl":"{{value|float/10}}","unit_of_meas":"%s","dev_cla":"%s",'
         '"stat_cla":"measurement","dev":{"ids":["%s"]}}'
         % (name, obj, BASE, ch, unit, dev_cla, DEV_ID))
    assert " " not in p, "payload must be space-free for OBK publish"
    cmd = f"publish {topic} {p} 1"
    assert len(cmd) < 505, f"too long for OBK buffer: {len(cmd)}"
    obk(cmd); print(f"sensor published via OBK: {obj} ({len(p)}B)")

sensor("curtemp",  "Shop_Temperature",   7, "°F", "temperature")
sensor("humidity", "Shop_Humidity",      8, "%",       "humidity")
sensor("setpoint", "Shop_Heat_Setpoint", 3, "°F", "temperature")

# --- climate: too big for OBK; publish this retained message ONCE yourself ---
climate = {
    "name": "Shop Thermostat", "unique_id": "mts300ma_shop_thermostat",
    "device": {"identifiers": [DEV_ID], "name": "Shop Thermostat",
               "manufacturer": "Meross (OpenBeken)", "model": "MTS300MA / RTL8720CM"},
    "temperature_unit": "F", "min_temp": 45, "max_temp": 95, "temp_step": 1,
    "modes": ["off", "heat"],
    "mode_state_topic": f"{BASE}/1/get", "mode_state_template": "{{ 'heat' if value|int>=1 else 'off' }}",
    "mode_command_topic": f"{BASE}/1/set", "mode_command_template": "{{ {'off':0,'heat':1}[value] }}",
    "current_temperature_topic": f"{BASE}/7/get", "current_temperature_template": "{{ value|float/10 }}",
    "current_humidity_topic": f"{BASE}/8/get", "current_humidity_template": "{{ value|float/10 }}",
    "temperature_state_topic": f"{BASE}/3/get", "temperature_state_template": "{{ value|float/10 }}",
    "temperature_command_topic": f"{BASE}/3/set", "temperature_command_template": "{{ (value|float*10)|int }}",
    "action_topic": f"{BASE}/12/get", "action_template": "{{ 'heating' if value|int==1 else 'idle' }}",
}
print("\n=== CLIMATE: publish this retained to homeassistant/climate/shop_thermostat/config ===")
print("HA Developer Tools -> Actions -> mqtt.publish:")
print("  topic: homeassistant/climate/shop_thermostat/config")
print("  retain: true")
print("  payload: |")
print("    " + json.dumps(climate))
