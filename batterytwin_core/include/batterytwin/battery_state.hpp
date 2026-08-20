#ifndef BATTERYTWIN_BATTERY_STATE_HPP
#define BATTERYTWIN_BATTERY_STATE_HPP

namespace batterytwin
{

struct BatteryState
{
    // Electrical state
    double voltage_v{0.0};
    double current_a{0.0};
    double power_w{0.0};

    // Battery state
    double soc{1.0};
    double soh{1.0};

    // Thermal state
    double temperature_c{25.0};

    // Energy state
    double energy_remaining_wh{0.0};
    double energy_consumed_wh{0.0};

    // Usage information
    double c_rate{0.0};

    // Simulation time
    double simulation_time_s{0.0};
};

}  // namespace batterytwin

#endif  // BATTERYTWIN_BATTERY_STATE_HPP
