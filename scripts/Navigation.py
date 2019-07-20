#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import tf
import math
import actionlib
import subprocess
import std_srvs.srv
from move_base_msgs.msg import MoveBaseAction,MoveBaseGoal
from std_msgs.msg import String,Bool,Float64
from geometry_msgs.msg import Twist,Quaternion,PoseWithCovarianceStamped
from ti_go_get_it.msg import Multi
from tf2_msgs.msg import TFMessage
import time
import sys

class Navigation:
    def __init__(self):
        self.destination_sub = rospy.Subscriber('/pose',Multi,self.Navigate)
    
        self.result_pub = rospy.Publisher('navigation/result',String,queue_size=10)
        self.search_list_pub = rospy.Publisher('search/list',String,queue_size=10)
        self.vel_pub = rospy.Publisher('/cmd_vel_mux/input/teleop',Twist,queue_size=1)
        self.clear_costmap = rospy.ServiceProxy('move_base/clear_costmaps',std_srvs.srv.Empty)
        self.reset_pub = rospy.Publisher('reconfiguration/input',Bool,queue_size=10)
        self.follow_result_pub = rospy.Publisher('follow/result',String,queue_size=1)
        
        self.cmd_vel = Twist()
        self.cmd_vel.angular.z = 0.0
        self.sub_state = 0
        self.pose_x = 0
        self.pose_y = 0

    def Navigate(self,destination):
        self.pose_x = destination.pose_x
        self.pose_y = destination.pose_y
        print 'destination x:',self.pose_x
        print 'destination y:',self.pose_y
        ac = actionlib.SimpleActionClient('move_base', MoveBaseAction)
        if ac.wait_for_server(rospy.Duration(5)) == 1:
            print "wait for action client rising up 0"
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = 'map'          # 地図座標系
        goal.target_pose.header.stamp = rospy.Time.now() # 現在時刻
        goal.target_pose.pose.position.x =  self.pose_x
        goal.target_pose.pose.position.y =  self.pose_y        
        q = tf.transformations.quaternion_from_euler(0, 0, 0)
        goal.target_pose.pose.orientation = Quaternion(q[0],q[1],q[2],q[3])
        ac.send_goal(goal);        
        while not rospy.is_shutdown():
            print 'get state is',ac.get_state()
            if ac.get_state == 1 and reset_flg == 1:                
                print 'Got out of the obstacle'
                self.reset_pub.publish(0)
                reset_flg = 0
            if ac.get_state() == 3:
                print "goal"
                result = String()
                result = "succsess"
                if destination.data != 'entrance' or destination.data != 'oprater':
                    self.result_pub.publish(result)
                    #rospy.sleep(1)
                if destination.data == 'entrance':
                    exit()
                if destination.data == 'oprater':
                    self.result_pub.publish("return_op")
                break
            if ac.get_state() == 4 and reset_flg == 0:
                print 'Buried in obstacles'
                self.clear_costmap()
                self.reset_pub.publish(1)
                reset_flg = 1
                ac = actionlib.SimpleActionClient('move_base', MoveBaseAction)
                if ac.wait_for_server(rospy.Duration(5)) == 1:
                    print "wait for action client rising up 1"
                goal = MoveBaseGoal()
                goal.target_pose.header.frame_id = 'map'          # 地図座標系
                goal.target_pose.header.stamp = rospy.Time.now() # 現在時刻
                goal.target_pose.pose.position.x =  self.pose_x
                goal.target_pose.pose.position.y =  self.pose_y
                q = tf.transformations.quaternion_from_euler(0, 0, 0)
                goal.target_pose.pose.orientation = Quaternion(q[0],q[1],q[2],q[3])
                ac.send_goal(goal);
        print "finish"
        
if __name__ == '__main__':
    rospy.init_node('ggi_navigation',anonymous=True)
    navigation = Navigation()
    rospy.spin()
    
