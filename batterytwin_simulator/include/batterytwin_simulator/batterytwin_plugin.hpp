#ifndef BATTERYTWIN_SIMULATOR__BATTERYTWIN_PLUGIN_HPP_
#define BATTERYTWIN_SIMULATOR__BATTERYTWIN_PLUGIN_HPP_

#include <gz/sim/System.hh>
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/float32.hpp>
#include <memory>

namespace batterytwin_simulator
{

class BatteryTwinPlugin
  : public gz::sim::System,
    public gz::sim::ISystemConfigure,
    public gz::sim::ISystemPreUpdate,
    public gz::sim::ISystemPostUpdate
{
public:
  BatteryTwinPlugin();
  ~BatteryTwinPlugin() override;

  // Called when the plugin is loaded
  void Configure(const gz::sim::Entity & _entity,
                 const std::shared_ptr<const sdf::Element> & _sdf,
                 gz::sim::EntityComponentManager & _ecm,
                 gz::sim::EventManager & _eventMgr) override;

  // Called before each physics update
  void PreUpdate(const gz::sim::UpdateInfo & _info,
                 gz::sim::EntityComponentManager & _ecm) override;

  // Called after each physics update
  void PostUpdate(const gz::sim::UpdateInfo & _info,
                  const gz::sim::EntityComponentManager & _ecm) override;

private:
  // ROS 2 Node and Publisher
  rclcpp::Node::SharedPtr ros_node_;
  rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr battery_pub_;
  rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr throttle_sub_;

  float current_throttle_ = 0.2f;

  // Simulation time tracking
  std::chrono::steady_clock::duration last_update_time_{0};
};

}  // namespace batterytwin_simulator

#endif  // BATTERYTWIN_SIMULATOR__BATTERYTWIN_PLUGIN_HPP_
