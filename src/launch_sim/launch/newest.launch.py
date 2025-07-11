import os
import xacro

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.event_handlers import OnProcessStart
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    # === File paths ===
    model_rel_path = "urdf/rover.urdf.xacro"
    world_rel_path = "worlds/oasis_fortress.sdf"

    model_path = os.path.join(
        get_package_share_directory("wave_rover_description"), model_rel_path)
    world_path = os.path.join(
        get_package_share_directory("wave_rover_description"), world_rel_path)

    # === Process xacro ===
    robot_description = xacro.process_file(model_path).toxml()

    world = LaunchConfiguration('world')

    world_arg = DeclareLaunchArgument(
        'world',
        default_value=world_path,
        description='Path to the world file to load'
    )

    # === Gazebo launch file ===
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
        launch_arguments={'gz_args': ['-r -v4', world] 'on_exit_shutdown': 'true'}.items()
    )

    # === Robot State Publisher ===
    rsp_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[{
            "robot_description": robot_description,
            "use_sim_time": True
        }]
    )

    # === Spawn Entity Node ===
    spawn_node = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'wave_rover',
                   '-z', '0.1'],
        output="screen"
    )

    # === Ensure spawn happens after RSP is running ===
    spawn_after_rsp = RegisterEventHandler(
        OnProcessStart(
            target_action=rsp_node,
            on_start=[spawn_node]
        )
    )

    return LaunchDescription([
        gazebo_launch,
        rsp_node,
        spawn_after_rsp
    ])

