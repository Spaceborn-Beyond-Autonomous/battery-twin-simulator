from batterytwin.soc_model import SOCModel


battery = SOCModel(
    capacity_ah=5.0,
    initial_soc=1.0
)

soc = battery.update(
    current_a=20.0,
    dt_s=1.0
)

print(f"SOC: {soc:.6f}")
print(f"SOC percentage: {soc * 100:.4f}%")
