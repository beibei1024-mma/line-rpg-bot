import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage

# 🎮 跨檔案導入你未來的「遊戲判斷核心」
import game_core

app = Flask(__name__)

# ⚙️ 讀取永久固定、不再變更的環境變數密鑰
line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))

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
    # 傳話筒唯一任務：收到訊息，立刻轉包交給遊戲核心去處理所有的攻擊與判定！
    game_core.process_game_logic(event, line_bot_api)

if __name__ == "__main__":
    app.run()
