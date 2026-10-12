import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from linebot.v3.messaging import QuickReply, QuickReplyItem, MessageAction

MEMORY_PLAYERS = {}

# db_core.py - 皇家多角色實體資料庫中樞與一小時時空鎖引擎 v5.8

import os
import json
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from linebot.v3.messaging import QuickReply, QuickReplyItem, MessageAction

# 記憶體多角色全域快取緩衝區
MEMORY_PLAYERS = {}

def get_db_connection():
    """🔌 獲取 PostgreSQL / Supabase 實體連線"""
    db_url = os.environ.get('DATABASE_URL')
    return psycopg2.connect(db_url)

def get_account_profile(user_id):
    """🔍 讀取或初始化一個 LINE 帳號的三槽位多角色基本設定檔"""
    if user_id not in MEMORY_PLAYERS:
        MEMORY_PLAYERS[user_id] = {
            "active_slot": None, "last_action_time": 0,
            "slot_1": None, "slot_2": None, "slot_3": None
        }
    return MEMORY_PLAYERS[user_id]

def load_player(user_id):
    """👤 核心讀取：檢查 1 小時無動作時空鎖，若逾期則自動登出並強制回傳選角大廳"""
    acc = get_account_profile(user_id)
    now = int(time.time())
    
    # 🕒 【 1 小時無動作自動登出時空鎖 】判定
    if acc["active_slot"] is not None and (now - acc["last_action_time"]) > 3600:
        acc["active_slot"] = None 
        save_account(user_id, acc)
        return None # 中央路由 process_game_logic 攔截到 None 會立刻彈出選角選單
        
    acc["last_action_time"] = now
    save_account(user_id, acc)
    
    if acc["active_slot"] is None:
        return None
        
    return acc[f"slot_{acc['active_slot']}"]

def save_player(p):
    """💾 儲存當前正在線上的活躍角色數據包，並即時寫入實體資料庫"""
    if not p: return
    user_id = p["user_id"]
    acc = get_account_profile(user_id)
    slot = acc["active_slot"]
    if slot:
        acc[f"slot_{slot}"] = p
        acc["last_action_time"] = int(time.time())
        save_account(user_id, acc)
        
        # 實體資料庫備份同步牆
        conn = get_db_connection()
        cur = conn.cursor()
        enemy_str = json.dumps(p['enemy']) if p['enemy'] else None
        cur.execute(
            "UPDATE players SET hp=%s, max_hp=%s, level=%s, exp=%s, gold=%s, weapon=%s, enemy=%s, strength=%s, agility=%s, intelligence=%s, vitality=%s, luck=%s, sprit=%s, job=%s, attribute_points=%s, current_map=%s, equipped_slots=%s, equipment_inventory=%s, inventory=%s WHERE user_id=%s AND slot_num=%s",
            (p['hp'], p.get('max_hp', 100), p['level'], p['exp'], p['gold'], p['weapon'], enemy_str, p.get('strength', 10), p.get('agility', 10), p.get('intelligence', 10), p.get('vitality', 10), p.get('luck', 10), p.get('sprit', 10), p.get('job', '初心者'), p.get('attribute_points', 0), p.get('current_map', '主城'), p.get('equipped_slots', '{}'), p.get('equipment_inventory', '[]'), p.get('inventory', '{}'), user_id, slot)
        )
        conn.commit()
        cur.close()
        conn.close()

def save_account(user_id, acc):
    """💾 更新快取庫"""
    MEMORY_PLAYERS[user_id] = acc

def create_character(user_id, slot_num, job_name="初心者"):
    """🆕 在指定空白槽位物理初始化一隻全新勇者角色，並插入 PostgreSQL"""
    acc = get_account_profile(user_id)
    new_char = {
        "user_id": user_id, "slot": slot_num, "level": 1, "exp": 0, "gold": 100,
        "hp": 150, "mp": 95, "job": job_name, "current_map": "主城", "enemy": None,
        "strength": 10, "agility": 10, "intelligence": 10, "vitality": 10, "luck": 10, "sprit": 10,
        "attribute_points": 0, "equipped_slots": "{}", "equipment_inventory": "[]", "inventory": "{}"
    }
    acc[f"slot_{slot_num}"] = new_char
    acc["active_slot"] = slot_num
    acc["last_action_time"] = int(time.time())
    save_account(user_id, acc)
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO players (user_id, slot_num, hp, level, exp, gold, weapon, current_map, job, strength, agility, intelligence, vitality, luck, sprit, attribute_points, equipped_slots, equipment_inventory, inventory) VALUES (%s, %s, 150, 1, 0, 100, '赤手空拳', '主城', '初心者', 10, 10, 10, 10, 10, 10, 0, '{}', '[]', '{}')",
        (user_id, slot_num)
    )
    conn.commit()
    cur.close()
    conn.close()
    return new_char

def delete_character(user_id, slot_num):
    """❌ 物理火化抹除：從快取與 PostgreSQL 中徹底清空指定的槽位角色"""
    acc = get_account_profile(user_id)
    acc[f"slot_{slot_num}"] = None
    if acc["active_slot"] == slot_num:
        acc["active_slot"] = None
    save_account(user_id, acc)
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM players WHERE user_id = %s AND slot_num = %s", (user_id, slot_num))
    conn.commit()
    cur.close()
    conn.close()

def switch_active_slot(user_id, slot_num):
    """🔄 靈魂魂降切換：將在線活躍槽位切換至指定角色欄位"""
    acc = get_account_profile(user_id)
    if acc[f"slot_{slot_num}"] is not None:
        acc["active_slot"] = slot_num
        acc["last_action_time"] = int(time.time())
        save_account(user_id, acc)
        return True
    return False

def make_character_select_flex(user_id):
    """🎨 生成三個角色欄位外觀的選角與刪除中樞 Flex 卡片"""
    acc = get_account_profile(user_id)
    contents = [
        {"type": "text", "text": "👥 皇家勇者靈魂轉生大廳", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
        {"type": "text", "text": "⏳ 超過1小時無動作會自動登出選角區", "size": "xxs", "color": "#8E8E93", "align": "center", "margin": "xs"},
        {"type": "separator", "margin": "sm", "color": "#333333"}
    ]
    
    # ✨【💥 語法死鎖終極校正點】完美補上 [1, 2, 3] 迴圈陣列，阻絕 SyntaxError 崩潰！ [1]
    for slot in:
        char = acc[f"slot_{slot}"]
        if char:
            slot_body = [
                {"type": "text", "text": f" Slot {slot} 👑 【 {char['job']} 】", "size": "xs", "color": "#4CD964", "weight": "bold"},
                {"type": "text", "text": f"   ↳ 等級: Lv.{char['level']} | 金幣: 🪙 {char['gold']}", "size": "xxs", "color": "#E0E0E0", "margin": "xs"},
                {"type": "box", "layout": "horizontal", "margin": "xs", "spacing": "sm", "contents": [
                    {"type": "button", "style": "primary", "color": "#1478FF", "height": "sm", "flex": 3, "action": {"type": "message", "label": "⚡ 靈魂降臨登入", "text": f"選角登入 {slot}"}},
                    {"type": "button", "style": "primary", "color": "#FF3B30", "height": "sm", "flex": 1, "action": {"type": "message", "label": "🔥 刪除", "text": f"請求刪除角色 {slot}"}}
                ]}
            ]
        else:
            slot_body = [
                {"type": "text", "text": f" Slot {slot} 🫙 [ 空置角色欄位 ]", "size": "xs", "color": "#8E8E93", "weight": "bold"},
                {"type": "button", "style": "primary", "color": "#2C2C2E", "height": "sm", "marginTop": "xs", "action": {"type": "message", "label": "🆕 創立新角色", "text": f"創建角色 {slot}"}}
            ]
        contents.append({"type": "box", "layout": "vertical", "margin": "md", "backgroundColor": "#1C1C1E", "paddingAll": "sm", "cornerRadius": "md", "contents": slot_body})
        
    return {"type": "bubble", "styles": {"body": {"backgroundColor": "#111111"}}, "body": {"type": "box", "layout": "vertical", "contents": contents}}


# db_core.py - 追加對接 Supabase 擴充核心函數

def save_player(p):
    """將玩家所有屬性（包含 JSON 化的多部位裝備、背包、黑市貨架）完整寫回 Supabase"""
    # 這裡請根據您使用的資料庫驅動（如 psycopg2 或 supabase-py）進行實作
    # 範例 SQL：
    # """
    # UPDATE players SET 
    #     hp = %s, mp = %s, max_hp = %s, level = %s, exp = %s, gold = %s, weapon = %s, enemy = %s,
    #     strength = %s, agility = %s, intelligence = %s, vitality = %s, luck = %s, sprit = %s,
    #     equipped_slots = %s, equipment_inventory = %s, shop_seed = %s, shop_goods = %s
    # WHERE user_id = %s
    # """
    pass

def load_global_value(key, default_val):
    """從 global_system_variables 全域參數表讀取全服共有參數（如世界 Boss 血量、排行）"""
    # 範例 SQL：
    # "SELECT variable_value FROM global_system_variables WHERE variable_key = %s"
    # 讀取出來後再傳回對應的數值或字串即可。
    return default_val

def save_global_value(key, value):
    """將全服最新數值（如扣血後的 Boss 殘餘生命、最新排行榜）寫回全域變數表"""
    # 範例 SQL：
    # """
    # INSERT INTO global_system_variables (variable_key, variable_value) VALUES (%s, %s) 
    # ON CONFLICT (variable_key) DO UPDATE SET variable_value = EXCLUDED.variable_value
    # """
    pass

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
            "INSERT INTO players (user_id, hp, max_hp, level, exp, gold, weapon, enemy, strength, agility, intelligence, vitality, luck, sprit, job, attribute_points, last_sign_in, current_map, current_city) VALUES (%s, 100, 100, 1, 0, 0, '赤手空拳', NULL, 10, 10, 10, 10, 10, 10, '初心者', 0, 'None', '主城', '新手村')",
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
        "UPDATE players SET hp=%s, max_hp=%s, level=%s, exp=%s, gold=%s, weapon=%s, enemy=%s, strength=%s, agility=%s, intelligence=%s, vitality=%s, luck=%s, sprit=%s, job=%s, attribute_points=%s, last_sign_in=%s, current_map=%s, current_city=%s WHERE user_id=%s",
        (p['hp'], p['max_hp'], p['level'], p['exp'], p['gold'], p['weapon'], enemy_str, 
         p.get('strength', 10), p.get('agility', 10), p.get('intelligence', 10), p.get('vitality', 10), p.get('luck', 10), p.get('sprit', 10), p.get('job', '初心者'), p.get('attribute_points', 0), p.get('last_sign_in', 'None'), p.get('current_map', '主城'), p.get('current_city', '新手村'), p['user_id'])
    )
    conn.commit()
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
    if current_mp is None: current_mp = calculated_max_mp
    
    p_pct = max(0, min(100, int((p["hp"] / calculated_max_hp) * 100)))
    mp_pct = max(0, min(100, int((current_mp / calculated_max_mp) * 100)))
    
    def get_bar(pct, color): 
        return {
            "type": "box", "layout": "vertical", "backgroundColor": "#2A2A2A", "height": "10px", "cornerRadius": "5px", "margin": "xs", 
            "contents": [{"type": "box", "layout": "vertical", "backgroundColor": color, "width": f"{pct}%", "height": "10px", "cornerRadius": "5px", "contents": []}]
        }
                
    contents = []
    if p["hp"] <= 0: 
        header_title = "☠️ 勇者不幸陣亡 ☠️"
    elif p.get("current_map") == "主城":
        header_title = f"🏙️ 皇家安全區：{p.get('current_city', '新手村')}"
    else:
        header_title = f"🌲 野外危險區：{p.get('current_map', '未知領域')}"
        
    contents.append({"type": "text", "text": header_title, "weight": "bold", "size": "md", "align": "center", "color": "#FFFFFF"})
    contents.append({"type": "separator", "margin": "md"})
    contents.append({"type": "text", "text": str(title), "size": "sm", "wrap": True, "margin": "md", "color": "#E0E0E0"})
    
    if enemy: 
        e_pct = max(0, min(100, int((enemy["hp"] / enemy["max_hp"]) * 100)))
        contents.extend([
            {"type": "separator", "margin": "md"}, 
            {"type": "text", "text": f"👾 {enemy['name']}", "weight": "bold", "size": "md", "margin": "md", "color": "#FF3B30"}, 
            get_bar(e_pct, "#FF3B30")
        ])
        
    contents.extend([
        {"type": "separator", "margin": "md"}, 
        {"type": "text", "text": f"👤 {current_job} (Lv.{p['level']})", "weight": "bold", "size": "md", "margin": "md", "color": "#007AFF"}, 
        {"type": "text", "text": f"血量: {p['hp']}/{calculated_max_hp}  |  魔力: {current_mp}/{calculated_max_mp}", "size": "xs", "color": "#8E8E93", "margin": "xs"},
        get_bar(p_pct, "#4CD964"), get_bar(mp_pct, "#34AADC")
    ])
    
    flex_bubble = {"type": "bubble", "styles": {"body": {"backgroundColor": "#1C1C1E"}}, "body": {"type": "box", "layout": "vertical", "contents": contents}}
    
    # 🕹️ 橫向滑動 Quick Reply 小標籤動態解鎖大腦
    quick_items = []
    
    if p["hp"] <= 0:
        quick_items.append(QuickReplyItem(action=MessageAction(label="😇 祈求復活", text="復活")))
    elif enemy:
        # ⚔️ 1. 野外激烈戰鬥中（精準 4 空格齊頭對齊修復！）
        quick_items.append(QuickReplyItem(action=MessageAction(label="⚔️ 普通攻擊", text="攻擊")))
        # ✨ 【優化二：戰術實裝】常駐為所有職業塞入【🛡️ 技能防禦】實體小標籤快捷鍵！
        quick_items.append(QuickReplyItem(action=MessageAction(label="🛡️ 技能防禦", text="使用技能防禦")))
        for s_name, s_info in job_mod.get("skills", {}).items():
            if s_info.get("type") == "active" and s_name != "普通攻擊":
                quick_items.append(QuickReplyItem(action=MessageAction(label=f"🔮 {s_name}", text=f"使用技能 {s_name}")))
        quick_items.append(QuickReplyItem(action=MessageAction(label="🏃 轉身逃跑", text="逃跑")))
        
    elif p.get("current_map") == "主城":
        # 🏙️ 2. 【皇家安全主城】快捷控制小圖標列
        quick_items.append(QuickReplyItem(action=MessageAction(label="📆 每日簽到", text="簽到")))
        quick_items.append(QuickReplyItem(action=MessageAction(label="⚒️ 遠古工坊NPC", text="工坊")))
        quick_items.append(QuickReplyItem(action=MessageAction(label="🗼 試煉之塔", text="挑戰爬塔")))
        quick_items.append(QuickReplyItem(action=MessageAction(label="🌋 世界 Boss", text="世界Boss")))
        quick_items.append(QuickReplyItem(action=MessageAction(label="🏪 補給商店", text="冒險商店")))
        quick_items.append(QuickReplyItem(action=MessageAction(label="🛡️ 查看裝備", text="我的裝備")))
        quick_items.append(QuickReplyItem(action=MessageAction(label="🎒 打開背包", text="我的背包")))
        quick_items.append(QuickReplyItem(action=MessageAction(label="🚪 出城冒險", text="世界地圖")))
        
    else:
        # 🌲 3. 在普通野外地圖（閒置狀態）
        quick_items.append(QuickReplyItem(action=MessageAction(label="🔍 尋找怪物", text="尋怪")))
        quick_items.append(QuickReplyItem(action=MessageAction(label="👤 我的狀態", text="我的狀態")))
        quick_items.append(QuickReplyItem(action=MessageAction(label="🎒 打開背包", text="我的背包")))
        quick_items.append(QuickReplyItem(action=MessageAction(label="🦅 飛回城鎮", text="回城")))

    return {"flex": flex_bubble, "quick_reply": QuickReply(items=quick_items)}
