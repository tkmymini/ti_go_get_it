## GoGetIt setup
$ sh mimi_setup.sh  
$ roslaunch e_manipulation motor_setup.launch  
$ rosrun ti_go_get_it ggi_followandnavi.sh  
$ rosrun chaser chaser  
$ rosrun e_object_recognizer object_recognizer.py  
$ rosrun e_grasping_position_detector e_grasping_position_detector  
$ rosrun manipulation manipulation.py  
$ roslaunch darknet_ros darknet_ros.launch  
$ rosrun ti_go_get_it SentenceReceiver.py  
$ rosrun ti_go_get_it Navigation.py  
$ rosrun ti_go_get_it GoGetItNode.py  
