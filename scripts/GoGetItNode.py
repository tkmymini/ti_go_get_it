#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import String,Bool,Float64

class GoGetItNode:
    def __init__(self):
        self.follow_state_sub = rospy.Subscriber('/follow/state',String,self.follow)#follow_stateの変更
        self.training_state_sub = rospy.Subscriber('/training/state',String,self.training)#training_stateの変更
        self.setup_result_sub = rospy.Subscriber('/setup/result',Bool,self.setupResult)
        self.navi_result_sub = rospy.Subscriber('navigation/result',Bool,self.navigateResult)
        self.mani_result_sub = rospy.Subscriber('/object/grasp_res',Bool,self.manipulateResult)
        self.com_sub = rospy.Subscriber('/command',Bool,self.receiveCommand)
        self.mani_obj = rospy.Subscriber('/object/manipulation',String,self.manipulationObj)
        self.change_pose_res_sub = rospy.Subscriber('/arm/changing_pose_res',Bool,self.changePoseResult)

        self.m4_reqest_pub = rospy.Publisher('/m4_controller/command',Float64,queue_size=1)
        self.m6_reqest_pub = rospy.Publisher('/m6_controller/command',Float64,queue_size=1)
        self.follow_request_pub = rospy.Publisher('/chase/request',String,queue_size=1)#followの開始・終了
        self.return_pub = rospy.Publisher('/sentence',String,queue_size=1)#SentenceReceiver.pyに送る
        self.mani_obj_req_pub = rospy.Publisher('/object/grasp_req',String,queue_size=1)
        self.followAPI_pub = rospy.Publisher('/followface',Bool,queue_size=1)
        self.trainingAPI_pub = rospy.Publisher('/trainingface',Bool,queue_size=1)
        self.commandAPI_pub = rospy.Publisher('/commandface',Bool,queue_size=1)
        self.returnAPI_pub = rospy.Publisher('/returnface',Bool,queue_size=1)
        self.changing_pose_req_pub = rospy.Publisher('/arm/changing_pose_req',String,queue_size=1)
        self.tts_pub = rospy.Publisher('/tts',String,queue_size = 1)

        #状態遷移するための変数
        self.main_state = 999
        self.sub_state = 0
        #state名(定数)
        self.setup = 'setup'
        self.command = 'command'
        self.finish = 'finish'
        #命令の受け取り
        self.receive_com = False
        #各stateの確認
        self.follow_state = 'null'
        self.training_state = 'null'
        #各result
        self.setup_result = False
        self.navigation_result = False
        self.manipulation_result = False
        self.arm_change_result = False
        #把持する物体名
        self.mani_obj = 'null'
        #成功した命令回数
        self.succsess_count = 0

        self.sentence = 'none'
        self.order_list = ['setup','command']
        
    def Setup(self):
        if self.setup_result == False:
            print "state is setup"
            self.m6_reqest_pub.publish(0.3)
            if self.sub_state == 0:
                self.followAPI_pub.publish(True)
                self.tts_pub.publish('Waiting')
                rospy.sleep(0.5)
                self.sub_state=1
            elif self.sub_state == 1:
                print 'followface'
                if self.follow_state == 'null':
                    print 'wait'
                if self.follow_state == 'start':
                    self.follow_request_pub.publish('start')#followの開始
                    self.tts_pub.publish('Ok')
                    rospy.sleep(0.5)
                    self.follow_state = 'now'
                elif self.follow_state == 'now':
                    print 'now'
                elif self.follow_state == 'stop':
                    self.tts_pub.publish('Ok')
                    rospy.sleep(0.5)
                    self.follow_request_pub.publish('stop')#followの終了#followの終了にラグがありすぎる場合はこの場所をsentecereceiveに書く
                    self.followAPI_pub.publish(False)
                    print 'stop'
                    self.follow_state = 'null'
                    self.sub_state=2
            elif self.sub_state == 2:
                self.trainingAPI_pub.publish(True)
                self.tts_pub.publish('Memorize start')
                rospy.sleep(1)
                self.sub_state=3
            elif self.sub_state == 3:
                print 'trainingface'
                if self.training_state == 'finish':
                    self.trainingAPI_pub.publish(False)
                    self.tts_pub.publish('Memorize fenish')
                    rospy.sleep(0.5)
                    self.training_state = 'null'
                    self.sub_state=0
        elif self.setup_result == True:
            self.trainingAPI_pub.publish(False)
            self.main_state = self.order_list[1]
            self.sub_state = 0
       
    def Command(self):
        if self.succsess_count < 5:#self.succsess_count < 繰り返したい回数
            print 'commandface'            
            if self.sub_state == 0:
                self.commandAPI_pub.publish(True)
                rospy.sleep(0.5)
                self.tts_pub.publish('Order please')
                self.sub_state = 1
            elif self.sub_state == 1:
                print 'waiting command'
                if self.receive_com == True:
                    self.commandAPI_pub.publish(False)
                    self.tts_pub.publish('Ok')
                    rospy.sleep(0.5)
                    self.receive_com = False
                    self.sub_state = 2
            elif self.sub_state == 2:
                print "state:Navigate"
                if self.navigation_result == True:
                    self.sub_state = 3
                    self.m6_reqest_pub.publish(-0.07)
                    self.mani_obj_req_pub.publish(self.mani_obj)
                    self.navigation_result = False
            elif self.sub_state == 3:
                print "state:Manipulation"
                if self.manipulation_result == True:
                    print 'state:arm change'
                    self.m6_reqest_pub.publish(0.3)
                    self.changing_pose_req_pub.publish('carry')             
                    rospy.sleep(2)#かかる時間によって変更
                    self.sub_state = 4
                    self.manipulation_result = False
            elif self.sub_state == 4:
                self.returnAPI_pub.publish(True)
                rospy.sleep(1)
                self.return_pub.publish("operator")
                self.sub_state = 5 
            elif self.sub_state == 5:
                print 'state:return operator'
                if self.navigation_result == True:
                    self.returnAPI_pub.publish(False)
                    self.navigation_result = False
                    self.sub_state = 6
            elif self.sub_state == 6:
                print 'state:arm change'
                self.changing_pose_req_pub.publish('give')
                rospy.sleep(3)#かかる時間によって変更
                self.sub_state = 7
            elif self.sub_state == 7:
                self.tts_pub.publish('Please pull it up')
                rospy.sleep(2)#時間の調整あり
                self.sub_state = 8
            elif self.sub_state == 8:
                if self.arm_change_result == True:
                    rospy.sleep(2)
                    self.arm_change_result = False
                    self.sub_state = 0
                    self.succsess_count += 1
                
                
    def finishState(self):
        self.commandAPI_pub.publish(False)
        print 'state is finish'
        self.tts_pub.publish('Finished go get it')
        print "--GGI finish--"
        exit()

    def follow(self,state):
        self.follow_state = state.data

    def training(self,state):
        self.training_state = state.data 

    def setupResult(self,result):
        self.setup_result = result.data

    def navigateResult(self,result):
        self.navigation_result = result.data
        print "navi result:",self.navigation_result
        
    def receiveCommand(self,flg):
        self.receive_com = flg.data

    def manipulationObj(self,obj):
        self.mani_obj = obj.data
        
    def manipulateResult(self,result):
        self.manipulation_result = result.data

    def changePoseResult(self,result):
        self.arm_change_result = result.data

    def loopMain(self):
        print 'start [go get it]'
        self.main_state = self.order_list[0]
        while not rospy.is_shutdown():
            print 'succsess count is:',self.succsess_count
            print ''
            if self.succsess_count == 2:#succsess_count == 繰り返したい回数
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
