# HA MQTT Discovery — auto-create the climate entity (no YAML edit)

OpenBeken's built-in auto-discovery only makes simple per-channel entities, not a
unified dual-setpoint climate. To have **HA create the climate entity via discovery**,
publish the single *retained* discovery message below once. HA picks it up
immediately and creates `climate.shop_thermostat` — no `configuration.yaml`, no restart.

## Easiest: HA Developer Tools → Actions → `mqtt.publish`

Paste this into the YAML editor of the action and Run it once:

The `{% raw %}...{% endraw %}` wrapper is REQUIRED — without it, HA tries to render
the `{{ ... }}` discovery templates at publish time and fails with
`UndefinedError: 'value' is undefined`. The raw block makes HA publish the JSON
(templates included) verbatim, which is what discovery needs.

```yaml
action: mqtt.publish
data:
  topic: homeassistant/climate/shop_thermostat/config
  retain: true
  payload: >-
    {% raw %}{
      "name": "Shop Thermostat",
      "unique_id": "mts300ma_shop_thermostat",
      "device": {"identifiers": ["mts300ma_shop"], "name": "Shop Thermostat",
                 "manufacturer": "Meross (OpenBeken)", "model": "MTS300MA / RTL8720CM"},
      "temperature_unit": "F",
      "min_temp": 45, "max_temp": 95, "temp_step": 1,
      "modes": ["off", "heat", "cool", "heat_cool"],
      "mode_stat_t": "rtl87x0CAE273F5A/1/get",
      "mode_stat_tpl": "{{ {0:'off',1:'heat',2:'cool',3:'heat_cool'}.get(value|int,'off') }}",
      "mode_cmd_t": "rtl87x0CAE273F5A/1/set",
      "mode_cmd_tpl": "{{ {'off':0,'heat':1,'cool':2,'heat_cool':3}[value] }}",
      "curr_temp_t": "rtl87x0CAE273F5A/7/get",
      "curr_temp_tpl": "{{ value|float/10 }}",
      "current_humidity_topic": "rtl87x0CAE273F5A/8/get",
      "current_humidity_template": "{{ value|float/10 }}",
      "temp_lo_stat_t": "rtl87x0CAE273F5A/3/get",
      "temp_lo_stat_tpl": "{{ value|float/10 }}",
      "temp_lo_cmd_t": "rtl87x0CAE273F5A/3/set",
      "temp_lo_cmd_tpl": "{{ (value|float*10)|int }}",
      "temp_hi_stat_t": "rtl87x0CAE273F5A/2/get",
      "temp_hi_stat_tpl": "{{ value|float/10 }}",
      "temp_hi_cmd_t": "rtl87x0CAE273F5A/2/set",
      "temp_hi_cmd_tpl": "{{ (value|float*10)|int }}"
    }{% endraw %}
```

To remove/undo: publish an empty retained payload to the same topic
(`topic: homeassistant/climate/shop_thermostat/config`, `payload: ""`, `retain: true`).

## Alternative: mosquitto_pub from any machine with broker creds
```bash
mosquitto_pub -h 192.168.1.25 -p 1883 -u homeassistant -P '<password>' -r \
  -t homeassistant/climate/shop_thermostat/config \
  -f homeassistant/discovery_climate_payload.json
```

## Notes
- `temperature_low/high` map to heat (dp3) / cool (dp2) — HA shows a two-handle
  band in heat_cool mode, which matches how the MTS300 actually works.
- Scaling ÷10 (device sends tenths of °F) is done in the templates.
- For the simpler single-entity `configuration.yaml` version, see `climate.yaml`.
- This supersedes nothing on the device; it's purely the HA side.
