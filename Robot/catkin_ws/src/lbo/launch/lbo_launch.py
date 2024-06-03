from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package = 'lbo',
            node_executable = 'odom',
            node_name = 'odom',
            output = 'screen',
        ),
        Node(
            package = 'lbo',
            node_executable = 'make_map',
            node_name = 'make_map',
            output = 'screen' ,
        ),
    ])