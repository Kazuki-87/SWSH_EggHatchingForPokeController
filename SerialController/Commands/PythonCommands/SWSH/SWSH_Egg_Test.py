#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.PythonCommandBase import PythonCommand, ImageProcPythonCommand
from Commands.PythonCommandBaseTrim import ImageProcPythonCommandTrim
from Commands.Keys import KeyPress, Button, Hat, Direction, Stick, Tilt
import requests
import time, cv2, os, re, datetime, glob, json
import datetime
import numpy as np

class SWSH_Egg_Test(ImageProcPythonCommandTrim):
    NAME = 'SWSH 色違い孵化 テスト'
    TAGS = ['SWSH', 'Shiny']

    def __init__(self, cam):
        super().__init__(cam)
        self.show_value = True
        self.lang = 'ENG'
        self.dispCheckLog = True
    
    def sendCommand(self, row: str, wait: float = 0.04):
        self.keys.ser.ser.write((row + '\r\n').encode('utf-8'))
        time.sleep(wait)
        self.checkIfAlive()

    def do(self):
        # 実行環境確認
        self.judgePokeConEdition()
        self.jprint_overwrite("---------------------------------------\n"+
                    "自動タマゴ孵化(SWSH)_色卵 テスト v1.1\n"+
                    "Copyright(c) 2026 【X】@cure_kazuki \n"+
                    "---------------------------------------")

        self.hasShiny = False
        self.shinyCol = 0
        self.shinyRow = 0

        #変数初期化
        self.use_LINEnotice = False
        self.is_sleep = True
        
        self.threshold = 0.7
        self.hatched_egg_total = 0
        self.shiny_total = 0

        ret = self.set_param()
        max_count = int(ret[0])
        self.use_LINEnotice = ret[1]
        self.is_sleep = ret[2]
        self.lang = ret[3]
        self.show_value = ret[4]
        self.target_status = ret[5]
        self.pkmn_name = ret[6]

        self.jprint_append( "パラメータ設定\n"+
                    f"【言語】{self.lang}\n"+
                    f"【厳選名】{self.pkmn_name}\n"+
                    f"【色違い上限数】{str(max_count)}\n"+
                    f"【画像認識近似値表示】{str(self.show_value)}\n"+
                    f"【LINE通知】{str(self.use_LINEnotice)}\n"+
                    "---------------------------------------")

        Lstick_down  = "0x0003 8 80 ff 80 80"   # LSTICK-DOWN
        Lstick_right = "0x0003 8 ff 80 80 80"   # LSTICK-RIGHT
        Neutral      = "0x0003 8 80 80 80 80"   # NEUTRAL

        self.wait(0.3)
        start_time = datetime.datetime.now()
        print("スタート！")
        test_mode_list = ['ステータス・色違いチェック',
        '育て屋',
        'ボックス名：きじゅん',
        'ボックス名：たまご',
        'ボックス空き状況',
        'そらをとぶ：育て屋',
        'そらをとぶ：キバ湖']

        if ret[7] == 'ステータス・色違いチェック':
            status = self.judgeStatus()
            print(status)
            self.isShiny()
        elif ret[7] == '育て屋':
            if (self.isContainTemplate('SWSH/EGG_Util/woman1.png', threshold=0.78, use_gray=True, show_value=self.show_value)
                or self.isContainTemplate('SWSH/EGG_Util/woman3.png', threshold=0.78, use_gray=True, show_value=self.show_value)):
                print('タマゴできたかも。')
                self.press(Button.A, 0.1, 2)
                if not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/notEggText.png', 0.85, use_gray=False, show_value=self.show_value):
                    print(f"タマゴ検知")
                    self.press(Button.A, 0.1, 1)
                    while not self.isContainTemplate(f'SWSH/EGG_Util/yy.png', 0.85, use_gray=False, show_value=self.show_value):
                        self.press(Button.A, 0.1, 3)
                    self.ouhukuSodateya()
                else:
                    print('タマゴできてなかった。')
                    while not self.isContainTemplate(f'SWSH/EGG_Util/yy.png', 0.85, use_gray=False, show_value=self.show_value):
                        self.press(Button.B, 0.1, 3)
                    self.ouhukuSodateya()
            else:
                self.ouhukuSodateya()
        elif ret[7] == 'ボックス名：きじゅん':
            if self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/boxNameBASE.png', 0.85,show_value=self.show_value):
                print('きじゅんのボックスが見つかりました。')
            else:
                print('きじゅんのボックスが見つかりませんでした。')
        elif ret[7] == 'ボックス名：たまご':
            if self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/boxNameEGG.png', 0.85,show_value=self.show_value):
                print('たまごのボックスが見つかりました。')
            else:
                print('たまごのボックスが見つかりませんでした。')
        elif ret[7] == 'ボックス空き状況':
            if (self.isContainTemplate(f'SWSH/EGG_Util/box1.png', 0.85,area=[258,258+113,740,740+112])
                or self.isContainTemplate(f'SWSH/EGG_Util/box2.png', 0.85,area=[258,258+113,740,740+112])):
                if not self.isContainTemplate(f'SWSH/EGG_Util/box3.png', 0.85,area=[258,258+113,740,740+112]):
                    print('となりのボックスに空きがあります。')
            else:
                print('となりのボックスに空きがありません。')
        elif ret[7] == 'そらをとぶ：育て屋':
            self.fryToSodateya()
        elif ret[7] == 'そらをとぶ：キバ湖':
            self.fryToEastLakeAxewell()
        
        self.finish()

    # 育て屋の前を往復する
    def ouhukuSodateya(self):
        self.press(Direction(Stick.LEFT,135), duration=2.5, wait=0.5)
        self.press(Direction(Stick.LEFT,45), duration=3, wait=1)
        return
                    
    # 東湖アクスウェルに移動する
    def fryToEastLakeAxewell(self):
        self.openMap()
        selectedEastLakeAxewell = False
        while not selectedEastLakeAxewell:
            while not self.isContainTemplate(f'SWSH/EGG_Util/engine.png', 0.85, use_gray=False, show_value=self.show_value):
                self.press(Button.R, 0.1, 0.5)
            self.press(Direction(Stick.LEFT,270), duration=0.2, wait=0.5)
            if self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/eastLakeAxewell.png', 0.85, use_gray=False, show_value=self.show_value):
                selectedEastLakeAxewell = True
        while not self.isContainTemplate(f'SWSH/EGG_Util/yy.png', 0.85, use_gray=False, show_value=self.show_value):
            self.press(Button.A, 0.1, 1)
        return
    
    # 育て屋に移動する
    def fryToSodateya(self):
        self.openMap()
        selectedSodateya = False
        while not selectedSodateya:
            while not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/turffield.png', 0.85, use_gray=False, show_value=self.show_value):
                self.press(Button.R, 0.1, 0.5)
            self.press(Direction(Stick.LEFT,0), duration=0.1, wait=0.5)
            self.press(Direction(Stick.LEFT,45), duration=0.01, wait=1)
            if self.isContainTemplate(f'SWSH/EGG_Util/sodateya.png', 0.70, use_gray=False, show_value=self.show_value):
                selectedSodateya = True
        while not self.isContainTemplate(f'SWSH/EGG_Util/yy.png', 0.85, use_gray=False, show_value=self.show_value):
            self.press(Button.A, 0.1, 1)
        return
    
    # 東湖アクスウェルの位置がずれている場合にリセットする
    def resetPositionEastLakeAxewell(self):
        self.openMap()
        selectedEastLakeAxewell = False
        if self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/eastLakeAxewell.png', 0.85, use_gray=False, show_value=self.show_value):
            selectedEastLakeAxewell = True
        else:
            while not selectedEastLakeAxewell:
                while not self.isContainTemplate(f'SWSH/EGG_Util/engine.png', 0.85, use_gray=False, show_value=self.show_value):
                    self.press(Button.R, 0.1, 0.5)
                self.press(Direction(Stick.LEFT,270), duration=0.2, wait=0.5)
                if self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/eastLakeAxewell.png', 0.85, use_gray=False, show_value=self.show_value):
                    selectedEastLakeAxewell = True
        while not self.isContainTemplate(f'SWSH/EGG_Util/yy.png', 0.85, use_gray=False, show_value=self.show_value):
            self.press(Button.A, 0.1, 1)
        return
    
    # メニューを閉じる
    def closeMenu(self):
        while not self.isContainTemplate('SWSH/EGG_Util/yy.png', 0.85):
            self.press(Button.B, 0.1, 1.0)
        return

    # レポートを書く
    def report(self):
        while not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/menu.png', 0.85):
            self.press(Button.X, 0.1, 1.0)
        self.press(Button.R, 0.1, 3.0)
        while not self.isContainTemplate('SWSH/EGG_Util/yy.png', 0.85):
            self.press(Button.A, 0.1, 1)
        return

    # マップを開く
    def openMap(self):
        while not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/menu.png', 0.85):
            self.press(Button.X, 0.1, 1.0)
        isSelectedMap = False
        if not self.isContainTemplate('SWSH/EGG_Util/map.png', 0.85):
            for i in range(5):
                self.press(Direction.RIGHT, 0.1, 0.5)
                if self.isContainTemplate('SWSH/EGG_Util/map.png', 0.85):
                    isSelectedMap = True
                    break
            for i in range(2):
                if not isSelectedMap:
                    self.press(Direction.DOWN, 0.1, 0.5)
                    if self.isContainTemplate('SWSH/EGG_Util/map.png', 0.85):
                        isSelectedMap = True
                if not isSelectedMap:
                    for i in range(5):
                        self.press(Direction.RIGHT, 0.1, 0.5)
                        if self.isContainTemplate('SWSH/EGG_Util/map.png', 0.85):
                            isSelectedMap = True
                            break
        else:
            isSelectedMap = True
        if isSelectedMap:
            self.press(Button.A, 0.1, 1.0)
            while not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/back.png', 0.85):
                self.wait(0.5)
        else:
            print("マップが見つかりませんでした。")
            self.finish()
    
    # 手持ちを開く
    def openTemochi(self):
        while not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/menu.png', 0.85):
            self.press(Button.X, 0.1, 1.0)
        isSelectedTemochi = False
        if not self.isContainTemplate('SWSH/EGG_Util/temochi.png', 0.85):
            for i in range(5):
                self.press(Direction.RIGHT, 0.1, 0.5)
                if self.isContainTemplate('SWSH/EGG_Util/temochi.png', 0.85):
                    isSelectedTemochi = True
                    break
            for i in range(2):
                if not isSelectedTemochi:
                    self.press(Direction.DOWN, 0.1, 0.5)
                    if self.isContainTemplate('SWSH/EGG_Util/temochi.png', 0.85):
                        isSelectedTemochi = True
                if not isSelectedTemochi:
                    for i in range(5):
                        self.press(Direction.RIGHT, 0.1, 0.5)
                        if self.isContainTemplate('SWSH/EGG_Util/temochi.png', 0.85):
                            isSelectedTemochi = True
                            break
        else:
            isSelectedTemochi = True
        if isSelectedTemochi:
            self.press(Button.A, 0.1, 3.0)
            return
        else:
            print("てもちが見つかりませんでした。")
            self.finish()
    
    # ボックスを開く
    def openBox(self):
        while not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/menu.png', 0.85):
            self.press(Button.X, 0.1, 1.0)
        isSelectedTemochi = False
        if not self.isContainTemplate('SWSH/EGG_Util/temochi.png', 0.85):
            for i in range(5):
                self.press(Direction.RIGHT, 0.1, 0.5)
                if self.isContainTemplate('SWSH/EGG_Util/temochi.png', 0.85):
                    isSelectedTemochi = True
                    break
            for i in range(2):
                if not isSelectedTemochi:
                    self.press(Direction.DOWN, 0.1, 0.5)
                    if self.isContainTemplate('SWSH/EGG_Util/temochi.png', 0.85):
                        isSelectedTemochi = True
                if not isSelectedTemochi:
                    for i in range(5):
                        self.press(Direction.RIGHT, 0.1, 0.5)
                        if self.isContainTemplate('SWSH/EGG_Util/temochi.png', 0.85):
                            isSelectedTemochi = True
                            break
        else:
            isSelectedTemochi = True
        if isSelectedTemochi:
            self.press(Button.A, 0.1, 3.0)
            self.press(Button.R, 0.1, 3.0)
            while not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/box.png', 0.85):
                # 手持ち状態のときはRボタンを押す
                if self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/openedTemochi.png', 0.85):
                    self.press(Button.R, 0.1, 3.0)
                # メニューでAボタンの押し漏れがあったときAボタンを押す
                if self.isContainTemplate('SWSH/EGG_Util/temochi.png', 0.85):
                    self.press(Button.A, 0.1, 3.0)
                self.wait(0.5)
        else:
            print("てもちが見つかりませんでした。")
            self.finish()
    
    # ボックスにポケモンを入れる（手持ち埋め要員）
    def putPokemons(self):
        while not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/multiselect.png', 0.85):
            self.press(Button.Y, 0.1, 1.0)
        while not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/boxNameBASE.png', 0.85):
            self.press(Button.L, 0.1, 3.0)
        self.press(Direction.LEFT, 0.1, 0.5)
        self.press(Direction.DOWN, 0.1, 0.5)
        self.press(Button.A, 0.1, 0.5)
        for i in range(4):
            self.press(Direction.DOWN, 0.1, 0.5)
        self.press(Button.A, 0.1, 0.5)
        self.press(Direction.UP, 0.1, 0.5)
        for i in range(6):
            self.press(Direction.RIGHT, 0.1, 0.5)
        self.press(Button.A, 0.1, 0.5)
        while not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/boxNameEGG.png', 0.85):
            self.press(Button.R, 0.1, 3.0)
    
    # ボックスからポケモンを引き出す（手持ち埋め要員）
    def pickUpPokemons(self):
        # 複数選択モード
        while not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/multiselect.png', 0.85):
            self.press(Button.Y, 0.1, 1.0)
        # BASEボックスへ移動
        while not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/boxNameBASE.png', 0.85):
            self.press(Button.L, 0.1, 3.0)
        # ボックス右上に移動
        for i in range(5):
            self.press(Direction.RIGHT, 0.1, 0.5)
        # 5匹を選択
        self.press(Button.A, 0.1, 0.5)
        for i in range(4):
            self.press(Direction.DOWN, 0.1, 0.5)
        self.press(Button.A, 0.1, 0.5)
        # 手持ちへ移動
        for i in range(6):
            self.press(Direction.LEFT, 0.1, 0.5)
        self.press(Direction.DOWN, 0.1, 0.5)
        self.press(Button.A, 0.1, 0.5)
        # EGGボックスへ移動
        while not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/boxNameEGG.png', 0.85):
            self.press(Button.R, 0.1, 3.0)


    # ボックスからタマゴを受け取る
    def pickUpEggs(self,count):
        num = count
        if not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/box.png', 0.85):
            self.openBox()
        # ボックス切り替え
        if num != 1 and num % 6 == 1:
            self.press(Button.R, 0.1, 1.0)
        # ボックス切り替えのタイミングで色違いがいた場合はリセットしているため、切り替えして一度レポートし、開きなおす。
        if self.hasShiny and num != 2 and num % 6 == 2:
            # ボックス切り替え
            self.press(Button.R, 0.1, 1.0)
            self.hasShiny = False
            # メニューを閉じる
            self.closeMenu()
            # レポートを書く
            self.report()
            # ボックスを開く
            self.openBox()
        while not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/multiselect.png', 0.85):
            self.press(Button.Y, 0.1, 1.0)
        num = (num % 6)
        if num == 0:
            num = 6
        for i in range(num - 1):
            self.press(Direction.RIGHT, 0.1, 0.5)
        self.press(Button.A, 0.1, 0.5)
        for i in range(4):
            self.press(Direction.DOWN, 0.1, 0.5)
        self.press(Button.A, 0.1, 0.5)
        for i in range(num):
            self.press(Direction.LEFT, 0.1, 0.5)
        self.press(Direction.DOWN, 0.1, 0.5)
        self.press(Button.A, 0.1, 0.5)
        self.closeMenu()
        return
    
    # タマゴを孵化させた後、ボックスに戻す
    def putHatchedEggs(self,count,eggs=5):
        num = count % 6
        if num == 0:
            num = 6
        hasShiny = False
        if not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/box.png', 0.85):
            self.openBox()
        while not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/multiselect.png', 0.85):
            self.press(Button.Y, 0.1, 1.0)
        self.press(Direction.LEFT, 0.1, 0.5)
        for i in range(eggs):
            self.press(Direction.DOWN, 0.1, 0.5)
            if i == 0:
                self.press(Button.A, 0.1, 0.5)
            if self.isShiny():
                self.hasShiny = True
                hasShiny = True
                if self.use_LINEnotice:
                    self.LINE_image("*** shiny ***")  # LINE通知不要なら削除
                self.shinyCol = num 
                self.shinyRow = i + 1
                print(f'色違い発見！: {self.shinyCol}列目 {self.shinyRow}段目')
                # if self.is_sleep:
                #     self.power_sleep()
                # self.finish()
                self.softReboot()
                return
        self.press(Button.A, 0.1, 0.5)
        self.press(Direction.UP, 0.1, 0.5)
        for i in range(num):
            self.press(Direction.RIGHT, 0.1, 0.5)
        self.press(Button.A, 0.1, 0.5)
        self.closeMenu()
        return
    
    # YYマーカーが表示されているか確認する
    def checkYY(self):
        return self.isContainTemplate(f'SWSH/EGG_Util/yy.png', 0.85, use_gray=False, show_value=self.show_value)

    # タマゴを孵化させる
    def hatching(self,eggs=5):
        """
        タマゴ孵化処理
        【戻り値】bool 成否

        Parameters
        ----------
        eggs : int
            手持ちのタマゴの数を引数に設定すると、その数分孵化処理を行う
        """        
        print('_method_hatching')
        hatched_eggs = 0
        for i in range(0, eggs):
            count = 0
            # start run
            self.hold([Direction(Stick.LEFT, 85), Direction(Stick.RIGHT, 180)])
            # hatching notice
            while not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/oya.png',0.85):
                count += 1
                if count >= 500:
                    self.holdEnd([Direction(Stick.LEFT, 85), Direction(Stick.RIGHT, 180)])
                    if self.checkHasEggs():
                        self.hold([Direction(Stick.LEFT, 85), Direction(Stick.RIGHT, 180)])
                        count = 0
                        continue
                    else:
                        print('ERROR: hatching - run time over')
                        return False,hatched_eggs
            # end run
            self.holdEnd([Direction(Stick.LEFT, 85), Direction(Stick.RIGHT, 180)])
            self.hatched_egg_total += 1
            hatched_eggs += 1
            self.jprint_append(f'egg hatching: {str(i+1)}/{eggs} total: {str(self.hatched_egg_total)}')
            count = 0 #マーカー認識ミスによるループ抜けのためカウントを初期化
            while not self.checkYY():
                self.press(Button.A, wait=0.5)
                count += 1
                if count >= 120 :
                    return False,hatched_eggs #whileループを抜ける
            # reset direction
            self.wait(2)
            self.press(Button.L, wait=0.5) 
            self.wait(0.3)
        return True,hatched_eggs
    
    # 手持ちにタマゴがあるか確認する
    def checkHasEggs(self):
        self.openTemochi()
        if self.isContainTemplate(f'SWSH/EGG_Util/egg.png', 0.85, use_gray=False, show_value=self.show_value):
            self.closeMenu()
            return True
        else:
            self.closeMenu()
            return False

    # 個体値チェック
    def judgeStatus(self):
        status = [3,3,3,3,3,3]
        # y,h,x,w
        status_area_list = [[139,45,990,145],
                            [180,45,990,145],
                            [218,45,990,145],
                            [254,45,990,145],
                            [289,45,990,145],
                            [327,45,990,145]]
        for i in range(len(status)):
            if self.checkBest(status_area_list[i][0],status_area_list[i][1],status_area_list[i][2],status_area_list[i][3]):
                status[i] = 31
            elif self.checkNoGood(status_area_list[i][0],status_area_list[i][1],status_area_list[i][2],status_area_list[i][3]):
                status[i] = 0
        return status
    
    # 理想個体比較
    def compStatus(self,status1,status2):
        for i in range(len(status1)):
            if status1[i] != status2[i]:
                return False
        return True
    
    # 個体値V判定
    def checkBest(self,y,h,x,w):
        if self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/statusBest.png', 0.85, use_gray=True, show_value=self.show_value, area=[y,y+h,x,x+w]):
            return True
        else:
            return False
    
    # 個体値0判定
    def checkNoGood(self,y,h,x,w):
        if self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/statusNoGood.png', 0.85, use_gray=True, show_value=self.show_value, area=[y,y+h,x,x+w]):
            return True
        else:
            return False
    
    # 色違い判定
    def isShiny(self):
        if self.isContainTemplate(f'SWSH/EGG_Util/shiny.png', 0.85, use_gray=True, show_value=self.show_value, area=[93,145,1224,1280]):
            self.jprint_append('色違いを確認！')
            return True
        else:
            return False
    
    # ポケモンを逃がす（ボックスでポケモンにカーソルを合わせた状態）
    def releasePokemon(self):
        state = 0
        while self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/lv.png', 0.85, use_gray=True, show_value=self.show_value,area=[19,19+48,1203,1203+56]):
            if state == 0:
                self.press(Button.A, 0.1, 0.5)
                while not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/release1.png', 0.85, use_gray=True, show_value=self.show_value):
                    self.press(Direction.UP, 0.1, 0.5)
                self.press(Button.A, 0.1, 0.5)
                state = 1
            elif state == 1:
                while not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/yes.png', 0.85, use_gray=True, show_value=self.show_value):
                    self.press(Direction.UP, 0.1, 0.5)
                self.press(Button.A, 0.1, 0.5)
                state = 2
            elif state == 2:
                self.press(Button.A, 0.1, 0.5)
            else:
                # ループ抜けのため状態を初期化
                state = 0
        return
    
    # 1ボックス分のポケモンを逃がす（フィールドの状態）
    def releasePokemon1Box(self):
        self.openBox()
        count = 1
        row = 1
        col = 1
        while count < 31:
            if self.target_status is not None: # 個体値厳選している場合は理想個体か確認してから逃がす
                if self.compStatus(self.target_status,self.judgeStatus()): # 理想個体の場合
                    self.jprint_append('理想個体を確認！')
                    self.movePokemonToEmpty(row, col)
                else:
                    self.releasePokemon()
            else:
                self.releasePokemon()
            if count % 6 == 0:
                self.press(Direction.DOWN, 0.1, 0.5)
                row += 1
            elif row % 2 == 1:
                self.press(Direction.RIGHT, 0.1, 0.5)
                col += 1
            else:
                self.press(Direction.LEFT, 0.1, 0.5)
                col -= 1
            count += 1
        self.closeMenu()
        return

    # ポケモンの位置を移動する（ボックスでポケモンにカーソルを合わせた状態）
    def moveCellFocus(self,row_from,col_from,row_to,col_to):
        row_diff = row_to - row_from
        col_diff = col_to - col_from
        for i in range(abs(row_diff)):
            if row_diff > 0:
                self.press(Direction.DOWN, 0.1, 0.5)
            else:
                self.press(Direction.UP, 0.1, 0.5)
        for i in range(abs(col_diff)):
            if col_diff > 0:
                self.press(Direction.RIGHT, 0.1, 0.5)
            else:
                self.press(Direction.LEFT, 0.1, 0.5)

    # # ポケモンをEGGボックス以降の空いている位置に左上から順に移動する（ボックスでポケモンにカーソルを合わせた状態）
    # def movePokemonToEmpty(self,row,col):
    #     self.press(Button.A, 0.1, 1)
    #     self.press(Button.A, 0.1, 1)
    #     base_area = [161,161+62,315,315+104]
    #     moveBoxCount = 0
    #     row_from = row
    #     col_from = col
    #     row_to = 1
    #     col_to = 1
    #     while True:
    #         self.press(Button.R, 0.1, 3.0)
    #         moveBoxCount += 1
    #         hasEmpty = False
    #         # 移動先のボックスに空きがあるか確認
    #         for i in range(5):
    #             for j in range(6):
    #                 y1 = base_area[0] + (96 * i)
    #                 y2 = base_area[1] + (96 * i)
    #                 x1 = base_area[2] + (91 * j)
    #                 x2 = base_area[3] + (91 * j)
    #                 if (self.isContainTemplate(f'SWSH/EGG_Util/emptyBox1.png', 0.85, use_gray=True, show_value=self.show_value, area=[y1,y2,x1,x2])
    #                     or self.isContainTemplate(f'SWSH/EGG_Util/emptyBox2.png', 0.85, use_gray=True, show_value=self.show_value, area=[y1,y2,x1,x2])):
    #                     row_to = i + 1
    #                     col_to = j + 1
    #                     hasEmpty = True
    #                     break
    #             if hasEmpty:
    #                 break
    #         if hasEmpty:
    #             break
    #         if moveBoxCount >= 32:
    #             print("空いている位置が見つかりませんでした。")
    #             self.power_sleep()
    #             self.finish()
    #     self.moveCellFocus(row_from, col_from, row_to, col_to)
    #     self.press(Button.A, 0.1, 0.5)
    #     for i in range(moveBoxCount):
    #         self.press(Button.L, 0.1, 3.0)
    #     while not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/boxNameEGG.png', 0.85):
    #         self.press(Button.L, 0.1, 3.0)
    #     self.moveCellFocus(row_to, col_to, row_from, col_from)

    def movePokemonToEmpty(self,row,col):
        self.press(Button.A, 0.1, 1)
        self.press(Button.A, 0.1, 1)
        while not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/boxList.png', 0.85):
            self.press(Direction.UP, 0.1, 0.5)
        self.press(Button.A, 0.1, 1)
        if (self.isContainTemplate(f'SWSH/EGG_Util/box1.png', 0.85,area=[258,258+113,740,740+112])
            or self.isContainTemplate(f'SWSH/EGG_Util/box2.png', 0.85,area=[258,258+113,740,740+112])):
            if not self.isContainTemplate(f'SWSH/EGG_Util/box3.png', 0.85,area=[258,258+113,740,740+112]):
                self.press(Direction.RIGHT, 0.1, 0.5)
                self.press(Button.A, 0.1, 1)
                self.press(Button.B, 0.1, 0.5)
                for i in range(row + 1):
                    self.press(Direction.DOWN, 0.1, 0.5)
        else:
            print('となりのボックスに空きがありません。')
            self.power_sleep()
            self.finish()



    # 色違いのタマゴを空いている位置に移動する（フィールドの状態）
    def moveShinyEggToEmpty(self):
        if self.shinyCol is not None and self.shinyRow is not None:
            self.openBox()
            self.moveCellFocus(1,1,self.shinyRow,self.shinyCol)
            self.movePokemonToEmpty(self.shinyRow, self.shinyCol)
            self.shinyCol = None
            self.shinyRow = None
            self.closeMenu()


    def judgePokeConEdition(self):
        '''
        PokeCon判別プログラム改
        developed by 非公表
        '''        
        if hasattr(self.__class__, 'print_t2b'):    # 継承している関数にprint_t1b関数が含まれるか? print_tb1関数はextension版のみ。
            self.mode_extension = True
            self.jprint("実行環境:Poke-Controller-Modified Extension")
        elif hasattr(self.__class__, 'dialogue6widget'):   # 継承している関数にdialogue6widget関数が含まれるか? dialogue6widget関数はmodified版/extension版のみ。
            self.mode_extension = False
            self.jprint("実行環境:Poke-Controller-Modified")
        else:
            print("本家PokeConでは実行できません。")
            self.finish()

    def jprint(self, text: str):
        '''
        print出力(上書きなし)
        developed by 非公表
        '''
        if self.mode_extension:
            self.print_tbs("a", text + "\n")
        else:
            print(text)

    def jprint_overwrite(self, text: str):
        '''
        print出力(上書きあり)
        developed by 非公表
        '''
        if self.mode_extension:
            self.print_tb("w", text + "\n")
        else:
            print(text)

    def jprint_append(self, text: str):
        '''
        print出力(上書きあり)
        developed by 非公表
        '''
        if self.mode_extension:
            self.print_tb("a", text + "\n")
        else:
            print(text)

    def set_param(self):
        is_set_param = False
        line_num = 6
        is_notice_LINE= True
        is_sleep = True
        lang_list = ['ENG']
        lang='ENG'
        show_value = True
        mode_list = ['チェックなし','6V','AS0-4V','CS0-4V','A0-5V','C0-5V','S0-5V']
        status_list = [None,
                        [31,31,31,31,31,31],
                        [31,0,31,31,31,0],
                        [31,31,31,0,31,0],
                        [31,0,31,31,31,31],
                        [31,31,31,0,31,31],
                        [31,31,31,31,31,0]]
        mode = 'チェックなし'
        pkmn_name = '剣盾'
        test_mode = 'ステータス・色違いチェック'
        test_mode_list = ['ステータス・色違いチェック','育て屋','ボックス名：きじゅん','ボックス名：たまご','ボックス空き状況','そらをとぶ：育て屋','そらをとぶ：キバ湖']

        while True:
            dialogue_list = [
                ['Entry','色違い最大数',line_num], #0
                ['Check','LINE通知する？',is_notice_LINE], #1
                ['Check','スリープする？',is_sleep], #2
                ['Combo','言語',lang_list,lang], #3
                ['Check','近似値表示',show_value], #4
                ['Combo','個体値チェックモード',mode_list,mode], #5
                ['Entry','ポケモン名',pkmn_name] #6
                ['Combo','テストモード',test_mode_list,test_mode], #7
            ]
            ret = self.dialogue6widget("BDSP自動孵化設定", dialogue_list)

            if type(ret) == bool:
                if ret == False:
                    self.jprint_append("キャンセルが押されました。プログラムを終了します。")
                    self.finish()
            elif "" not in ret[:-2]:
                break
            else:
                self.jprint("未設定項目があります。再度設定してください。")
                continue
        
        if ret[5] != 'チェックなし':
            ret[5] = status_list[mode_list.index(ret[5])]
        else:
            ret[5] = None
        return ret

    def softReboot(self):
        """
        ソフトの再起動（ソフトウェアの起動確認メッセージ対応）
        """
        print("_method(SV_util)_softReboot")
        error_count = 0
        # reset
        while not self.isContainTemplate("SWSH/EGG_Util/_select_user.png"):
            error_count += 1
            self.press(Button.HOME, wait=2) #HOMEに戻る
            self.press(Button.X) #ゲーム終了選択画面
            self.press(Button.A, wait=4.5) #はいを選択
            # DLC確認画面が開かれている場合
            if self.isContainTemplate("SWSH/EGG_Util/_askDLC.png"):
                self.press(Direction.UP) #上
                self.press(Button.A, wait=4.5) #選択
                break
            self.press(Button.A, wait=1.5) #ゲームを開始
            self.wait(1)
            if error_count > 10:
                print("ERROR:softReboot - error_count count over")
                return False
        error_count = 0
        self.press(Button.A, wait=5)
        # repeat A
        while not self.checkYY():
            self.press(Button.A, wait=2)
            error_count += 1
            if error_count > 120:
                print("ERROR:softReboot - error_count count over")
                return False
        return True

    # スリープモードにする
    def power_sleep(self):
        self.press(Button.HOME, wait=2) #HOMEに戻る
        self.press(Direction.DOWN,wait=0.3)
        self.press(Direction.DOWN,wait=0.3)
        self.press(Direction.DOWN,wait=0.3)
        self.press(Direction.DOWN,wait=0.3)
        self.press(Direction.RIGHT,wait=0.3)
        self.press(Direction.RIGHT,wait=0.3)
        self.press(Direction.RIGHT,wait=0.3)
        self.press(Direction.RIGHT,wait=0.3)
        self.press(Direction.RIGHT,wait=0.3)
        self.press(Direction.RIGHT,wait=0.3)
        self.press(Direction.RIGHT,wait=0.3)
        self.press(Direction.RIGHT,wait=0.3)
        self.press(Direction.RIGHT,wait=0.3)
        self.press(Button.A, wait=1.5)
        self.press(Button.A, wait=1.5)
        self.press(Button.A, wait=1.5)