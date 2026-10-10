import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# 從系統環境變數讀取 LINE 的密鑰
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

# 當玩家傳送文字訊息時，觸發這個函式
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text.strip()

    # 簡單的 MUD 遊戲邏輯測試
    if user_msg == "開始冒險":
        reply_text = "⚔️ 你拔出了新手木劍，走進了神秘的史萊姆森林！\n輸入【攻擊】來迎戰怪物！"
    elif user_msg == "攻擊":
        reply_text = "💥 你對史萊姆造成了 5 點傷害！史萊姆倒下了！\n💰 獲得金幣 +10、經驗值 +5！"
    else:
        reply_text = f"勇者，我聽不懂「{user_msg}」。\n請輸入【開始冒險】來展開旅程！"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

if __name__ == "__main__":
    app.run()
