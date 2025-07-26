import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/louise/Development/wave_rover_gazebo_ws/install/launch_sim'
