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
  
  // Create Subscriber for throttle commands to dynamically change current
  throttle_sub_ = ros_node_->create_subscription<std_msgs::msg::Float32>(
    "/drone/throttle", 10,
    [this](const std_msgs::msg::Float32::SharedPtr msg) {
      this->current_throttle_ = msg->data;
    });

  current_throttle_ = 0.2f; // Hover throttle (approx 10-15A)

  RCLCPP_INFO(ros_node_->get_logger(), "BatteryTwinPlugin Configured. Listening to /drone/throttle");
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

  // Calculate dynamic current draw based on throttle (0.0 to 1.0)
  // Base current of 2.0A (electronics) + up to 50.0A max motor draw
  float dynamic_current = 2.0f + (50.0f * current_throttle_);

  auto msg = std_msgs::msg::Float32();
  msg.data = dynamic_current;

  battery_pub_->publish(msg);

  // Spin the ROS node so it can handle throttle callbacks
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
