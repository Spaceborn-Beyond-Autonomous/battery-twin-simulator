import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent / "batterytwin_core"))

import asyncio
import json
import math
import threading
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

import rclpy
from rclpy.node import Node
from batterytwin_msgs.msg import BatteryTwinState

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global dictionary to hold the latest telemetry from ROS 2
latest_telemetry = {
    "voltage": 22.2,
    "current": 0.0,
    "soc": 1.0,
    "temperature": 25.0,
    "power": 0.0,
    "energy_remaining": 111.0,
    "soh": 1.0,
    "over_voltage": False,
    "under_voltage": False,
    "over_temperature": False,
    "under_temperature": False,
    "over_current": False,
    "fault": False,
    "healthy": True
}

class DashboardROSNode(Node):
    def __init__(self):
        super().__init__('dashboard_backend_node')
        self.sub = self.create_subscription(
            BatteryTwinState,
            '/battery/state',
            self.state_callback,
            10
        )
        self.get_logger().info("Dashboard ROS 2 Node initialized, listening to /battery/state")

    def state_callback(self, msg):
        global latest_telemetry
        latest_telemetry["voltage"] = getattr(msg, "voltage", 22.2)
        latest_telemetry["current"] = getattr(msg, "current", 0.0)
        latest_telemetry["soc"] = getattr(msg, "state_of_charge", 100.0) / 100.0
        latest_telemetry["temperature"] = getattr(msg, "temperature", 25.0)
        latest_telemetry["power"] = getattr(msg, "power", 0.0)
        latest_telemetry["energy_remaining"] = (getattr(msg, "remaining_capacity", 5000.0) / 1000.0) * latest_telemetry["voltage"]
        latest_telemetry["soh"] = getattr(msg, "state_of_health", 100.0) / 100.0
        latest_telemetry["over_voltage"] = getattr(msg, "over_voltage", False)
        latest_telemetry["under_voltage"] = getattr(msg, "under_voltage", False)
        latest_telemetry["over_temperature"] = getattr(msg, "over_temperature", False)
        latest_telemetry["under_temperature"] = getattr(msg, "under_temperature", False)
        latest_telemetry["over_current"] = getattr(msg, "over_current", False)
        latest_telemetry["fault"] = getattr(msg, "fault", False)
        latest_telemetry["healthy"] = getattr(msg, "healthy", True)

ros_node = None
ros_thread = None

@app.on_event("startup")
def startup_event():
    global ros_node, ros_thread
    try:
        rclpy.init(args=None)
        ros_node = DashboardROSNode()
        ros_thread = threading.Thread(target=rclpy.spin, args=(ros_node,), daemon=True)
        ros_thread.start()
        print("ROS 2 Integration Started Successfully!")
    except Exception as e:
        print(f"Failed to start ROS 2: {e}")

@app.on_event("shutdown")
def shutdown_event():
    global ros_node
    if ros_node:
        ros_node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()

@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Dashboard Frontend Connected!")
    
    async def receive_commands():
        try:
            while True:
                data = await websocket.receive_text()
                # Here we could forward commands back to ROS 2 topics
                pass
        except WebSocketDisconnect:
            pass

    async def send_telemetry():
        try:
            while True:
                time_val = datetime.now().timestamp()
                
                v = latest_telemetry["voltage"]
                c = latest_telemetry["current"]
                soc = latest_telemetry["soc"]
                soh = latest_telemetry["soh"]
                power_w = latest_telemetry["power"] if latest_telemetry["power"] > 1.0 else 1.0
                energy_wh = latest_telemetry["energy_remaining"]
                
                endurance_minutes = (energy_wh / power_w) * 60.0
                
                num_cells = 6
                avg_cell_voltage = v / num_cells
                cell_voltages = [
                    round(avg_cell_voltage + math.sin(time_val + i) * 0.015, 3) 
                    for i in range(num_cells)
                ]
                
                rpm = 5000.0 + (c * 120.0)
                pwm = 1100.0 + (c * 15.0)
                thrust = (rpm / 1000.0) ** 2 * 0.06
                torque = c * 0.025
                
                payload = {
                    "active_profile": "6S (ROS 2 Integrated)",
                    "voltage": v,
                    "current": c,
                    "soc": soc * 100.0,
                    "temperature": latest_telemetry["temperature"],
                    "endurance_min": endurance_minutes,
                    "energy_remaining": energy_wh,
                    "cell_voltages": cell_voltages,
                    "protection_status": {
                        "over_voltage": latest_telemetry["over_voltage"],
                        "under_voltage": latest_telemetry["under_voltage"],
                        "over_temperature": latest_telemetry["over_temperature"],
                        "under_temperature": latest_telemetry["under_temperature"],
                        "over_current": latest_telemetry["over_current"],
                        "fault": latest_telemetry["fault"],
                        "healthy": latest_telemetry["healthy"]
                    },
                    "thermal_metrics": {
                        "heat_generation_w": c * 0.05,
                        "heat_loss_w": 2.0,
                        "temp_rate_c_per_s": 0.01,
                        "ambient_c": 25.0
                    },
                    "degradation": {
                        "soh": soh * 100.0,
                        "effective_capacity_ah": 5.0 * soh,
                        "resistance_factor": 1.0 + (1.0 - soh),
                        "equivalent_full_cycles": 10
                    },
                    "propulsion": {
                        "esc_status": "ARMED" if latest_telemetry["healthy"] else "FAULT",
                        "rpm": rpm,
                        "pwm": pwm,
                        "thrust": thrust,
                        "torque": torque,
                        "power": power_w
                    }
                }
                
                await websocket.send_text(json.dumps(payload))
                await asyncio.sleep(0.1) # 10 Hz
        except Exception as e:
            print(f"Simulation loop error: {e}")

    await asyncio.gather(receive_commands(), send_telemetry())
