#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import rospy
import subprocess
from geometry_msgs.msg import Twist
from std_msgs.msg import String 
import time
import json

class VoiceRecognizer:
    def __init__(self):
        self.voice_cmd_sub = rospy.Subscriber('follow/voice_cmd/input',String,self.CheckVoiceCmd)
        self.vocie_sub = rospy.Subscriber('voice_recog',String,self.Receive)
        self.command_init_sub = rospy.Subscriber('command/init',String,self.initCommand)
        self.voice_cancel_sub = rospy.Subscriber('voice/cancel',String,self.cancelVoice)

        self.recog_word_pub = rospy.Publisher('recognition/result/word',String,queue_size=10)
        self.follow_pub = rospy.Publisher('follow/command/result',String,queue_size=10)
        self.follow_request_pub = rospy.Publisher('follow/request',String,queue_size=10)
        self.changing_pose_req_pub = rospy.Publisher('/arm/changing_pose_req',String,queue_size=1)
        self.changing_pose_result_pub = rospy.Publisher('/arm_change/result',String,queue_size=1)
        self.vel_pub = rospy.Publisher('/cmd_vel_mux/input/teleop',Twist,queue_size=1)
        self.voice_cancel_pub = rospy.Publisher('voice/cancel',String,queue_size=1)
        self.command_check_pub = rospy.Publisher('command/check',String,queue_size=1)
        
        self.cmd_vel_right = Twist()
        self.cmd_vel_right.angular.z = -1.5
        self.cmd_vel_left = Twist()
        self.cmd_vel_left.angular.z = 1.5        
        self.discovery_location_num = 0
        self.discovery_object_num = 0
        self.command_num = 0
        self.voice_cancel = 'Null'
        self.recog_location = 'Null'
        self.recog_object = 'Null'
        self.sentence = ' '
        
        self.location_list = [
            [0,'kitchen','keep','key','cutting','year','bag','kill','kids','key gene','take us back to','kitty','キッチン'],
            [0,'living','leaving','levy','meeting','leading','being','evening','reading','active','media','リビング','オレフィン','livin','自民'],
            [0,'dining','died','death','ocean','ダイニング','ダイイング'],
            [0,'children','child','chear'],
            [0,'hallway','hall','host'],
            [0,'bartable','bar','table','bath','double','board'],
            [0,'balcony','bag on','about one','buck on','bargain','body going','balble'],
            [0,'bedroom','bit too','beat','bed to','but the room','bath room','but','back','better','ベッドルーム','bid to','メタル','ベッド','ルーム','ベルン','ネット'],
            [0,'entrance','interes','end of','his and the','around','enter','entire','end','anton','エントランス'],
            [0,'finish','フィニッシュ','フィッシュ']]
        self.object_list = [
            [0,'apple','apl'],
            [0,'banana','bak'],
            [0,'bikkle','vicl','びっくり','リップル','ビックル'],
            [0,'cupnoodle','カップヌードル','ヌード','カップ'],
            [0,'potelong','ポテロン','ポテロング','ポテチ'],
            [0,'chipstar','ジェットスター','チップスター']]
        self.follow_command_list = ['follow','Follow Me','ハロウィン','Follow','Follow me','フォロー','フォロミー','ホロミン','ホミン']
        self.command_list = [['right','ライト','Right','レフティ'],
                             ['left','レフト','Left'],
                             ['yes','Yes','YES','イエス'],
                             ['no','ノー','脳','No','NO'],
                             ['cancel','キャンセル'],
                             ['thank you','Thank you','サンキュー','センキュー']]

    def JsonStringToDictation(self, _json):
        #print(_json)
        dictation = json.loads(_json) # jsonで書かれた文字列を辞書型にする
        # json.loadsでunicodeに変換された文字列をstrにする
        import types
        for key in dictation:
            key_type = dictation[key]
            if type(key_type) == unicode: # unicodeをstrにする
                #print(key_type)
                #print(dictation[key])
                dictation[key] = dictation[key].encode('utf-8')
        return dictation
            
    def Receive(self, _receive_str):
        dict_data = self.JsonStringToDictation(_receive_str.data)
        self.sentence = dict_data["word"]
        self.recog_location = 'Null'
        self.recog_object = 'Null'
        self.discovery_location_num = 0
        self.discovery_object_num = 0      
        rospy.sleep(0.5)
        print 'receive voice is :',self.sentence
        if self.sentence != ' ':
            for num in range(0,len(self.location_list)):
                for words_num in range(1,len(self.location_list[num])):
                    if self.location_list[num][words_num] in self.sentence:
                        #print "word is ",self.location_list[num][1]
                        self.location_list[num][0] = self.sentence.count(self.location_list[num][words_num])                        
                    else:
                        pass
            if self.location_list[self.location_list.index(max(self.location_list))][0] > 0:                
                print '送る文字は',self.location_list[self.location_list.index(max(self.location_list))][1]
                self.recog_location = self.location_list[self.location_list.index(max(self.location_list))][1]
                for num in range(0,len(self.location_list)): 
                    self.location_list[num][0] = 0
                self.location_list[self.location_list.index(max(self.location_list))][1] == 'Null'
                self.discovery_location_num = 1
                
            for num in range(0,len(self.object_list)):
                for words_num in range(1,len(self.object_list[num])):
                    if self.object_list[num][words_num] in self.sentence:
                        #print "word is ",self.object_list[num][1]
                        self.object_list[num][0] = self.sentence.count(self.object_list[num][words_num]) 
                    else:
                        pass
            if self.object_list[self.object_list.index(max(self.object_list))][0] > 0:                
                print '送る文字は',self.object_list[self.object_list.index(max(self.object_list))][1]
                self.recog_object = self.object_list[self.object_list.index(max(self.object_list))][1]
                for num in range(0,len(self.object_list)): 
                    self.object_list[num][0] = 0
                self.object_list[self.object_list.index(max(self.object_list))][1] == 'Null'
                self.discovery_object_num = 1
                
            if self.command_num == 0 and self.discovery_location_num == 0 and self.discovery_object_num == 0:
                print 'receive command'
                for num in range(0,len(self.command_list)):
                    for words_num in range(0,len(self.command_list[num])):
                        if self.command_list[num][words_num] in self.sentence:
                            self.command_num = 1
                            print 'command is: ',self.command_list[num][0]
                            if self.command_list[num][0] == 'cancel':
                                self.voice_cancel_pub.publish('cancel')
                            if self.command_list[num][0] == 'yes' or self.command_list[num][0] == 'no':
                                print 'pub :',self.command_list[num][0]
                                self.command_check_pub.publish(self.command_list[num][0])
                            if self.command_list[num][0] == 'thank you':
                                self.changing_pose_req_pub.publish('release')
                                self.changing_pose_result_pub.publish('succsess')
                            if self.command_list[num][0] == 'right':
                                print 'right'
                                for i in range(0,500):
                                    self.vel_pub.publish(self.cmd_vel_right)
                                    print 'turn'
                                self.command_num = 0
                            if self.command_list[num][0] == 'left':
                                print 'left'
                                for i in range(0,500):
                                    self.vel_pub.publish(self.cmd_vel_left)
                                    print 'turn'
                                self.command_num = 0
                        else:
                            pass
                if self.command_num == 0:
                    print 'please say again'
            else:
                voice_word = (self.recog_location + "," + self.recog_object)
                self.recog_word_pub.publish(voice_word)
                print 'voice_word is:',voice_word

    def cancelVoice(self,result):
        print 'cancel :',result.data
        self.voice_cancel = result.data
        if self.voice_cancel == 'success':
            CMD = '/usr/bin/picospeaker %s' % 'location and object cancel'
            subprocess.call(CMD.strip().split(" "))
            rospy.sleep(1)
            self.voice_cancel = 'Null'
            self.command_num = 0
        elif self.voice_cancel == 'failed':
            print 'can not cancel'
            print 'again'
            self.voice_cancel = 'Null'
            self.command_num = 0
                
    def initCommand(self,command):
        print command.data
        print 'processing finish'
        self.command_num = 0
                          
    def CheckVoiceCmd(self,word):
        self.word = word.data
        loop = 1
        while (loop):
            rospy.sleep(0.5)
            for num in range(0,len(self.follow_command_list)):
                if self.follow_command_list[num] in self.sentence:
                    self.follow_request_pub.publish('follow')
                    self.follow_pub.publish('succsess')
                    loop = 0
                    break
        self.sentence = ' '
                                                
if __name__ == '__main__':
    rospy.init_node('ggi_voice_recognizer',anonymous=True)
    voice_recognizer = VoiceRecognizer()
    rospy.spin()
    
