xterm -geometry 80x5+0+0 -e "/opt/ros/kinetic/bin/roslaunch turtlebot_bringup minimal.launch" &
2 sleep 7s
3 xterm -geometry 80x5+0+120 -e "/opt/ros/kinetic/bin/roslaunch turtlebot_bringup 3dsensor.launch" &
4 sleep 7s
5 xterm -geometry 80x5+600+0 -e "/opt/ros/kinetic/bin/roslaunch turtlebot_navigation gmapping_demo.launch" &
6 sleep 7s
7 #xterm -geometry 80x5+600+120 -e "/opt/ros/kinetic/bin/roslaunch turtlebot_rviz_launchers view_navigation.launch" &
8 #sleep 7s
9 xterm -geometry 80x5+0+620 -e "/opt/ros/kinetic/bin/roslaunch e_manipulation motor_setup.launch"&
10 sleep 7s
11 xterm -geometry 80x5+0+220 -e "/opt/ros/kinetic/bin/rosrun reconfigure_inflation reconfigure_inflation_server.py " &
12 sleep 5s
13 xterm -geometry 80x50+600+220 -e "/opt/ros/kinetic/bin/rosrun go_get_it Follow.py" &
14 sleep 2s
15 xterm -geometry 80x5+600+320 -e "/opt/ros/kinetic/bin/rosrun go_get_it VoiceRecognizer.py" &
16 sleep 2s
17 xterm -geometry 80x5+600+420 -e "/opt/ros/kinetic/bin/rosrun go_get_it VoiceReceiver.py" &
18 sleep 2s
19 xterm -geometry 80x5+600+520 -e "/opt/ros/kinetic/bin/rosrun go_get_it Navigation.py" &
20 sleep 2s
21 xterm -geometry 80x7+600+620 -e "/opt/ros/kinetic/bin/rosrun go_get_it GoGetItNode.py"&
22 sleep 3s
23 xterm -geometry 80x5+0+320 -e "/opt/ros/kinetic/bin/rosrun e_object_recognizer object_recognizer.py" &
24 sleep 3s
25 xterm -geometry 80x5+0+420 -e "/opt/ros/kinetic/bin/rosrun e_grasping_position_detector e_grasping_position_detector" &
26 sleep 3s
27 xterm -geometry 80x5+0+520 -e "/opt/ros/kinetic/bin/rosrun e_manipulation manipulation.py" &
28 sleep 3s
29 xterm -geometry 170x10+0+900 -e "/usr/bin/python ~/catkin_ws/src/speech_recog/scripts/speech_recog_normal.py"&
30 sleep 5s
31 #xterm -geometry 80x5+0+220 -e "/opt/ros/kinetic/bin/roslaunch realsense_camera r200_nodelet_rgbd.launch" &
32 #sleep 5s
33 #xterm -geometry 80x5+0+220 -e "/opt/ros/kinetic/bin/roslaunch darknet_ros darknet_ros_gdb.launch"
34 #sleep 5s
