#!/usr/bin/env python3

import os
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
    
    # Set environment variables for Gazebo to find the models
    pkg_share = FindPackageShare(package='wave_rover_description').find('wave_rover_description')
    
    # Get current environment variables
    current_ign_resource_path = os.environ.get('IGN_GAZEBO_RESOURCE_PATH', '')
    current_ign_model_path = os.environ.get('IGN_GAZEBO_MODEL_PATH', '')
    current_gz_resource_path = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    current_gz_model_path = os.environ.get('GZ_SIM_MODEL_PATH', '')
    
    # Build new paths including our package
    new_resource_paths = [pkg_share]
    if current_ign_resource_path:
        new_resource_paths.append(current_ign_resource_path)
    if current_gz_resource_path:
        new_resource_paths.append(current_gz_resource_path)
    
    new_model_paths = [os.path.join(pkg_share, 'models')]
    if current_ign_model_path:
        new_model_paths.append(current_ign_model_path)
    if current_gz_model_path:
        new_model_paths.append(current_gz_model_path)
    
    gazebo_env = {
        'IGN_GAZEBO_RESOURCE_PATH': ':'.join(new_resource_paths),
        'IGN_GAZEBO_MODEL_PATH': ':'.join(new_model_paths),
        'GZ_SIM_RESOURCE_PATH': ':'.join(new_resource_paths),
        'GZ_SIM_MODEL_PATH': ':'.join(new_model_paths)
    }
    
    # Launch Ignition Gazebo with the world file
    gazebo_launch = ExecuteProcess(
        cmd=['ign', 'gazebo', '-r', world_file_path],
        output='screen',
        additional_env=gazebo_env
    )
    
    # Bridge for ROS 2 integration (launch after a delay to ensure Gazebo is ready)
    bridge = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='ros_gz_bridge',
                executable='parameter_bridge',
                arguments=[
                    '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
                    '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
                    '/joint_states@sensor_msgs/msg/JointState@gz.msgs.Model',
                    '/clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock'
                ],
                output='screen'
            )
        ]
    )
    
    return LaunchDescription([
        use_sim_time_arg,
        gazebo_launch,
        bridge
    ])
