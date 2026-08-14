# Battery Twin Simulator

A modular battery digital-twin simulator designed for autonomous systems, robotics, UAVs, and simulation environments.

The project provides a physics-inspired battery simulation core that models electrical, thermal, energy, aging, and protection behavior. The architecture is designed to support future integration with ROS 2, Gazebo, telemetry systems, PX4/ArduPilot, and larger digital-twin platforms.

---

## Project Status

**Current status:** BatteryTwin Core implemented and tested.

### Core test status

```text
Passed: 9
Failed: 0
Total : 9

ALL BATTERYTWIN CORE TESTS PASSED

Current implementation is available on:

feature/battery-twin-core

The branch is ready for team review and integration.

Features
Electrical Models
State of Charge (SOC)
Open Circuit Voltage (OCV)
Internal resistance
RC polarization
Terminal voltage
Current limits
C-rate calculation
Power calculation
Energy consumption and remaining energy
Thermal Model

The thermal model uses a lumped thermal representation:

Q_gen  = I²R


Q_loss = h(T - T_ambient)


dT/dt = (Q_gen - Q_loss) / C_th

It models:

Battery heat generation
Heat transfer to the environment
Battery temperature
Ambient temperature
Thermal capacitance
Battery Aging

The simulator includes:

State of Health (SOH)
Effective capacity degradation
Internal resistance increase
Charge-throughput tracking
Equivalent Full Cycle (EFC) calculation

The aging model is integrated with the main battery model so that degradation affects battery capacity and resistance.

Battery Protection

The protection system monitors:

Over-voltage
Under-voltage
Over-temperature
Under-temperature
Over-current
Maximum discharge current
Maximum charge current

Protection limits are configurable.

Architecture

The current BatteryTwin Core follows a modular architecture:

                    BatteryModel
                         |
        +----------------+----------------+
        |                |                |
        v                v                v
     SOC Model        OCV Model      Resistance Model
        |                |                |
        +----------------+----------------+
                         |
                         v
                    RC Model
                         |
                         v
                  Terminal Voltage
                         |
              +----------+----------+
              |                     |
              v                     v
         Power Model          Thermal Model
              |                     |
              v                     v
        Energy Model          Temperature
                                    |
                                    v
                              Protection Model


                    Aging Model
                         |
              +----------+----------+
              |                     |
              v                     v
        Capacity Factor      Resistance Factor
Battery State

The simulator maintains a unified battery state containing:

Voltage
Current
Power
SOC
SOH
Temperature
Remaining Energy
Consumed Energy
C-rate
Simulation Time
Configuration

Battery parameters are provided through YAML configuration files.

Example battery:

Spektrum Smart LiPo 6S 5000mAh 100C

Configuration includes:

Battery chemistry
Number of series cells
Number of parallel cells
Nominal capacity
Nominal voltage
Maximum pack voltage
Continuous discharge C-rating
Maximum charge C-rating
Nominal energy
Battery mass
Initial temperature
Ambient temperature
Thermal capacity
Heat-transfer coefficient

Configuration file:

config/batteries/spektrum_6s_5000mah_100c.yaml
Project Structure
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
├── config/
│   └── batteries/
│       └── spektrum_6s_5000mah_100c.yaml
│
├── include/
│   └── batterytwin/
│       ├── battery_config.hpp
│       └── battery_state.hpp
│
├── tests/
│   ├── run_all.py
│   ├── test_aging_model.py
│   ├── test_battery_aging_integration.py
│   ├── test_battery_config_loader.py
│   ├── test_battery_model.py
│   ├── test_charging_battery.py
│   ├── test_current_limits.py
│   ├── test_energy_model.py
│   ├── test_idle_battery.py
│   ├── test_integrated_battery.py
│   ├── test_ocv_model.py
│   ├── test_power_model.py
│   ├── test_protection_model.py
│   ├── test_rc_model.py
│   ├── test_resistance_model.py
│   ├── test_soc_model.py
│   ├── test_thermal_model.py
│   └── test_voltage_model.py
│
├── CMakeLists.txt
├── package.xml
└── README.md
Running the Tests

From the project directory:

cd ~/batterytwin_ws/src/batterytwin_core

Run the complete test suite:

python3 -m tests.run_all

Expected result:

============================================================
                 TEST SUMMARY
============================================================
Passed: 9
Failed: 0
Total : 9
============================================================
ALL BATTERYTWIN CORE TESTS PASSED
============================================================
Running Individual Tests

Battery model:

python3 -m tests.test_battery_model

Integrated battery simulation:

python3 -m tests.test_integrated_battery

Battery aging:

python3 -m tests.test_battery_aging_integration

Thermal model:

python3 -m tests.test_thermal_model

Protection model:

python3 -m tests.test_protection_model

Resistance model:

python3 -m tests.test_resistance_model

Charging:

python3 -m tests.test_charging_battery

Current limits:

python3 -m tests.test_current_limits
Example Simulation Output

A 6S 5000 mAh LiPo simulation at 20 A discharge produces results such as:

t= 1s | SOC=99.8889% | Voltage=24.774 V | Current=20.00 A | Power=495.48 W
t= 2s | SOC=99.7778% | Voltage=24.750 V | Current=20.00 A | Power=495.00 W
t= 3s | SOC=99.6667% | Voltage=24.728 V | Current=20.00 A | Power=494.56 W
...

The simulation simultaneously tracks:

SOC
Voltage
Current
Power
Energy
Temperature
SOH
C-rate
Simulation time
Current Integration Roadmap

The BatteryTwin Core is designed to become the foundation for a larger simulation and digital-twin system.

Planned integration areas include:

ROS 2
ROS 2 battery state publisher
Battery telemetry topics
ROS 2 parameter configuration
Runtime battery simulation control
Gazebo
Battery simulation plugin
Simulation-time synchronization
Power consumption integration
Robot/UAV energy simulation
Telemetry
Battery telemetry streaming
Logging
Monitoring
Fault/event reporting
Autonomous Systems

Integration targets may include:

UAVs
Mobile robots
Autonomous vehicles
PX4
ArduPilot
Digital Twin

Future work includes connecting the BatteryTwin simulation with the broader digital-twin and telemetry infrastructure.

Future Enhancements

Potential future extensions include:

Environment and seasonal models
Ambient temperature profiles
Summer / monsoon / winter conditions
Custom environmental conditions
More detailed LiPo electrochemical behavior
Cell-level simulation
Battery pack imbalance
Cooling system models
Advanced aging mechanisms
Fault injection
Sensor noise and telemetry faults
ROS 2 / Gazebo integration
PX4 / ArduPilot integration
Real battery data validation
Development

The project is designed as a modular simulation core so individual models can be developed and tested independently before being integrated into the complete BatteryTwin system.

When adding a new model:

Implement the model inside batterytwin/.
Add unit tests inside tests/.
Integrate the model into BatteryModel if required.
Run the complete test suite.
Verify that all existing tests continue to pass.
Submit changes through a feature branch and Pull Request.
Branching Strategy

Development should be performed using feature branches.

Example:

main
 │
 ├── feature/battery-twin-core
 ├── feature/ros2-integration
 ├── feature/gazebo-integration
 └── feature/telemetry-integration

Changes should be reviewed before merging into main.

License

License information will be added according to the Spaceborn project requirements.

Maintainers

Spaceborn — Beyond Autonomous

BatteryTwin Simulator development team.
