#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from batterytwin_msgs.msg import BatteryTwinState
from std_msgs.msg import Float32
from ament_index_python.packages import get_package_share_directory
import os

from batterytwin.battery_config_loader import load_battery_config
from batterytwin.battery_model import BatteryModel

class BatteryPhysicsNode(Node):
    def __init__(self):
        super().__init__('battery_physics_node')
        
        # Publisher for the battery state
        self.state_pub = self.create_publisher(BatteryTwinState, '/battery/state', 10)
        
        # Subscriptions (e.g. current draw from motors)
        # For a full integration, you would subscribe to motor current here.
        # But for now, we'll maintain a fixed current draw or allow a topic to override it.
        self.current_draw_sub = self.create_subscription(
            Float32, '/battery/current_draw', self.current_draw_callback, 10
        )
        self.current_draw = 15.0  # default 15A draw
        
        # Load the battery config
        pkg_share = get_package_share_directory('batterytwin_core')
        config_path = os.path.join(pkg_share, 'config', 'batteries', 'spektrum_6s_5000mah_100c.yaml')
        
        try:
            self.config = load_battery_config(config_path)
            self.get_logger().info(f"Loaded battery config: {self.config.name}")
        except Exception as e:
            self.get_logger().error(f"Failed to load battery config: {e}")
            raise e
            
        self.battery = BatteryModel(config=self.config, initial_soc=1.0)
        
        # Timer to run physics at 10 Hz (dt = 0.1s)
        self.timer_period = 0.1
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        
    def current_draw_callback(self, msg):
        self.current_draw = msg.data
        
    def timer_callback(self):
        # Update the battery physics model
        state = self.battery.update(
            current_a=self.current_draw,
            dt_s=self.timer_period,
            temperature_c=25.0  # ambient temp
        )
        
        # Publish the new state
        msg = BatteryTwinState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.voltage = state.voltage_v
        msg.current = state.current_a
        msg.power = state.power_w
        msg.state_of_charge = state.soc * 100.0  # percentage
        msg.state_of_health = state.soh * 100.0  # percentage
        msg.temperature = state.temperature_c
        msg.remaining_capacity = (state.energy_remaining_wh / self.config.nominal_voltage_v) * 1000.0 # mAh approx
        msg.design_capacity = self.config.nominal_capacity_ah * 1000.0
        # For internal resistance, we don't have it directly in state without accessing the model,
        # but we can leave it default or try to calculate it.
        msg.internal_resistance = 0.02
        
        self.state_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = BatteryPhysicsNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
