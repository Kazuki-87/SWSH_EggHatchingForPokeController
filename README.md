# SWSH_EggHatchingForPokeController

自動タマゴ孵化（色違いチェック）スクリプト（Pokémon Sword & Shield）  
本スクリプトは Poke-Controller 用の自動孵化ツールです。

## 概要
このリポジトリには 1 ボックス（30個）単位でタマゴ孵化と色違い判定を自動化するコマンドに加えて、以下の追加コードが含まれます。

- 画像認識のテスト用コマンド: `SWSH_Egg_Test`（ファイル: SerialController/Commands/PythonCommands/SWSH/SWSH_Egg_Test.py）  
  - 画像テンプレート認識や各種チェックの確認を行うためのテストモードを提供します。
- 繰り返しなし（単一実行）バージョン: `SWSH_Egg`（ファイル: SerialController/Commands/PythonCommands/SWSH/SWSH_Egg.py）  
  - 繰り返し実行を行わず、受け取り・孵化を単発で行う実行モードを提供します。
- 逃がし処理の自動化コマンド: `SWSH_Egg_1BOX_Only_Release`（ファイル: SerialController/Commands/PythonCommands/SWSH/SWSH_Egg_1BOX_Only_Release.py）  
  - 1ボックス分（30匹）のポケモンを自動で判定・逃がす（または退避）処理を行います。

メイン実装は `SWSH_Egg_1BOX` 系（SerialController/Commands/PythonCommands/SWSH/）にあります。詳しい処理は以下のメソッドを参照してください。

- メイン実行: `SWSH_Egg_1BOX.do`  
- 設定ダイアログ: `SWSH_Egg_1BOX.set_param`  
- 孵化処理: `SWSH_Egg_1BOX.hatching`  
- 色違い判定: `SWSH_Egg_1BOX.isShiny`  
- 色違い発見時リセット: `SWSH_Egg_1BOX.softReboot`  
- 実行終了後スリープ移行: `SWSH_Egg_1BOX.power_sleep`

## 追加ファイルの概要
- SerialController/Commands/PythonCommands/SWSH/SWSH_Egg_Test.py  
  - テストモード: ステータス・色違いチェック、育て屋確認、ボックス名チェック、ボックス空き状況確認、そらをとぶテスト等を行えます。
- SerialController/Commands/PythonCommands/SWSH/SWSH_Egg.py  
  - 単回実行（繰り返しなし）で卵受け取り～孵化などを使いやすくしたバージョンです。
- SerialController/Commands/PythonCommands/SWSH/SWSH_Egg_1BOX_Only_Release.py  
  - 逃がし処理に特化。個体値や色違いを検出した場合に別ボックスへ移す処理を自動化します。

## 紹介動画（1サイクル解説動画）
1サイクル分の動作の解説をしてます。こちらのREADMEと合わせてご確認ください。

[![自動孵化デモ動画](https://img.youtube.com/vi/f64I7NhG7AM/maxresdefault.jpg)](https://youtu.be/f64I7NhG7AM)

## 処理概要（簡易フロー）
1. 実行環境確認（Poke-Controller Modified/Extension 判定）  
2. ダイアログでパラメータを設定（色違い上限、LINE 通知、言語など）  
3. 育て屋でタマゴを受け取る → 孵化場へ移動（必要に応じて：SWSH_Egg / SWSH_Egg_1BOX）  
4. 走らせて孵化判定（色違いを検出したら通知・リセット）  
5. 孵化済みポケモンをボックス操作で戻す/逃がす → サイクルを繰り返す（SWSH_Egg_1BOX または SWSH_Egg_1BOX_Only_Release）  
（詳細は上記メソッド参照）

## 開始前の準備
1. Poke-Controller Modified または Extension が動作する環境を用意する（実行環境は各コマンドの `judgePokeConEdition` で判定）。  
2. Switch と Poke-Controller（シリアル/USB）を接続する。  
3. カメラ/映像入力を接続し、画面表示がテンプレート画像と一致するように配置する。テンプレートは下記フォルダを使用：
   - SerialController/Commands/Template/SWSH/EGG_Util/ENG/  
   - SerialController/Commands/Template/SWSH/EGG_Util/JPN/  

## 使用方法（概略）
1. Poke-Controller の UI から目的のコマンド名を選択して実行（表示名は各クラスの NAME 属性）。
   - 画像認識テストを行う場合: 「SWSH 色違い孵化 テスト」(SWSH_Egg_Test)  
   - 繰り返しなしで単発実行する場合: 「SWSH 色違い孵化 繰り返しなし」(SWSH_Egg)  
   - 1ボックスの逃がし処理のみ行う場合: 「SWSH 色違い孵化 1BOX 逃がし処理のみ」(SWSH_Egg_1BOX_Only_Release)  
   - 通常の長周期（繰り返し）自動孵化: 「SWSH 色違い孵化 1BOX」等（SWSH_Egg_1BOX 系）
2. ダイアログでパラメータを設定（色違い上限数・言語・LINE 通知など）。
   - 「個体値チェックモード」では、モードに応じた個体値配列（例: 6V, A0-5V など）を選択できます。
   - 言語は現在「ENG」「JPN」のみ対応しています。
3. 実行中はカメラ映像とテンプレート認識の状態を確認し、必要に応じてテンプレートを更新。

## 開始前チェックリスト
- [ ] Switch の画面とテンプレートの表示が一致している  
- [ ] カメラの角度・解像度が固定されている  
- [ ] テンプレート画像が `SerialController/Commands/Template/SWSH/EGG_Util/` にある  
- [ ] 必要なら LINE トークン等の設定を済ませる（LINE 通知を利用する場合）

## 前提条件
以下の準備をしておくこと。

1. 特定のボックス名の命名と配置
- 卵をボックスに送るために手持ちを埋める要員を配置する「きじゅん」ボックス、卵を配置する「たまご」ボックス、色卵や理想個体を格納する空きボックスの3つを用意します。「きじゅん」ボックスと「たまご」ボックスの言語別命名は以下の通りです。

言語 | きじゅん | たまご
---|---|---
JPN | きじゅん | たまご
ENG | BASE | EGG

- 各ボックスは9,10,11番目に配置してください。

2. 手持ちを埋めておく
- 最初に卵の受け取りから始まるため、手持ちを埋めてください。

3. メニュー画面でマップと手持ちを同じ行に配置する（推奨）
- メニュー機能を選択する際、同じ行に配置すると探索が最小限で済みます。時短になります。

![参考画像1](expImg/exp1.png)  
![参考画像2](expImg/exp2.png)  
![参考画像3](expImg/exp3.png)  
![参考画像4](expImg/exp4.png)

## テストとデバッグ
- 画像認識の挙動確認は `SWSH_Egg_Test` を利用してください。テストモードで各テンプレートの検出状況を確認し、テンプレート画像を再取得してください。
- 単回実行（繰り返しなし）の動作確認は `SWSH_Egg` を利用します。長時間動作前にこちらで一次確認を推奨します。
- 逃がし処理の自動化は `SWSH_Egg_1BOX_Only_Release` を使ってボックス内の処理（色違い/個体値判定 → 退避）を検証してください。

## 参照ファイル
- コマンド本体（配置例）:
  - SerialController/Commands/PythonCommands/SWSH/SWSH_Egg_1BOX.py  
  - SerialController/Commands/PythonCommands/SWSH/SWSH_Egg_1BOX_Only_Release.py  
  - SerialController/Commands/PythonCommands/SWSH/SWSH_Egg_Test.py  
  - SerialController/Commands/PythonCommands/SWSH/SWSH_Egg.py
- テンプレート: SerialController/Commands/Template/SWSH/EGG_Util/ENG/ / SerialController/Commands/Template/SWSH/EGG_Util/JPN/  
- 説明画像フォルダ: expImg/  
- 参考フォルダ（ライン通知設定について）： 参考/

## ライン通知設定について
本プログラムではライン通知によって色違いの報告や孵化数の定期報告をさせています。LINE 通知設定や別通知サービスへの置換手順は `参考/` フォルダを参照してください。

## 注意事項
- 画面フォントや解像度がテンプレートと異なると認識精度が下がります。テンプレート画像は実機で再キャプチャして調整してください。  
- 長時間稼働するため、電源と接続の安定を確保してください。  
- 本スクリプトは改変された Poke-Controller（Modified/Extension）を想定しています。純正版では動作しない可能性があります。  
- 新規追加のテストおよび単回実行スクリプトは実行前に手動でテンプレート・メニュー状態を確認して動作確認を行ってください。

---

最後に、必要なら英語版やトラブルシュート、テンプレート作成手順を追加します。
