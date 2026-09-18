# Powertrain Validation Findings

This document records validation results from the reference powertrain
configuration included in this repository.

The results are simulation outputs for the specified model parameters and
should not be treated as measured flight-test or hardware-validation data.

## Current-Limiting Behavior

Reference configuration:

- Motor: EMAX ECO II 2807-1300KV
- Propeller: 10x4.5 in, 2-blade
- Battery: Spektrum Smart LiPo 6S 5000mAh, 22.2 V nominal
- Motor current limit: 25 A

The reference model reaches the configured motor current limit at
approximately 50% throttle.

Once the current limit is reached, the simulated motor torque cannot
increase further because motor torque is derived from current. As a result,
the simulated RPM reaches a plateau of approximately 9537 RPM from 50% to
100% throttle.

This behavior is a consequence of the current-limit assumptions in the
reference model and should not be interpreted as a general characteristic
of all motors, ESCs, or propellers.

## Hover and Endurance Estimate

For a simulated 1.2 kg quadcopter using the reference configuration, the
model estimated:

- Hover current: approximately 24.4 A total
- Electrical power: approximately 541 W
- Estimated hover endurance: approximately 9.8 minutes

These values depend on the model parameters and assumptions used by the
simulator.

## Dynamic Thrust

The dynamic-thrust model showed a sharp reduction in simulated performance
near low state of charge.

The behavior is influenced by the interaction between battery voltage,
motor current limiting, and the powertrain model. Different battery,
motor, ESC, and propeller parameters can produce different results.

## Torque Margin

The torque analysis showed no additional simulated torque margin above
approximately 50% throttle for the reference configuration.

At 40% throttle, the model reported approximately 11.8% remaining torque
margin.

These values are configuration-specific and are provided as reference
simulation results.

## Environmental Effects

The environmental-effects model produced approximately constant thrust
across the tested altitude range for the reference configuration.

This behavior resulted from the interaction between reduced air density
and the current-limited RPM behavior of the reference model. The result
should therefore not be interpreted as a general physical property of UAV
propulsion systems.

## Alternative Motor Configuration

The runtime configuration API was used to evaluate an alternative 900KV
motor configuration.

For the tested parameters, the simulation produced approximately:

- 40% lower current at the tested throttle point
- 42.5% efficiency versus 32.4% for the reference configuration
- Increased simulated torque margin

These results demonstrate how the powertrain API can be used to compare
different motor configurations without modifying the underlying model
implementation.

## Scope

The powertrain subsystem is intended as a configurable reference
implementation. Motor, ESC, propeller, battery, and environmental
parameters can be changed to represent other systems.

Simulation results should be validated against manufacturer data,
bench measurements, and flight-test data before being used for real-world
vehicle design or operational decisions.
