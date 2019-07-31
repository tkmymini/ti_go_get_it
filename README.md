## GoGetIt setup
$ roscore  
$ roslaunch turtlebot_bringup minimal.launch  
$ roslaunch turtlebot_bringup 3dsensor.launch  
$ roslaunch realsense2_camera rs_rgbd.launch   
$ roslaunch e_manipulation motor_setup.launch  
$ roslaunch camera_tf start_camera_tf.launch  
$ roslaunch turtlebot_navigation gmapping_demo.launch  
$ roslaunch turtlebot_rviz_launchers view_navigation.launch  
$ rosrun chaser chaser  
$ rosrun e_object_recognizer object_recognizer.py  
$ rosrun e_grasping_position_detector e_grasping_position_detector  
$ rosrun manipulation manipulation.py  
$ roslaunch darknet_ros darknet_ros.launch  
$ rosrun ti_go_get_it SentenceReceiver.py  
$ rosrun ti_go_get_it Navigation.py  
$ rosrun ti_go_get_it GoGetItNode.py  
