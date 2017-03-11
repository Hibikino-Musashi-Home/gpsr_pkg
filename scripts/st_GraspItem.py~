#!/usr/bin/env python
# -*- coding: utf-8 -*-


#--------------------------------------------------
##指定されたオブジェクトを探し把持するステートマシン
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
            smach.StateMachine.add('GraspItem', GraspItem(),
                                   transitions = {'exit1':'ARM_Open'})
            smach.StateMachine.add('ARM_Open', ARM_Open(), 
                                   transitions = {'exit1':'ApproachToObj'})
            smach.StateMachine.add('ApproachToObj', ApproachToObj(), 
                                   transitions = {'exit1':'Img_FindObj'})
            smach.StateMachine.add('Img_FindObj', Img_FindObj(), 
                                   transitions = {'exit1':'exit',
                                                  'exit2':'ARM_GraspObj'})
            smach.StateMachine.add('ARM_GraspObj', ARM_GraspObj(), 
                                   transitions = {'exit1':'BackFromObj'})
            smach.StateMachine.add('BackFromObj', BackFromObj(), 
                                   transitions = {'exit1':'ARM_Close'})
            smach.StateMachine.add('ARM_Close', ARM_Close(), 
                                   transitions = {'exit1':'exit'})


#--------------------------------------------------
#--------------------------------------------------
class GraspItem(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['exit1'])


    def execute(self,userdata):
        #rospy.loginfo(u'ファイル名:'+os.path.basename(__file__)+u'ステート名:'+self.__class__.__name__+u'を実行')
        return 'exit1'



#--------------------------------------------------
#--------------------------------------------------
class ARM_Open(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()

        call(['rosrun', 'common_pkg', 'iarm_open.py'])
                
        commonf_dbg_sm_stepout()
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class ApproachToObj(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()
        
        call(['rosrun', 'common_pkg', 'approach_obj.py'])
                       
        commonf_dbg_sm_stepout()
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class Img_FindObj(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1', 'exit2'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()

        i_command=rospy.get_param('/param/command/i_command')
        command=rospy.get_param('/param/command/detail')[i_command]
        rospy.set_param('/param/iarm/obj/id', int(command['What']))

        Popen(['rosrun', 'common_pkg', 'img_obj_rec.py'])

        if call(['rosrun', 'common_pkg', 'img_obj_proc']) != 0:
            commonf_node_killer('img_obj_rec')

            commonf_pubf_cam_pan(0)
            commonf_pubf_cam_tilt(0)

            iarm_action_client = actionlib.SimpleActionClient('iarm_action', iARMAction)
            iarm_action_client.wait_for_server()

            goal = iARMGoal()

            goal.iarm_goal = 's:iARMCtrl,EndOpening,0,0.2:e'
            iarm_action_client.send_goal(goal)
            iarm_action_client.wait_for_result()

            goal.iarm_goal = 's:iARMCtrl,KeyCmd,i:e'
            iarm_action_client.send_goal(goal)
            iarm_action_client.wait_for_result()

            goal.iarm_goal = 's:iARMCtrl,JointAng,-1.57,0,0,0,0,0,0.785,0,0,0,0,0:e'
            iarm_action_client.send_goal(goal)
            iarm_action_client.wait_for_result()

            commonf_dbg_sm_stepout()
            return 'exit1'            
        else:
            commonf_node_killer('img_obj_rec')

            commonf_dbg_sm_stepout()            
            return 'exit2'


#--------------------------------------------------
#--------------------------------------------------
class ARM_GraspObj(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()

        Popen(['roslaunch', 'common_pkg', 'ar_tracker.launch'])

        call(['rosrun', 'common_pkg', 'iarm_grasp.py'])

        commonf_dbg_sm_stepout()
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class BackFromObj(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()

        commonf_speech_single('４５センチ後退。')
        
        commonf_pubf_cmd_vel(-0.15, 0, 0, 0, 0, 0)
        rospy.sleep(3)
        commonf_pubf_cmd_vel(0, 0, 0, 0, 0, 0)
        
        commonf_dbg_sm_stepout()
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class ARM_Close(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()
        
        call(['rosrun', 'common_pkg', 'iarm_close.py'])
                
        commonf_node_killer('ar_track_alvar')

        commonf_dbg_sm_stepout()
        return 'exit1'
