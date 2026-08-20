#include "batterytwin_simulator/batterytwin_plugin.hpp"
#include <gz/plugin/Register.hh>
#include <gz/sim/Model.hh>
#include <gz/sim/Util.hh>
#include <iostream>

namespace batterytwin_simulator
{

BatteryTwinPlugin::BatteryTwinPlugin()
{
}

BatteryTwinPlugin::~BatteryTwinPlugin()
{
}

void BatteryTwinPlugin::Configure(const gz::sim::Entity & _entity,
                                  const std::shared_ptr<const sdf::Element> & _sdf,
                                  gz::sim::EntityComponentManager & _ecm,
                                  gz::sim::EventManager & /*_eventMgr*/)
{
  // Make sure rclcpp is initialized (it might be initialized elsewhere, but this is safe)
  if (!rclcpp::ok()) {
    rclcpp::init(0, nullptr);
  }

  // Create ROS 2 node
  ros_node_ = rclcpp::Node::make_shared("batterytwin_gazebo_plugin");
  
  // Create Publisher for current draw
  battery_pub_ = ros_node_->create_publisher<std_msgs::msg::Float32>("/battery/current_draw", 10);
  
  RCLCPP_INFO(ros_node_->get_logger(), "BatteryTwinPlugin Configured. Publishing current draw.");
}

void BatteryTwinPlugin::PreUpdate(const gz::sim::UpdateInfo & _info,
                                  gz::sim::EntityComponentManager & _ecm)
{
  if (_info.paused) {
    return;
  }
}

void BatteryTwinPlugin::PostUpdate(const gz::sim::UpdateInfo & _info,
                                   const gz::sim::EntityComponentManager & _ecm)
{
  if (_info.paused) {
    return;
  }

  // Publish the current draw from the drone (simulated constant for now)
  auto msg = std_msgs::msg::Float32();
  msg.data = 15.0f; // 15 Amps draw

  battery_pub_->publish(msg);

  // Spin the ROS node so it can handle callbacks (if we add subscribers later)
  rclcpp::spin_some(ros_node_);
}

}  // namespace batterytwin_simulator

// Register the plugin with Gazebo
GZ_ADD_PLUGIN(
  batterytwin_simulator::BatteryTwinPlugin,
  gz::sim::System,
  batterytwin_simulator::BatteryTwinPlugin::ISystemConfigure,
  batterytwin_simulator::BatteryTwinPlugin::ISystemPreUpdate,
  batterytwin_simulator::BatteryTwinPlugin::ISystemPostUpdate
)
GZ_ADD_PLUGIN_ALIAS(batterytwin_simulator::BatteryTwinPlugin, "batterytwin_simulator")
