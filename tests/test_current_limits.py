from batterytwin.battery_config_loader import load_battery_config
from batterytwin.battery_model import BatteryModel


config = load_battery_config(
    "config/batteries/spektrum_6s_5000mah_100c.yaml"
)

battery = BatteryModel(config=config)

print(
    f"Maximum discharge current: "
    f"{battery.get_max_discharge_current():.2f} A"
)

print(
    f"Maximum charge current: "
    f"{battery.get_max_charge_current():.2f} A"
)

print("\nTesting valid discharge...")
battery.validate_current(20.0)
print("PASS")

print("\nTesting valid charge...")
battery.validate_current(-10.0)
print("PASS")

print("\nTesting excessive charge...")
try:
    battery.validate_current(-20.0)
    print("FAIL")
except ValueError as e:
    print(f"PASS: {e}")

print("\nTesting excessive discharge...")
try:
    battery.validate_current(600.0)
    print("FAIL")
except ValueError as e:
    print(f"PASS: {e}")
