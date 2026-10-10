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
    """【真・防彈優化】將所有 LINE 不支援的敏感排版標籤全部剔除，確保 100% 順暢發送不已讀"""
    import jobs
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    job_mod = jobs.JOBS_DATA.get(current_job, jobs.JOBS_DATA["初心者"])
    
    base_vit = p.get("vitality", 10 + (level * 3))
    vit_val = int(base_vit * job_mod["vit_mod"])
    calculated_max_hp = 100 + (vit_val * 5) + (level * 15)
    
    p_pct = max(0, min(100, int((p["hp"] / calculated_max_hp) * 100)))
    
    def get_bar(pct, color): 
        return {
            "type": "box", "layout": "vertical", "backgroundColor": "#2A2A2A", "height": "10px", "cornerRadius": "5px", "margin": "md", 
            "contents": [{"type": "box", "layout": "vertical", "backgroundColor": color, "width": f"{pct}%", "height": "10px", "cornerRadius": "5px"}]
        }
                
    contents = []
    
    # ⚔️ 1. 頂部動態戰報日誌區 
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
    
    # 📝 2. 戰報詳細日誌內容區（100% 標準乾淨格式，絕無 lineSpacing 屬性）
    contents.append({
        "type": "text", "text": str(title), "size": "sm", "wrap": True, "margin": "md"
    })
    
    # 👾 3. 敵方怪物血條區
    if enemy: 
        e_pct = max(0, min(100, int((enemy["hp"] / enemy["max_hp"]) * 100)))
        contents.extend([
            {"type": "separator", "margin": "md"}, 
            {"type": "text", "text": f"👾 {enemy['name']}", "weight": "bold", "size": "md", "margin": "md", "color": "#FF3B30"}, 
            {"type": "text", "text": f"血量狀態: {max(0, enemy['hp'])} / {enemy['max_hp']}", "size": "xs", "color": "#8E8E93", "margin": "xs"}, 
            get_bar(e_pct, "#FF3B30")
        ])
        
    # 👤 4. 勇者血條固定區
    contents.extend([
        {"type": "separator", "margin": "md"}, 
        {"type": "text", "text": f"👤 勇者進度 ({current_job} Lv.{p['level']})", "weight": "bold", "size": "md", "margin": "md", "color": "#007AFF"}, 
        {"type": "text", "text": f"血量狀態: {p['hp']} / {calculated_max_hp}", "size": "xs", "color": "#8E8E93", "margin": "xs"}, 
        get_bar(p_pct, "#4CD964")
    ])
    
    return {"type": "bubble", "body": {"type": "box", "layout": "vertical", "contents": contents}}
