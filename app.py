import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage

# 🚀 導入 LINE 官方原生支援 QuickReply 的標準發送模組
from linebot.v3.messaging import ApiClient, Configuration, MessagingApi

import game_core

app = Flask(__name__)

# 🔒 讀取永久固定、不再變更的環境憑證密鑰
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ⚙️ 建立新版智慧按鈕專用的組態元件
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 🎯 收到訊息，交給遊戲核心處理，同時把新版組態傳遞過去，以便發送底部的滑動小圖標按鈕！
    game_core.process_game_logic(event, line_bot_api, configuration)

if __name__ == "__main__":
    app.run()
