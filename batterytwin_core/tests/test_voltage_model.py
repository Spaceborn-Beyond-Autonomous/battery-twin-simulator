from batterytwin.resistance_model import ResistanceModel
from batterytwin.voltage_model import VoltageModel


resistance = ResistanceModel(
    resistance_ohm=0.020
)

voltage_model = VoltageModel()


soc = 0.80
temperature_c = 25.0
current_a = 20.0
ocv_v = 24.0

internal_resistance = resistance.get_resistance(
    soc,
    temperature_c
)

terminal_voltage = voltage_model.calculate(
    ocv_v,
    current_a,
    internal_resistance
)

power_w = terminal_voltage * current_a


print(f"Resistance: {internal_resistance:.3f} ohm")
print(f"OCV: {ocv_v:.3f} V")
print(f"Current: {current_a:.3f} A")
print(f"Terminal voltage: {terminal_voltage:.3f} V")
print(f"Power: {power_w:.3f} W")

