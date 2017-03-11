#!/usr/bin/env python
# -*- coding: utf-8 -*-


#--------------------------------------------------
#RCJ2016 GPSR用パラメータのROSノード
#
#author: Yutaro ISHIDA
#date: 16/03/17
#--------------------------------------------------


import sys
import roslib
sys.path.append(roslib.packages.get_pkg_dir('common_pkg') + '/scripts/common')

from common_import import *
from common_function import *
from common_param import *


#--------------------------------------------------
#メイン関数
#--------------------------------------------------
if __name__ == '__main__':
    node_name = os.path.basename(__file__)
    node_name = node_name.split('.')
    rospy.init_node(node_name[0])


    rospy.set_param('/param/dbg/sm/all', 0) #bool    

    #選択されたデバッグモードを使う
    if rospy.get_param('/param/dbg/sm/all') == 0:
        #上の方が優先度高い
        rospy.set_param('/param/dbg/sm/flow', 0) #bool 全ての機能なしでsmを流す
        rospy.set_param('/param/dbg/sm/stepin', 0) #bool ステートごとにキー入力を促す
        rospy.set_param('/param/dbg/sm/stepout', 0) #bool ステートごとにキー入力を促す
        rospy.set_param('/param/dbg/speech/onlyspeech', 0) #bool 音声認識のみのデバッグ
        rospy.set_param('/param/dbg/speech/ssynlog', 0) #bool 音声合成の文章をデバッグ表示
    #全デバッグモードを使う、else以下は触らない
    else:
        rospy.set_param('/param/dbg/sm/flow', 1) #bool
        rospy.set_param('/param/dbg/sm/stepin', 1) #bool ステートごとにキー入力を促す
        rospy.set_param('/param/dbg/sm/stepout', 1) #bool ステートごとにキー入力を促す
        rospy.set_param('/param/dbg/speech/onlyspeech', 1) #bool 音声認識のみのデバッグ
        rospy.set_param('/param/dbg/speech/ssynlog', 1) #bool 音声合成の文章をデバッグ表示


    rospy.set_param('/param/command/len', 0) #int コマンド全体の長さ
    rospy.set_param('/param/command/i_command',0)#int　現在のコマンドインデックス
    rospy.set_param('/param/command/detail', [])#コマンド全体
    
    ##以下コマンドの説明
    #'コマンド名' 
    #1 '詳細'
    #2 '/param/command/detailに格納するときの形式'
    #3 '使用パラメータ'

    #'MOVE'
    #1 'Toに入っているキーの座標を/param/move/place_coordinateから探し、移動する'
    #2 '{'com_name':'MOVE','To':'#place_coordinateのキーのどれか#'}'
    #3 
    rospy.set_param('/param/place/db',[{'place_id':1, 'place_name_j':'開始点','place_name_e':'start point','pos':{'X':2.0,'Y':0.12,'Yaw':0.0},'place_class':'pos'},
                                       {'place_id':2, 'place_name_j':'フィールド外','place_name_e':'out of field','pos':{'X':8.13,'Y':-2.42,'Yaw':-1.61},'place_class':'pos'},
                                       {'place_id':3, 'place_name_j':'コリドー','place_name_e':'','pos':{'X':3.4,'Y':0.12,'Yaw':0.0},'place_class':'room'},
                                       {'place_id':4, 'place_name_j':'ダイニング','place_name_e':'','pos':{'X':4.37,'Y':5.33,'Yaw':1.59},'place_class':'room'},
                                       {'place_id':5, 'place_name_j':'ライブラリー','place_name_e':'','pos':{'X':6.36,'Y':0.27,'Yaw':0.0},'place_class':'room'},
                                       {'place_id':6, 'place_name_j':'リビング','place_name_e':'','pos':{'X':8.29,'Y':5.21,'Yaw':1.07},'place_class':'table'},
                                       {'place_id':7, 'place_name_j':'テーブルセット','place_name_e':'','pos':{'X':4.96,'Y':5.62,'Yaw':1.58},'place_class':'table'},
                                       {'place_id':8, 'place_name_j':'ダイニングテーブル','place_name_e':'','pos':{'X':5.92,'Y':6.13,'Yaw':0.0},'place_class':'table'}, 
                                       {'place_id':9, 'place_name_j':'サイドテーブル','place_name_e':'','pos':{'X':6.11,'Y':9.51,'Yaw':0.0},'place_class':'table'},
                                       {'place_id':10, 'place_name_j':'ブックシェルフ','place_name_e':'','pos':{'X':10.96,'Y':-0.10,'Yaw':-1.52},'place_class':'pos'},
                                       {'place_id':11, 'place_name_j':'リビングテーブル','place_name_e':'','pos':{'X':8.36,'Y':7.02,'Yaw':0.0},'place_class':'shell'},
                                       {'place_id':12, 'place_name_j':'ソファ','place_name_e':'','pos':{'X':8.33,'Y':7.15,'Yaw':0.0},'place_class':'pos'},
                                       {'place_id':13, 'place_name_j':'テレビボード','place_name_e':'','pos':{'X':9.73,'Y':8.42,'Yaw':1.59},'place_class':'chair'},])
  
    #'FIND_ITEM' 
    #1 'Whatに入っている名前の物体を探す' 2月6日現在　探すだけで何をするのかが不明。もし掴むだけならこのコマンドは不要
    #2 '{'com_name':'FIND_ITEM','What':'#探す物体の名前#'}'
    #3 無し 

    #'GRASP'
    #1 'Whatに入っている名前の物体を把持する'
    #2 '{'com_name':'GRASP','What':'#把持する物体のID#'}'
    #3 ''

    #'PLACE'
    #1 '現在把持している物体を指定された場所に置く'
    #2 '{'com_name':'PLACE','Where':'置く場所のID'}'
    #3 MOVEと共通

    #'HAND'
    #1 '現在把持している物体を目の前の人に渡す'
    #2 '{'com_name':'HAND'}'
    #3 無し

    #'FIND_PERSON'
    #1 '近くにいる人を探し、その人の近くまで移動する'
    #2 '{'com_name':'FIND_PERSON'}'
    #3 無し

    #'FOLLOW'
    #1 '目の前の人を追跡する'
    #2 '{'com_name':'FOLLOW'}'
    #3 無し

    #'CALL'
    #1 'Whoに入っている名前を呼ぶ'
    #2 '{'com_name':'CALL','Who':'#呼ぶ名前#'}'
    #3 無し

    #'ASK'
    #1 'Whatに入っている質問を行い、その答えを/param/ansに格納する'
    #2 '{'com_name':'ASK','What':'#質問内容#'}'
    #3 質問の答え 'TELL'と共有
    rospy.set_param('/param/ans',[])

    #'TELL'
    #1 '/param/ansに格納されている内容を教える '時間を教えて'等の答えも/param/ansに入れておく'
    #2 '{'com_name':'TELL'}'
    #3 教える内容 'ASK'と共有

    #'ANSWER'
    #1 質問を聞いて答える
    #2 '{'com_name':'ANSWER'}'
    #3 無し


    main_rate = rospy.Rate(30)
    while not rospy.is_shutdown():
        main_rate.sleep()
