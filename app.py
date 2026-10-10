import os
import random
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
)

app = Flask(__name__)

# 讀取 LINE 的密鑰
line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))

# 記憶體玩家資料
players = {}

# 怪物圖鑑
MONSTERS = {
    "slime": {"name": "綠色史萊姆", "min_hp": 15, "max_hp": 25, "atk": 3, "gold_range": (10, 20), "exp": 10},
    "goblin": {"name": "哥布林小偷", "min_hp": 35, "max_hp": 50, "atk": 6, "gold_range": (25, 40), "exp": 25}
}

# 商店武器圖鑑 (名稱, 價格, 攻擊力加成)
SHOP_WEAPONS = {
    "木劍": {"price": 50, "atk_bonus": 5},
    "鐵劍": {"price": 150, "atk_bonus": 15}
}

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
    user_id = event.source.user_id
    user_msg = event.message.text.strip()

    # 初始化玩家資料
    if user_id not in players:
        players[user_id] = {
            "hp": 100, "max_hp": 100, "level": 1, "exp": 0, "gold": 0, "enemy": None, "weapon": "赤手空拳"
        }

    p = players[user_id]
    reply_text = ""

    # 1. 檢視狀態
    if user_msg == "我的狀態":
        w_bonus = SHOP_WEAPONS[p["weapon"]]["atk_bonus"] if p["weapon"] in SHOP_WEAPONS else 0
        reply_text = (
            f"👤 【勇者狀態】\n"
            f"等級: Lv.{p['level']}\n"
            f"血量: {p['hp']} / {p['max_hp']}\n"
            f"裝備: ⚔️ {p['weapon']} (傷害+{w_bonus})\n"
            f"經驗值: {p['exp']} / {p['level'] * 50}\n"
            f"金幣: 💰 {p['gold']}\n\n"
            f"💡 輸入【冒險商店】購買神兵利器！"
        )
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

    # 2. 尋找怪物
    elif user_msg == "尋找怪物":
        if p["hp"] <= 0:
            reply_text = "❌ 你已經陣亡了！請輸入【復活】來重整旗鼓。"
        elif p["enemy"] is not None:
            reply_text = f"⚔️ 你眼前正卡著一隻【{p['enemy']['name']}】！請先專心輸入【攻擊】！"
        else:
            m_type = random.choice(list(MONSTERS.keys()))
            m_template = MONSTERS[m_type]
            m_hp = random.randint(m_template["min_hp"], m_template["max_hp"])
            
            p["enemy"] = {
                "name": m_template["name"], "hp": m_hp, "max_hp": m_hp, "atk": m_template["atk"],
                "gold_range": m_template["gold_range"], "exp": m_template["exp"]
            }
            reply_text = (
                f"⚠️ 遭遇野生怪物！\n👾 【{p['enemy']['name']}】出現了！\n"
                f"🩸 怪物血量: {p['enemy']['hp']} / {p['enemy']['max_hp']}\n\n"
                f"⚔️ 請點擊【攻擊】或輸入【逃跑】！"
            )
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

    # 3. 攻擊指令
    elif user_msg == "攻擊":
        if p["hp"] <= 0:
            reply_text = "❌ 你已經陣亡了！請輸入【復活】。"
        elif p["enemy"] is None:
            reply_text = "🧐 周圍空空如也，沒有怪物。點擊【尋找怪物】出發吧！"
        else:
            enemy = p["enemy"]
            w_bonus = SHOP_WEAPONS[p["weapon"]]["atk_bonus"] if p["weapon"] in SHOP_WEAPONS else 0
            p_dmg = random.randint(5, 12) + (p["level"] * 2) + w_bonus
            enemy["hp"] -= p_dmg
            
            combat_log = f"💥 你揮舞【{p['weapon']}】！對【{enemy['name']}】造成 {p_dmg} 點傷害！\n"

            if enemy["hp"] <= 0:
                gold_get = random.randint(enemy["gold_range"][0], enemy["gold_range"][1])
                exp_get = enemy["exp"]
                
                p["gold"] += gold_get
                p["exp"] += exp_get
                p["enemy"] = None
                
                combat_log += f"🎉 擊敗了【{enemy['name']}】！\n💰 獲得金幣 +{gold_get}\n✨ 獲得經驗值 +{exp_get}\n"
                
                lvl_up_need = p["level"] * 50
                if p["exp"] >= lvl_up_need:
                    p["level"] += 1
                    p["exp"] -= lvl_up_need
                    p["max_hp"] += 15
                    p["hp"] = p["max_hp"]
                    combat_log += f"🎊 恭喜！你升級到了 Lv.{p['level']}！HP已補滿！\n"
                
                reply_text = combat_log
            else:
                m_atk = random.randint(1, enemy["atk"])
                p["hp"] -= m_atk
                combat_log += f"🩹 【{enemy['name']}】反擊！你受到了 {m_atk} 點傷害！\n"
                
                if p["hp"] <= 0:
                    p["hp"] = 0
                    p["enemy"] = None
                    combat_log += "💀 你被擊倒了！請點擊【復活】。"
                else:
                    combat_log += (
                        f"------------------\n"
                        f"🩸 你的血量: {p['hp']} / {p['max_hp']}\n"
                        f"👾 怪物血量: {enemy['hp']} / {enemy['max_hp']}"
                    )
                reply_text = combat_log
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

    # 4. 冒險商店指令（升級為精美 Flex Message 卡片）
    elif user_msg == "冒險商店":
        flex_contents = {
            "type": "bubble",
            "body": {
                "type": "box", "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "🏪 村莊武器店", "weight": "bold", "size": "xl", "color": "#1DB446"},
                    {"type": "text", "text": f"你目前擁有: 💰 {p['gold']} 金幣", "size": "sm", "color": "#555555", "margin": "md"},
                    {"type": "separator", "margin": "lg"},
                    # 商品 1：木劍
                    {
                        "type": "box", "layout": "horizontal", "margin": "lg", "align": "center",
                        "contents": [
                            {"type": "text", "text": "⚔️ 木劍 (傷害+5)", "weight": "bold", "size": "md", "flex": 3},
                            {"type": "button", "action": {"type": "message", "label": "💰 50", "text": "購買木劍"}, "style": "primary", "color": "#E6A23C", "height": "sm", "flex": 2}
                        ]
                    },
                    # 商品 2：鐵劍
                    {
                        "type": "box", "layout": "horizontal", "margin": "lg", "align": "center",
                        "contents": [
                            {"type": "text", "text": "⚔️ 鐵劍 (傷害+15)", "weight": "bold", "size": "md", "flex": 3},
                            {"type": "button", "action": {"type": "message", "label": "💰 150", "text": "購買鐵劍"}, "style": "primary", "color": "#F56C6C", "height": "sm", "flex": 2}
                        ]
                    }
                ]
            }
        }
        # 使用 FlexSendMessage 發送精美卡片
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text="開啟了冒險商店", contents=flex_contents)
        )

    # 5. 購買邏輯
    elif user_msg.startswith("購買"):
        item_name = user_msg.replace("購買", "").strip()
        if item_name in SHOP_WEAPONS:
            cost = SHOP_WEAPONS[item_name]["price"]
            if p["gold"] >= cost:
                p["gold"] -= cost
                p["weapon"] = item_name
                reply_text = f"🛍️ 購買成功！你裝備了【{item_name}】！\n💰 剩餘金幣: {p['gold']}\n趕快去【尋找怪物】試試新武器的威力吧！"
            else:
                reply_text = f"❌ 金幣不足！【{item_name}】需要 {cost} 金幣，你只有 {p['gold']} 金幣。再去多打幾隻史萊姆吧！"
        else:
            reply_text = "❌ 本店沒有販售這項商品。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

    # 6. 逃跑與復活
    elif user_msg == "逃跑":
        p["enemy"] = None
        reply_text = "💨 成功逃跑了！"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    elif user_msg == "復活":
        if p["hp"] > 0:
            reply_text = "你還活著呢！"
        else:
            p["hp"] = int(p["max_hp"] * 0.5)
            p["gold"] = max(0, p["gold"] - 20)
            reply_text = f"😇 復活成功！血量恢復至 {p['hp']}，扣除 20 金幣。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    else:
        reply_text = "請點擊下方選單開始遊戲！"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

if __name__ == "__main__":
    app.run()
