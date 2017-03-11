#!/usr/bin/env python
# -*- coding: utf-8 -*-


#--------------------------------------------------
#RCJ2016 GPSR用ステートマシンのROSノード
#
#author: Yutaro ISHIDA
#date: 16/03/21
#--------------------------------------------------


import sys
import roslib
sys.path.append(roslib.packages.get_pkg_dir('common_pkg') + '/scripts/common')

from common_import import *
from common_function import *


import st_CallPerson
import st_FollowPerson
import st_GraspItem
import st_HandItem
import st_Img_FindItem
import st_Img_FindPerson
import st_PlaceItem
import st_SLAM_Move
import st_SRec_AnswerQuestion
import st_SRec_AskPerson
import st_TelltoPerson


rospy.sleep(5) #paramノードが立ち上がるまで待つ


#--------------------------------------------------
#ステートマシン設計規則
#--------------------------------------------------
#ステートを跨ぐデータはパラメータ(/param/以下)に保存する


#--------------------------------------------------
#--------------------------------------------------
class init(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class WaitStartSig(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()

        raw_input('#####Type enter key to start#####')

        commonf_dbg_sm_stepout()
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class DetectDoorOpen(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()

        call(['rosrun', 'common_pkg','detect_dooropen.py'])

        commonf_dbg_sm_stepout()
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class SLAM_GotoCommandPosition(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['exit1'])


    def execute(self, userdata):
        commonf_dbg_sm_stepin()

        #place_db = rospy.get_param("/param/place/db")

        #commonf_actionf_move_base(place_db[0]['pos']['X'], place_db[0]['pos']['Y'], place_db[0]['pos']['Yaw'])

        commonf_dbg_sm_stepout()            
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class SRec_AskCommand(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['exit1','err_in_speech_rec'])


    def execute(self,userdata):
        commonf_dbg_sm_stepin()

        if commonf_actionf_speech_rec(self.__class__.__name__) == True: #音声認識ノードに現在のステートに対する処理が記述されていた時
            rospy.set_param('/param/command/i_command',-1)            

            commonf_speech_single('まずは経由地点に移動します。')
            commonf_actionf_move_base(6.36, 0.27, 1.57)
            commonf_speech_single('ここは経由地点です。')

            commonf_dbg_sm_stepout()
            return 'exit1'
        else: #音声認識ノードに現在のステートに対する処理が記述されていない時
            commonf_dbg_sm_stepout()            
            return 'err_in_speech_rec'


#--------------------------------------------------
#--------------------------------------------------
class SolveCommand(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['MOVE','FIND_ITEM','GRASP','PLACE','FIND_PERSON','FOLLOW','CALL','ASK','TELL','ANSWER','HAND','exit1'])


    def execute(self,userdata):
        commonf_dbg_sm_stepin()

        i_command=rospy.get_param("/param/command/i_command")+1
        rospy.set_param("/param/command/i_command",i_command)

        if i_command < rospy.get_param("/param/command/len"):
            command_details=rospy.get_param("/param/command/detail")
            command=command_details[i_command]

            commonf_dbg_sm_stepout()            
            return command['com_name']
        else:
            commonf_dbg_sm_stepout()            
            return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
class SLAM_LeaveArena(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['exit1'])

    def execute(self,userdata):
        commonf_dbg_sm_stepin()

        place_db = rospy.get_param("/param/place/db")

        commonf_actionf_move_base(place_db[1]['pos']['X'], place_db[1]['pos']['Y'], place_db[1]['pos']['Yaw'])

        commonf_dbg_sm_stepout()            
        return 'exit1'


#--------------------------------------------------
#--------------------------------------------------
if __name__ == '__main__':
    node_name = os.path.basename(__file__)
    node_name = node_name.split('.')
    rospy.init_node(node_name[0])


    sm = smach.StateMachine(outcomes=['exit'])


    #起動音を再生する
    commonf_actionf_sound_effect_single('launch')

   
    commonf_pubf_scan_mode('lrf')

    commonf_pubf_cam_pan(0.523)
    commonf_pubf_cam_tilt(0.523)
    commonf_pubf_mic_pan(-0.523)
    commonf_pubf_mic_tilt(-0.523)
    rospy.sleep(0.5)
    commonf_pubf_cam_pan(0)
    commonf_pubf_cam_tilt(0)
    commonf_pubf_mic_pan(0)
    commonf_pubf_mic_tilt(-0.349)
    rospy.sleep(0.5)

    commonf_pubf_cmd_vel(0, 0, 0, 0, 0, 0)

    commonf_actionf_cam_lift(0.555)


    #ここで入力を促して、最初のステートのトランジションを決める
    #commonf_speech_single('タスク、ＧＰＳＲをスタート。')
    #commonf_speech_single('スタートステートを指定して下さい。')
    rospy.loginfo('タスク、ＧＰＳＲをスタート')
    rospy.loginfo('スタートステートを指定して下さい')

    print '#####If you want to start from first state, please type enter key#####'
    start_state = raw_input('#####Please Input First State Name##### >> ')
    if not start_state:
        start_state = 'WaitStartSig'

    #commonf_speech_single('ステートマシンをスタート。')
    rospy.loginfo('ステートマシンをスタート')


    with sm:
        smach.StateMachine.add('init', init(), 
                               transitions={'exit1':start_state})
        smach.StateMachine.add('WaitStartSig', WaitStartSig(), 
                               transitions={'exit1':'DetectDoorOpen'})
        smach.StateMachine.add('DetectDoorOpen', DetectDoorOpen(), 
                               transitions={'exit1':'SLAM_GotoCommandPosition'})
        smach.StateMachine.add('SLAM_GotoCommandPosition', SLAM_GotoCommandPosition(), 
                               transitions={'exit1':'SRec_AskCommand'})
        smach.StateMachine.add('SRec_AskCommand', SRec_AskCommand(),
                               transitions={'exit1':'SolveCommand',
                                            'err_in_speech_rec':'exit'})
        smach.StateMachine.add('SolveCommand',SolveCommand(),
                               transitions={'MOVE':'SLAM_Move',
                                            'FIND_ITEM':'Img_FindItem',
                                            'GRASP':'GraspItem',
                                            'PLACE':'PlaceItem', #未完成
                                            'HAND':'HandItem', #未完成
                                            'FIND_PERSON':'Img_FindPerson',
                                            'FOLLOW':'FollowPerson',
                                            'CALL':'CallPerson', #多分なし
                                            'ASK':'SRec_AskPerson', #多分なし
                                            'TELL':'TelltoPerson', #多分なし
                                            'ANSWER':'SRec_AnswerQuestion',
                                            'exit1':'SLAM_LeaveArena'})
        smach.StateMachine.add('SLAM_Move',st_SLAM_Move.MainState(),
                               transitions={'exit':'SolveCommand'})
        smach.StateMachine.add('FollowPerson',st_FollowPerson.MainState(),
                               transitions={'exit':'SolveCommand'})
        smach.StateMachine.add('Img_FindItem',st_Img_FindItem.MainState(),
                               transitions={'exit':'SolveCommand'})
        smach.StateMachine.add('Img_FindPerson',st_Img_FindPerson.MainState(),
                               transitions={'exit':'SolveCommand'})
        smach.StateMachine.add('GraspItem',st_GraspItem.MainState(),
                               transitions={'exit':'SolveCommand'})
        smach.StateMachine.add('PlaceItem',st_PlaceItem.MainState(),
                               transitions={'exit':'SolveCommand'})
        smach.StateMachine.add('HandItem',st_HandItem.MainState(),
                               transitions={'exit':'SolveCommand'})
        smach.StateMachine.add('CallPerson',st_CallPerson.MainState(),
                               transitions={'exit':'SolveCommand'})
        smach.StateMachine.add('SRec_AskPerson',st_SRec_AskPerson.MainState(),
                               transitions={'exit':'SolveCommand'})
        smach.StateMachine.add('TelltoPerson',st_TelltoPerson.MainState(),
                               transitions={'exit':'SolveCommand'})
        smach.StateMachine.add('SRec_AnswerQuestion',st_SRec_AnswerQuestion.MainState(),
                               transitions={'exit':'SolveCommand'})
        smach.StateMachine.add('SLAM_LeaveArena',SLAM_LeaveArena(),
                               transitions={'exit1':'exit'})


    sis = smach_ros.IntrospectionServer('sm', sm, '/SM_ROOT')
    sis.start()


    outcome = sm.execute()


    commonf_speech_single('タスクを終了します。')
    raw_input('#####Type Ctrl + c key to end#####')


    while not rospy.is_shutdown():
        rospy.spin()
