from batterytwin.thermal_model import ThermalModel


thermal = ThermalModel(
    thermal_capacity_j_per_k=650.0,
    heat_transfer_w_per_k=3.0,
    initial_temperature_c=25.0,
    ambient_temperature_c=25.0,
)


for t in range(1, 11):

    temperature = thermal.update(
        current_a=20.0,
        resistance_ohm=0.020,
        dt_s=1.0,
    )

    print(
        f"t={t:2d}s | "
        f"Temperature={temperature:.6f} °C"
    )
