#!/usr/bin/env python3
"""
Test script to validate robot spawning in Gazebo Fortress.
This script builds the workspace and launches the simulation.
"""

import os
import subprocess
import sys

def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    print(f"Return code: {result.returncode}")
    if result.stdout:
        print(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr}")
    return result

def main():
    # Set workspace directory
    workspace_dir = "/home/louise/Development/wave_rover_gazebo_ws"
    
    print("=== Building the workspace ===")
    build_result = run_command("colcon build --symlink-install", cwd=workspace_dir)
    
    if build_result.returncode != 0:
        print("Build failed! Please check the errors above.")
        return 1
    
    print("\n=== Sourcing the workspace ===")
    source_cmd = f"source {workspace_dir}/install/setup.bash"
    
    print("\n=== Launching the simulation ===")
    launch_cmd = f"{source_cmd} && ros2 launch launch_sim SIMLAUNCHER.launch.py"
    
    print(f"To launch the simulation, run:")
    print(f"cd {workspace_dir}")
    print(f"source install/setup.bash")
    print(f"ros2 launch launch_sim SIMLAUNCHER.launch.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
