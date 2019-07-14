#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from geometry_msgs.msg import Twist
import subprocess
from std_msgs.msg import String,Bool,Float64

class GoGetItNode:
    def __init__(self):
        self.follow_state_sub = rospy.Subscriber('/follow',String,self.follow)#follow_stateの変更
        self.training_state_sub = rospy.Subscriber('/training',String,self.training)#training_stateの変更
        self.setup_result_sub = rospy.Subscriber('/setup/result',Bool,self.setupResult)
        self.navi_result_sub = rospy.Subscriber('navigation/result',String,self.navigateResult)
        self.mani_result_sub = rospy.Subscriber('/object/grasp_res',Bool,self.manipulateResult)
        self.arm_change_result_sub = rospy.Subscriber('/arm_change/result',String,self.arm_changeResult)
        self.com_sub = rospy.Subscriber('/command',Bool,self.receiveCommand)
        self.mani_obj = rospy.Subscriber('/object/manipulation',String,self.manipulationObj)

        self.m6_reqest_pub = rospy.Publisher('/m6_controller/command',Float64,queue_size=1)
        self.follow_request_pub = rospy.Publisher('follow_human',String,queue_size=10)#followの開始・終了
        self.return_pub = rospy.Publisher('/return/operator',String,queue_size=10)#voicereceiver.pyに送る
        self.mani_obj_req_pub = rospy.Publisher('/object/grasp_req',String,queue_size=10)
        self.followAPI_pub = rospy.Publisher('/followface',Bool,queue_size=10)
        self.trainingAPI_pub = rospy.Publisher('/trainingface',Bool,queue_size=10)
        self.commandAPI_pub = rospy.Publisher('/commandface',Bool,queue_size=10)
        self.vel_pub = rospy.Publisher('/cmd_vel_mux/input/teleop',Twist,queue_size=1)
        self.changing_pose_req_pub = rospy.Publisher('/arm/changing_pose_req',String,queue_size=1)
        self.command_init_pub = rospy.Publisher('command/init',String,queue_size=1)
   
        self.main_state = 999
        self.sub_state = 0
        self.cmd_vel = Twist()
        self.cmd_vel.angular.z = 1.5
        self.setup = 'setup'
        self.command = 'command'
        self.finish = 'finish'
        self.succsess_count = 0
        self.receive_com = False
        self.follow_state = 'null'
        self.training_state = 'null'
        self.setup_result = False
        self.navigation_result = 'Null'
        self.manipulation_result = 'Null'
        self.arm_change_result = 'Null'
        self.mani_obj = 'null'

        self.order_list = ['setup','command']
        
    def Setup(self):
        if self.setup_result == False:
            print "state is setup"
            #self.m6_reqest_pub.publish(0.0)
            if self.sub_state == 0:
                self.followAPI_pub.publish(True)
                self.sub_state=1
            elif self.sub_state == 1:
                print 'followface'
                if self.follow_state == 'start':
                    self.follow_request_pub.publish('start')#followの開始
                    CMD = '/usr/bin/picospeaker %s' % 'Ok'
                    subprocess.call(CMD.strip().split(" "))
                    rospy.sleep(0.5)
                    self.follow_state = 'now'
                elif self.follow_state == 'now':
                    print 'follow now'
                elif self.follow_state == 'stop':
                    self.follow_request_pub.publish('stop')#followの終了#followの終了にラグがありすぎる場合はこの場所をsentecereceiveに書こうかな
                    self.followAPI_pub.publish(False)
                    self.follow_state = 'null'
                    self.sub_state=2
            elif self.sub_state == 2:
                self.trainingAPI_pub.publish(True)
                self.sub_state=3
            elif self.sub_state == 3:
                print 'trainingface'
                if self.training_state == 'stop':
                    self.trainingAPI_pub.publish(False)
                    self.sub_state=0
        elif self.setup_result == True:
            self.main_state = self.order_list[1]
            self.sub_state = 0
       
    def Command(self):
        if self.succsess_count < 5:#self.succsess_count < 繰り返したい回数#test
            print 'state is decide order'            
            if self.sub_state == 0:
                self.commandAPI_pub.publish(True)
                rospy.sleep(0.5)
                CMD = '/usr/bin/picospeaker %s' % 'Order please'
                subprocess.call(CMD.strip().split(" "))
                self.sub_state = 1
            elif self.sub_state == 1:
                print 'command_flg is:',self.receive_com
                if self.receive_com == True:
                    #self.m6_reqest_pub.publish(-0.8)
                    CMD = '/usr/bin/picospeaker %s' % 'Ok'
                    subprocess.call(CMD.strip().split(" "))
                    rospy.sleep(0.5)
                    self.receive_com = False
                    self.sub_state = 2
            elif self.sub_state == 2:
                print "state is Navigate"
                if self.navigation_result == 'succsess':
                    self.sub_state = 3
                    self.mani_obj_req_pub.publish(self.mani_obj)
                    self.navigation_result = 'Null'
                elif self.navigation_result == 'failed':
                    print 'again'
            elif self.sub_state == 3:
                print "state is manipulation"
                if self.manipulation_result == True:
                    self.changing_pose_req_pub.publish('carry')             
                    rospy.sleep(2)
                    self.sub_state = 4
                    self.manipulation_result = 'Null'
                elif self.manipulation_result == False:
                    print 'again'
            elif self.sub_state == 4:
                self.return_pub.publish("operator")
                self.sub_state = 5 
            elif self.sub_state == 5:
                print 'return operator' 
                if self.navigation_result == 'succsess':
                    #self.m6_reqest_pub.publish(0.0)
                    self.sub_state = 6
                elif self.navigation_result == 'failed':
                    print 'again'
            elif self.sub_state == 6:
                CMD = '/usr/bin/picospeaker %s' % 'Here you are'
                subprocess.call(CMD.strip().split(" "))
                self.sub_state = 7
            elif self.sub_state == 7:
                print 'waiting arm change'
                if self.arm_change_result == 'succsess':
                    CMD = '/usr/bin/picospeaker %s' % 'you are welcome'
                    subprocess.call(CMD.strip().split(" "))
                    rospy.sleep(1.5)
                    self.command_init_pub.publish('thank you')#commandの初期化だと思う
                    print 'end of this state'
                    self.sub_state = 0
                    self.navigation_result = 'Null'
                    self.arm_change_result = 'Null'
                    self.succsess_count += 1
                    
    def finishState(self):
        self.commandAPI_pub.publish(False)
        print 'state is finish'
        CMD = '/usr/bin/picospeaker %s' % 'I finished go get it'
        subprocess.call(CMD.strip().split(" "))
        print "--finish--"
        exit()

    def follow(self,state):
        self.follow_state = state.data
    def training(self,state):
        self.training_state = state.data 
            
    def setupResult(self,result):
        self.setup_result = result.data

    def navigateResult(self,result):
        self.navigation_result = result.data
        
    def receiveCommand(self,flg):
        self.receive_com = flg.data

    def manipulationObj(self,obj):
        self.mani_obj = obj.data
        
    def manipulateResult(self,result):
        self.manipulation_result = result.data

    def arm_changeResult(self,result):
        self.arm_change_result = result.data

    def loopMain(self):
        print 'start [go get it]'
        self.main_state = self.order_list[0]
        while not rospy.is_shutdown():
            #print '<main loop> state is:',self.main_state
            print 'succsess count is:',self.succsess_count
            print ''
            if self.succsess_count == 5:#succsess_count == 繰り返したい回数
                self.finishState()
            if self.main_state == self.setup:
                self.Setup()
            elif self.main_state == self.command:
                self.Command()
            rospy.sleep(0.5)    
    
if __name__ == '__main__':
    rospy.init_node('go_get_it_node')
    go_get_it = GoGetItNode()
    rospy.sleep(1)
    go_get_it.loopMain()
    rospy.spin()
