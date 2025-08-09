#!/usr/bin/env python3

import os
from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare




def generate_launch_description():
    # Get path to the package
    pkg_share = get_package_share_directory('wave_rover_description')

    # Paths to models and world file
    model_path = os.path.join(pkg_share, 'models')
    world_file_path = os.path.join(pkg_share, 'worlds', 'circuit1_plugins.sdf')
    
    # Declare launch arguments
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )
    
   # Environment setup
    # Only use source workspace for model/resource lookup
    set_gz_resource_path = SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', pkg_share)

    os.environ['GZ_SIM_RESOURCE_PATH'] = pkg_share

    gazebo_launch = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_file_path],
        output='screen'
    )

    ros_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock@ignition.msgs.Clock",
            "/cmd_vel@geometry_msgs/msg/Twist@ignition.msgs.Twist",
            "/odom@nav_msgs/msg/Odometry@ignition.msgs.Odometry",
            "/joint_states@sensor_msgs/msg/JointState@ignition.msgs.Model",
            "/tf@tf2_msgs/msg/TFMessage@ignition.msgs.Pose_V",
            "/camera/camera_info@sensor_msgs/msg/CameraInfo@ignition.msgs.CameraInfo",
            "/camera/points@sensor_msgs/msg/PointCloud2@ignition.msgs.PointCloudPacked",
            "/camera/image_raw@sensor_msgs/msg/Image@ignition.msgs.Image",
            "/camera/depth_image@sensor_msgs/msg/Image@ignition.msgs.Image"
        ],
        output="screen",
        parameters=[
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
        ]
    )

    # ros_ign_image_bridge = Node(
    #     package="ros_ign_image",
    #     executable="image_bridge",
    #     arguments=[
    #         "/camera/image_raw",
    #         "/camera/depth_image"
    #     ]
    # )

    return LaunchDescription([
        use_sim_time_arg,
        set_gz_resource_path,
        gazebo_launch,
        ros_bridge
    ])
