#! /usr/bin/env python
# -*- coding: utf-8 -*-


#--------------------------------------------------
#RCJ2016 GPSR用音声認識ActionのROSノード
#
#author: Takahiro TSUCHIDA
#date: 16/03/21
#--------------------------------------------------


#-----------speech recognition------------------------
from __future__ import print_function
import socket
from contextlib import closing
import commands
from copy import deepcopy

import re
import MeCab
import csv
import numpy as np
import copy
#-----------speech recognition------------------------


import sys
import roslib
sys.path.append(roslib.packages.get_pkg_dir('common_pkg') + '/scripts/common')

from common_import import *
from common_function import *

rospy.sleep(5) #paramノードが立ち上がるまで待つ


#--------------------------------------------------
#--------------------------------------------------
class SpeechRec(object):
    #--------------------------------------------------
    #-------------------------------------------------- 
    def __init__(self, julius_bufsize, julius_sock, RecgDicts, verbClass):
        self._speech_rec_action_server = actionlib.SimpleActionServer('speech_rec_action', SpeechRecAction, execute_cb = self.speech_rec)
        self._speech_rec_action_server.start()
        self.julius_bufsize = julius_bufsize
        self.julius_sock = julius_sock
        self.RecgDicts = RecgDicts
        self.verbClass = verbClass

    #--------------------------------------------------
    #-------------------------------------------------- 
    def speech_rec(self, goal):
        #--------------------------------------------------
        #コマンドを受け付け、時系列に添ってパラメータサーバに格納する。また、格納した後、オペレータにコマンドが正しいか確認する
        #-------------------------------------------------- 
        if goal.speech_rec_goal == 'SRec_AskCommand':
            if rospy.get_param('/param/dbg/sm/flow') == 0:
                commonf_speech_single('オペレーターさん、開始音のあとに、命令をどうぞ。')
                #rospy.sleep(1.5)

                rospy.set_param('/param/command/i_command', 0)
                text2id = {}
                places = rospy.get_param('/param/place/db')
                text2id['places'] = dict([[place['place_name_j'].encode('utf-8'), place['place_id']] for place in places])
                objs = rospy.get_param('/param/obj/db')
                text2id['objs'] = dict([[obj['obj_name_j'].encode('utf-8'), obj['obj_id']] for obj in objs])

                cmd_understand_flag = 0
                cmd_list = []
                while 1:
                    elements = {
                        'Locations': [[0, '開始点']],
                        'Items': [[1, '物体']],
                        'Names': [[2, '人']],
                        #'Contents': [[3, '時間']],
                    }

                    print('-------- Ask Command -------------')
                    text = self.voice2text()
                    words = self.textSplit(text)

                    v_count = 0
                    for word in words:
                        if word[0] == 1:
                            v_count += 1

                    if text == '':
                        pass
                    elif v_count < 3:  # 3:
                        commonf_speech_single('すみません。聞き取れませんでした。カスタムオペレータのかたに変わってください')
                    else:
                        #print(text)
                        try:
                            actions = self.setActions_cat1(words, elements)
                            # 表示
                            for action in actions:
                                if action[0] in ['Move_in', 'Move_out', 'Move_fin', 'Move_return']:
                                    cmd_list.append({'com_name': 'MOVE', 'To': action[1]['To']})
                                elif action[0] == 'Find' and 'Item' in action[1]:
                                    cmd_list.append({'com_name': 'FIND_ITEM', 'What': action[1]['Item']})
                                elif action[0] == 'Find' and 'Name' in action[1]:
                                    cmd_list.append({'com_name': 'FIND_PERSON'})
                                #elif action[0] == 'Grasp&Move':
                                #    cmd_list.append({'com_name': 'GRASP', 'What': action[1]['Item']})
                                #    cmd_list.append({'com_name': 'MOVE', 'To': action[1]['To']})
                                #    cmd_list.append({'com_name': 'PLACE'})
                                elif action[0] == 'Grasp':
                                    cmd_list.append({'com_name': 'FIND_ITEM', 'What': action[1]['Item']})
                                    cmd_list.append({'com_name': 'GRASP', 'What': action[1]['Item']})
                                elif action[0] == 'Place':
                                    cmd_list.append({'com_name': 'MOVE', 'To': action[1]['To']})
                                    cmd_list.append({'com_name': 'PLACE', 'To': action[1]['To']})
                                #elif action[0] == 'Dump':
                                #    cmd_list.append({'com_name': 'MOVE', 'To': action[1]['To']})
                                #    cmd_list.append({'com_name': 'PLACE'})
                                elif action[0] == 'Follow':
                                    cmd_list.append({'com_name': 'FIND_PERSON'})
                                    cmd_list.append({'com_name': 'FOLLOW'})
                                #elif action[0] == 'Call':
                                #    cmd_list.append({'com_name': 'CALL', 'who': action[1]['Name']})
                                #elif action[0] == 'Ask':
                                #    cmd_list.append({'com_name': 'FIND_PERSON'})
                                #    cmd_list.append({'com_name': 'Ask', 'What': action[1]['Content']})
                                #elif action[0] == 'Tell':
                                #    cmd_list.append({'com_name': 'FIND_PERSON'})
                                #    cmd_list.append({'com_name': 'Tell'})
                                elif action[0] == 'Answer':
                                    cmd_list.append({'com_name': 'FIND_PERSON'})
                                    cmd_list.append({'com_name': 'ANSWER'})
                                elif action[0] == 'Hand':
                                    cmd_list.append({'com_name': 'HAND'})
                                else:
                                    pass

                            # 同じものが連続しているのを削除
                            del_list = []
                            for i in xrange(len(cmd_list)-1):
                                if cmd_list[i] == cmd_list[i+1]:
                                    del_list.append(i+1)
                            for i in del_list[-1::-1]:
                                del cmd_list[i]

                            # FIND_ITEM + GRASP の場合 FIND_ITEM を削除
                            del_list = []
                            for i in xrange(len(cmd_list)-1):
                                if cmd_list[i]['com_name'] == 'FIND_ITEM' and cmd_list[i+1]['com_name'] == 'GRASP':
                                    del_list.append(i)
                            for i in del_list[-1::-1]:
                                del cmd_list[i]
                            

                            cmds = '命令は、'
                            #print(len(cmd_list), cmd_list)
                            flag_follow = 0
                            for cmd in cmd_list:
                                if flag_follow == 1:
                                    cmds += '移動したあとに、'
                                    flag_follow == 0
                                if cmd['com_name'] == 'MOVE':
                                    cmds += cmd['To']+'に移動して、'
                                elif cmd['com_name'] == 'FIND_ITEM':
                                    cmds += cmd['What']+'を見つけて、'
                                elif cmd['com_name'] == 'GRASP':
                                    cmds += cmd['What']+'を見つけて、それを掴んで、'
                                elif cmd['com_name'] == 'PLACE':
                                    cmds += cmd['To']+'に置いて、'
                                elif cmd['com_name'] == 'HAND':
                                    cmds += 'それを渡して、'
                                elif cmd['com_name'] == 'FIND_PERSON':
                                    cmds += 'ひとを見つけて、'
                                elif cmd['com_name'] == 'FOLLOW':
                                    cmds += 'そのひとに着いて行って、'
                                    flag_follow = 1
                                elif cmd['com_name'] == 'ANSWER':
                                    cmds += 'そのひとの質問に答えて、'

                                for k, v in cmd.items():
                                    if k == 'To':
                                        cmd['To'] = int(text2id['places'][v])
                                    elif k == 'What':
                                        cmd['What'] = int(text2id['objs'][v])
                                    else:
                                        pass
                                        
                            cmds += 'でいいですか？'
                            
                            if cmds == '命令は、でいいですか？':
                                cmd_list = []
                                commonf_speech_single('おかしな文章が入力されました。カスタムオペレータのかたに変わってください')
                            else:
                                commonf_speech_single(cmds)
                                commonf_speech_single('開始音の後に、それであってるよ。間違ってるよ。でお答え下さい。')

                                while 1:
                                    print('-------- ok or ng -------------')
                                    text1 = self.voice2text()
                                    flag = self.returnFlag('CMD', text1)
                                    if text1 == '':
                                        pass
                                    elif flag == 'ok':
                                        #commonf_speech_single('かしこまりました')
                                        cmd_understand_flag = 1
                                        break
                                    elif flag == 'ng':
                                        cmd_list = []
                                        commonf_speech_single('すみません。命令を全部聞き取れませんでした。カスタムオペレータのかたが命令を言ってください')
                                        break
                                    else:
                                        commonf_speech_single('もう一度、開始音のあとに、それであってるよ。か。間違ってるよ。を言ってください。')

                        except (TypeError, NameError, KeyError) as Err:
                            commonf_speech_single('おかしな文章が入力されました。カスタムオペレータのかたに変わってください')
                            print(Err)
                            cmd_list = []

                        if cmd_understand_flag == 1:    
                            # 最後が MOVE to フィールド外 の場合 MOVE を削除
                            if cmd_list[-1]['com_name'] == 'MOVE':
                                if cmd_list[-1]['To'] == int(text2id['places']['フィールド外']):
                                    del cmd_list[-1]
                            break

                #場所や物体名をidに変換

                rospy.set_param('/param/command/detail', cmd_list)
                rospy.set_param('/param/command/len', len(cmd_list))
                print(len(cmd_list), cmd_list)
                #以下rulebook2015Category1のサンプル
                #[ベッドルームに行って、人を探して、その人の質問に答えて]
                #rospy.set_param('/param/command/detail', [{'com_name':'MOVE','To':'BEDROOM'},
                #                                          {'com_name':'FIND_PERSON'},
                #                                          {'com_name':'ANSWER'}])
                #rospy.set_param('/param/command/len',3)
                #rospy.set_param('/param/ans',datetime.now().strftime("現在時刻は%Y年%m月%d日 %H時%M分%S秒です"))

                #[ディナーテーブルに行って、クラッカーを掴んで、サイドテーブルに持っていって]
                #rospy.set_param('/param/command/detail', [{'com_name':'MOVE','To':'DINNERTABLE'},
                #                                          {'com_name':'GRASP','What':'crackers'},
                #                                          {'com_name':'MOVE','To':'SIDETABLE'},
                #                                          {'com_name':'PLACE'}])
                #rospy.set_param('/param/command/len',4)

                #[リビングルームにいる人にコーラを持っていって、彼の質問に答えて]
                #rospy.set_param('/param/command/detail',[{'com_name':'MOVE','To':'COLAPOINT'},
                #                                         {'com_name':'GRASP','What':'COLA'},
                #                                         {'com_name':'MOVE','To':'LIVINGROOM'},
                #                                         {'com_name':'FIND_PERSON'},
                #                                         {'com_name':'HAND'},
                #                                         {'com_name':'ANSWER'}])
                #rospy.set_param('/param/command/len',6)

                #[ドアに行って、そこにいる人に名前を聞いて、私におしえて]
                #rospy.set_param('/param/command/detail',[{'com_name':'MOVE','To':'DOOR'},
                #                                         {'com_name':'FIND_PERSON'},
                #                                         {'com_name':'ASK','What':'name'},
                #                                         {'com_name':'MOVE','To':'OPERATOR'},
                #                                         {'com_name':'TELL'}])
                #rospy.set_param('/param/command/len',5)
                #rospy.set_param('/param/ans',datetime.now().strftime("現在時刻は%Y年%m月%d日 %H時%M分%S秒です"))

                pass

            commonf_speech_single('コマンドを理解しました。')

            result = SpeechRecResult(speech_rec_result = True)
            self._speech_rec_action_server.set_succeeded(result)


        #--------------------------------------------------
        #-------------------------------------------------- 
        elif goal.speech_rec_goal == 'SRec_AskPerson':
            if rospy.get_param('/param/dbg/sm/flow') == 0:
                # i_command = rospy.get_param('/param/command/i_command')
                # command = rospy.get_param('/param/command/detail')[i_command]
                # TODO 質問の答えを/param/ansに格納する
                # if command['What'] == '名前':
                    # commonf_speech_single('質問します。あなたの名前はなんですか。')
                # if command['What'] == '時間':
                    # commonf_speech_single('質問します。今は何時何分ですか。')
                commonf_speech_single('処理が記述されていません')
                pass

            result = SpeechRecResult(speech_rec_result = True)
            self._speech_rec_action_server.set_succeeded(result)
          
  
        #--------------------------------------------------
        #--------------------------------------------------
        elif goal.speech_rec_goal == 'FollowPerson':
            if rospy.get_param('/param/dbg/sm/flow') == 0:
                #追跡停止の呼びかけを認識する
                #[止まって]
                while 1:
                    stop_flag = 0
                    text1 = self.voice2text()
                    flag = self.returnFlag('CMD', text1)
                    if text1 == '':
                        pass
                    elif flag == 'stop':
                        commonf_speech_single('止まります。')
                        break
                        #commonf_speech_single('止まりますか？')
                        #while 1:
                        #    text2 = self.voice2text()
                        #    flag = self.returnFlag('CMD', text2)
                        #    if text == '':
                        #        pass
                        #    elif flag == 'ok':
                        #        stop_flag = 1
                        #        break
                        #    elif flag == 'ng':
                        #        commonf_speech_single('追跡を再開します。１メートル前に立ってください')
                        #        break
                        #    else:
                        #if stop_flag == 1:
                        #    break
                    else:
                        commonf_speech_single('すみません。聞き取れませんでした。')

                #commonf_speech_single('処理が記述されていません')
                pass

            result = SpeechRecResult(speech_rec_result = True)
            self._speech_rec_action_server.set_succeeded(result)


        #--------------------------------------------------
        #--------------------------------------------------
        elif goal.speech_rec_goal == 'SRec_AnswerQuestion':
            if rospy.get_param('/param/dbg/sm/flow') == 0:
                i_command = rospy.get_param('/param/command/i_command')
                command = rospy.get_param('/param/command/detail')[i_command]
                commonf_speech_single('質問をどうぞ')
                anss = {
                    'q1': 'わたしは、ふくおかけんからきました',  # どこからきましたか
                    'q2': '私の名前は、えくしあです',  # あなたの名前は
                    'q3': '今日は、はれです',  # 今日の天気は
                    'q4': '今日は、さんがつにじゅうごにちです',  # 今日の日付は
                    'q5': '今日は、きんようびです',  # 今日は何曜日ですか
                    'q6': 'ここは、あいちこうぎょうだいがくです',  # ここはどこですか
                    'q7': '私のしょぞくは、ひびきのむさしあっとほーむです',  # 所属名を教えてください
                    }
                while 1:
                    q_num = self.voice2text()
                    if q_num in ['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7']:
                        ans = anss[q_num]
                        commonf_speech_single(ans)
                        break

            result = SpeechRecResult(speech_rec_result = True)
            self._speech_rec_action_server.set_succeeded(result)


        #--------------------------------------------------
        #--------------------------------------------------
        else:
            rospy.logwarn('[speech_rec]: ステートに対する処理が記述されていません。')
            result = SpeechRecResult(speech_rec_result = False)
            self._speech_rec_action_server.set_succeeded(result)


    #--------------------------------------------------
    #-------------------------------------------------- 
    def setActions_cat1(self, words, elements):
        i = 4
        actions = []

        actionClass = {
            '1': ['Move_in', {'To': ''}],
            '2': ['Move_out', {'To': 'フィールド外'}],
            '3': ['Move_fin', {'To': 'フィールド外'}],
            '4': ['Move_return', {'To': elements['Locations'][-1][1]}],
            '5': ['Find', {'Item': '', 'Name': ''}],
            '6': ['Grasp', {'Item': ''}],
            #'7': ['Grasp&Move', {'To': '', 'Item': ''}],
            '8': ['Place', {'To': '', 'Item': ''}],
            #'9': ['Dump', {'To': 'ダストビン', 'Item': ''}],
            '10': ['Follow', {'Name': ''}],
            #'11': ['Call', {'Name': ''}],
            #'12': ['Ask', {'Content': ''}],
            #'13': ['Tell', {}],
            '14': ['Answer', {}],
            '15': ['Hand', {}]
        }

        for word in words:
            if word[0]:
                verb = word[1]
                #csvを用いて動詞を分類して必要な要素を抽出
                verbInfos = np.array(self.verbClass[1:]).T.tolist()
                try:
                    vclass = verbInfos[1][verbInfos[0].index(verb)]
                except:
                    print("error : non verb List "+verb)
                else:
                    if vclass == '999':
                        pass
                    else:
                        action = actionClass[vclass]
                        if vclass == '1':
                            action[1]['To'] = elements['Locations'][-1][1]
                        elif vclass == '2':
                            pass
                        elif vclass == '3':
                            pass
                        elif vclass == '4':
                            pass
                        elif vclass == '5':
                            if elements['Items'][-1][0] > elements['Names'][-1][0]:
                                action[1]['Item'] = elements['Items'][-1][1]
                                del action[1]['Name']
                            else:
                                action[1]['Name'] = elements['Names'][-1][1]
                                del action[1]['Item']
                        elif vclass == '6':
                            action[1]['Item'] = elements['Items'][-1][1]
                        elif vclass == '7':
                            action[1]['To'] = elements['Locations'][-1][1]
                            action[1]['Item'] = elements['Items'][-1][1]
                        elif vclass == '8':
                            action[1]['To'] = elements['Locations'][-1][1]
                            action[1]['Item'] = elements['Items'][-1][1]
                        elif vclass == '9':
                            action[1]['Item'] = elements['Items'][-1][1]
                        elif vclass == '10':
                            action[1]['Name'] = elements['Names'][-1][1]
                        elif vclass == '11':
                            action[1]['Name'] = elements['Names'][-1][1]
                        elif vclass == '12':
                            action[1]['Name'] = elements['Names'][-1][1]
                        #elif vclass == '13':
                        #    action[1]['Content'] = elements['Contents'][-1][1]
                        elif vclass == '14':
                            pass
                        elif vclass == '15':
                            pass
                        else:
                            action = 'error'
                        actions.append(deepcopy(action))

            else:
                for name in self.RecgDicts['Names']:
                    if word[1] == name:
                        elements['Names'].append([i, name])
                for item in self.RecgDicts['Items']:
                    if word[1] == item:
                        elements['Items'].append([i, item])
                for loc in self.RecgDicts['Locations']:
                    if word[1] == loc:
                        elements['Locations'].append([i, loc])
                #for content in self.RecgDicts['Contents']:
                #    if word[1] == loc:
                #        elements['Contents'].append([i, content])
                i += 1

        return actions


    #--------------------------------------------------
    #-------------------------------------------------- 
    def transVerbOrg(self, text):
        MeCabMode = '-Ochasen'
        tagger = MeCab.Tagger(MeCabMode)
        node = tagger.parseToNode(text)
        s = ''
        while node:
            surface = node.surface
            meta = node.feature.split(",")
            if meta[0] == '動詞':
                s += meta[6]
            elif meta[1] == '格助詞':
                s += surface
            elif meta[0] == '名詞':
                s += surface
            else:
                pass
            node = node.next
        return s


    #--------------------------------------------------
    #-------------------------------------------------- 
    def textSplit(self, text):
        text = text.replace('取って', '持って')
        text = text.replace('にある', '行く')
        text = text.replace('にいる', '行く')
        text = text.replace('持って来て', '把持する戻る渡す')
        text = text.replace('持って行って', '把持する行く置く')
        text = text.replace('から持って来て', '行く把持する戻る渡す')
        text = text.replace('来て', '戻る')
        text = text.replace('付いて行って', '追跡する')
        text = text.replace('置かれた', '行く')
        text = text.replace('の上', '行く')
        textVerbOrg = self.transVerbOrg(text)
        #print(textVerbOrg)

        MeCabMode = '-Ochasen'
        tagger = MeCab.Tagger(MeCabMode)
        node = tagger.parseToNode(textVerbOrg)
        words = []
        noun_flag = 0
        while node:
            surface = node.surface
            meta = node.feature.split(",")
            if meta[0] == '名詞' and noun_flag:
                words[-1][1] += node.surface
                noun_flag = 1
            elif meta[0] == '名詞':
                words.append([0, node.surface])
                noun_flag = 1
            elif meta[0] == '動詞' and meta[6] == 'する' and noun_flag:
                words[-1][1] += 'する'
                words[-1][0] = 1
                noun_flag = 0
            elif meta[0] == '動詞':
                words.append([1, meta[6]])
                noun_flag = 0
            else:
                noun_flag = 0

            node = node.next

        return words


    #--------------------------------------------------
    #Juliusから返ってきた出力（sock,bufsize,XML形式）から、文章部分の抽出を行う関数
    #-------------------------------------------------- 
    def voice2text(self):
        #sentence = ''
        #追加socket削除するため以下2行を追加
        socket = self.julius_sock
        commonf_actionf_sound_effect_multi('speech_rec')
        rospy.sleep(0.5)
        os.system('amixer -c 2 sset "Mic" 40%')
        #rospy.sleep(0.5)
        recv_data = socket.recv(self.julius_bufsize)
        recv_data = ''
        #print('------ speech rec start ------------')
        while True:
            #socket = self.julius_sock
            recv_data += socket.recv(self.julius_bufsize)
            #sentence_start = re.findall(r'<s>', recv_data)
            sentence_end = re.findall(r'</s>', recv_data)
            if sentence_end:
                sentence = ''
                matchs = re.findall(r'<WHYPO WORD=".*?"', recv_data)
                for match in matchs:
                    s = match[13:-1]
                    sentence += s
                out_sentence = sentence.strip()
                break
        os.system('amixer -c 2 sset "Mic" 0%')
        print(out_sentence)
        return out_sentence


    #--------------------------------------------------
    #認識した文章に対応するフラグを返す
    #--------------------------------------------------    
    def returnFlag(self, state, text):
        if text == '':
            return 'error'
        RecgDict = self.RecgDicts[state]
        for k, v in RecgDict.items():
            if text.find(k) >= 0:
                return v
        else:
            return 0


#--------------------------------------------------
#メイン関数
#--------------------------------------------------
if __name__ == '__main__':
    node_name = os.path.basename(__file__)
    node_name = node_name.split('.')
    rospy.init_node(node_name[0])


    #初期設定
    #-----------speech recognition------------------------
    julius_host = 'localhost'
    julius_port = 10500
    julius_bufsize = 4096 * 4

    julius_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    julius_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, julius_bufsize)
    julius_sock.connect((julius_host, julius_port))
    RecgDicts = {
        'Names': [
            '人',
            # 'マイケル', 'クリストファー', 'マシュー', 'ジョシュア', 'デイビッド', 'ジェームス',
            # 'ダニエル', 'ロバート', 'ジョン', 'ジョセフ', 'ジェシカ', 'ジェニファー', 'アマンダ',
            # 'アシュリー', 'サラ', 'ステファニー', 'メリッサ', 'ニコール', 'エリザベス', 'ヘザー'
        ],
        'Items': [
            '物体',
            # 'グリーンティ', 'オレンジジュース', 'ブラウンティ',
            # 'ジャパニーズティ', 'レッドティ', 'レモンティ', 'ストロベリージュース',

            # 'カップスター', 'カップヌードル', 'シーフードヌードル',
            # 'コリアンスープ', 'エッグスープ', 'オニオンドレッシング',
            # 'ジャパニーズドレッシング', 'チップスター', 'プリングルス',

            # 'ロングポテト', 'ブルーポテト', 'レッドポテト', 'スティックポテト',
            # 'ブリーチ', 'クロスクリーナー', 'ソフナー', 'ディッシュクリーナー', 'バスクリーナー'
        ],
        'Locations': [
            '外',
            # 'リビングルーム', 'ダイニングルーム', 'チルドレンライブラリー',
            # 'サイドテーブル', 'ディナーテーブル', 'レセプションテーブル', 'ソファー'
            #, 'ダイニングルーム', 'リビングルーム', 'コリドー', 'キッチンルーム', 'ビジタールーム',
            #'ダイニングテーブル', 'ダイニングソファ', 'リビングソファ',
            #'サイドテーブル',
            #'リビングテーブル', 'キッチンテーブル', 'チルドレンライブラリー', 'レセプションテーブル'
        ],
        #'Contents': [
        #    '名前', '時間'
        #],
        'CMD': {'エクシアちょっときて': 'start', 'ここで止まって': 'stop', 'それであってるよ': 'ok', '間違ってるよ': 'ng'}
    }

    objs = rospy.get_param('/param/obj/db')
    RecgDicts['Items'].extend([obj['obj_name_j'].encode('utf-8') for obj in objs])
    locations = rospy.get_param('/param/place/db')
    RecgDicts['Locations'].extend([location['place_name_j'].encode('utf-8') for location in locations])

    # 動詞ファイルを読み込み
    csv_obj = csv.reader(open(os.path.abspath(os.path.dirname(__file__)) + '/verb_light.csv', 'r'))
    #csv_obj = csv.reader(open('/home/athome05/iyutaro_ws/src/gpsr_pkg/scripts/verb_light.csv', 'r'))
    #csv_obj = csv.reader(open('/home/athome08/ttakahiro_ws/src/gpsr_pkg/scripts/verb_light.csv', 'r'))
    verbClass = np.array([v for v in csv_obj])
    #-----------speech recognition------------------------

    speech_rec = SpeechRec(julius_bufsize, julius_sock, RecgDicts, verbClass)


    main_rate = rospy.Rate(30)
    while not rospy.is_shutdown():
        main_rate.sleep()
