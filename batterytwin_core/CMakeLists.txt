cmake_minimum_required(VERSION 3.8)
project(batterytwin_core)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclcpp REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

# Install Python modules
ament_python_install_package(batterytwin)

# Install configs and scripts
install(DIRECTORY config
  DESTINATION share/${PROJECT_NAME}
)
install(PROGRAMS scripts/battery_physics_node.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
