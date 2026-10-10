import os
import random
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# 讀取 LINE 的密鑰
line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))

# 暫時用記憶體儲存玩家狀態（玩家的 LINE ID 為 Key）
# 格式: { "user_id": { "hp": 100, "max_hp": 100, "level": 1, "exp": 0, "gold": 0, "enemy": None } }
players = {}

# 怪物圖鑑
MONSTERS = {
    "slime": {"name": "綠色史萊姆", "min_hp": 15, "max_hp": 25, "atk": 3, "gold_range": (5, 15), "exp": 10},
    "goblin": {"name": "哥布林", "min_hp": 30, "max_hp": 45, "atk": 6, "gold_range": (15, 30), "exp": 25}
    "Reinforced goblin": {"name": "強化哥布林", "min_hp": 60, "max_hp": 90, "atk": 10, "gold_range": (30, 60), "exp": 50}
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

    # 如果是新玩家，初始化資料
    if user_id not in players:
        players[user_id] = {
            "hp": 100, "max_hp": 100, "level": 1, "exp": 0, "gold": 0, "enemy": None
        }

    p = players[user_id]
    reply_text = ""

    # 1. 檢視狀態指令
    if user_msg == "我的狀態":
        reply_text = (
            f"👤 【勇者狀態】\n"
            f"等級: Lv.{p['level']}\n"
            f"血量: {p['hp']} / {p['max_hp']}\n"
            f"經驗值: {p['exp']} / {p['level'] * 50}\n"
            f"金幣: 💰 {p['gold']}\n"
            f"提示：輸入【尋找怪物】開始戰鬥！"
        )

    # 2. 遇怪指令
    elif user_msg == "尋找怪物":
        if p["hp"] <= 0:
            reply_text = "❌ 你已經陣亡了！請輸入【復活】來重整旗鼓。"
        elif p["enemy"] is not None:
            reply_text = f"⚔️ 你眼前正卡著一隻【{p['enemy']['name']}】！請先專心輸入【攻擊】！"
        else:
            # 隨機抽一隻怪物
            m_type = random.choice(list(MONSTERS.keys()))
            m_template = MONSTERS[m_type]
            m_hp = random.randint(m_template["min_hp"], m_template["max_hp"])
            
            # 將怪物的當前血量和資料存在玩家身上
            p["enemy"] = {
                "name": m_template["name"],
                "hp": m_hp,
                "max_hp": m_hp,
                "atk": m_template["atk"],
                "gold_range": m_template["gold_range"],
                "exp": m_template["exp"]
            }
            reply_text = (
                f"⚠️ 遭遇野生怪物！\n"
                f"👾 【{p['enemy']['name']}】出現了！\n"
                f"🩸 怪物血量: {p['enemy']['hp']} / {p['enemy']['max_hp']}\n\n"
                f"⚔️ 請輸入【攻擊】或【逃跑】！"
            )

    # 3. 攻擊指令
    elif user_msg == "攻擊":
        if p["hp"] <= 0:
            reply_text = "❌ 你已經陣亡了！請輸入【復活】。"
        elif p["enemy"] is None:
            reply_text = "🧐 周圍空空如也，沒有怪物可以攻擊。輸入【尋找怪物】出發吧！"
        else:
            enemy = p["enemy"]
            # 玩家對怪物造成隨機傷害 (基於等級)
            p_dmg = random.randint(5, 12) + (p["level"] * 2)
            enemy["hp"] -= p_dmg
            
            combat_log = f"💥 你奮力一擊！對【{enemy['name']}】造成 {p_dmg} 點傷害！\n"

            # 檢查怪物是否死亡
            if enemy["hp"] <= 0:
                gold_get = random.randint(enemy["gold_range"][0], enemy["gold_range"][1])
                exp_get = enemy["exp"]
                
                p["gold"] += gold_get
                p["exp"] += exp_get
                p["enemy"] = None  # 清空戰鬥狀態
                
                combat_log += f"🎉 擊敗了【{enemy['name']}】！\n💰 獲得金幣 +{gold_get}\n✨ 獲得經驗值 +{exp_get}\n"
                
                # 檢查是否升級
                lvl_up_need = p["level"] * 50
                if p["exp"] >= lvl_up_need:
                    p["level"] += 1
                    p["exp"] -= lvl_up_need
                    p["max_hp"] += 15
                    p["hp"] = p["max_hp"]  # 升級滿血
                    combat_log += f"🎊 恭喜！你升級到了 Lv.{p['level']}！最大血量提升，HP已補滿！\n"
                
                reply_text = combat_log
            else:
                # 怪物沒死，換怪物反擊
                m_atk = random.randint(1, enemy["atk"])
                p["hp"] -= m_atk
                
                combat_log += f"🩹 【{enemy['name']}】反擊！你受到了 {m_atk} 點傷害！\n"
                
                # 檢查玩家是否死亡
                if p["hp"] <= 0:
                    p["hp"] = 0
                    p["enemy"] = None  # 玩家死了也清空戰鬥
                    combat_log += "💀 你被擊倒了！眼前一片漆黑... 請輸入【復活】。"
                else:
                    combat_log += (
                        f"------------------\n"
                        f"🩸 你的血量: {p['hp']} / {p['max_hp']}\n"
                        f"👾 怪物血量: {enemy['hp']} / {enemy['max_hp']}\n\n"
                        f"⚔️ 請繼續輸入【攻擊】！"
                    )
                reply_text = combat_log

    # 4. 逃跑指令
    elif user_msg == "逃跑":
        if p["enemy"] is None:
            reply_text = "你本來就很安全，不需要逃跑。輸入【尋找怪物】去冒險吧！"
        else:
            # 50% 成功率
            if random.choice([True, False]):
                p["enemy"] = None
                reply_text = "💨 你轉身拔腿就跑，成功甩開了怪物！"
            else:
                m_atk = random.randint(1, p["enemy"]["atk"])
                p["hp"] -= m_atk
                if p["hp"] <= 0:
                    p["hp"] = 0
                    p["enemy"] = None
                    reply_text = f"❌ 逃跑失敗！你被【{p['enemy']['name']}】從背後偷襲受到 {m_atk} 點傷害！你陣亡了！"
                else:
                    reply_text = f"❌ 逃跑失敗！被【{p['enemy']['name']}】攔住了！你受到 {m_atk} 點傷害！\n🩸 目前血量: {p['hp']} / {p['max_hp']}"

    # 5. 復活指令
    elif user_msg == "復活":
        if p["hp"] > 0:
            reply_text = "心跳還很有力！你不需要復活。輸入【我的狀態】檢查看看。"
        else:
            p["hp"] = int(p["max_hp"] * 0.5)  # 半血復活
            p["gold"] = max(0, p["gold"] - 20)  # 扣除20金幣當過路費
            reply_text = f"😇 神秘的光芒包圍了你...你復活了！\n🩸 血量恢復至半滿 ({p['hp']})\n💸 復活手續費扣除 20 金幣（目前金幣：{p['gold']}）"

    else:
        reply_text = "歡迎來到文字世界！請試試輸入以下指令：\n【我的狀態】\n【尋找怪物】"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

if __name__ == "__main__":
    app.run()
