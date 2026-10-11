import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor

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
        # ✨ 在初始註冊時，同步加入 mp=50 的設定
        cur.execute(
            "INSERT INTO players (user_id, hp, max_hp, mp, level, exp, gold, weapon, enemy, strength, agility, intelligence, vitality, luck, sprit, job, attribute_points) VALUES (%s, 100, 100, 50, 1, 0, 0, '赤手空拳', NULL, 10, 10, 10, 10, 10, 10, '初心者', 0)",
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
    
    # ✨ 在 SQL UPDATE 語句中，精準同步寫入 mp=%s 欄位
    cur.execute(
        "UPDATE players SET hp=%s, max_hp=%s, mp=%s, level=%s, exp=%s, gold=%s, weapon=%s, enemy=%s, strength=%s, agility=%s, intelligence=%s, vitality=%s, luck=%s, sprit=%s, job=%s, attribute_points=%s WHERE user_id=%s",
        (p['hp'], p['max_hp'], p.get('mp', 50), p['level'], p['exp'], p['gold'], p['weapon'], enemy_str, 
         p.get('strength', 10), p.get('agility', 10), p.get('intelligence', 10), p.get('vitality', 10), p.get('luck', 10), p.get('sprit', 10), p.get('job', '初心者'), p.get('attribute_points', 0), p['user_id'])
    )
    conn.commit()
    cur.close()
    conn.close()

def make_battle_card(title, p, enemy):
    import jobs
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    job_mod = jobs.JOBS_DATA.get(current_job, jobs.JOBS_DATA["初心者"])
    
    base_vit = p.get("vitality", 10 + (level * 3))
    vit_val = int(base_vit * job_mod["vit_mod"])
    calculated_max_hp = 100 + (vit_val * 5) + (level * 15)
    
    # 🔷 計算最大魔力與當前 MP 百分比
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
    
    if "擊敗對手" in title:
        header_title = "🏆 戰鬥大獲全勝 🏆"
    elif "突破成功" in title:
        header_title = "✨ 天賦覺醒突破 ✨"
    elif "配點成功" in title:
        header_title = "💪 屬性天賦加點 💪"
    else:
        header_title = "⚔️ 戰場即時動態 ⚔️"
        
    contents.append({"type": "text", "text": header_title, "weight": "bold", "size": "md", "align": "center"})
    contents.append({"type": "separator", "margin": "md"})
    contents.append({"type": "text", "text": str(title), "size": "sm", "wrap": True, "margin": "md"})
    
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
        # 顯示血量條
        {"type": "text", "text": f"血量狀態: {p['hp']} / {calculated_max_hp}", "size": "xs", "color": "#8E8E93", "margin": "xs"}, 
        get_bar(p_pct, "#4CD964"),
        # ✨ UI 優化：在戰鬥卡片中同步渲染「魔力條（藍色）」
        {"type": "text", "text": f"魔力狀態: {current_mp} / {calculated_max_mp}", "size": "xs", "color": "#8E8E93", "margin": "xs"}, 
        get_bar(mp_pct, "#34AADC")
    ])
    
    return {"type": "bubble", "body": {"type": "box", "layout": "vertical", "contents": contents}}
