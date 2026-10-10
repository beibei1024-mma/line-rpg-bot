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
        # 👑 【核心能力值初始化】在新玩家建立時，將原創基礎屬性：力量10、敏捷10、智力10 完美塞入資料庫！
        cur.execute(
            "INSERT INTO players (user_id, hp, max_hp, level, exp, gold, weapon, enemy, strength, agility, intelligence) VALUES (%s, 100, 100, 1, 0, 0, '赤手空拳', NULL, 10, 10, 10)",
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
    
    # 👑 【核心能力值鎖存】確保更新進度時，玩家的力量、敏捷、智力同步安全鎖進 Supabase 雲端！
    cur.execute(
        "UPDATE players SET hp=%s, max_hp=%s, level=%s, exp=%s, gold=%s, weapon=%s, enemy=%s, strength=%s, agility=%s, intelligence=%s WHERE user_id=%s",
        (p['hp'], p['max_hp'], p['level'], p['exp'], p['gold'], p['weapon'], enemy_str, p.get('strength', 10), p.get('agility', 10), p.get('intelligence', 10), p['user_id'])
    )
    conn.commit()
    cur.close()
    conn.close()

def make_battle_card(title, p, enemy):
    """【原創史詩優化】將死板的文字戰報，包裝成具備區塊化、動態圖示的高階卡片結構"""
    p_pct = max(0, min(100, int((p["hp"] / p["max_hp"]) * 100)))
    
    def get_bar(pct, color): 
        return {
            "type": "box", "layout": "vertical", "backgroundColor": "#2A2A2A", "height": "10px", "cornerRadius": "5px", "margin": "md", 
            "contents": [{"type": "box", "layout": "vertical", "backgroundColor": color, "width": f"{pct}%", "height": "10px", "cornerRadius": "5px"}]
        }
                
    # 🌟 基礎容器排版
    contents = []
    
    # ⚔️ 1. 頂部動態戰報日誌區
    if "擊敗對手" in title:
        header_color = "#FFD700"
        header_title = "🏆 🟢 戰鬥大獲全勝 🟢 🏆"
    else:
        header_color = "#111111"
        header_title = "⚔️ 📊 戰場即時動態 📊 ⚔️"
        
    contents.append({"type": "text", "text": header_title, "weight": "bold", "size": "md", "color": header_color, "align": "center"})
    contents.append({"type": "separator", "margin": "lg"})
    
    # 📝 2. 戰報詳細日誌內容區
    log_text = title.replace("\n", " \n ")
    contents.append({
        "type": "text", "text": log_text, "size": "sm", "color": "#333333", "wrap": True, "margin": "lg", "lineSpacing": "xxl"
    })
    
    # 👾 3. 敵方怪物血條區
    if enemy: 
        e_pct = max(0, min(100, int((enemy["hp"] / enemy["max_hp"]) * 100)))
        contents.extend([
            {"type": "separator", "margin": "lg"}, 
            {"type": "text", "text": f"👾 {enemy['name']}", "weight": "bold", "size": "md", "margin": "md", "color": "#FF3B30"}, 
            {"type": "text", "text": f"血量狀態: {max(0, enemy['hp'])} / {enemy['max_hp']}", "size": "xs", "color": "#8E8E93", "margin": "xs"}, 
            get_bar(e_pct, "#FF3B30")
        ])
        
    # 👤 4. 勇者血條固定區
    contents.extend([
        {"type": "separator", "margin": "lg"}, 
        {"type": "text", "text": f"👤 勇者進度 (Lv.{p['level']})", "weight": "bold", "size": "md", "margin": "md", "color": "#007AFF"}, 
        {"type": "text", "text": f"血量狀態: {p['hp']} / {p['max_hp']}", "size": "xs", "color": "#8E8E93", "margin": "xs"}, 
        get_bar(p_pct, "#4CD964")
    ])
    
    return {"type": "bubble", "body": {"type": "box", "layout": "vertical", "contents": contents}}
