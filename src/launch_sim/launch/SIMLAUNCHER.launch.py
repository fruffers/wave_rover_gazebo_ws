#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare, LaunchConfiguration


def generate_launch_description():
    # Get the package directories
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_wave_rover_description = get_package_share_directory('wave_rover_description')

    default_world = os.path.join(pkg_wave_rover_description, 'worlds', 'oasis_fortress.sdf')

    world = LaunchConfiguration('world')

    default_world_arg = DeclareLaunchArgument(
        'default_world_file',
        default_value=default_world,
        description='World file to load in Gazebo as default'
    )
    
    # Define launch arguments
    world_file_arg = DeclareLaunchArgument(
        'world_file',
        default_value='empty.world',
        description='World file to load in Gazebo'
    )
    
    robot_name_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='wave_rover',
        description='Name of the robot'
    )
    
    robot_x_arg = DeclareLaunchArgument(
        'robot_x',
        default_value='0.0',
        description='X position of the robot'
    )
    
    robot_y_arg = DeclareLaunchArgument(
        'robot_y',
        default_value='0.0',
        description='Y position of the robot'
    )
    
    robot_z_arg = DeclareLaunchArgument(
        'robot_z',
        default_value='0.1',
        description='Z position of the robot'
    )
    
    # Path to the SDF file
    sdf_file_path = os.path.join(pkg_wave_rover_description, 'urdf', 'CLEAN_ROVER.sdf')
    
    # Launch Gazebo Fortress
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ]),
        launch_arguments={
            'gz_args': ['-r -v4', world],
            'on_exit_shutdown': 'true',
            'world': PathJoinSubstitution([
                FindPackageShare('wave_rover_description'),
                'worlds',
                LaunchConfiguration('default_world_file')
            ]),
            'verbose': 'true',
            'pause': 'false',
            'use_sim_time': 'true'
        }.items()
    )
    
    # Read the SDF file content
    with open(sdf_file_path, 'r') as file:
        robot_description = file.read()
    
    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True
        }]
    )
    
    # Spawn robot in Gazebo
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        name='spawn_wave_rover',
        arguments=[
            '-name', LaunchConfiguration('wave_rover'),
            '-file', sdf_file_path,
            '-x', LaunchConfiguration('robot_x'),
            '-y', LaunchConfiguration('robot_y'),
            '-z', LaunchConfiguration('robot_z')
        ],
        output='screen'
    )
    
    # ROS-Gazebo Bridge for topics
    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        arguments=[
            # Camera topics
            '/camera/image_raw@sensor_msgs/msg/Image@ignition.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo@ignition.msgs.CameraInfo',
            '/camera/depth/image_raw@sensor_msgs/msg/Image@ignition.msgs.Image',
            '/camera/depth/camera_info@sensor_msgs/msg/CameraInfo@ignition.msgs.CameraInfo',
            '/camera/points@sensor_msgs/msg/PointCloud2@ignition.msgs.PointCloudPacked',
            
            # Control topics
            '/cmd_vel@geometry_msgs/msg/Twist@ignition.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry@ignition.msgs.Odometry',
            
            # Joint states
            '/joint_states@sensor_msgs/msg/JointState@ignition.msgs.Model',
            
            # TF
            '/tf@tf2_msgs/msg/TFMessage@ignition.msgs.Pose_V'
        ],
        output='screen'
    )
    
    # Clock bridge for simulation time
    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='clock_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock'],
        output='screen'
    )
    
    # Joint State Publisher (for static joints)
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{
            'use_sim_time': True
        }]
    )
    
    # Delay robot spawn to ensure Gazebo is ready
    delayed_spawn = TimerAction(
        period=3.0,
        actions=[spawn_robot]
    )
    
    # Delay bridge to ensure robot is spawned
    delayed_bridge = TimerAction(
        period=5.0,
        actions=[ros_gz_bridge]
    )
    
    return LaunchDescription([
        # Launch arguments
        default_world_arg,
        robot_name_arg,
        robot_x_arg,
        robot_y_arg,
        robot_z_arg,
        
        # Launch Gazebo
        gazebo_launch,
        
        # Robot State Publisher
        robot_state_publisher,
        
        # Joint State Publisher
        joint_state_publisher,
        
        # Clock bridge (start immediately)
        clock_bridge,
        
        # Delayed spawn and bridge
        delayed_spawn,
        delayed_bridge
    ])
