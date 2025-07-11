import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():

    # Declare launch arguments
    world_arg = DeclareLaunchArgument(
        'world_name',
        default_value='oasis_fortress.sdf',
        description='Name of the world file to load'
    )

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    # Get package paths
    pkg_share = FindPackageShare('wave_rover_description').find('wave_rover_description')
    world_file = PathJoinSubstitution([
        FindPackageShare('wave_rover_description'),
        'worlds',
        LaunchConfiguration('world_name')
    ])

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

    # Launch Ignition Gazebo (Fortress)
    gazebo = ExecuteProcess(
        cmd=[
            'ign', 'gazebo',
            world_file,
            '-v', '4'  # Verbose level 4
        ],
        output='screen'
    )

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[
            {'robot_description': robot_description},
            {'use_sim_time': LaunchConfiguration('use_sim_time')}
        ],
        output='screen'
    )

    # Joint State Publisher (optional, for manual joint control)
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        output='screen'
    )

    # Spawn the robot in Gazebo
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'wave_rover',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.1'
        ],
        output='screen'
    )

    # Bridge between ROS 2 and Ignition Gazebo - Updated for your specific topics
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
            '/wave_rover/cmd_vel@geometry_msgs/msg/Twist@ignition.msgs.Twist',
            '/wave_rover/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
            '/wave_rover/joint_states@sensor_msgs/msg/JointState[ignition.msgs.Model',
            '/wave_rover/pose@geometry_msgs/msg/PoseArray[ignition.msgs.Pose_V',
            '/camera/image_raw@sensor_msgs/msg/Image[ignition.msgs.Image',
            '/camera/depth/image_raw@sensor_msgs/msg/Image[ignition.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo[ignition.msgs.CameraInfo',
            '/camera/depth/points@sensor_msgs/msg/PointCloud2[ignition.msgs.PointCloudPacked'
        ],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        output='screen'
    )

    return LaunchDescription([
        world_arg,
        use_sim_time_arg,
        gazebo_resource_path,
        gazebo_model_path,
        robot_state_publisher,
        joint_state_publisher,
        gazebo,
        spawn_entity,
        bridge
    ])
