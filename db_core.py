import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from linebot.v3.messaging import QuickReply, QuickReplyItem, MessageAction

# ⚡ 優化：利用記憶體快取與全域連線池概念降低連線開銷
MEMORY_PLAYERS = {}
_db_pool_url = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(_db_pool_url)

def load_player(user_id):
    # O(1) 記憶體優先讀取
    if user_id in MEMORY_PLAYERS:
        return MEMORY_PLAYERS[user_id]
        
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT * FROM players WHERE user_id = %s", (user_id,))
        player = cur.fetchone()
        
        # 当找不到玩家時，提早防錯插入並 commit，簡化邏輯流程
        if not player:
            cur.execute(
                "INSERT INTO players (user_id, hp, max_hp, level, exp, gold, weapon, enemy, strength, agility, intelligence, vitality, luck, sprit, job, attribute_points, last_sign_in, current_map, current_city) VALUES (%s, 100, 100, 1, 0, 0, '赤手空拳', NULL, 10, 10, 10, 10, 10, 10, '初心者', 0, 'None', '主城', '新手村')",
                (user_id,)
            )
            conn.commit()
            cur.execute("SELECT * FROM players WHERE user_id = %s", (user_id,))
            player = cur.fetchone()
    finally:
        cur.close()
        conn.close()
        
    if player:
        if player['enemy']: 
            player['enemy'] = json.loads(player['enemy'])
        MEMORY_PLAYERS[user_id] = dict(player)
        return MEMORY_PLAYERS[user_id]
    return None

def save_player(p):
    user_id = p['user_id']
    MEMORY_PLAYERS[user_id] = p
    
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        enemy_str = json.dumps(p['enemy']) if p['enemy'] else None
        cur.execute(
            "UPDATE players SET hp=%s, max_hp=%s, level=%s, exp=%s, gold=%s, weapon=%s, enemy=%s, strength=%s, agility=%s, intelligence=%s, vitality=%s, luck=%s, sprit=%s, job=%s, attribute_points=%s, last_sign_in=%s, current_map=%s, current_city=%s WHERE user_id=%s",
            (p['hp'], p['max_hp'], p['level'], p['exp'], p['gold'], p['weapon'], enemy_str, 
             p.get('strength', 10), p.get('agility', 10), p.get('intelligence', 10), p.get('vitality', 10), p.get('luck', 10), p.get('sprit', 10), p.get('job', '初心者'), p.get('attribute_points', 0), p.get('last_sign_in', 'None'), p.get('current_map', '主城'), p.get('current_city', '新手村'), user_id)
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()

def make_battle_card(title, p, enemy):
    """【皇家地圖分流完全體】依位置動態切換小圖標，戰鬥中常駐解鎖技能防禦熱鍵"""
    import jobs
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    job_mod = jobs.JOBS_DATA.get(current_job, jobs.JOBS_DATA["初心者"])
    
    vit_val = int(p.get("vitality", 10) * job_mod["vit_mod"])
    calculated_max_hp = 100 + (vit_val * 5) + (level * 15)
    men_val = int(p.get("sprit", 10) * job_mod["men_mod"])
    calculated_max_mp = 50 + (men_val * 4) + (level * 5)
    
    current_mp = p.get("mp", calculated_max_mp)
    if current_mp is None: 
        current_mp = calculated_max_mp
    
    # 進度條百分比計算改用更快速的常數邊界約束
    p_hp = p["hp"]
    p_pct = 0 if p_hp <= 0 else (100 if p_hp >= calculated_max_hp else int((p_hp / calculated_max_hp) * 100))
    mp_pct = 0 if current_mp <= 0 else (100 if current_mp >= calculated_max_mp else int((current_mp / calculated_max_mp) * 100))
    
    def get_bar(pct, color): 
        return {
            "type": "box", "layout": "vertical", "backgroundColor": "#2A2A2A", "height": "10px", "cornerRadius": "5px", "margin": "xs", 
            "contents": [{"type": "box", "layout": "vertical", "backgroundColor": color, "width": f"{pct}%", "height": "10px", "cornerRadius": "5px", "contents": []}]
        }
                
    contents = []
    if p_hp <= 0: 
        header_title = "☠️ 勇者不幸陣亡 ☠️"
    elif p.get("current_map") == "主城":
        header_title = f"🏙️ 皇家安全區：{p.get('current_city', '新手村')}"
    else:
        header_title = f"🌲 野外危險區：{p.get('current_map', '未知領域')}"
        
    contents.append({"type": "text", "text": header_title, "weight": "bold", "size": "md", "align": "center", "color": "#FFFFFF"})
    contents.append({"type": "separator", "margin": "md"})
    contents.append({"type": "text", "text": str(title), "size": "sm", "wrap": True, "margin": "md", "color": "#E0E0E0"})
    
    # 👾 怪物狀態渲染區（已加入數值顯示優化）
    if enemy: 
        e_hp = enemy["hp"]
        e_max = enemy["max_hp"]
        e_pct = 0 if e_hp <= 0 else (100 if e_hp >= e_max else int((e_hp / e_max) * 100))
        
        # ⚡ 核心優化點：比照角色面板，在怪物的血條上方安插精確的血量數值欄位
        contents.extend([
            {"type": "separator", "margin": "md"}, 
            {"type": "text", "text": f"👾 {enemy['name']}", "weight": "bold", "size": "md", "margin": "md", "color": "#FF3B30"}, 
            {"type": "text", "text": f"血量: {e_hp}/{e_max}", "size": "xs", "color": "#8E8E93", "margin": "xs"}, # 👈 精準加入這行
            get_bar(e_pct, "#FF3B30")
        ])
        
    contents.extend([
        {"type": "separator", "margin": "md"}, 
        {"type": "text", "text": f"👤 {current_job} (Lv.{p['level']})", "weight": "bold", "size": "md", "margin": "md", "color": "#007AFF"}, 
        {"type": "text", "text": f"血量: {p_hp}/{calculated_max_hp}  |  魔力: {current_mp}/{calculated_max_mp}", "size": "xs", "color": "#8E8E93", "margin": "xs"},
        get_bar(p_pct, "#4CD964"), get_bar(mp_pct, "#34AADC")
    ])
    
    flex_bubble = {"type": "bubble", "styles": {"body": {"backgroundColor": "#1C1C1E"}}, "body": {"type": "box", "layout": "vertical", "contents": contents}}
    
    # 🕹️ Quick Reply 記憶體最佳化分配
    quick_items = []
    
    if p_hp <= 0:
        quick_items.append(QuickReplyItem(action=MessageAction(label="😇 祈求復活", text="復活")))
    elif enemy:
        quick_items.append(QuickReplyItem(action=MessageAction(label="⚔️ 普通攻擊", text="攻擊")))
        quick_items.append(QuickReplyItem(action=MessageAction(label="🛡️ 技能防禦", text="使用技能防禦")))
        for s_name, s_info in job_mod.get("skills", {}).items():
            if s_info.get("type") == "active" and s_name != "普通攻擊":
                quick_items.append(QuickReplyItem(action=MessageAction(label=f"🔮 {s_name}", text=f"使用技能 {s_name}")))
        quick_items.append(QuickReplyItem(action=MessageAction(label="🏃 轉身逃跑", text="逃跑")))
        
    elif p.get("current_map") == "主城":
        quick_items.extend([
            QuickReplyItem(action=MessageAction(label="📆 每日簽到", text="簽到")),
            QuickReplyItem(action=MessageAction(label="⚒️ 遠古工坊NPC", text="工坊")),
            QuickReplyItem(action=MessageAction(label="🗼 試煉之塔", text="挑戰爬塔")),
            QuickReplyItem(action=MessageAction(label="🌋 世界 Boss", text="挑戰世界Boss")),
            QuickReplyItem(action=MessageAction(label="🏪 補給商店", text="冒險商店")),
            QuickReplyItem(action=MessageAction(label="🛡️ 查看裝備", text="我的裝備")),
            QuickReplyItem(action=MessageAction(label="🎒 打開背包", text="我的背包")),
            QuickReplyItem(action=MessageAction(label="🚪 出城冒險", text="世界地圖"))
        ])
    else:
        quick_items.extend([
            QuickReplyItem(action=MessageAction(label="🔍 尋找怪物", text="尋怪")),
            QuickReplyItem(action=MessageAction(label="👤 我的狀態", text="我的狀態")),
            QuickReplyItem(action=MessageAction(label="🎒 打開背包", text="我的背包")),
            QuickReplyItem(action=MessageAction(label="🦅 飛回城鎮", text="回城"))
        ])

    return {"flex": flex_bubble, "quick_reply": QuickReply(items=quick_items)}
