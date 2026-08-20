#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from batterytwin_msgs.msg import BatteryTwinState
from pymavlink import mavutil
import time

class MavlinkTranslator(Node):
    def __init__(self):
        super().__init__('mavlink_translator')
        
        # Connect to MAVLink endpoint (UDP localhost:14550 is typical for QGC or SITL)
        # In a real scenario, this might be a serial port or different UDP port.
        self.declare_parameter('mavlink_uri', 'udpout:127.0.0.1:14550')
        mav_uri = self.get_parameter('mavlink_uri').get_parameter_value().string_value
        
        self.get_logger().info(f'Connecting to MAVLink at {mav_uri}...')
        self.mav_connection = mavutil.mavlink_connection(mav_uri)
        self.get_logger().info('Connected to MAVLink endpoint!')
        
        # Subscribe to our BatteryTwinState topic from Gazebo plugin
        self.subscription = self.create_subscription(
            BatteryTwinState,
            '/battery/state',
            self.battery_callback,
            10
        )
        self.subscription  # prevent unused variable warning
        
    def battery_callback(self, msg: BatteryTwinState):
        """
        Translates the ROS 2 BatteryTwinState message into a MAVLink BATTERY_STATUS message.
        """
        # MAVLink BATTERY_STATUS (ID #147) fields:
        # id: Battery ID (0 for main)
        # battery_function: Function of the battery (0=Unknown, 1=All flight systems)
        # type: Type (e.g., 3=LIPO)
        # temperature: Temperature in INT16 (celsius * 100). INT16_MAX if unknown.
        # voltages: Array of 10 cell voltages in mV (UINT16). UINT16_MAX if unknown.
        # current_battery: Battery current in cA (10mA) (INT16). -1 if unknown.
        # current_consumed: Consumed charge in mAh (INT32). -1 if unknown.
        # energy_consumed: Consumed energy in hJ (INT32). -1 if unknown.
        # battery_remaining: Remaining battery energy in percent (INT8). -1 if unknown.
        
        # Extract values
        temp_c_100 = int(msg.temperature * 100)
        
        # We only have total voltage, not per cell. Let's just put total in the first cell, 
        # or simulate 6 cells if it's 6S. For simplicity, just total in voltages[0].
        # In actual PX4 implementation, it expects per cell or handles single total well.
        voltages = [int(msg.voltage * 1000)] + [65535] * 9  # 65535 = UINT16_MAX (Unknown)
        
        current_ca = int(msg.current * 100)
        soc_percent = int(msg.state_of_charge)
        
        # Send the MAVLink message
        self.mav_connection.mav.battery_status_send(
            0,                  # id
            1,                  # battery_function (MAV_BATTERY_FUNCTION_ALL)
            3,                  # type (MAV_BATTERY_TYPE_LIPO)
            temp_c_100,         # temperature
            voltages,           # voltages array
            current_ca,         # current_battery
            -1,                 # current_consumed (-1 = unknown for now)
            -1,                 # energy_consumed
            soc_percent         # battery_remaining
        )
        
        self.get_logger().debug(
            f'Sent MAVLink BATTERY_STATUS: V={msg.voltage:.2f}V, I={msg.current:.2f}A, SOC={soc_percent}%'
        )

def main(args=None):
    rclpy.init(args=args)
    translator = MavlinkTranslator()
    
    try:
        rclpy.spin(translator)
    except KeyboardInterrupt:
        pass
    finally:
        translator.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
