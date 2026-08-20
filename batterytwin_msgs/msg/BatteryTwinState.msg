std_msgs/Header header

# Basic Electrical Metrics
float32 voltage             # Current terminal voltage (V)
float32 current             # Current draw (A)
float32 power               # Power consumption (W)

# Battery Health & Capacity
float32 state_of_charge     # SOC percentage (0.0 to 100.0)
float32 state_of_health     # SOH percentage (0.0 to 100.0)
float32 remaining_capacity  # Remaining capacity in mAh
float32 design_capacity     # Original design capacity in mAh

# Physics & Thermal Metrics
float32 internal_resistance # Current internal resistance (Ohms)
float32 voltage_sag         # Instantaneous voltage sag (V)
float32 temperature         # Battery temperature (Celsius)

# Powertrain Aggregates
float32 total_thrust        # Total thrust generated (if applicable)
float32 total_torque        # Total torque generated
uint16[] motor_rpms         # Array of RPMs for all motors
