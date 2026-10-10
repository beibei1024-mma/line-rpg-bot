import os, random, json, psycopg2, base64
from flask import Flask, request, abort
from psycopg2.extras import RealDictCursor
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage

app = Flask(__name__)
line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))

MONSTERS = {
    "slime": {"name": "綠色史萊姆", "min_hp": 20, "max_hp": 20, "atk": 3, "gold_range": (10, 500), "exp": 50},
    "goblin": {"name": "哥布林小偷", "min_hp": 45, "max_hp": 45, "atk": 6, "gold_range": (25, 1000), "exp": 100}
}
SHOP_WEAPONS = {"木劍": {"price": 50, "atk_bonus": 5}, "鐵劍": {"price": 150, "atk_bonus": 15}}

def get_db_connection():
    db_url = os.environ.get('DATABASE_URL')
    return psycopg2.connect(db_url)

def load_player(user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM players WHERE user_id = %s", (user_id,))
    player = cur.fetchone()
    if not player:
        cur.execute("INSERT INTO players (user_id, hp, max_hp, level, exp, gold, weapon, enemy) VALUES (%s, 100, 100, 1, 0, 0, '赤手空拳', NULL)", (user_id,))
        conn.commit()
        cur.execute("SELECT * FROM players WHERE user_id = %s", (user_id,))
        player = cur.fetchone()
    cur.close(); conn.close()
    if player and player['enemy']: player['enemy'] = json.loads(player['enemy'])
    return dict(player)

def save_player(p):
    conn = get_db_connection()
    cur = conn.cursor()
    enemy_str = json.dumps(p['enemy']) if p['enemy'] else None
    cur.execute("UPDATE players SET hp=%s, max_hp=%s, level=%s, exp=%s, gold=%s, weapon=%s, enemy=%s WHERE user_id=%s", (p['hp'], p['max_hp'], p['level'], p['exp'], p['gold'], p['weapon'], enemy_str, p['user_id']))
    conn.commit(); cur.close(); conn.close()

def make_battle_card(title, p, enemy):
    p_pct = max(0, min(100, int((p["hp"] / p["max_hp"]) * 100)))
    e_pct = max(0, min(100, int((enemy["hp"] / enemy["max_hp"]) * 100))) if enemy else 0
    def get_bar(pct, color): return {"type": "box", "layout": "vertical", "backgroundColor": "#E0E0E0", "height": "8px", "cornerRadius": "4px", "margin": "sm", "contents": [{"type": "box", "layout": "vertical", "backgroundColor": color, "width": f"{pct}%", "height": "8px", "cornerRadius": "4px"}]}
    contents = [{"type": "text", "text": title, "weight": "bold", "size": "md", "color": "#111111", "wrap": True}]
    if enemy: contents.extend([{"type": "separator", "margin": "md"}, {"type": "text", "text": f"👾 {enemy['name']}", "weight": "bold", "size": "md", "margin": "md", "color": "#FF3B30"}, {"type": "text", "text": f"HP: {max(0, enemy['hp'])} / {enemy['max_hp']}", "size": "xs", "color": "#666666"}, get_bar(e_pct, "#FF3B30")])
    contents.extend([{"type": "separator", "margin": "md"}, {"type": "text", "text": "👤 勇者狀態", "weight": "bold", "size": "md", "margin": "md", "color": "#007AFF"}, {"type": "text", "text": f"HP: {p['hp']} / {p['max_hp']}", "size": "xs", "color": "#666666"}, get_bar(p_pct, "#4CD964")])
    return {"type": "bubble", "body": {"type": "box", "layout": "vertical", "contents": contents}}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try: handler.handle(body, signature)
    except InvalidSignatureError: abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_msg = event.message.text.replace(" ", "").strip()
    p = load_player(user_id)

    if user_msg == "我的狀態":
        w_bonus = SHOP_WEAPONS[p["weapon"]]["atk_bonus"] if p["weapon"] in SHOP_WEAPONS else 0
        reply_text = f"👤 【勇者狀態】\n等級: Lv.{p['level']}\n血量: {p['hp']} / {p['max_hp']}\n裝備: ⚔️ {p['weapon']} (傷害+{w_bonus})\n經驗值: {p['exp']} / {p['level'] * 50}\n金幣: 💰 {p['gold']}\n\n💡 輸入【冒險商店】購買神兵利器！"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    elif user_msg == "尋找怪物":
        if p["hp"] <= 0:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 你已經陣亡了！請點擊【復活】。"))
            return
        if p["enemy"] is not None:
            card = make_battle_card("⚔️ 你的眼前還卡著一隻怪！請專心應戰！", p, p["enemy"])
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="遭遇怪物", contents=card))
            return
        m_type = random.choice(list(MONSTERS.keys()))
        m_template = MONSTERS[m_type]
        m_hp = random.randint(m_template["min_hp"], m_template["max_hp"])
        p["enemy"] = {"name": m_template["name"], "hp": m_hp, "max_hp": m_hp, "atk": m_template["atk"], "gold_range": m_template["gold_range"], "exp": m_template["exp"]}
        save_player(p)
        card = make_battle_card("⚠️ 野生怪物出現了！", p, p["enemy"])
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="遭遇怪物", contents=card))
    elif user_msg == "攻擊":
        if p["hp"] <= 0 or p["enemy"] is None:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="❌ 無法攻擊（可能已陣亡或周圍沒有怪物）。"))
            return
        enemy = p["enemy"]
        w_bonus = SHOP_WEAPONS[p["weapon"]]["atk_bonus"] if p["weapon"] in SHOP_WEAPONS else 0
        p_dmg = random.randint(5, 12) + (p["level"] * 2) + w_bonus
        enemy["hp"] -= p_dmg
        log = f"💥 你揮舞【{p['weapon']}】對【{enemy['name']}】造成 {p_dmg} 點傷害！\n"
        if enemy["hp"] <= 0:
            gold_get = random.randint(enemy["gold_range"][0], enemy["gold_range"][1])
            p["gold"] += gold_get; p["exp"] += enemy["exp"]; p["enemy"] = None
            log += f"🎉 擊敗對手！獲得金幣 +{gold_get}、經驗值 +{enemy['exp']}！"
            if p["exp"] >= p["level"] * 50:
                p["exp"] -= p["level"] * 50; p["level"] += 1; p["max_hp"] += 15; p["hp"] = p["max_hp"]
                log += f"\n🎊 恭喜升級到 Lv.{p['level']}！HP已補滿！"
            save_player(p)
            card = make_battle_card(log, p, None)
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="戰鬥結束", contents=card))
        else:
            m_atk = random.randint(1, enemy["atk"])
            p["hp"] -= m_atk
            log += f"🩹 【{enemy['name']}】反擊！你受到 {m_atk} 點傷害！"
            if p["hp"] <= 0: p["hp"] = 0; p["enemy"] = None; log += "\n💀 你被擊倒了！請點擊【復活】。"
            save_player(p)
            card = make_battle_card(log, p, enemy if p["hp"] > 0 else None)
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="戰鬥回合", contents=card))
    elif user_msg == "冒險商店":
        flex_contents = {"type": "bubble", "body": {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "🏪 村莊武器店", "weight": "bold", "size": "xl", "color": "#1DB446"}, {"type": "text", "text": f"你目前擁有: 💰 {p['gold']} 金幣", "size": "sm", "color": "#555555", "margin": "md"}, {"type": "separator", "margin": "lg"}, {"type": "box", "layout": "horizontal", "margin": "lg", "align": "center", "contents": [{"type": "text", "text": "⚔️ 木劍 (傷害+5)", "weight": "bold", "size": "md", "flex": 3}, {"type": "button", "action": {"type": "message", "label": "💰 50", "text": "購買木劍"}, "style": "primary", "color": "#E6A23C", "height": "sm", "flex": 2}]}, {"type": "box", "layout": "horizontal", "margin": "lg", "align": "center", "contents": [{"type": "text", "text": "⚔️ 鐵劍 (傷害+15)", "weight": "bold", "size": "md", "flex": 3}, {"type": "button", "action": {"type": "message", "label": "💰 150", "text": "購買鐵劍"}, "style": "primary", "color": "#F56C6C", "height": "sm", "flex": 2}]}]}}
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="開啟了冒險商店", contents=flex_contents))
    elif user_msg.startswith("購買"):
        item_name = user_msg.replace("購買", "").strip()
        if item_name in SHOP_WEAPONS:
            cost = SHOP_WEAPONS[item_name]["price"]
            if p["gold"] >= cost: p["gold"] -= cost; p["weapon"] = item_name; reply_text = f"🛍️ 購買成功！你裝備了【{item_name}】！\n💰 剩餘金幣: {p['gold']}"
            else: reply_text = f"❌ 金幣不足！還差 {cost - p['gold']} 金幣。"
        else: reply_text = "❌ 本店沒有販售這項商品。"
        save_player(p); line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    elif user_msg == "逃跑":
        p["enemy"] = None; save_player(p)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="💨 成功逃跑了！"))
    elif user_msg == "復活":
        if p["hp"] > 0: reply_text = "你還活著呢！"
        else: p["hp"] = int(p["max_hp"] * 0.5); p["gold"] = max(0, p["gold"] - 20); reply_text = f"😇 復活成功！血量恢復至 {p['hp']}，扣除 20 金幣。"
        save_player(p); line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    else: line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請點擊下方選單開始遊戲！"))

if __name__ == "__main__": app.run()
