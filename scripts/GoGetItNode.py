#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from geometry_msgs.msg import Twist
import subprocess
from std_msgs.msg import String,Bool,Float64

class GoGetItNode:
    def __init__(self):
        self.command_result_sub = rospy.Subscriber('follow/command/result',String,self.commandResult)
        self.follow_result_sub = rospy.Subscriber('follow/result',String,self.followResult)
        self.navi_result_sub = rospy.Subscriber('navigation/result',String,self.navigateResult)
        self.mani_result_sub = rospy.Subscriber('/object/grasp_res',Bool,self.manipulateResult)
        self.search_result_sub = rospy.Subscriber('/object/recog_res',Bool,self.searchResult)
        self.cmmand_list_sub = rospy.Subscriber('command/request',String,self.receiveCommand)
        self.arm_change_result_sub = rospy.Subscriber('/arm_change/result',String,self.arm_changeResult)

        self.voice_cmd_pub = rospy.Publisher('follow/voice_cmd/input',String,queue_size=10)
        self.m6_reqest_pub = rospy.Publisher('/m6_controller/command',Float64,queue_size=1)
        self.follow_request_pub = rospy.Publisher('follow_human',String,queue_size=10)
        self.chaser_pub = rospy.Publisher('follow/start',String,queue_size=10)
        self.remember_pub = rospy.Publisher('navigation/remembering_place',String,queue_size=10)
        self.destination_pub = rospy.Publisher('navigation/input',String,queue_size=10)
        self.search_pub = rospy.Publisher('/object/recog_req',String,queue_size=10)
        self.mani_pub = rospy.Publisher('/object/grasp_req',String,queue_size=10)
        self.google_start_pub = rospy.Publisher('google_req/start',String,queue_size=10)
        self.google_stop_pub = rospy.Publisher('google_req/stop',String,queue_size=10)
        self.vel_pub = rospy.Publisher('/cmd_vel_mux/input/teleop',Twist,queue_size=1)
        self.changing_pose_req_pub = rospy.Publisher('/arm/changing_pose_req',String,queue_size=1)
        self.command_init_pub = rospy.Publisher('command/init',String,queue_size=1)
        
        self.main_state = 999
        self.sub_state = 0
        self.cmd_vel = Twist()
        self.cmd_vel.angular.z = 1.5
        self.wait = 'wait'
        self.follow = 'follow'
        self.receive_command = 'decideOrder'
        self.navigate = 'go'
        self.search_object = 'find'
        self.manipulate_object = 'manipulate'
        self.return_operator = 'return'
        self.finish = 'finish'
        self.order_num = 0
        self.succsess_count = 0
        self.receive_command_flg = 0
        self.follow_result = 'Null'
        self.navigation_result = 'Null'
        self.search_result = 'Null'
        self.manipulation_result = 'Null'
        self.arm_change_result = 'Null'
        self.command_result = 'Null'

        self.command_list = []
        self.order_list = [['wait','hoge'],
                           ['follow','hoge'],
                           ['decideOrder','hoge']]
        
    def waitFollowing(self):
        print "state is wait"
        if self.sub_state == 0:
            self.m6_reqest_pub.publish(0.0)
            self.voice_cmd_pub.publish('follow')
            self.chaser_pub.publish('chaser')
            self.google_start_pub.publish('start')
            self.sub_state = 1
        elif self.sub_state == 1:
            if self.command_result == 'succsess':
                print 'end of this state'
                self.order_num +=1
                self.main_state = self.order_list[self.order_num][0]
                self.sub_state = 0
                self.recognize_result = 'Null'
            elif self.command_result == 'failed':
                print 'again'
                self.sub_state = 0
                
    def followState(self):
        print "state is follow"
        if self.sub_state == 0:
            CMD = '/usr/bin/picospeaker %s' % 'Ok'
            subprocess.call(CMD.strip().split(" "))
            rospy.sleep(0.5)                     
            self.sub_state = 1
        elif self.sub_state == 1:
            if self.follow_result == 'succsess':
                print 'end of this state'
                self.order_num +=1
                self.main_state = self.order_list[self.order_num][0]
                self.sub_state = 0
                self.follow_result = 'Null'
            elif self.follow_result == 'failed':
                print 'again'
                self.sub_state = 0
        
    def decideOrder(self):
        if self.succsess_count < 5:#self.succsess_count < 繰り返したい回数#test
            print 'state is decide order'            
            if self.sub_state == 0:
                rospy.sleep(0.5)
                CMD = '/usr/bin/picospeaker %s' % 'Order please'
                subprocess.call(CMD.strip().split(" "))
                self.sub_state = 1
            elif self.sub_state == 1:
                print 'command_flg is:',self.receive_command_flg
                if self.receive_command_flg == 1:
                    self.m6_reqest_pub.publish(-0.8)
                    CMD = '/usr/bin/picospeaker %s' % 'Ok'
                    subprocess.call(CMD.strip().split(" "))
                    #self.google_stop_pub.publish('stop')
                    rospy.sleep(0.5)
                    print 'complate order list is:'
                    print self.order_list
                    print ''
                    self.receive_command_flg = 0
                    self.sub_state = 0
                    self.order_num = 0
                    self.main_state = self.order_list[self.order_num][0]
                    print 'main state is:',self.main_state
                    
    def navigateState(self):
        print "state is Navigate"
        if self.sub_state == 0:
            self.destination_pub.publish(self.order_list[self.order_num][1])
            self.sub_state = 1
        elif self.sub_state == 1:
            print 'navi now'
            if self.navigation_result == 'succsess':
                print 'end of this state'
                self.order_num += 1
                self.main_state = self.order_list[self.order_num][0]
                self.sub_state = 0
                self.navigation_result = 'Null'
            elif self.navigation_result == 'failed':
                print 'again'
                self.sub_state = 0

    def searchObject(self):
        print "state is search object"
        if self.sub_state == 0:
            self.search_pub.publish(self.order_list[self.order_num][1])
            self.sub_state = 1
        elif self.sub_state == 1:
            if self.search_result == True:
                print 'end of this state'
                self.order_num +=1
                self.main_state = self.order_list[self.order_num][0]
                self.sub_state = 0
                self.search_result = 'Null'
            elif self.search_result == False:
                print 'again'
                self.vel_pub.publish(self.cmd_vel)
                self.sub_state = 0
                
    def manipulateObject(self):
        print "state is manipulate object"
        if self.sub_state == 0:
            self.mani_pub.publish(self.order_list[self.order_num][1])
            self.sub_state = 1
        elif self.sub_state == 1:
            if self.manipulation_result == True:
                self.changing_pose_req_pub.publish('carry')             
                rospy.sleep(2)
                print 'end of this state'
                self.order_num +=1
                self.main_state = self.order_list[self.order_num][0]
                self.sub_state = 0
                self.manipulation_result = 'Null'
            elif self.manipulation_result == False:
                print 'again'
                self.sub_state = 0
            
    def returnOperator(self):
        print "state is return"
        if self.sub_state == 0:
            self.destination_pub.publish(self.order_list[self.order_num][1])
            self.sub_state = 1 
        elif self.sub_state == 1:
            print 'return operator' 
            if self.navigation_result == 'succsess':
                self.m6_reqest_pub.publish(0.0)
                #self.google_start_pub.publish('start')
                self.sub_state = 2
            elif self.navigation_result == 'failed':
                print 'again'
                self.sub_state = 0
        elif self.sub_state == 2:
            CMD = '/usr/bin/picospeaker %s' % 'Here you are'
            subprocess.call(CMD.strip().split(" "))
            self.sub_state = 3
        elif self.sub_state == 3:
            print 'waiting arm change'
            if self.arm_change_result == 'succsess':
                CMD = '/usr/bin/picospeaker %s' % 'you are welcome'
                subprocess.call(CMD.strip().split(" "))
                rospy.sleep(1.5)
                self.command_init_pub.publish('thank you')
                print 'end of this state'
                self.order_num +=1
                self.main_state = self.order_list[self.order_num][0]
                self.sub_state = 0
                self.navigation_result = 'Null'
                self.arm_change_result = 'Null'
                self.succsess_count += 1

    def finishState(self):
        print 'state is finish'
        #self.google_start_pub.publish('stop')
        self.destination_pub.publish('entrance')
        print 'going entrance'
        if self.navigation_result == 'succsess':
            print 'おわり。'
            rospy.sleep(1)
            CMD = '/usr/bin/picospeaker %s' % 'I finished go get it'
            subprocess.call(CMD.strip().split(" "))
            print "--finish--"
            exit()

    def receiveCommand(self,command):
        self.command_list = []
        print 'receive command'
        if self.receive_command_flg == 0:
            command_array = command.data.split(",")
            for loop in range(len(command_array)):
                self.command_list.append(command_array[loop].split(" "))
                print 'command_list is:'
                print self.command_list
                print ''
                self.order_list = self.command_list
            self.receive_command_flg = 1

    def navigateResult(self,result):
        self.navigation_result = result.data

    def commandResult(self,result):
        print result.data
        self.command_result = result.data

    def followResult(self,result):
        self.follow_result = result.data

    def searchResult(self,result):
        self.search_result = result.data

    def manipulateResult(self,result):
        self.manipulation_result = result.data

    def arm_changeResult(self,result):
        self.arm_change_result = result.data

    def loopMain(self):
        print 'start [go get it]'
        self.main_state = self.order_list[self.order_num][0]
        while not rospy.is_shutdown():
            print 'order list is:'
            print self.order_list
            print '<main loop> state is:',self.main_state
            print 'succsess count is:',self.succsess_count
            print ''
            if self.succsess_count == 5:#succsess_count == 繰り返したい回数
                self.finishState()    
            if self.main_state == self.wait:
                self.waitFollowing()
            elif self.main_state == self.follow:
                self.followState()
            elif self.main_state == self.receive_command:
                self.decideOrder()
            elif self.main_state == self.navigate:
                self.navigateState()
            elif self.main_state == self.search_object:
                self.searchObject()
            elif self.main_state == self.manipulate_object:
                self.manipulateObject()
            elif self.main_state == self.return_operator:
                self.returnOperator()
            rospy.sleep(0.5)    
    
if __name__ == '__main__':
    rospy.init_node('go_get_it_node')
    go_get_it = GoGetItNode()
    rospy.sleep(0.5)
    go_get_it.loopMain()
    rospy.spin()
