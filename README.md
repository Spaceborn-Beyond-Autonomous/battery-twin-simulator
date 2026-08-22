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
```

```
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
```

## Running for the first time
chmod +x run_dashboard.sh

## Execute Command
./run_dashboard.sh

---

## 🚀 ROS 2 & Gazebo Integration (Task C - BTS-C)

This section covers running the full integrated system: **Gazebo Simulation + Physics Engine + Dashboard**, all connected via ROS 2 topics.

### Prerequisites
- Ubuntu 24.04 (or WSL2)
- ROS 2 Jazzy installed (`/opt/ros/jazzy`)
- Gazebo Harmonic (`gz-sim8`)
- Node.js & npm (for the React frontend)

### 1. Build the ROS 2 Workspace
```bash
cd batterytwin_workspace
source /opt/ros/jazzy/setup.bash
colcon build
source install/setup.bash
```

### 2. Setup Dashboard Virtual Environment
The dashboard backend needs `rclpy` (ROS 2 Python). You **must** use `--system-site-packages` so it can access ROS 2 packages.

```bash
cd batterytwin_workspace/src/dashboard/backend
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install -r ../requirements.txt
pip install "uvicorn[standard]"
```

### 3. Running the Full System
Open **4 separate terminals**:

**Terminal 1 — Gazebo Simulation**
```bash
cd batterytwin_workspace
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch batterytwin_simulator simulator.launch.py
```

**Terminal 2 — Physics Engine Node**
```bash
cd batterytwin_workspace
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run batterytwin_core battery_physics_node.py
```

**Terminal 3 — Dashboard Backend (FastAPI)**
```bash
cd batterytwin_workspace
source /opt/ros/jazzy/setup.bash
source install/setup.bash
cd src/dashboard/backend
source venv/bin/activate
python3 -m uvicorn main:app --reload
```
> You should see: `ROS 2 Integration Started Successfully!`

**Terminal 4 — Dashboard Frontend (React)**
```bash
cd batterytwin_workspace/src/dashboard/frontend
npm install
npm run dev
```

Open your browser at **http://localhost:5173** to see the live dashboard.

### 4. Simulating Dynamic Flight Maneuvers
To manually change the battery current draw (simulating drone throttle changes), open a **5th terminal**:

```bash
cd batterytwin_workspace
source /opt/ros/jazzy/setup.bash

# Full throttle — 50 Amps (aggressive maneuvers)
ros2 topic pub /battery/current_draw std_msgs/msg/Float32 "{data: 50.0}" -1

# Hovering — 5 Amps (low throttle)
ros2 topic pub /battery/current_draw std_msgs/msg/Float32 "{data: 5.0}" -1

# Idle — 2 Amps (motors off, electronics only)
ros2 topic pub /battery/current_draw std_msgs/msg/Float32 "{data: 2.0}" -1
```

The dashboard will react in **real-time** — voltage drops, temperature rises, and SoC decreases dynamically based on your input.

### ROS 2 Topic Architecture
| Topic | Type | Description |
|---|---|---|
| `/battery/current_draw` | `std_msgs/Float32` | Current draw input (Amps) |
| `/battery/state` | `batterytwin_msgs/BatteryTwinState` | Full battery telemetry output |

### ⚠️ Important Notes
- **Do NOT commit** `venv/`, `node_modules/`, or `__pycache__/` folders.
- On WSL2/Ubuntu 24.04, always use `--system-site-packages` when creating the venv, otherwise `rclpy` will not be found.
- Always `source /opt/ros/jazzy/setup.bash` and `source install/setup.bash` before running any ROS 2 command.
