# lux-mon Home Assistant integration

Native Home Assistant integration for [lux-mon](https://github.com/jmewing/lux-mon).

This integration connects to the lux-mon REST API and exposes:

- Live inverter sensors (SOC, voltage, current, power, energy, temperatures, etc.).
- Energy Dashboard sensors (`pv_energy_total`, `grid_import_energy_total`, etc.).
- Controllable settings as `number`, `select`, and `switch` entities.
- Alert states as `binary_sensor` entities.
- Quick charge actions via `button` entities.

## Installation

### HACS (recommended)

1. Add this repository as a custom repository in HACS.
2. Install the **lux-mon** integration.
3. Restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration** and search for **lux-mon**.

### Manual

1. Download the latest `luxmon.zip` release asset.
2. Extract it into `<config>/custom_components/luxmon/`.
3. Restart Home Assistant.

## Configuration

The integration only needs the host and port of the lux-mon API server. The default host is `192.168.1.100` and port is `8080`.

After setup, you can change the polling interval and device name from the integration options.

## Security note

Inverter serial numbers and datalog serial numbers are **never** stored in this integration. They remain in your lux-mon `.env` file or settings database. The integration uses a user-supplied host and an arbitrary device ID slug only.

## Development

- Run `scripts/release.sh` to build `custom_components/luxmon.zip`.
- Validate with `hassfest` from the Home Assistant core checkout.

## License

MIT
