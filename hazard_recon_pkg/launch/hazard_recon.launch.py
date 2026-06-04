from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='hazard_recon_pkg',
            executable='yolo_detection_node',
            name='yolo_detection_node',
            output='screen',
        ),
        Node(
            package='hazard_recon_pkg',
            executable='servo_payload_node',
            name='servo_payload_node',
            output='screen',
        ),
    ])
