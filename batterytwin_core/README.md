# BatteryTwin Core

BatteryTwin Core is the Python-based battery simulation component of the BatteryTwin Simulator.

It provides modular models for:

- State of charge (SoC)
- Open-circuit voltage (OCV)
- Internal resistance
- Battery voltage
- Current and power
- Energy consumption
- Thermal behavior
- Battery aging
- Protection and current limits
- RC transient behavior
- Battery configuration loading

## Configuration

The example battery configuration is:

`config/batteries/spektrum_6s_5000mah_100c.yaml`

It describes a 6S 5000 mAh LiPo battery and is used by the included tests and ROS 2 integration.

## Testing

From the repository root:

`python3 batterytwin_core/tests/run_all.py`

## ROS 2 Integration

The package includes:

`scripts/battery_physics_node.py`

This node integrates the battery simulation with ROS 2.

## License

This project is released under the MIT License.

See the repository-level `LICENSE.md` for the complete license text.
