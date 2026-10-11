import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor

# 🚀 LINE v3 SDK 必備的快速回應物件元件
from linebot.v3.messaging import QuickReply, QuickReplyItem, MessageAction

MEMORY_PLAYERS = {}

def get_db_connection():
    db_url = os.environ.get('DATABASE_URL')
    return psycopg2.connect(db_url)

def load_player(user_id):
    if user_id in MEMORY_PLAYERS:
        return MEMORY_PLAYERS[user_id]
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM players WHERE user_id = %s", (user_id,))
    player = cur.fetchone()
    if not player:
        cur.execute(
            "INSERT INTO players (user_id, hp, max_hp, level, exp, gold, weapon, enemy, strength, agility, intelligence, vitality, luck, sprit, job, attribute_points) VALUES (%s, 100, 100, 1, 0, 0, '赤手空拳', NULL, 10, 10, 10, 10, 10, 10, '初心者', 0)",
            (user_id,)
        )
        conn.commit()
        cur.execute("SELECT * FROM players WHERE user_id = %s", (user_id,))
        player = cur.fetchone()
    cur.close()
    conn.close()
    if player and player['enemy']: 
        player['enemy'] = json.loads(player['enemy'])
    MEMORY_PLAYERS[user_id] = dict(player)
    return MEMORY_PLAYERS[user_id]

def save_player(p):
    MEMORY_PLAYERS[p['user_id']] = p
    conn = get_db_connection()
    cur = conn.cursor()
    enemy_str = json.dumps(p['enemy']) if p['enemy'] else None
    cur.execute(
        "UPDATE players SET hp=%s, max_hp=%s, level=%s, exp=%s, gold=%s, weapon=%s, enemy=%s, strength=%s, agility=%s, intelligence=%s, vitality=%s, luck=%s, sprit=%s, job=%s, attribute_points=%s WHERE user_id=%s",
        (p['hp'], p['max_hp'], p['level'], p['exp'], p['gold'], p['weapon'], enemy_str, 
         p.get('strength', 10), p.get('agility', 10), p.get('intelligence', 10), p.get('vitality', 10), p.get('luck', 10), p.get('sprit', 10), p.get('job', '初心者'), p.get('attribute_points', 0), p['user_id'])
    )
    conn.commit()
    cur.close()
    conn.close()

def make_battle_card(title, p, enemy):
    """【Quick Reply 智慧完全體】生成完美過審的黑曜石血條卡片"""
    import jobs
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    job_mod = jobs.JOBS_DATA.get(current_job, jobs.JOBS_DATA["初心者"])
    
    # 計算血量與魔力上限
    vit_val = int(p.get("vitality", 10 + (level * 3)) * job_mod["vit_mod"])
    calculated_max_hp = 100 + (vit_val * 5) + (level * 15)
    men_val = int(p.get("sprit", 10 + (level * 2)) * job_mod["men_mod"])
    calculated_max_mp = 50 + (men_val * 4) + (level * 5)
    current_mp = p.get("mp", calculated_max_mp)
    
    p_pct = max(0, min(100, int((p["hp"] / calculated_max_hp) * 100)))
    mp_pct = max(0, min(100, int((current_mp / calculated_max_mp) * 100)))
    
    def get_bar(pct, color): 
        return {
            "type": "box", "layout": "vertical", "backgroundColor": "#2A2A2A", "height": "10px", "cornerRadius": "5px", "margin": "xs", 
            "contents": [{
                "type": "box", 
                "layout": "vertical", 
                "backgroundColor": color, 
                "width": f"{pct}%", 
                "height": "10px", 
                "cornerRadius": "5px",
                "contents": [] # 🌟 【Bug 核心修復】補上這個空列表，解決新版 v3 SDK Pydantic 嚴格驗證閃退問題！
            }]
        }
                
    contents = []
    
    # 🧠 戰報標頭狀態判定
    if "擊敗對手" in title: header_title = "🏆 戰鬥大獲全勝 🏆"
    elif "突破成功" in title: header_title = "✨ 天賦覺醒突破 ✨"
    elif "配點成功" in title: header_title = "💪 屬性天賦加點 💪"
    elif p["hp"] <= 0: header_title = "☠ "
    else: header_title = "⚔ 戰場即時動態 ⚔"
        
    contents.append({"type": "text", "text": header_title, "weight": "bold", "size": "md", "align": "center", "color": "#FFFFFF"})
    contents.append({"type": "separator", "margin": "md"})
    
    if enemy and "env" in enemy:
        contents.append({
            "type": "box", "layout": "horizontal", "margin": "md", "backgroundColor": "#2C2C2E", "paddingAll": "sm", "cornerRadius": "md",
            "contents": [{"type": "text", "text": f"🌀 戰場環境：{enemy['env']}", "size": "xs", "color": "#FFCC00", "weight": "bold"}]
        })
        
    contents.append({"type": "text", "text": str(title), "size": "sm", "wrap": True, "margin": "md", "color": "#E0E0E0"})
    
    if enemy: 
        e_pct = max(0, min(100, int((enemy["hp"] / enemy["max_hp"]) * 100)))
        contents.extend([
            {"type": "separator", "margin": "md"}, 
            {"type": "text", "text": f"👾 {enemy['name']}", "weight": "bold", "size": "md", "margin": "md", "color": "#FF3B30"}, 
            {"type": "text", "text": f"血量狀態: {max(0, enemy['hp'])} / {enemy['max_hp']}", "size": "xs", "color": "#8E8E93", "margin": "xs"}, 
            get_bar(e_pct, "#FF3B30")
        ])
        
    contents.extend([
        {"type": "separator", "margin": "md"}, 
        {"type": "text", "text": f"👤 勇者狀態 ({current_job} Lv.{p['level']})", "weight": "bold", "size": "md", "margin": "md", "color": "#007AFF"}, 
        {"type": "text", "text": f"血量狀態: {p['hp']} / {calculated_max_hp}", "size": "xs", "color": "#8E8E93", "margin": "xs"}, 
        get_bar(p_pct, "#4CD964"),
        {"type": "text", "text": f"魔力狀態: {current_mp} / {calculated_max_mp}", "size": "xs", "color": "#8E8E93", "margin": "xs"}, 
        get_bar(mp_pct, "#34AADC")
    ])
    
    flex_bubble = {
        "type": "bubble",
        "styles": {"body": {"backgroundColor": "#1C1C1E"}},
        "body": {
            "type": "box", 
            "layout": "vertical", 
            "contents": contents
        }
    }
    
    quick_items = []
    if p["hp"] <= 0:
        quick_items.append(QuickReplyItem(action=MessageAction(label="😇 祈求復活", text="復活")))
    elif enemy:
        quick_items.append(QuickReplyItem(action=MessageAction(label="🗡 攻擊", text="攻擊")))
        quick_items.append(QuickReplyItem(action=MessageAction(label="🔮 技能書", text="技能書")))
        quick_items.append(QuickReplyItem(action=MessageAction(label="🏃 逃跑", text="逃跑")))
    else:
        quick_items.append(QuickReplyItem(action=MessageAction(label="🔍 尋找怪物", text="尋怪")))
        quick_items.append(QuickReplyItem(action=MessageAction(label="🎒 我的背包", text="我的背包")))
        quick_items.append(QuickReplyItem(action=MessageAction(label="👤 我的狀態", text="我的狀態")))
        quick_items.append(QuickReplyItem(action=MessageAction(label="🗺 世界地圖", text="世界地圖")))
        quick_items.append(QuickReplyItem(action=MessageAction(label="🏪 冒險商店", text="冒險商店")))

    quick_reply_object = QuickReply(items=quick_items)
    return {"flex": flex_bubble, "quick_reply": quick_reply_object}
