import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable
from launch_ros.actions import Node
from launch.substitutions import TextSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():

    pkg_share = FindPackageShare("wave_rover_description").find("wave_rover_description")
    
    sdf_file = os.path.join(pkg_share, "urdf", "wave_rover.sdf")
    world_file = os.path.join(pkg_share, "worlds", "oasis.world")

    # Set GAZEBO_MODEL_PATH to the parent directory of wave_rover_description
    gazebo_model_path = os.path.dirname(pkg_share)

    set_gazebo_model_path = SetEnvironmentVariable(
        name='GAZEBO_MODEL_PATH',
        value=TextSubstitution(text=gazebo_model_path)
    )

    # Launch Gazebo with the necessary plugins
    gazebo = ExecuteProcess(
        cmd=[
            'gazebo',
            '--verbose',
            world_file,
            '-s', 'libgazebo_ros_init.so',
            '-s', 'libgazebo_ros_factory.so'
        ],
        output='screen'
    )

    # Spawn the SDF model into Gazebo
    spawn = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-entity", "wave_rover",
            "-file", sdf_file,
            "-x", "0", "-y", "0", "-z", "0.05"
        ],
        output="screen"
    )
    
    # robot_description = Command([
    # FindExecutable(name="xacro"), " ",
    # PathJoinSubstitution([
    # FindPackageShare("wave_rover_description"), "urdf",
    # 	"wave_rover.urdf.xacro"
    # 	])
    # ])
    
    # robot_spawn_node = Node(
    # package="gazebo_ros",
    # executable="spawn_entity.py",
    # arguments=["-topic","robot_description",
    # "-entity","robot"],
    # output="screen"
    
    # robot_state_publisher_node = Node(
    # 	package="robot_state_publisher",
    #	executable="robot_state_publisher",
    #	parameters="[{"robot_description" : robot_description}],
    #	output="screen"
    # )
    
    # joint_state_publisher_node = Node(
    #	package="joint_state_publisher",
    #	executable="joint_state_publisher",
    #	output="screen"
    # )   

    return LaunchDescription([
        set_gazebo_model_path,
        gazebo,
        spawn
    ])


