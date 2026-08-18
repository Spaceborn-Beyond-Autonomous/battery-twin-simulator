# Battery Twin Simulator

A modular battery digital-twin simulator designed for autonomous systems, robotics, UAVs, and simulation environments.

The project provides a physics-inspired battery simulation core that models electrical, thermal, energy, aging, and protection behavior. The architecture is designed to support integration with ROS 2, Gazebo, telemetry systems, PX4/ArduPilot, and modern web dashboards.

---

## Project Status

**Current status:** BatteryTwin Core & Real-time Web Dashboard implemented and tested.

### Core test status

```text
Passed: 9
Failed: 0
Total : 9

ALL BATTERYTWIN CORE TESTS PASSED

battery-twin-simulator/
│
├── batterytwin/
│   ├── __init__.py
│   ├── aging_model.py
│   ├── battery_config.py
│   ├── battery_config_loader.py
│   ├── battery_model.py
│   ├── battery_state.py
│   ├── energy_model.py
│   ├── ocv_model.py
│   ├── power_model.py
│   ├── protection_model.py
│   ├── rc_model.py
│   ├── resistance_model.py
│   ├── soc_model.py
│   ├── thermal_model.py
│   └── voltage_model.py
│
├── dashboard/
│   ├── backend/
│   │   └── main.py
│   └── frontend/
│       ├── src/
│       │   └── App.tsx
│       └── package.json
│
├── config/
│   └── batteries/
│       └── spektrum_6s_5000mah_100c.yaml
│
├── tests/
│   ├── run_all.py
│   ...
│
├── requirements.txt
├── run_dashboard.sh
└── README.md


## Running for the first time
chmod +x run_dashboard.sh

## Execute Command
./run_dashboard.sh
