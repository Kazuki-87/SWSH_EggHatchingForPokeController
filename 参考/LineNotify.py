#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import configparser
import requests
import cv2
import io
import os
from PIL import Image
from logging import getLogger, DEBUG, NullHandler


def convert_bgr_to_bytes(image_bgr):
    '''
    BGRの画像をbyte形式に変換する
    '''
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(image_rgb)
    png = io.BytesIO()              # 空のio.BytesIOオブジェクトを用意
    image.save(png, format='png')   # 空のio.BytesIOオブジェクトにpngファイルとして書き込み
    b_frame = png.getvalue()        # io.BytesIOオブジェクトをbytes形式で読みとり
    return b_frame


class Line_Notify:
    LINE_TOKEN_PATH = os.path.join(os.path.dirname(__file__), 'profiles', 'default', 'line_token.ini')

    def __init__(self, token_name='token'):
        self._logger = getLogger(__name__)
        self._logger.addHandler(NullHandler())
        self._logger.setLevel(DEBUG)
        self._logger.propagate = True

        self.res = None
        self.token_file = configparser.ConfigParser(comment_prefixes='#', allow_no_value=True)
        self.open_file_with_utf8()
        self.webhook_url = self.token_file['DISCORD']['webhook_url']
        self.res = requests.get(self.webhook_url)
        self.status = self.res.status_code

    def open_file_with_utf8(self):
        """
        utf-8 のファイルを BOM ありかどうかを自動判定して読み込む
        """
        line_token_path = os.path.join(os.path.dirname(__file__), 'profiles/default/discord_settings.ini')
        is_with_bom = self.is_utf8_file_with_bom(line_token_path)

        encoding = 'utf-8-sig' if is_with_bom else 'utf-8'

        self._logger.debug("Load token file")
        self.token_file.read(line_token_path, encoding)

    def is_utf8_file_with_bom(self, filename):
        """
        utf-8 ファイルが BOM ありかどうかを判定する
        """
        line_first = open(filename, encoding='utf-8').readline()
        return line_first[0] == '\ufeff'

    def __str__(self):
        if self.status == 401:
            self._logger.error("Invalid token")
            return "DISCORD Webhook Check FAILED."
        elif self.status == 200:
            self._logger.info("Valid token")
            return "DISCORD Webhook Check OK!"

    def send_message(self, notification_message, image=None, token='token'):
        """
        LINEにテキスト/画像を通知する
        imageが設定されていなければテキストのみ、設定されていればテキストと画像を通知する
        imageはBGRを想定する
        """
        webhook_url = self.webhook_url
        try:
            data = None
            files = None
            data = {'content': f'{notification_message}'}
            if image is not None:
                b_frame = convert_bgr_to_bytes(image)
                files = {'attachement': ('screen_shot.png',b_frame)}

            # 何故か画像のみの送信はできなかった。
            if files is not None:  # テキストと画像
                self.res = requests.post(webhook_url, data=data, files=files)
                send_data_type = "テキスト・画像"
                send_data_type_eng = "image with text"
            else:                  # テキスト
                self.res = requests.post(webhook_url,json=data)
                send_data_type = "テキスト"
                send_data_type_eng = "text"

            if self.res.status_code == 200:
                print(f"[DISCORD]{send_data_type}を送信しました。")
                self._logger.info(f"Send {send_data_type_eng}")
            elif self.res.status_code == 204:
                print(f"[DISCORD]{send_data_type}を送信しました。")
                self._logger.info("Send text")
            else:
                print(f"[DISCORD]{send_data_type}の送信に失敗しました。")
                self._logger.error(f"Failed to send {send_data_type_eng}")
        except KeyError:
            print('Webhook URLが間違っています')
            self._logger.error('Using the wrong webhook url')

    def getRateLimit(self):
        print("DISCORDに送信上限はたぶんないです。")

if __name__ == "__main__":
    '''
    status  HTTPステータスコードに準拠した値
       200  成功時
       401  アクセストークンが無効
    '''
    LINE = Line_Notify()
    print(LINE)
    LINE.getRateLimit()
