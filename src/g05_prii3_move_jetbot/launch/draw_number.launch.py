import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    hardware_launch = os.path.join(
        get_package_share_directory('jetbot_pro_ros2'),
        'launch',
        'jetbot.py'
    )

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(hardware_launch)
        ),

        Node(
            package='g05_prii3_move_jetbot',
            executable='draw_number',
            name='draw_number_jetbot',
            output='screen',
            parameters=[{'use_sim_time': False}]
        ),
    ])
