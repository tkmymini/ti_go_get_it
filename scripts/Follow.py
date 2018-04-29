#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import shlex
import rospy
from std_msgs.msg import String 
from tf2_msgs.msg import TFMessage
from geometry_msgs.msg import Twist,TransformStamped,Vector3
CMD = 'rosrun'

def command(file_name):
    try:
        # シェルコマンドを実行する
        command = CMD + ' ' + file_name
        # subprocess.check_call()
        proc = subprocess.Popen(shlex.split(command))
        proc.communicate()
    except:
        print("error")
       
class Follow:
    def __init__(self):
        self.follow_request_sub = rospy.Subscriber('follow/request',String,self.Follow)
        self.follow_start_sub =rospy.Subscriber('follow/start',String,self.Start)
        
        self.state_apoitment_pub = rospy.Publisher('state/apoitment',String,queue_size=10)
        self.follow_request_pub = rospy.Publisher('/chase/request',String,queue_size=10)
                
        self.follow_request = 'Null'
                
    def Follow(self,request):
        print 'receive request'
        self.follow_request = request.data
        rospy.sleep(0.5)
        if self.follow_request == 'follow':
            self.follow_request_pub.publish('start')
            self.state_apoitment_pub.publish('follow')
        elif self.follow_request == 'finish':
            self.follow_request_pub.publish('stop')
            self.state_apoitment_pub.publish('navigate')
            #command('map_server map_saver -f /home/nvidia/maps/slam_map1')
            rospy.sleep(1)

    def Start(self,start):
        print 'follow start'
        command('chaser chaser')
        
if __name__ == '__main__':
    rospy.init_node('ggi_follow',anonymous=True)
    follow = Follow()
    rospy.spin()
