xterm -geometry 80x5+0+350 -e "/opt/ros/kinetic/bin/roslaunch camera_tf start_camera_tf.launch" &
sleep 3s
xterm -geometry 80x5+0+460 -e "/opt/ros/kinetic/bin/roslaunch turtlebot_navigation gmapping_demo.launch" 


