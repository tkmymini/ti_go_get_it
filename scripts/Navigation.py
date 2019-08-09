#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import rospy
import tf
import math
import actionlib
import std_srvs.srv
from ti_go_get_it.msg import Multi
from tf2_msgs.msg import TFMessage
from std_msgs.msg import String,Bool,Float64
from actionlib_msgs.msg import GoalStatusArray
from move_base_msgs.msg import MoveBaseAction,MoveBaseGoal
from geometry_msgs.msg import Twist,Quaternion,PoseWithCovarianceStamped,PoseStamped


class Navigation:
    def __init__(self):
        self.destination_sub = rospy.Subscriber('/pose',Multi,self.Navigate)

        self.navi_result_pub = rospy.Publisher('navigation/result',Bool,queue_size=1)
        self.vel_pub = rospy.Publisher('/cmd_vel_mux/input/teleop',Twist,queue_size=1)
        self.clear_costmap = rospy.ServiceProxy('move_base/clear_costmaps',std_srvs.srv.Empty)
        self.navi_pub = rospy.Publisher('/move_base_simple/goal',PoseStamped,queue_size = 1)
               
        self.cmd_vel = Twist()
        self.cmd_vel.angular.z = 0.0
        self.sub_state = 0
        self.pose_x = 999
        self.pose_y = 999
        self.pose_z = 999
        self.pose_w = 999
        self.navi_status = 99

 
    def Navigate(self,destination):
        self.pose_x = destination.pose_x
        self.pose_y = destination.pose_y
        self.pose_z = destination.pose_z
        self.pose_w = destination.pose_w
        print 'destination x:',self.pose_x
        print 'destination y:',self.pose_y
        print 'destination z:',self.pose_z
        print 'destination w:',self.pose_w                      
 
        ac = actionlib.SimpleActionClient('move_base', MoveBaseAction)
        if ac.wait_for_server(rospy.Duration(5)) == 1:
            print "wait for action client rising up 0"
        print 'server coms up'
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = 'map'          # 地図座標系
        goal.target_pose.header.stamp = rospy.Time.now() # 現在時刻
        goal.target_pose.pose.position.x =  self.pose_x
        goal.target_pose.pose.position.y =  self.pose_y
        goal.target_pose.pose.orientation.z = self.pose_z
        goal.target_pose.pose.orientation.z = self.pose_w
        ac.send_goal(goal);
            
        while not rospy.is_shutdown():
            if ac.get_state() == 1:
                print 'Got out of the obstacle'
            elif ac.get_state() == 3:
                print "goal"
                result = Bool()
                result = True
                self.navi_result_pub.publish(result)
                break
            elif ac.get_state() == 4:
                print 'Buried in obstacles'
                self.clear_costmap()
                goal = MoveBaseGoal()
                goal.target_pose.header.frame_id = 'map'          # 地図座標系
                goal.target_pose.header.stamp = rospy.Time.now() # 現在時刻
                goal.target_pose.pose.position.x =  self.pose_x
                goal.target_pose.pose.position.y =  self.pose_y
                goal.target_pose.pose.orientation.z = self.pose_z
                goal.target_pose.pose.orientation.z = self.pose_w
                ac.send_goal(goal);
        print "navigation finished"
        
if __name__ == '__main__':
    rospy.init_node('ggi_navigation',anonymous=True)
    navigation = Navigation()
    rospy.spin()
    
