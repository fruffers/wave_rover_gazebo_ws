#!/usr/bin/env python3

import os
from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, TimerAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Get the path to the package
    pkg_share = FindPackageShare(package='wave_rover_description').find('wave_rover_description')
    
    # Path to the world file
    world_file_path = os.path.join(pkg_share, 'worlds', 'simple_rover_world.sdf')
    
    # Declare launch arguments
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )
    
    # Set environment variables for Gazebo Harmonic to find the models
    pkg_share = FindPackageShare(package='wave_rover_description').find('wave_rover_description')
    current_gz_resource_path = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    current_gz_model_path = os.environ.get('GZ_SIM_MODEL_PATH', '')
    new_resource_paths = [pkg_share]
    if current_gz_resource_path:
        new_resource_paths.append(current_gz_resource_path)
    new_model_paths = [os.path.join(pkg_share, 'models')]
    if current_gz_model_path:
        new_model_paths.append(current_gz_model_path)
    gazebo_env = {
        'GZ_SIM_RESOURCE_PATH': ':'.join(new_resource_paths),
        'GZ_SIM_MODEL_PATH': ':'.join(new_model_paths)
    }
    # Launch Gazebo Harmonic with the world file
    gazebo_launch = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_file_path],
        output='screen',
        additional_env=gazebo_env
    )

    bridge_params = os.path.join(get_package_share_directory('wave_rover_description'), 'urdf/config', 'gz_bridge.yaml')
    ros_gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments= [
            '--ros-args',
            '-p',
            f'config_file:={bridge_params}'
        ]
    )

    # image_params = os.path.join(get_package_share_directory('wave_rover_description'), 'urdf/config', 'gz_image_bridge.yaml')
    # ros_gz_image_bridge = Node(
    #     package="ros_gz_image",
    #     executable="image_bridge",
    #     arguments= ["/camera/image_raw", "/camera/depth_image"]
    # )
    
    return LaunchDescription([
        use_sim_time_arg,
        gazebo_launch,
        ros_gz_bridge
    ])
