from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription,TimerAction
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():

    diffdrive_dir = get_package_share_directory('diffdrive_bot')

    control_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(diffdrive_dir, 'launch', 'control.launch.py')
        )
    )

    side_length_arg = DeclareLaunchArgument(
        'side_length',
        default_value='0.5',
        description='Length of each square side in metres'
    )

    rotate_server = Node(
        package='my_robot_nodes',
        executable='rotate_server',
        output='screen'
    )

    square_driver = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='my_robot_nodes',
                executable='square_driver',
                output='screen',
                parameters=[{
                    'side_length': LaunchConfiguration('side_length')
            }]
        )
    ]
)

    return LaunchDescription([
        side_length_arg,
        control_launch,
        rotate_server,
        square_driver
    ])
