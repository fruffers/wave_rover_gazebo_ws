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

    # Start with just an empty world to test basic functionality
    gazebo = ExecuteProcess(
        cmd=['ign', 'gazebo', 'empty.sdf', '-v', '4'],
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

    # Spawn the robot with a longer delay
    spawn_entity = TimerAction(
        period=5.0,  # Wait 5 seconds for Gazebo to fully load
        actions=[
            Node(
                package='ros_gz_sim',
                executable='create',
                arguments=[
                    '-topic', 'robot_description',
                    '-name', 'wave_rover',
                    '-x', '0.0',
                    '-y', '0.0', 
                    '-z', '0.5'  # Higher up to make sure it's visible
                ],
                output='screen'
            )
        ]
    )

    # Minimal bridge - just clock for now
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock'
        ],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher,
        gazebo,
        spawn_entity,
        bridge
    ])
