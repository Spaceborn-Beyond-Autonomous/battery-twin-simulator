cmake_minimum_required(VERSION 3.8)
project(batterytwin_simulator)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(batterytwin_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(gz_sim_vendor REQUIRED)
find_package(gz_plugin_vendor REQUIRED)

# Workaround to find Gazebo Harmonic in ROS2 Jazzy vendored locations
list(APPEND CMAKE_PREFIX_PATH "/opt/ros/jazzy/opt/gz_sim_vendor")
list(APPEND CMAKE_PREFIX_PATH "/opt/ros/jazzy/opt/gz_plugin_vendor")

find_package(gz-sim8 REQUIRED)
find_package(gz-plugin2 REQUIRED COMPONENTS register)

# Gazebo system plugins are usually built as shared libraries
add_library(batterytwin_plugin SHARED
  src/batterytwin_plugin.cpp
)
target_include_directories(batterytwin_plugin PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
ament_target_dependencies(batterytwin_plugin
  rclcpp
  batterytwin_msgs
  std_msgs
)
target_link_libraries(batterytwin_plugin
  gz-sim8::gz-sim8
  gz-plugin2::gz-plugin2-register
)

install(TARGETS batterytwin_plugin
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY include/
  DESTINATION include
)

install(DIRECTORY models launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
