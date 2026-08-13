#ifndef BATTERYTWIN_BATTERY_CONFIG_HPP
#define BATTERYTWIN_BATTERY_CONFIG_HPP

#include <string>

namespace batterytwin
{

struct BatteryConfig
{
    std::string name;
    std::string chemistry;

    int series_cells;
    int parallel_cells;

    double nominal_capacity_ah;

    double nominal_voltage_v;
    double cell_nominal_voltage_v;
    double cell_max_voltage_v;
    double pack_max_voltage_v;

    double continuous_discharge_c;
    double maximum_charge_c;

    double nominal_energy_wh;

    double mass_kg;
};

}  // namespace batterytwin

#endif  // BATTERYTWIN_BATTERY_CONFIG_HPP

