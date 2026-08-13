from batterytwin.energy_model import EnergyModel


energy = EnergyModel(
    initial_energy_wh=111.0
)

power_w = 500.0
dt_s = 1.0


for step in range(10):

    remaining = energy.update(
        power_w=power_w,
        dt_s=dt_s
    )

    print(
        f"t={step + 1:2d}s | "
        f"Consumed={energy.get_consumed_energy():.6f} Wh | "
        f"Remaining={remaining:.6f} Wh"
    )
