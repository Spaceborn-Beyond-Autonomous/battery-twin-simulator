# BatteryTwin Simulator

BatteryTwin Simulator is a modular battery and powertrain simulation project with Python models, ROS 2 integration, Gazebo simulation support, MAVLink translation, and a web dashboard.

## Features

- Battery state-of-charge modeling
- Open-circuit voltage modeling
- Internal resistance modeling
- Voltage and power estimation
- Energy consumption modeling
- Thermal modeling
- Battery aging
- Battery protection and current limits
- RC transient behavior
- Modular electric powertrain modeling
- Motor and ESC simulation
- Propeller thrust modeling
- Torque and efficiency analysis
- Flight endurance estimation
- Environmental effects
- ROS 2 integration
- Gazebo simulation plugin
- MAVLink translation
- Real-time web dashboard

## Repository Structure

```text
battery-twin-simulator-clean/
├── batterytwin_core/              # Battery physics and ROS 2 package
├── batterytwin_msgs/              # ROS 2 custom messages
├── batterytwin_simulator/         # Gazebo / ROS 2 integration
├── batterytwin_mavlink/           # MAVLink translation
├── powertrain/                    # Modular powertrain simulation
├── dashboard/                     # FastAPI + React dashboard
├── docs/                          # Technical documentation
├── requirements.txt
├── run_dashboard.sh
├── README.md
└── LICENSE.md
```

## BatteryTwin Core

The core battery models are located in `batterytwin_core/batterytwin/`.

They cover SoC, OCV, resistance, voltage, current, power, energy, thermal behavior, aging, protection, and RC dynamics.

### Battery configuration

The included example is:

`batterytwin_core/config/batteries/spektrum_6s_5000mah_100c.yaml`

It represents a 6S 5000 mAh LiPo battery.

### Testing

From the repository root:

```bash
cd batterytwin_core && python3 tests/run_all.py
```

## Powertrain

The `powertrain/` package provides modular motor, ESC, propeller, thrust, torque, efficiency, current, environmental, and endurance models.

Run its validation with:

```bash
PYTHONPATH=. python3 -m powertrain.powertrain_engine
```

The validation covers steady-state operation, hover estimation, torque margin, altitude effects, and battery state-of-charge effects.

## ROS 2 Packages

- `batterytwin_core` — battery physics and ROS 2 integration
- `batterytwin_msgs` — custom ROS 2 messages
- `batterytwin_simulator` — Gazebo and ROS 2 simulator integration
- `batterytwin_mavlink` — MAVLink translation

## Dashboard

The repository includes a FastAPI backend and React/Vite frontend for local telemetry visualization.

Start it with:

```bash
./run_dashboard.sh
```

The development frontend normally runs at `http://localhost:5173` and the backend at `http://127.0.0.1:8000`.

## Python Dependencies

```bash
python3 -m pip install -r requirements.txt
```

ROS 2 components require a compatible ROS 2 installation and their declared ROS 2 dependencies.

## ROS 2 Build

From a ROS 2 workspace:

```bash
colcon build
source install/setup.bash
```

## Validation

The repository has been validated with the BatteryTwin core test suite and the Powertrain Engine validation scenarios.

## License

This project is released under the MIT License. See `LICENSE.md` for the complete license text.

## Contributions

Contributions, bug reports, documentation improvements, tests, and simulation extensions are welcome.
