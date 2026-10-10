import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor

# 🚀 本地快取記憶體暫存區：普通互毆扣血只在本地計算，打死怪才同步回雲端，大幅提升回傳速度
MEMORY_PLAYERS = {}

def get_db_connection():
    # 讀取你在 Render 後台設定的環境變數，永久固定，安全不外洩！
    db_url = os.environ.get('DATABASE_URL')
    return psycopg2.connect(db_url)

def load_player(user_id):
    # ⚡ 記憶體優先讀取機制（0 秒延遲）
    if user_id in MEMORY_PLAYERS:
        return MEMORY_PLAYERS[user_id]
        
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM players WHERE user_id = %s", (user_id,))
    player = cur.fetchone()
    
    if not player:
        # 新增初始玩家防呆機制
        cur.execute(
            "INSERT INTO players (user_id, hp, max_hp, level, exp, gold, weapon, enemy) VALUES (%s, 100, 100, 1, 0, 0, '赤手空拳', NULL)",
            (user_id,)
        )
        conn.commit()
        cur.execute("SELECT * FROM players WHERE user_id = %s", (user_id,))
        player = cur.fetchone()
        
    cur.close()
    conn.close()
    
    if player and player['enemy']: 
        player['enemy'] = json.loads(player['enemy'])
        
    # 同步寫入暫存
    MEMORY_PLAYERS[user_id] = dict(player)
    return MEMORY_PLAYERS[user_id]

def save_player(p):
    # 同步刷新本地暫存
    MEMORY_PLAYERS[p['user_id']] = p
    
    # 強制寫入 Supabase 雲端資料庫
    conn = get_db_connection()
    cur = conn.cursor()
    enemy_str = json.dumps(p['enemy']) if p['enemy'] else None
    cur.execute(
        "UPDATE players SET hp=%s, max_hp=%s, level=%s, exp=%s, gold=%s, weapon=%s, enemy=%s WHERE user_id=%s",
        (p['hp'], p['max_hp'], p['level'], p['exp'], p['gold'], p['weapon'], enemy_str, p['user_id'])
    )
    conn.commit()
    cur.close()
    conn.close()

def make_battle_card(title, p, enemy):
    # 繪製彩色血條卡片的標準基礎模組
    p_pct = max(0, min(100, int((p["hp"] / p["max_hp"]) * 100)))
    e_pct = max(0, min(100, int((enemy["hp"] / enemy["max_hp"]) * 100))) if enemy else 0
    
    def get_bar(pct, color): 
        return {"type": "box", "layout": "vertical", "backgroundColor": "#E0E0E0", "height": "8px", "cornerRadius": "4px", "margin": "sm", 
                "contents": [{"type": "box", "layout": "vertical", "backgroundColor": color, "width": f"{pct}%", "height": "8px", "cornerRadius": "4px"}]}
                
    contents = [{"type": "text", "text": title, "weight": "bold", "size": "md", "color": "#111111", "wrap": True}]
    
    if enemy: 
        contents.extend([
            {"type": "separator", "margin": "md"}, 
            {"type": "text", "text": f"👾 {enemy['name']}", "weight": "bold", "size": "md", "margin": "md", "color": "#FF3B30"}, 
            {"type": "text", "text": f"HP: {max(0, enemy['hp'])} / {enemy['max_hp']}", "size": "xs", "color": "#666666"}, 
            get_bar(e_pct, "#FF3B30")
        ])
        
    contents.extend([
        {"type": "separator", "margin": "md"}, 
        {"type": "text", "text": "👤 勇者狀態", "weight": "bold", "size": "md", "margin": "md", "color": "#007AFF"}, 
        {"type": "text", "text": f"HP: {p['hp']} / {p['max_hp']}", "size": "xs", "color": "#666666"}, 
        get_bar(p_pct, "#4CD964")
    ])
    return {"type": "bubble", "body": {"type": "box", "layout": "vertical", "contents": contents}}
