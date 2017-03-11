#!/usr/bin/env python
# -*- coding: utf-8 -*-


#--------------------------------------------------
#質問をして答えを記録するステートマシン
#
#author: Yuta KIYAMA
#date: 16/03/12
#--------------------------------------------------


import sys
import roslib
sys.path.append(roslib.packages.get_pkg_dir('common_pkg') + '/scripts/common')

from common_import import *
from common_function import *


#--------------------------------------------------
#ステートマシン設計規則
#--------------------------------------------------
#ステートを跨ぐデータはパラメータ(/param/以下)に保存する


#--------------------------------------------------
#このファイル内のステートマシンの宣言部分
#--------------------------------------------------
class MainState(smach.StateMachine):
    def __init__(self):
        smach.StateMachine.__init__(self, outcomes=['exit'])
        with self:
        #以降にステートを追加
            smach.StateMachine.add('SRec_AskPerson', SRec_AskPerson(),
                                   transitions={'exit1':'exit', 
                                                'err_in_speech_rec':'exit'})


#--------------------------------------------------
#--------------------------------------------------
class SRec_AskPerson(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['exit1','err_in_speech_rec'])


    def execute(self,userdata):
        #rospy.loginfo(u'ファイル名:'+os.path.basename(__file__)+u'ステート名:'+self.__class__.__name__+u'を実行')
        commonf_dbg_sm_stepin()

        if commonf_actionf_speech_rec(self.__class__.__name__) == True: #音声認識ノードに現在のステートに対する処理が記述されていた時
            commonf_dbg_sm_stepout()
            return 'exit1'
        else: #音声認識ノードに現在のステートに対する処理が記述されていない時
            commonf_dbg_sm_stepout()            
            return 'err_in_speech_rec'

