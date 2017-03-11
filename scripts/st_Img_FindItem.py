#!/usr/bin/env python
# -*- coding: utf-8 -*-


#--------------------------------------------------
#指定された物体を探すステートマシン
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
            smach.StateMachine.add('Img_FindItem', Img_FindItem(),
                                   transitions = {'exit1':'exit'})


#--------------------------------------------------
#--------------------------------------------------
class Img_FindItem(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['exit1'])


    def execute(self,userdata):
        #rospy.loginfo(u'ファイル名:'+os.path.basename(__file__)+u'ステート名:'+self.__class__.__name__+u'を実行')
        commonf_dbg_sm_stepin()

        i_command=rospy.get_param('/param/command/i_command')
        command=rospy.get_param('/param/command/detail')[i_command]
        rospy.set_param('/param/iarm/obj/id', int(command['What']))

        Popen(['rosrun', 'common_pkg', 'img_obj_rec.py'])

        call(['rosrun', 'common_pkg', 'img_obj_proc'])
    
        commonf_node_killer('img_obj_rec')

        commonf_dbg_sm_stepout()            
        return 'exit1'



