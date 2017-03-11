#!/usr/bin/env python
# -*- coding: utf-8 -*-


#--------------------------------------------------
#人を探すステートマシン
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
            smach.StateMachine.add('Img_FindPerson', Img_FindPerson(),
                                   transitions = {'exit1':'exit'})


#--------------------------------------------------
#--------------------------------------------------
class Img_FindPerson(smach.State):
    def __init__(self):
        smach.State.__init__(self,outcomes=['exit1'])

    def execute(self,userdata):
        #rospy.loginfo(u'ファイル名:'+os.path.basename(__file__)+u'ステート名:'+self.__class__.__name__+u'を実行')
        commonf_dbg_sm_stepin()

        if rospy.get_param('/param/dbg/sm/flow') == 0 and rospy.get_param('/param/dbg/speech/onlyspeech') == 0:        
            commonf_speech_single('カメラモード切り替え中。')

            call(['rosnode', 'kill', '/camera/camera_nodelet_manager'])    
            call(['rosnode', 'kill', '/camera/depth_metric'])
            call(['rosnode', 'kill', '/camera/depth_metric_rect'])
            call(['rosnode', 'kill', '/camera/depth_points'])
            call(['rosnode', 'kill', '/camera/depth_rectify_depth'])
            call(['rosnode', 'kill', '/camera/depth_registered_rectify_depth'])
            call(['rosnode', 'kill', '/camera/points_xyzrgb_hw_registered'])
            call(['rosnode', 'kill', '/camera/rectify_color'])
            rospy.sleep(5)

            os.system('yes | rosnode cleanup')
            os.system('echo horihori|sudo -S service udev reload')
        
            Popen(['rosrun', 'openni_tracker', 'openni_tracker'])
            rospy.sleep(2)


        call(['rosrun', 'common_pkg', 'detect_approach_parson.py'])


        if rospy.get_param('/param/dbg/sm/flow') == 0 and rospy.get_param('/param/dbg/speech/onlyspeech') == 0:        
            commonf_speech_single('カメラモード切り替え中。')        

            commonf_node_killer('openni_tracker')
            rospy.sleep(5)
        
            os.system('yes | rosnode cleanup')
            os.system('echo horihori|sudo -S service udev reload')

            Popen(['roslaunch', 'openni2_launch', 'openni2.launch'])
            rospy.sleep(2)

        commonf_dbg_sm_stepout()
        return 'exit1'
