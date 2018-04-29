xterm -geometry 80x5+0+0 -e "/opt/ros/kinetic/bin/roslaunch turtlebot_bringup minimal.launch" &
sleep 7s
xterm -geometry 80x5+0+120 -e "/opt/ros/kinetic/bin/roslaunch turtlebot_bringup 3dsensor.launch" &
sleep 7s
xterm -geometry 80x5+600+0 -e "/opt/ros/kinetic/bin/roslaunch turtlebot_navigation gmapping_demo.launch" &
sleep 7s
#xterm -geometry 80x5+600+120 -e "/opt/ros/kinetic/bin/roslaunch turtlebot_rviz_launchers view_navigation.launch" &     
#sleep 7s
xterm -geometry 80x5+0+620 -e "/opt/ros/kinetic/bin/roslaunch e_manipulation motor_setup.launch"&
sleep 7s
xterm -geometry 80x5+0+220 -e "/opt/ros/kinetic/bin/rosrun reconfigure_inflation reconfigure_inflation_server.py " &
sleep 5s
xterm -geometry 80x50+600+220 -e "/opt/ros/kinetic/bin/rosrun go_get_it Follow.py" &
sleep 2s
xterm -geometry 80x5+600+320 -e "/opt/ros/kinetic/bin/rosrun go_get_it VoiceRecognizer.py" &
sleep 2s
xterm -geometry 80x5+600+420 -e "/opt/ros/kinetic/bin/rosrun go_get_it VoiceReceiver.py" &
sleep 2s
xterm -geometry 80x5+600+520 -e "/opt/ros/kinetic/bin/rosrun go_get_it Navigation.py" &
sleep 2s
xterm -geometry 80x7+600+620 -e "/opt/ros/kinetic/bin/rosrun go_get_it GoGetItNode.py"&
sleep 3s
xterm -geometry 80x5+0+320 -e "/opt/ros/kinetic/bin/rosrun e_object_recognizer object_recognizer.py" &
sleep 3s
xterm -geometry 80x5+0+420 -e "/opt/ros/kinetic/bin/rosrun e_grasping_position_detector e_grasping_position_detector" &
sleep 3s
xterm -geometry 80x5+0+520 -e "/opt/ros/kinetic/bin/rosrun e_manipulation manipulation.py" &
sleep 3s
xterm -geometry 170x10+0+900 -e "/usr/bin/python ~/catkin_ws/src/speech_recog/scripts/speech_recog_normal.py"&
sleep 5s
#xterm -geometry 80x5+0+220 -e "/opt/ros/kinetic/bin/roslaunch realsense_camera r200_nodelet_rgbd.launch" &
#sleep 5s
#xterm -geometry 80x5+0+220 -e "/opt/ros/kinetic/bin/roslaunch darknet_ros darknet_ros_gdb.launch" 
#sleep 5s
