# lux-mon Home Assistant integration

Native Home Assistant integration for [lux-mon](https://github.com/jmewing/lux-mon).

This integration connects to the lux-mon REST API and exposes:

- Live inverter sensors (SOC, voltage, current, power, energy, temperatures, etc.).
- Energy Dashboard sensors (`pv_energy_total`, `grid_import_energy_total`, etc.).
- Controllable settings as `number`, `select`, and `switch` entities.
- Alert states as `binary_sensor` entities.
- Quick charge actions via `button` entities.
- Service calls: `luxmon.quick_charge_start`, `luxmon.quick_charge_stop`, `luxmon.set_setting`, and `luxmon.load_automation_rules`.

## Installation

### HACS (recommended)

1. Add this repository as a custom repository in HACS (category: **Integration**).
2. Install the **lux-mon** integration.
3. Restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration** and search for **lux-mon**.

### Manual

1. Download the latest `luxmon.zip` release asset.
2. Extract it into `<config>/custom_components/luxmon/`.
3. Restart Home Assistant.

## Configuration

The integration only needs the host and port of the lux-mon API server. The default host is `192.168.1.100` and port is `8080`.

After setup, you can change the polling interval, device ID, and inverter model from the integration options.

## Services

The following services are registered under the `luxmon` domain:

- `luxmon.quick_charge_start` — start a timed AC quick charge.
- `luxmon.quick_charge_stop` — stop an active quick charge and restore the prior current.
- `luxmon.set_setting` — write any lux-mon runtime setting by name.
- `luxmon.load_automation_rules` — replace the full automation rule set.

See `custom_components/luxmon/services.yaml` for field definitions.

## Security note

Inverter serial numbers and datalog serial numbers are **never** stored in this integration. They remain in your lux-mon `.env` file or settings database. The integration uses a user-supplied host and an arbitrary device ID slug only.

## Development

- Run `scripts/release.sh` to build `custom_components/luxmon.zip`.
- Validate with `hassfest` from the Home Assistant core checkout.

## License

MIT
