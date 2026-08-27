# lux-mon Home Assistant entity contract

This document maps lux-mon API register/setting names to Home Assistant entity metadata. It is the source of truth for the `custom_components/luxmon` integration.

## Security note

No inverter serials or datalog serials appear in this repo. Device identifiers inside Home Assistant are derived from the user-supplied host and an arbitrary `device_id` only.

## Sensor mapping

Keys come from lux-mon `GET /api/status` under `registers`. The integration creates one `sensor` per key. Static metadata is in `custom_components/luxmon/const.py:SENSOR_METADATA`; keys not listed there fall back to a plain sensor with the unit returned by lux-mon.

| lux-mon key | Name | device_class | state_class | unit | enabled default |
|---|---|---|---|---|---|
| `soc` | Battery SOC | `battery` | `measurement` | `%` | yes |
| `soh` | Battery SOH | — | `measurement` | `%` | yes |
| `battery_voltage` | Battery voltage | `voltage` | `measurement` | `V` | yes |
| `battery_current` | Battery current | `current` | `measurement` | `A` | yes |
| `pv1_voltage` | PV1 voltage | `voltage` | `measurement` | `V` | yes |
| `pv2_voltage` | PV2 voltage | `voltage` | `measurement` | `V` | yes |
| `pv3_voltage` | PV3 voltage | `voltage` | `measurement` | `V` | yes |
| `pv1_power` | PV1 power | `power` | `measurement` | `W` | yes |
| `pv2_power` | PV2 power | `power` | `measurement` | `W` | yes |
| `pv3_power` | PV3 power | `power` | `measurement` | `W` | yes |
| `pv_power_total` | PV power total | `power` | `measurement` | `W` | yes |
| `pv_energy_total` | PV energy total | `energy` | `total_increasing` | `kWh` | yes |
| `grid_import_power` | Grid import power | `power` | `measurement` | `W` | yes |
| `grid_export_power` | Grid export power | `power` | `measurement` | `W` | yes |
| `grid_import_energy_total` | Grid import energy total | `energy` | `total_increasing` | `kWh` | yes |
| `grid_export_energy_total` | Grid export energy total | `energy` | `total_increasing` | `kWh` | yes |
| `battery_in_energy_total` | Battery charge energy total | `energy` | `total_increasing` | `kWh` | yes |
| `battery_out_energy_total` | Battery discharge energy total | `energy` | `total_increasing` | `kWh` | yes |
| `eps_power` | EPS power | `power` | `measurement` | `W` | yes |
| `grid_voltage_r` | Grid voltage R | `voltage` | `measurement` | `V` | yes |
| `grid_frequency` | Grid frequency | `frequency` | `measurement` | `Hz` | yes |
| `temp_inverter` | Inverter temperature | `temperature` | `measurement` | `°C` | yes |
| `temp_battery` | Battery temperature | `temperature` | `measurement` | `°C` | yes |
| `temp_radiator_1` | Radiator 1 temperature | `temperature` | `measurement` | `°C` | no |
| `temp_radiator_2` | Radiator 2 temperature | `temperature` | `measurement` | `°C` | no |
| `fault` | Fault code | — | — | — | no |

## Control entity mapping

Control entities are discovered from lux-mon `GET /api/settings/controllable`. The integration uses the `type`, `min`, `max`, `step`, `options`, and `unit` fields returned by that endpoint.

| lux-mon type | HA platform | value write path |
|---|---|---|
| `number` | `number` | `PUT /api/settings/{name}` |
| `select` | `select` | `PUT /api/settings/{name}` |
| `checkbox` / `boolean` | `switch` | `PUT /api/settings/{name}` |

## Alert / binary sensor mapping

Binary sensors come from lux-mon `GET /api/alerts/live`. They use `device_class: problem`.

| lux-mon alert key | Name |
|---|---|
| `battery_soc_low` | Battery SOC low |
| `battery_soc_critical` | Battery SOC critical |
| `battery_temp_high` | Battery temperature high |
| `inverter_temp_high` | Inverter temperature high |
| `grid_loss` | Grid loss |
| `fault_active` | Fault active |

## Button mapping

Buttons call lux-mon quick-charge endpoints.

| lux-mon button key | Endpoint |
|---|---|
| `quick_charge_start` | `POST /api/quick-charge/start` |
| `quick_charge_stop` | `POST /api/quick-charge/stop` |

## Diagnostics

Download diagnostics from the device page to see:
- Configured host/port/scan interval.
- Last update success status.
- Snapshot ID and timestamp.
- Count of registers and first 50 register keys.

No serials, IPs, or tokens are included.
