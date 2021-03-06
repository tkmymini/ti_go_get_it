#!/usr/bin/env python
# -*- coding: utf-8 -*

import rospy
from std_msgs.msg import String,Bool
from ti_go_get_it.msg import Multi
from tf2_msgs.msg import TFMessage
from nav_msgs.msg import Odometry

class SetenceReceiver:
    def __init__(self):
        self.followAPI_sub = rospy.Subscriber('/followface',Bool,self.fAPI)
        self.trainingAPI_sub = rospy.Subscriber('/trainingface',Bool,self.tAPI)
        self.commandAPI_sub = rospy.Subscriber('/commandface',Bool,self.cAPI)
        self.returnAPI_sub = rospy.Subscriber('/returnface',Bool,self.rAPI)
        self.voice_sub = rospy.Subscriber("/sentence",String,self.voice)
        self.tf_sub = rospy.Subscriber("/odom",Odometry,self.BaseCB)

        self.follow_state_pub = rospy.Publisher('/follow/state',String,queue_size=1)
        self.training_state_pub = rospy.Publisher('/training/state',String,queue_size=1)
        self.setup_result_pub  = rospy.Publisher('/setup/result',Bool,queue_size=1)
        self.com_pub  = rospy.Publisher('/command',Bool,queue_size=1)
        self.pose_pub  = rospy.Publisher('/pose',Multi,queue_size=1)
        self.object_pub = rospy.Publisher('/object/manipulation',String,queue_size=10)

        self.pose_x=999
        self.pose_y=999
        self.pose_z=999
        self.pose_w=999
        self.sentence = "null"
        self.pose_flg = False
        self.f_state = False
        self.t_state = False
        self.c_state = False
        self.r_state = False
        self.setup_list = []
        self.temporary_list = []

    def voice(self,sentence):
        self.sentence = sentence.data
        print "sentence:",sentence.data

    def fAPI(self,f_state): 
        self.f_state = f_state.data
     
    def tAPI(self,t_state):
        self.t_state = t_state.data
        
    def cAPI(self,c_state):
        self.c_state = c_state.data
        
    def rAPI(self,r_state):
        self.r_state = r_state.data
        
    def API(self):
        while not rospy.is_shutdown():
            print 'which state'
            self.sentence = 'null'
            while (self.f_state):#followface
                print 'followface'
                if self.sentence == 'follow':#followの開始 
                    self.follow_state_pub.publish('start')
                    self.sentence = 'null'
                elif self.sentence == 'stop':#followの終了
                    self.follow_state_pub.publish('stop')
                    self.sentence = 'null'
                    self.pose_flg = True
                                 
            while (self.t_state):#trainingface
                print 'trainingface'
                print 'setup list:'
                print self.setup_list
                print ''
                if self.sentence == 'finish':#記憶の終了
                    self.training_state_pub.publish('finish')
                    if self.temporary_list != []:
                        self.temporary_list.insert(0,self.pose_x)#x座標を0列目
                        self.temporary_list.insert(1,self.pose_y)#y座標を1列目
                        self.temporary_list.insert(2,self.pose_z)#z座標を2列目
                        self.temporary_list.insert(3,self.pose_w)#w座標を3列目
                        self.setup_list.append(self.temporary_list)#座標とオブジェクト情報を含んだlistをsetup_listに追加
                        self.temporary_list = []
                        self.sentence = 'null'
                    elif self.temporary_list == []:#temporary_listの中身が空なら何も追加しない
                        print 'not add list'
                        self.sentence = 'null'
                
                if self.sentence == 'change':#faceの切り替わり[setup→ command]オペの場所で終わるとしてその座標を記憶する
                    self.temporary_list= ['operator']
                    self.temporary_list.insert(0,self.pose_x)
                    self.temporary_list.insert(1,self.pose_y)
                    self.temporary_list.insert(2,self.pose_z)
                    self.temporary_list.insert(3,self.pose_w)
                    self.setup_list.append(self.temporary_list) 
                    self.temporary_list = []
                    self.sentence = 'null'
                    self.setup_result_pub.publish(True)
        
                if self.sentence != 'null' and self.sentence != 'operator' and self.sentence != 'stop' and self.sentence != 'follow' and self.sentence != 'start' and self.sentence != 'finish':#これらはコマンドなので配列に追加しないようにはじく#operatorは決まっているので途中で追加しないようにはじく
                    split_sentence=self.sentence.split()
                    self.temporary_list.extend(split_sentence)#sentenceを一時的にtemporary_listに格納
                    #self.pose_flg = False
                    print "temporary list:",self.temporary_list
                    self.sentence = 'null'
                                                    
            while (self.c_state):#commandface
                print 'command fase'
                print "setup_list:",self.setup_list
                if self.sentence != 'null':
                    for column in range(0,len(self.setup_list)):
                        for row in range(4,len(self.setup_list[column])):
                            if self.setup_list[column][row] in self.sentence:
                                self.com_pub.publish(True)
                                pose_x = self.setup_list[column][0]#x座標(命令の物体または目的地の)
                                pose_y = self.setup_list[column][1]#y座標(命令の物体または目的地の)
                                pose_z = self.setup_list[column][2]#z座標(命令の物体または目的地の)
                                pose_w = self.setup_list[column][3]#w座標(命令の物体または目的地の)
                                msg = Multi()
                                msg.pose_x = pose_x
                                msg.pose_y = pose_y
                                msg.pose_z = pose_z
                                msg.pose_w = pose_w
                                self.pose_pub.publish(msg)#[x,y,z,w]の配列をnavigationにpublish
                                print "msg:",msg
                                rospy.sleep(10)
                                self.object_pub.publish(self.setup_list[column][row])#把持するオブジェクトをマスタにpublish
                                #print 'command is:',self.setup_list[column][row]
                    self.sentence = 'null'

                elif self.sentence == 'null':
                    print '           //waiting command//'
                    
            while (self.r_state):#returnface
                print 'return fase'
                print "sentence:",self.sentence
                if self.sentence != 'null':
                    for column in range(0,len(self.setup_list)):
                        for row in range(4,len(self.setup_list[column])):
                            if self.setup_list[column][row] in self.sentence:
                                pose_x = self.setup_list[column][0]#x座標(命令の物体または目的地の)
                                pose_y = self.setup_list[column][1]#y座標(命令の物体または目的地の)
                                pose_z = self.setup_list[column][2]#z座標(命令の物体または目的地の)
                                pose_w = self.setup_list[column][3]#w座標(命令の物体または目的地の)
                                msg = Multi()
                                msg.pose_x = pose_x
                                msg.pose_y = pose_y
                                msg.pose_z = pose_z
                                msg.pose_w = pose_w
                                print "msg",msg
                                rospy.sleep(10)
                                self.pose_pub.publish(msg)#[x,y,z,w]の配列をnavigationにpublish
                    self.sentence = 'null'
                                
    def BaseCB(self,pose):
        try:
            print 'x:',pose.pose.pose.position.x
            print 'y:',pose.pose.pose.position.y
            print 'z:',pose.pose.pose.orientation.z
            print 'w:',pose.pose.pose.orientation.w
            if self.pose_flg == True:
                self.pose_x=pose.pose.pose.position.x
                self.pose_y=pose.pose.pose.position.y
                self.pose_z=pose.pose.pose.orientation.z
                self.pose_w=pose.pose.pose.orientation.w
                self.pose_flg = False
                print "-- memorize place --"
        except AttributeError:
            print 'error'
            pass
                    
if __name__ == '__main__':
    rospy.init_node('SetenceReceiver',anonymous=True)
    SR=SetenceReceiver()
    SR.API()
    rospy.sleep(1)
    rospy.spin()
