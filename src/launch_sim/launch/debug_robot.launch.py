import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():

    # Get package paths
    pkg_share = FindPackageShare('wave_rover_description').find('wave_rover_description')
    
    # Robot description using the corrected fortress files
    xacro_file = os.path.join(pkg_share, 'urdf', 'rover_fortress.urdf.xacro')
    robot_description = Command(['xacro ', xacro_file])

    # Print debug info
    print(f"Package path: {pkg_share}")
    print(f"XACRO file: {xacro_file}")
    print(f"File exists: {os.path.exists(xacro_file)}")

    # Robot State Publisher (start this first)
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

    # Test if robot_description is working
    test_robot_description = ExecuteProcess(
        cmd=['ros2', 'topic', 'echo', 'robot_description', '--once'],
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher,
        test_robot_description
    ])
