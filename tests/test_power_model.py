from batterytwin.power_model import PowerModel


model = PowerModel()

discharge_power = model.calculate(
    voltage_v=22.0,
    current_a=20.0,
)

charge_power = model.calculate(
    voltage_v=22.0,
    current_a=-10.0,
)

idle_power = model.calculate(
    voltage_v=22.0,
    current_a=0.0,
)

print("Discharge power:", discharge_power)
print("Charge power:", charge_power)
print("Idle power:", idle_power)
