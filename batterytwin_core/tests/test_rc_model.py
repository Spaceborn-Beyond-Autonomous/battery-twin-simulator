from batterytwin.rc_model import RCModel


rc = RCModel(
    resistance_ohm=0.010,
    capacitance_f=1000.0
)


current_a = 20.0
dt_s = 1.0


for step in range(10):

    voltage = rc.update(
        current_a=current_a,
        dt_s=dt_s
    )

    print(
        f"t={step + 1:2d}s | "
        f"Polarization voltage={voltage:.6f} V"
    )
