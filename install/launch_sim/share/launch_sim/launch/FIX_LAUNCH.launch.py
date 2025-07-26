# https://gazebosim.org/docs/latest/migrating_gazebo_classic_ros2_packages/

from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import (DeclareLaunchArgument, SetEnvironmentVariable,
                            IncludeLaunchDescription, SetLaunchConfiguration)
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration, TextSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    pkg_ros_gz_sim = get_package_share_directory("ros_gz_sim")
    pkg_waverover_description_gz_sim = get_package_share_directory("wave_rover_description")
    gz_launch_path = PathJoinSubstitution([pkg_ros_gz_sim, "launch", "gz_sim.launch.py"])
    gz_model_path = PathJoinSubstitution([pkg_waverover_description_gz_sim, "models"])

    # Create a Node to launch the Gazebo server
    gz_server_node = Node(
        package='ros_gz_sim',
        executable='gz_server',
        arguments=['-r', PathJoinSubstitution([pkg_waverover_description_gz_sim, "worlds", LaunchConfiguration("world_file")])],
        output='screen'
    )

    # Create a Node to launch the Gazebo client
    gz_client_node = Node(
        package='ros_gz_sim',
        executable='gz_client',
        output='screen'
    )

    # Spawn the robot into the world
    spawn_robot_node = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-file', PathJoinSubstitution([pkg_waverover_description_gz_sim, 'urdf', 'CLEAN_ROVER_MANUAL.sdf']),
            '-name', LaunchConfiguration('robot_name'),
            '-x', LaunchConfiguration('robot_x'),
            '-y', LaunchConfiguration('robot_y'), 
            '-z', LaunchConfiguration('robot_z')
        ],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            "default_world",
            default_value="start",
            description="Gazebo world file to load"
        ),
        DeclareLaunchArgument(
            "robot_name",
            default_value="wave_rover",
            description="Name of the robot to spawn"
        ),
        DeclareLaunchArgument(
            "robot_x",
            default_value="0.0",
            description="X position to spawn the robot"
        ),
        DeclareLaunchArgument(
            "robot_y", 
            default_value="0.0",
            description="Y position to spawn the robot"
        ),
        DeclareLaunchArgument(
            "robot_z",
            default_value="0.5", 
            description="Z position to spawn the robot"
        ),
        SetLaunchConfiguration(name="world_file",
                               value=[LaunchConfiguration("default_world"),
                                      TextSubstitution(text=".sdf")]),
        SetEnvironmentVariable("GZ_SIM_RESOURCE_PATH", gz_model_path),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gz_launch_path),
            launch_arguments={
                "gz_args": [PathJoinSubstitution([pkg_waverover_description_gz_sim, "worlds", LaunchConfiguration("world_file")])],
                "on_exit_shutdown": "True"
            }.items(),
        ),
        gz_server_node,
        gz_client_node,
        spawn_robot_node
    ])



