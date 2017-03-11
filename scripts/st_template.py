#!/usr/bin/env python
# -*- coding: utf-8 -*-


#--------------------------------------------------
#hogehogeステートマシン
#
#author: Taro HIBIKINO
#date: yy/mm/dd
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
            smach.StateMachine.add('State1', State1(),
                                   transitions = {'exit1':'State2'})
            smach.StateMachine.add('State2', State2(),
                                   transitions = {'exit2':'exit'})


#--------------------------------------------------
#最初に実行されるステート
#--------------------------------------------------
class State1(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['exit1'])


    def execute(self,userdata):
        #rospy.loginfo(u'ファイル名:'+os.path.basename(__file__)+u'ステート名:'+self.__class__.__name__+u'を実行')
        return 'exit1'


#--------------------------------------------------
#2番目に実行されるステート
#--------------------------------------------------
class State2(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['exit1'])


    def execute(self,userdata):

        #ここに処理を記述

        return 'exit1'
