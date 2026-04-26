# Discord 通知モジュールへの差し替え手順

このプロジェクトで LINE 通知モジュールを Discord（Webhook）版に差し替える手順を記載します。

要点
- Python モジュール（通知ロジック）はプロジェクトのルートにある SerialController ディレクトリ直下に配置します（ファイル名: LineNotify.py を上書き）。
- Webhook 設定は ini ファイルとして SerialController/profiles/default に配置します（ファイル名: discord_settings.ini）。

手順（コピペ可能なコマンド例）
- ディレクトリ作成（必要な場合）
  - Unix/macOS:
    mkdir -p SerialController/profiles/default
  - Windows (cmd):
    md SerialController\profiles\default

- ファイル配置（ワークスペース内のサンプルを使う場合）
  - Unix/macOS:
    cp 参考/LineNotify.py SerialController/LineNotify.py
    cp 参考/discord_settings.ini SerialController/profiles/default/discord_settings.ini
  - Windows (cmd):
    copy 参考\LineNotify.py SerialController\LineNotify.py
    copy 参考\discord_settings.ini SerialController\profiles\default\discord_settings.ini

設定ファイル（SerialController/profiles/default/discord_settings.ini の例）
```ini
[DISCORD]
webhook_url = https://discord.com/api/webhooks/あなたの_webhook_URL