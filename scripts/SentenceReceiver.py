#!/usr/bin/env python
# -*- coding: utf-8 -*

import rospy
from std_msgs.msg import String,Bool
from ti_go_get_it.msg import Multi
from tf2_msgs.msg import TFMessage

class SetenceReceiver:
    def __init__(self):
        self.com_sub = rospy.Subscriber('/voice/mode/change',String,self.ChangeState)
        self.voice_sub = rospy.Subscriber("/sentence",String,self.Voice)
        self.tf_sub = rospy.Subscriber("/tf",TFMessage,self.BaseCB)
        self.navi_entrace_sub = #玄関専用のnavigationのCB関数entranceが入ってきたら玄関へnavi

        self.follow_pub = rospy.Publisher('/follow',Bool,queue_size=10)
        self.setup_result_pub  = rospy.Publisher('/setup/result',Bool,queue_size=10)
        self.com_pub  = rospy.Publisher('/command',Bool,queue_size=10)
        self.pose_pub  = rospy.Publisher('/pose',Multi,queue_size=10)
        self.object_pub = rospy.Publisher('/object/manipulation',String,queue_size=10)

        self.pose_x=999
        self.pose_y=999
        self.append_flg = False
        self.memo_flg = False
        self.com = "null"
        
        self.setup_list = []
        self.temporary_list = []

    def Voice(self,sentence):
        print "sentence:",sentence.data
        if self.state == "setup":
            print "setup voice is",sentece.data

            if sentence.data == 'follow':#followの開始 
                self.follow_result_pub(True)
                
            if sentence.data == 'stop':#followの終了かつsetupの終了#ここまだ#
                self.setup_result_pub(True)
                self.setup_list.append('operator')
                print "pose x is",self.pose_x
                print "pose y is",self.pose_y
                self.temporary_list.insert(0,self.pose_x)
                self.temporary_list.insert(1,self.pose_y)
                self.setup_list.append(self.temporary_list)
                self.temporary_list = []
                
            if sentence.data == 'start':#記憶開始
                self.memo_flg = True
                print "-- memorize start --"
                
            if sentence.data == 'finish':#記憶の終了
                self.memo_flg = False
                if self.temporary_list != []:
                    self.temporary_list.insert(0,self.pose_x)
                    self.temporary_list.insert(1,self.pose_y)
                    self.setup_list.append(self.temporary_list)
                    self.temporary_list = []
                    self.append_flg = False
                    print "-- memorize finish --"
                    print "setup list is:",self.setup_list
                else:
                    print "/not object.try again/"
                    
            print "//please say sentence//"
            
            if self.memo_flg == True and sentence.data != 'stop' and sentence.data != 'follow' and sentence.data != 'start' and sentence.data != 'finish':
                split_sentence=sentence.data.split()
                self.temporary_list.extend(split_sentence)
                print "temporary list:",self.temporary_list

        if self.state == "command":
            print 'command is:',sentence.data
            self.com = sentence.data
            for column in range(0,len(self.setup_list)):
                for row in range(2,len(self.setup_list[column])):
                    if self.setup_list[column][row] in self.com:
                        self.com_pub.publish(True)
                        pose_x = self.setup_list[column][0]
                        pose_y = self.setup_list[column][1]
                        print 'pose_x',pose_x
                        print 'pose_y',pose_y
                        msg = Multi()
                        msg.pose_x = pose_x
                        msg.pose_y = pose_y
                        self.pose_pub.publish(msg)
                        self.object_pub.publish(self.setup_list[column][row])
                        print 'command is:',self.setup_list[column][row]
                    else:
                        print 'not ob'

    def ChangeState(self,state):
        self.state = state.data
        
    def BaseCB(self,pose):
        try:
            if pose.transforms[0].header.frame_id == 'odom':
                if self.memo_flg == True and self.append_flg == False:
                    self.pose_x=pose.transforms[0].transform.translation.x
                    self.pose_y=pose.transforms[0].transform.translation.y
                    self.append_flg = True
                    print "-- memorize place --"
        except AttributeError:
            print 'error'
            pass
                    
if __name__ == '__main__':
    rospy.init_node('SetenceReceiver',anonymous=True)
    SR=SetenceReceiver()
    rospy.spin()
