import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor

# 🚀 本地快取記憶體暫存區：普通互毆扣血只在本地計算，打死怪才同步回雲端，大幅提升回傳速度
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
    """【視覺化按鈕圖卡升級版】動態生成附帶行動按鈕的 Flex Message 卡片"""
    import jobs
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    job_mod = jobs.JOBS_DATA.get(current_job, jobs.JOBS_DATA["初心者"])
    
    # 計算血量上限
    base_vit = p.get("vitality", 10 + (level * 3))
    vit_val = int(base_vit * job_mod["vit_mod"])
    calculated_max_hp = 100 + (vit_val * 5) + (level * 15)
    
    # 計算魔力上限
    base_men = p.get("sprit", 10 + (level * 2))
    men_val = int(base_men * job_mod["men_mod"])
    calculated_max_mp = 50 + (men_val * 4) + (level * 5)
    current_mp = p.get("mp", calculated_max_mp)
    
    p_pct = max(0, min(100, int((p["hp"] / calculated_max_hp) * 100)))
    mp_pct = max(0, min(100, int((current_mp / calculated_max_mp) * 100)))
    
    def get_bar(pct, color): 
        return {
            "type": "box", "layout": "vertical", "backgroundColor": "#2A2A2A", "height": "10px", "cornerRadius": "5px", "margin": "xs", 
            "contents": [{"type": "box", "layout": "vertical", "backgroundColor": color, "width": f"{pct}%", "height": "10px", "cornerRadius": "5px"}]
        }
                
    contents = []
    
    # ⚔️ 1. 頂部動態戰報標頭
    if "擊敗對手" in title:
        header_title = "🏆 戰鬥大獲全勝 🏆"
    elif "突破成功" in title:
        header_title = "✨ 天賦覺醒突破 ✨"
    elif "配點成功" in title:
        header_title = "💪 屬性天賦加點 💪"
    elif p["hp"] <= 0:
        header_title = "☠️ 勇者不幸陣亡 ☠️"
    else:
        header_title = "⚔️ 戰場即時動態 ⚔️"
        
    contents.append({"type": "text", "text": header_title, "weight": "bold", "size": "md", "align": "center", "color": "#FFFFFF"})
    contents.append({"type": "separator", "margin": "md"})
    contents.append({"type": "text", "text": str(title), "size": "sm", "wrap": True, "margin": "md", "color": "#E0E0E0"})
    
    # 👾 2. 敵方怪物血條區
    if enemy: 
        e_pct = max(0, min(100, int((enemy["hp"] / enemy["max_hp"]) * 100)))
        contents.extend([
            {"type": "separator", "margin": "md"}, 
            {"type": "text", "text": f"👾 {enemy['name']}", "weight": "bold", "size": "md", "margin": "md", "color": "#FF3B30"}, 
            {"type": "text", "text": f"血量狀態: {max(0, enemy['hp'])} / {enemy['max_hp']}", "size": "xs", "color": "#8E8E93", "margin": "xs"}, 
            get_bar(e_pct, "#FF3B30")
        ])
        
    # 👤 3. 勇者狀態與雙血條區
    contents.extend([
        {"type": "separator", "margin": "md"}, 
        {"type": "text", "text": f"👤 勇者進度 ({current_job} Lv.{p['level']})", "weight": "bold", "size": "md", "margin": "md", "color": "#007AFF"}, 
        {"type": "text", "text": f"血量狀態: {p['hp']} / {calculated_max_hp}", "size": "xs", "color": "#8E8E93", "margin": "xs"}, 
        get_bar(p_pct, "#4CD964"),
        {"type": "text", "text": f"魔力狀態: {current_mp} / {calculated_max_mp}", "size": "xs", "color": "#8E8E93", "margin": "xs"}, 
        get_bar(mp_pct, "#34AADC")
    ])
    
    # 🕹️ 4. 底部智慧型動態按鈕選單 (Footer Box)
    footer_contents = []
    
    if p["hp"] <= 0:
        # 💀 狀況 A：玩家陣亡，強制只能點擊復活
        footer_contents.append({
            "type": "button", "style": "primary", "color": "#8E8E93", "height": "sm",
            "action": {"type": "message", "label": "😇 祈求神聖復活", "text": "復活"}
        })
    elif enemy:
        # ⚔️ 狀況 B：戰鬥進行中，帶出戰鬥鐵三角按鈕
        footer_contents.append({
            "type": "box", "layout": "horizontal", "spacing": "sm",
            "contents": [
                {"type": "button", "style": "primary", "color": "#FF3B30", "height": "sm", "action": {"type": "message", "label": "🗡️ 攻擊", "text": "攻擊"}},
                {"type": "button", "style": "primary", "color": "#34AADC", "height": "sm", "action": {"type": "message", "label": "🔮 技能", "text": "技能"}}
            ]
        })
        footer_contents.append({
            "type": "button", "style": "secondary", "height": "sm", "marginTop": "sm",
            "action": {"type": "message", "label": "🏃 嘗試逃跑", "text": "逃跑"}
        })
    else:
        # 🌲 狀況 C：閒置狀態（沒怪），帶出探索與移動按鈕
        footer_contents.append({
            "type": "box", "layout": "horizontal", "spacing": "sm",
            "contents": [
                {"type": "button", "style": "primary", "color": "#4CD964", "height": "sm", "action": {"type": "message", "label": "🔍 尋找怪物", "text": "尋怪"}},
                {"type": "button", "style": "secondary", "height": "sm", "action": {"type": "message", "label": "🗺️ 世界地圖", "text": "世界地圖"}}
            ]
        })
    
    # 建立最終完整的卡片結構（底色改為高質感深色系主題 #1C1C1E）
    flex_bubble = {
        "type": "bubble",
        "styles": {
            "body": {"backgroundColor": "#1C1C1E"},
            "footer": {"backgroundColor": "#2C2C2E", "separator": True}
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": contents
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "xs",
            "contents": footer_contents
        }
    }
    
    return flex_bubble
