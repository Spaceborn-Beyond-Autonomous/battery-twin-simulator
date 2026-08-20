import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, AppendEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_simulator = get_package_share_directory('batterytwin_simulator')

    # Model file path
    sdf_file = os.path.join(pkg_simulator, 'models', 'battery', 'model.sdf')

    # To let Gazebo find the plugin, we append the workspace lib directory to GZ_SIM_SYSTEM_PLUGIN_PATH
    # It usually installs to <workspace>/install/batterytwin_simulator/lib/batterytwin_simulator
    plugin_path = os.path.join(
        get_package_share_directory('batterytwin_simulator'), 
        '..', '..', 'lib', 'batterytwin_simulator'
    )
    
    set_plugin_path = AppendEnvironmentVariable(
        'GZ_SIM_SYSTEM_PLUGIN_PATH',
        plugin_path
    )

    # Launch Gazebo Sim with an empty world
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r empty.sdf'}.items()
    )

    # Spawn the Battery entity in Gazebo
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
            '-name', 'battery_twin',
            '-file', sdf_file,
            '-z', '0.5'
        ]
    )

    return LaunchDescription([
        set_plugin_path,
        gz_sim,
        spawn_entity
    ])
