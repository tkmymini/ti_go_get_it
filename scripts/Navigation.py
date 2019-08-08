#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import rospy
import tf
import math
import actionlib
import subprocess
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
        self.navi_status_sub = rospy.Subscriber('move_base/status',GoalStatusArray,self.NaviStatusCB)
    
        self.result_pub = rospy.Publisher('navigation/result',String,queue_size=1)
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

    def NaviStatusCB(self,receive_msg):
        try:
            self.navi_status = receive_msg.status_list[0].status
        except IndexError:
            print 'error'
            pass

    def Navigate(self,destination):
        self.pose_x = destination.pose_x
        self.pose_y = destination.pose_y
        self.pose_z = destination.pose_z
        self.pose_w = destination.pose_w
        print 'destination x:',self.pose_x
        print 'destination y:',self.pose_y
        print 'destination w:',self.pose_w
        
        goal = PoseStamped()
        goal.header.frame_id = 'map'          # 地図座標系
        goal.header.stamp = rospy.Time.now() # 現在時刻
        goal.pose.position.x =  self.pose_x
        goal.pose.position.y =  self.pose_y  
        goal.pose.orientation.z = self.pose_z      
        goal.pose.orientation.w = self.pose_w
        self.navi_pub.publish(goal)
               
        while not rospy.is_shutdown():
            if self.navi_status == 1:                
                print 'Got out of the obstacle'
            elif self.navi_status == 3:
                print "goal"
                print "w:",self.pose_w
                rospy.sleep(10)
                result = String()
                result = "succsess"
                self.result_pub.publish(result)
                self.navi_status = 0
                break
            elif self.navi_status == 4:
                print 'Buried in obstacles'
                self.clear_costmap()
                goal = PoseStamped()
                goal.header.frame_id = 'map'          # 地図座標系
                goal.header.stamp = rospy.Time.now() # 現在時刻
                goal.pose.position.x =  self.pose_x
                goal.pose.position.y =  self.pose_y
                goal.pose.orientation.z = self.pose_z
                goal.pose.orientation.w = self.pose_w
                self.navi_pub.publish(goal)
        print "navi finish"
        
if __name__ == '__main__':
    rospy.init_node('ggi_navigation',anonymous=True)
    navigation = Navigation()
    rospy.spin()
    
