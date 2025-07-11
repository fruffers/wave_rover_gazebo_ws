import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable, TimerAction
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():

    # Get package paths
    pkg_share = FindPackageShare('wave_rover_description').find('wave_rover_description')
    
    # Robot description using the corrected fortress files
    xacro_file = os.path.join(pkg_share, 'urdf', 'rover_fortress.urdf.xacro')
    robot_description = Command(['xacro ', xacro_file])

    # Set environment variables for Gazebo Fortress
    gazebo_resource_path = SetEnvironmentVariable(
        name='IGN_GAZEBO_RESOURCE_PATH',
        value=os.path.join(pkg_share, 'worlds')
    )

    gazebo_model_path = SetEnvironmentVariable(
        name='IGN_GAZEBO_MODEL_PATH',
        value=os.path.dirname(pkg_share)
    )

    # Launch Ignition Gazebo world with ground plane
    world_file = os.path.join(pkg_share, 'worlds', 'oasis_fortress.sdf')
    gazebo = ExecuteProcess(
        cmd=['ign', 'gazebo', world_file, '-v', '4'],
        output='screen'
    )

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[
            {'robot_description': robot_description},
            {'use_sim_time': True}
        ],
        output='screen'
    )

    # Spawn the robot in Gazebo with delay to ensure Gazebo is ready
    spawn_entity = TimerAction(
        period=3.0,  # Wait 3 seconds for Gazebo to fully load
        actions=[
            Node(
                package='ros_gz_sim',
                executable='create',
                arguments=[
                    '-topic', 'robot_description',
                    '-name', 'wave_rover',
                    '-x', '0.0',
                    '-y', '0.0',
                    '-z', '0.2'  # Slightly higher to ensure it's above ground
                ],
                output='screen'
            )
        ]
    )

    # Basic bridge for testing
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
            '/wave_rover/cmd_vel@geometry_msgs/msg/Twist@ignition.msgs.Twist',
            '/wave_rover/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry'
        ],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    return LaunchDescription([
        gazebo_resource_path,
        gazebo_model_path,
        robot_state_publisher,
        gazebo,
        spawn_entity,
        bridge
    ])
