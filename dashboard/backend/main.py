import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))

import asyncio
import json
import math
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from batterytwin.battery_config_loader import load_battery_config
from batterytwin.battery_model import BatteryModel
from batterytwin.protection_model import ProtectionModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config_path = pathlib.Path(__file__).parent.parent.parent / "config" / "batteries" / "spektrum_6s_5000mah_100c.yaml"
config = load_battery_config(str(config_path))

sim_container = {
    "model": BatteryModel(config=config, initial_soc=1.0, initial_soh=1.0),
    "profile": "6S",
    "fault_injection": {
        "over_voltage": False,
        "over_temperature": False,
        "over_current": False
    }
}

@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("connection open")
    
    async def receive_commands():
        try:
            while True:
                data = await websocket.receive_text()
                command = json.loads(data)
                action = command.get("action")
                
                if action == "set_profile":
                    profile = command.get("profile")
                    sim_container["profile"] = profile
                    sim_container["model"] = BatteryModel(config=config, initial_soc=1.0, initial_soh=1.0)
                    sim_container["fault_injection"] = {"over_voltage": False, "over_temperature": False, "over_current": False}
                
                elif action == "inject_fault":
                    fault_type = command.get("fault")
                    state_val = command.get("state", False)
                    if fault_type in sim_container["fault_injection"]:
                        sim_container["fault_injection"][fault_type] = state_val
                        print(f"Fault injection updated: {sim_container['fault_injection']}")
        except WebSocketDisconnect:
            pass

    async def send_telemetry():
        try:
            while True:
                battery = sim_container["model"]
                profile = sim_container["profile"]
                faults = sim_container["fault_injection"]
                
                time_val = datetime.now().timestamp()
                
                # Apply simulated fault modifications
                current_load = 80.0 if faults["over_current"] else (30.0 + 15.0 * math.sin(time_val))
                
                dt = 0.5
                try:
                    state = battery.update(
                        current_a=current_load,
                        dt_s=dt,
                        temperature_c=battery.state.temperature_c
                    )
                except ValueError:
                    current_load = 10.0
                    state = battery.update(current_a=current_load, dt_s=dt)

                # Force overrides if injected
                if faults["over_voltage"]:
                    state.voltage_v = battery.protection_model.max_voltage_v + 1.5
                if faults["over_temperature"]:
                    state.temperature_c = battery.protection_model.max_temperature_c + 10.0

                rpm = 5000.0 + (current_load * 120.0)
                pwm = 1100.0 + (current_load * 15.0)
                thrust = (rpm / 1000.0) ** 2 * 0.06
                torque = current_load * 0.025

                power_w = state.power_w if state.power_w > 1.0 else 1.0
                endurance_minutes = (state.energy_remaining_wh / power_w) * 60.0

                soh_percent = state.soh * 100.0
                effective_capacity = battery.get_effective_capacity_ah()
                resistance_factor = battery.aging_model.get_resistance_factor()
                efc = battery.aging_model.cycle_count

                # Cell-level distribution
                num_cells = 6 if profile == "6S" else (4 if profile == "4S" else 3)
                avg_cell_voltage = state.voltage_v / num_cells
                cell_voltages = [
                    round(avg_cell_voltage + math.sin(time_val + i) * 0.015, 3) 
                    for i in range(num_cells)
                ]

                # Thermal model metrics
                thermal_gen = getattr(battery.thermal_model, 'heat_generation_w', 0.0)
                thermal_loss = getattr(battery.thermal_model, 'heat_loss_w', 0.0)
                temp_rate = getattr(battery.thermal_model, 'temperature_rate_c_per_s', 0.0)
                ambient_temp = getattr(battery.thermal_model, 'ambient_temperature_c', 25.0)

                # Protection model evaluation using Anand's ProtectionModel logic[cite: 2]
                prot_status = battery.protection_model.check(
                    voltage_v=state.voltage_v,
                    temperature_c=state.temperature_c,
                    current_a=state.current_a
                )

                payload = {
                    "active_profile": profile,
                    "voltage": state.voltage_v,
                    "current": state.current_a,
                    "soc": state.soc * 100.0,
                    "temperature": state.temperature_c,
                    "endurance_min": endurance_minutes,
                    "energy_remaining": state.energy_remaining_wh,
                    "cell_voltages": cell_voltages,
                    "protection_status": {
                        "over_voltage": prot_status.over_voltage,
                        "under_voltage": prot_status.under_voltage,
                        "over_temperature": prot_status.over_temperature,
                        "under_temperature": prot_status.under_temperature,
                        "over_current": prot_status.over_current,
                        "fault": prot_status.fault,
                        "healthy": prot_status.healthy
                    },
                    "thermal_metrics": {
                        "heat_generation_w": thermal_gen,
                        "heat_loss_w": thermal_loss,
                        "temp_rate_c_per_s": temp_rate,
                        "ambient_c": ambient_temp
                    },
                    "degradation": {
                        "soh": soh_percent,
                        "effective_capacity_ah": effective_capacity,
                        "resistance_factor": resistance_factor,
                        "equivalent_full_cycles": efc
                    },
                    "propulsion": {
                        "esc_status": "ARMED" if prot_status.healthy else "FAULT",
                        "rpm": rpm,
                        "pwm": pwm,
                        "thrust": thrust,
                        "torque": torque,
                        "power": state.power_w
                    }
                }
                
                await websocket.send_text(json.dumps(payload))
                await asyncio.sleep(dt)
        except Exception as e:
            print(f"Simulation loop error: {e}")
            import traceback
            traceback.print_exc()

    await asyncio.gather(receive_commands(), send_telemetry())
