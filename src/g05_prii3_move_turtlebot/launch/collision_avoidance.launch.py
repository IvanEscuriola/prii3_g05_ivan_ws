import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    ExecuteProcess,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    paquete = get_package_share_directory(
        'g05_prii3_move_turtlebot'
    )

    gazebo_launch = os.path.join(
        get_package_share_directory('turtlebot3_gazebo'),
        'launch',
        'empty_world.launch.py'
    )

    cubo = os.path.join(paquete, 'models', 'cubo.sdf')

    crear_cubo = ExecuteProcess(
        cmd=[
            'gz', 'service',
            '-s', '/world/default/create',
            '--reqtype', 'gz.msgs.EntityFactory',
            '--reptype', 'gz.msgs.Boolean',
            '--timeout', '10000',
            '--req',
            (
                f'sdf_filename: "{cubo}", '
                'name: "cubo", '
                'pose: {position: {x: 1.5, y: 0.0, z: 0.5}}'
            ),
        ],
        output='screen'
    )

    eliminar_cubo = ExecuteProcess(
        cmd=[
            'gz', 'service',
            '-s', '/world/default/remove',
            '--reqtype', 'gz.msgs.Entity',
            '--reptype', 'gz.msgs.Boolean',
            '--timeout', '5000',
            '--req', 'name: "cubo", type: MODEL',
        ],
        output='screen'
    )

    return LaunchDescription([
        SetEnvironmentVariable('TURTLEBOT3_MODEL', 'waffle'),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gazebo_launch)
        ),

        Node(
            package='g05_prii3_move_turtlebot',
            executable='collision_avoidance',
	    name='collision_avoidance',
            output='screen',
            parameters=[{'use_sim_time': True}]
        ),

        TimerAction(
            period=5.0,
            actions=[crear_cubo]
        ),

        TimerAction(
            period=30.0,
            actions=[eliminar_cubo]
        ),
    ])
