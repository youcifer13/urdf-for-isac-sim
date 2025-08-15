import launch
from launch.substitutions import Command, LaunchConfiguration
import launch_ros
from launch.conditions import IfCondition
import os
from launch_ros.descriptions import ParameterValue

def generate_launch_description():
    pkg_share = launch_ros.substitutions.FindPackageShare(package='simplified_urdf_test_description').find('simplified_urdf_test_description')
    default_model_path = os.path.join(pkg_share, 'urdf/simplified_urdf_test.xacro')
    default_rviz_config_path = os.path.join(pkg_share, 'config/display.rviz')
    world_path = os.path.join(pkg_share, 'worlds/room.sdf')
    # sdf_path = os.path.join(pkg_share, 'models/urdf/simplified_urdf_test/model.sdf')
    use_sim_time = LaunchConfiguration('use_sim_time')
    robot_state_publisher_node = launch_ros.actions.Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'use_sim_time': use_sim_time}, {'robot_description': ParameterValue(Command(['xacro ', LaunchConfiguration('model')]), value_type=str)}]
    )
    joint_state_publisher_node = launch_ros.actions.Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'use_sim_time': use_sim_time}],
    )
    rviz_node = launch_ros.actions.Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rvizconfig')],
        parameters=[{'use_sim_time': use_sim_time}],
    )
    spawn_entity = launch_ros.actions.Node(
        condition=IfCondition(use_sim_time),
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'simplified_urdf_test', '-topic', 'robot_description'],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    return launch.LaunchDescription([
        launch.actions.DeclareLaunchArgument(name='use_sim_time', default_value='True',
                                            description='Flag to enable use_sim_time'),
        launch.actions.DeclareLaunchArgument(name='model', default_value=default_model_path,
                                            description='Absolute path to robot urdf file'),
        launch.actions.DeclareLaunchArgument(name='rvizconfig', default_value=default_rviz_config_path,
                                            description='Absolute path to rviz config file'),
        launch.actions.ExecuteProcess(condition=IfCondition(use_sim_time), cmd=['gazebo', '--verbose', '-s',
                                            'libgazebo_ros_init.so', '-s', 'libgazebo_ros_factory.so', world_path],
                                        output='screen'),
        joint_state_publisher_node,
        robot_state_publisher_node,
        spawn_entity,
        rviz_node,
    ])
