import os
import xacro

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnProcessStart
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    # === File paths ===
    model_rel_path = "urdf/rover.urdf.xacro"
    world_rel_path = "worlds/empty.world"

    model_path = os.path.join(
        get_package_share_directory("wave_rover_description"), model_rel_path)
    world_path = os.path.join(
        get_package_share_directory("wave_rover_description"), world_rel_path)

    # === Process xacro ===
    robot_description = xacro.process_file(model_path).toxml()

    # === Gazebo launch file ===
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("gazebo_ros"), "launch", "gazebo.launch.py")
        ),
        launch_arguments={"world": world_path}.items()
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
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=["-topic", "robot_description", "-entity", "wave_rover"],
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

