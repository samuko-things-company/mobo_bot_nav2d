import os

from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, RegisterEventHandler
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch.conditions import IfCondition



def generate_launch_description():

    my_nav_pkg = get_package_share_directory('mobo_bot_nav2d')
    my_robot_sim_pkg = get_package_share_directory('mobo_bot_sim')
    my_robot_view_pkg = get_package_share_directory('mobo_bot_rviz')
    
    world_file_name = 'test_world.world'
    world_path = os.path.join(my_robot_sim_pkg, 'world', world_file_name)

    use_rviz = 'False' # you can change to 'True' or 'False'

    # initialize launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time')
    world = LaunchConfiguration('world')
    view_mapping_in_rviz = LaunchConfiguration('view_mapping_in_rviz')

    # declare launch arguments
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use sim time if true'
    )

    declare_world_cmd = DeclareLaunchArgument(
        'world',
        default_value=world_path,
        description='SDF world file'
    )

    declare_view_mapping_in_rviz_cmd = DeclareLaunchArgument(
        'view_mapping_in_rviz',
        default_value=use_rviz,
        description='whether to run run rviz or not')


    sim_robot = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(my_robot_sim_pkg,'launch','sim.launch.py')]
            ), 
            launch_arguments={'use_sim_time': use_sim_time,
                              'world': world,
                              'view_robot_in_rviz': 'False'}.items()
    )

    view_robot = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(my_robot_view_pkg,'launch','build_map_with_slam.launch.py')]
            ), 
            condition=IfCondition(view_mapping_in_rviz)
    )
    
    
    slam_mapping_param_file = os.path.join(my_nav_pkg,'config','my_slam_mapping_params_online_async.yaml')
    slam_mapping_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[slam_mapping_param_file],
    )





    # Create the launch description and populate
    ld = LaunchDescription()


    # add the necessary declared launch arguments to the launch description
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_world_cmd)
    ld.add_action(declare_view_mapping_in_rviz_cmd)
    
    # Add the nodes to the launch description
    ld.add_action(sim_robot)
    ld.add_action(view_robot)
    ld.add_action(slam_mapping_node)

    return ld




    