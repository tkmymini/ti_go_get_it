#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import shlex
import rospy
from std_msgs.msg import String
cmd = 'rosrun'

def command(file_name):
    try:
        # シェルコマンドを実行する
        command = cmd + ' ' + file_name
        # subprocess.check_call()
        proc = subprocess.Popen(shlex.split(command))
        proc.communicate()
    except:
        print("error")

class VoiceReceiver:
    def __init__(self):
        self.voice_sub = rospy.Subscriber('recognition/result/word',String,self.receiveVoice)
        self.state_apoitment_sub = rospy.Subscriber('state/apoitment',String,self.StateApoitment)
        self.search_list_sub = rospy.Subscriber('search/list',String,self.receiveSearchList)
        self.command_check_sub = rospy.Subscriber('command/check',String,self.checkCommand)
        
        self.location_pub = rospy.Publisher('location/voice/word',String,queue_size=10)
        self.object_pub = rospy.Publisher('object/voice/word',String,queue_size=10)
        self.command_list_pub = rospy.Publisher('command/request',String,queue_size=10)
        self.command_init_pub = rospy.Publisher('command/init',String,queue_size=1)
        self.follow_request_pub = rospy.Publisher('follow/request',String,queue_size=10)

        self.state = 'Null'
        self.sub_state = 0
        self.destination = 'Null'
        self.manipulate_object = 'Null'
        self.command_check_flg = 'Null'
        
        self.location_list = ['kichen','living','dining','children','hallway','bartable','balcony','bedroom','entrance','finish']
        self.object_list = ['apple','banana','cupnoodle','bikkle','potelong','chipstar']
        #voice_recognizerに追加したものはすべてlocation_list,object_listに追加しておく
        self.search_list = []
        
    def receiveVoice(self,voice):
        voice_array = voice.data.split(",")
        self.voice_word = voice_array
        print 'received_sentence:',self.voice_word
        print 'location:',self.voice_word[0]
        print 'object:',self.voice_word[1]              
        if self.state == 'follow':
            if 'Null' in self.voice_word:
                for location_num in range(0,len(self.location_list)):
                    if self.voice_word[0] in self.location_list[location_num]:
                        print 'send location is:',self.voice_word[0]
                        self.location_pub.publish(self.voice_word[0])
                        if self.voice_word[0] == 'entrance':
                            self.object_pub.publish('hoge')
                        if self.voice_word[0] == 'finish':
                            self.object_pub.publish('hoge')
                            self.follow_request_pub.publish('finish')
                        else:
                            pass    
                for object_num in range(0,len(self.object_list)):    
                    if self.voice_word[1] in self.object_list[object_num]:
                        print 'send object is:',self.voice_word[1]
                        self.object_pub.publish(self.voice_word[1])         
                    else:
                        pass
            else:
                print 'again'    
        elif self.state == 'navigate':
            loop = 1
            while(loop):
                for location_search_num in range(0,len(self.search_list)):
                    if self.voice_word[0] in self.search_list[location_search_num][0]:
                        self.destination = self.voice_word[0]
                        print 'location is:',self.destination
                    else:
                        pass
                for object_search_num in range(0,len(self.search_list)):
                    if self.voice_word[1] in self.search_list[object_search_num][1]:
                        self.manipulate_object = self.voice_word[1]
                        print 'manipulation object is:',self.manipulate_object
                    else:
                        pass
                print 'desti is:',self.destination
                print 'mani_ob is:',self.manipulate_object
                print 'sub_state is :',self.sub_state
                if self.destination != 'Null' and self.manipulate_object != 'Null':
                    if self.sub_state == 0:
                        command_list = ('go ' + self.destination + ','+ 'find ' + self.manipulate_object + ',' + 'manipulate ' + self.manipulate_object + ',' + 'return ' + 'finish' + ',' + 'decideOrder ' + 'hoge')                        
                        CMD = '/usr/bin/picospeaker %s' % 'Should I bring a %(object)s and %(location)s?' % {'object':self.manipulate_object,'location':self.destination}
                        subprocess.call(CMD.strip().split(" "))
                        rospy.sleep(1)
                        CMD = '/usr/bin/picospeaker %s' % 'Please answer with yes or no'
                        subprocess.call(CMD.strip().split(" "))
                        rospy.sleep(1)
                        self.sub_state = 1
                    if self.sub_state == 1:
                        if self.command_check_flg == 'yes':
                            self.command_list_pub.publish(command_list)
                            print 'command list is:'
                            print command_list
                            print ''
                            self.destination = 'Null'
                            self.manipulate_object = 'Null'
                            self.voice_word[0] = 'Null'
                            self.voice_word[1] = 'Null'
                            self.command_check_flg = 'Null'
                            self.command_init_pub.publish('yes')
                            self.sub_state = 2
                        if self.command_check_flg == 'no':
                            self.destination = 'Null'
                            self.manipulate_object = 'Null'
                            self.voice_word[0] = 'Null'
                            self.voice_word[1] = 'Null'
                            self.command_check_flg = 'Null'
                            self.sub_state = 0
                            self.command_init_pub.publish('no')
                            CMD = '/usr/bin/picospeaker %s' % 'please again order'
                            subprocess.call(CMD.strip().split(" "))
                            rospy.sleep(2)
                            self.sub_state = 2
                    if self.sub_state == 2:
                        self.sub_state = 0
                        loop = 0
                        pass
                                
                elif self.destination == 'Null' and self.manipulate_object != 'Null' or self.destination != 'Null' and self.manipulate_object == 'Null':
                        self.destination = 'Null'
                        self.manipulate_object = 'Null'
                        self.voice_word[0] = 'Null'
                        self.voice_word[1] = 'Null'
                        CMD = '/usr/bin/picospeaker %s' % 'please again order'
                        subprocess.call(CMD.strip().split(" "))
                        rospy.sleep(2)                            
                        loop = 0
                        
    def StateApoitment(self,state):
        self.state = state.data
        print 'state is: ',self.state

    def checkCommand(self,check):
        print 'receive responce'
        if check.data == 'yes':
            self.command_check_flg = 'yes'
        elif check.data == 'no':
            self.command_check_flg = 'no'

    def receiveSearchList(self,follow_list):
        search_list = follow_list.data.split(",")
        self.search_list.append(search_list)
        print 'search list is:',self.search_list
            
if __name__ == '__main__':
    rospy.init_node('ggi_voice_receiver',anonymous=True)
    voice_receiver = VoiceReceiver()
    rospy.spin()
