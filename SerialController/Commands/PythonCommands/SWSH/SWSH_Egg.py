#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.PythonCommandBase import PythonCommand, ImageProcPythonCommand
from Commands.PythonCommandBaseTrim import ImageProcPythonCommandTrim
from Commands.Keys import KeyPress, Button, Hat, Direction, Stick, Tilt
import requests
import time, cv2, os, re, datetime, glob, json
import datetime
import numpy as np

class SWSH_Egg(ImageProcPythonCommandTrim):
    NAME = 'SWSH 色違い孵化 繰り返しなし'
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

        self.hasShiny = False
        self.shinyLine = 0

        #変数初期化
        line_num = 6
        self.use_LINEnotice = False
        self.is_sleep = True
        
        self.threshold = 0.7
        self.hatched_egg_total = 0

        ret = self.set_param()
        line_num = int(ret[0])
        self.use_LINEnotice = ret[1]
        self.is_sleep = ret[2]
        self.lang = ret[3]
        self.show_value = ret[4]
        mode = ret[5]

        Lstick_down  = "0x0003 8 80 ff 80 80"   # LSTICK-DOWN
        Lstick_right = "0x0003 8 ff 80 80 80"   # LSTICK-RIGHT
        Neutral      = "0x0003 8 80 80 80 80"   # NEUTRAL

        self.wait(0.3)
        count = 0
        max_count = line_num * 5
        start_time = datetime.datetime.now()
        print("スタート！")

        try:
            if mode == '卵受け取りのみ' or mode == '卵受け取り～孵化':
                while True:
                    self.fryToSodateya()
                    self.press(Direction(Stick.LEFT,180), duration=1.5, wait=0.5)
                    self.press(Direction(Stick.LEFT,90), duration=1.5, wait=0.5)
                    self.press(Direction(Stick.LEFT,45), duration=5, wait=0.5)
                    while count < max_count:
                        if (self.isContainTemplate('SWSH/EGG_Util/woman1.png', threshold=0.78, use_gray=True, show_value=self.show_value)
                            or self.isContainTemplate('SWSH/EGG_Util/woman3.png', threshold=0.78, use_gray=True, show_value=self.show_value)):
                            self.press(Button.A, 0.1, 2)
                            if not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/notEggText.png', 0.85, use_gray=False, show_value=self.show_value):
                                count += 1
                                print(f"タマゴ検知: {count}個目")
                                self.press(Button.A, 0.1, 1)
                                while not self.isContainTemplate(f'SWSH/EGG_Util/yy.png', 0.85, use_gray=False, show_value=self.show_value):
                                    self.press(Button.A, 0.1, 3)
                                self.ouhukuSodateya()
                            else:
                                while not self.isContainTemplate(f'SWSH/EGG_Util/yy.png', 0.85, use_gray=False, show_value=self.show_value):
                                    self.press(Button.B, 0.1, 3)
                                self.ouhukuSodateya()
                        else:
                            self.ouhukuSodateya()
                    cycle_end_time = datetime.datetime.now()
                    if self.use_LINEnotice:
                        self.LINE_text(f'SWSH卵受け取り完了\n【個数】{count}\n【総実行時間】{cycle_end_time - start_time}')
                    break
                    # if self.is_sleep:
                    #     self.power_sleep()
                    # self.finish()

            if mode == '孵化のみ' or mode == '卵受け取り～孵化':
                while True:
                    count = 0
                    self.fryToEastLakeAxewell()
                    self.openBox()
                    self.putPokemons()
                    self.closeMenu()
                    self.report()
                    while count < line_num:
                        self.jprint_append(f'孵化: {count + 1}列目')
                        self.pickUpEggs(count+1)
                        self.hatching()
                        self.putHatchedEggs(count+1)
                        self.resetPositionEastLakeAxewell()
                        self.report()
                        count += 1
                    cycle_end_time = datetime.datetime.now()
                    if self.use_LINEnotice:
                        self.LINE_text(f'SWSH孵化完了\n【個数】{count*5}\n【総実行時間】{cycle_end_time - start_time}')
                    break
        except:
            if self.use_LINEnotice:
                self.LINE_image("*** Error ***")  # LINE通知不要なら削除

        if self.is_sleep:
            self.power_sleep()
        self.finish()


    def ouhukuSodateya(self):
        self.press(Direction(Stick.LEFT,135), duration=2.5, wait=0.5)
        self.press(Direction(Stick.LEFT,45), duration=3, wait=1)
        return
                    
    
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
    
    def closeMenu(self):
        while not self.isContainTemplate('SWSH/EGG_Util/yy.png', 0.85):
            self.press(Button.B, 0.1, 1.0)
        return

    def report(self):
        while not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/menu.png', 0.85):
            self.press(Button.X, 0.1, 1.0)
        self.press(Button.R, 0.1, 3.0)
        while not self.isContainTemplate('SWSH/EGG_Util/yy.png', 0.85):
            self.press(Button.A, 0.1, 1)
        return

    
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
    
    def putHatchedEggs(self,count):
        num = count % 6
        if num == 0:
            num = 6
        hasShiny = False
        if not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/box.png', 0.85):
            self.openBox()
        while not self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/multiselect.png', 0.85):
            self.press(Button.Y, 0.1, 1.0)
        self.press(Direction.LEFT, 0.1, 0.5)
        for i in range(5):
            self.press(Direction.DOWN, 0.1, 0.5)
            if i == 0:
                self.press(Button.A, 0.1, 0.5)
            if self.isShiny():
                self.hasShiny = True
                hasShiny = True
                if self.use_LINEnotice:
                    self.LINE_image("*** shiny ***")  # LINE通知不要なら削除
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
    
    def checkYY(self):
        return self.isContainTemplate(f'SWSH/EGG_Util/yy.png', 0.85, use_gray=False, show_value=self.show_value)

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
            while self.checkYY():
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
    
    def checkHasEggs(self):
        self.openTemochi()
        if self.isContainTemplate(f'SWSH/EGG_Util/egg.png', 0.85, use_gray=False, show_value=self.show_value):
            self.closeMenu()
            return True
        else:
            self.closeMenu()
            return False

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
    
    def compStatus(self,status1,status2,mode):
        for i in range(len(status1)):
            if status1[i] != status2[i]:
                return False
        return True
    
    def checkBest(self,y,h,x,w):
        if self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/statusBest.png', 0.85, use_gray=True, show_value=self.show_value, area=[y,y+h,x,x+w]):
            return True
        else:
            return False
    
    def checkNoGood(self,y,h,x,w):
        if self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/statusNoGood.png', 0.85, use_gray=True, show_value=self.show_value, area=[y,y+h,x,x+w]):
            return True
        else:
            return False
    
    def isShiny(self):
        if self.isContainTemplate(f'SWSH/EGG_Util/shiny.png', 0.85, use_gray=True, show_value=self.show_value, area=[93,145,1224,1280]):
            self.jprint_append('色違いを確認！')
            return True
        else:
            return False
    
    def releasePokemon(self):
        state = 0
        while self.isContainTemplate(f'SWSH/EGG_Util/{self.lang}/lv.png', 0.85, use_gray=True, show_value=self.show_value):
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
    
    def releasePokemon1Box(self):
        self.openBox()
        count = 1
        row = 1
        while count < 31:
            self.releasePokemon()
            if count % 6 == 0:
                self.press(Direction.DOWN, 0.1, 0.5)
                row += 1
            elif row % 2 == 1:
                self.press(Direction.RIGHT, 0.1, 0.5)
            else:
                self.press(Direction.LEFT, 0.1, 0.5)
            count += 1
        return

        

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
        mode_list = ['卵受け取りのみ','孵化のみ','卵受け取り～孵化']
        mode = '卵受け取り～孵化'

        while True:
            dialogue_list = [
                ['Entry','孵化数',line_num], #0
                ['Check','LINE通知する？',is_notice_LINE], #1
                ['Check','スリープする？',is_sleep], #2
                ['Combo','言語',lang_list,lang], #3
                ['Check','近似値表示',show_value], #4
                ['Combo','モード',mode_list,mode], #5
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