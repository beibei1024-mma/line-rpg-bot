# db_core.py - 資料庫連接池與主卡片生成器 (完整按鈕與黑市選單版)

import os
import json
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from linebot.v3.messaging import QuickReply, QuickReplyItem, MessageAction

_db_pool_url = os.environ.get('DATABASE_URL')
_connection_pool = None

def get_db_connection():
    global _connection_pool
    if _connection_pool is None:
        try:
            _connection_pool = pool.SimpleConnectionPool(1, 15, _db_pool_url)
        except Exception:
            return psycopg2.connect(_db_pool_url)
    try:
        return _connection_pool.getconn()
    except Exception:
        return psycopg2.connect(_db_pool_url)

def release_db_connection(conn):
    global _connection_pool
    if _connection_pool is not None:
        try:
            _connection_pool.putconn(conn)
            return
        except Exception:
            pass
    try:
        conn.close()
    except Exception:
        pass

def load_player(user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    player = None
    try:
        cur.execute("SELECT * FROM players WHERE user_id = %s", (user_id,))
        player = cur.fetchone()
        if not player:
            cur.execute(
                """INSERT INTO players (
                    user_id, name, hp, max_hp, level, exp, gold, weapon, helmet, armor, pants, shoes, 
                    necklace, ring1, ring2, bracelet, sub_hand, badge, cash_item1, cash_item2, cash_item3, 
                    enemy, strength, agility, intelligence, vitality, luck, sprit, job, attribute_points, 
                    last_sign_in, current_map, current_city
                ) VALUES (
                    %s, '新進勇者', 100, 100, 1, 0, 0, '赤手空拳', '冒險者頭巾', '冒險者皮甲', '冒險者布長褲', '冒險者草鞋', 
                    '無', '無', '無', '無', '無', '無', '無', '無', '無', 
                    NULL, 10, 10, 10, 10, 10, 10, '初心者', 0, 
                    'None', '主城', '新手村'
                )""",
                (user_id,)
            )
            conn.commit()
            cur.execute("SELECT * FROM players WHERE user_id = %s", (user_id,))
            player = cur.fetchone()
    finally:
        cur.close()
        release_db_connection(conn)

    if player:
        p_dict = dict(player)
        if p_dict.get('enemy') and isinstance(p_dict['enemy'], str):
            try:
                p_dict['enemy'] = json.loads(p_dict['enemy'])
            except Exception:
                p_dict['enemy'] = None
        if isinstance(p_dict.get('inventory'), str):
            try:
                p_dict['inventory'] = json.loads(p_dict['inventory'])
            except Exception:
                p_dict['inventory'] = {"items": {}, "materials": {}}
        elif not p_dict.get('inventory'):
            p_dict['inventory'] = {"items": {}, "materials": {}}
        return p_dict
    return None

def save_player(p):
    user_id = p['user_id']
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        enemy_str = json.dumps(p['enemy'], ensure_ascii=False) if p.get('enemy') else None
        inv_data = p.get('inventory', {"items": {}, "materials": {}})
        inv_str = json.dumps(inv_data, ensure_ascii=False) if isinstance(inv_data, dict) else str(inv_data)

        w_inv_data = p.get('weapon_inventory', "[]")
        w_inv_str = json.dumps(w_inv_data, ensure_ascii=False) if isinstance(w_inv_data, list) else str(w_inv_data)

        cur.execute(
            """UPDATE players SET 
                name=%s, hp=%s, max_hp=%s, mp=%s, level=%s, exp=%s, gold=%s, 
                weapon=%s, helmet=%s, armor=%s, pants=%s, shoes=%s, necklace=%s, 
                ring1=%s, ring2=%s, bracelet=%s, sub_hand=%s, badge=%s, 
                cash_item1=%s, cash_item2=%s, cash_item3=%s, enemy=%s, 
                strength=%s, agility=%s, intelligence=%s, vitality=%s, luck=%s, sprit=%s, 
                job=%s, attribute_points=%s, last_sign_in=%s, current_map=%s, current_city=%s,
                inventory=%s, weapon_inventory=%s, tower_layer=%s, world_boss_damage=%s, forge_weapon_bonus=%s
               WHERE user_id=%s""",
            (
                p.get('name', '新進勇者'), p['hp'], p['max_hp'], p.get('mp', 50), p['level'], p['exp'], p['gold'],
                p.get('weapon', '赤手空拳'), p.get('helmet', '冒險者頭巾'), p.get('armor', '冒險者皮甲'),
                p.get('pants', '冒險者布長褲'), p.get('shoes', '冒險者草鞋'), p.get('necklace', '無'),
                p.get('ring1', '無'), p.get('ring2', '無'), p.get('bracelet', '無'),
                p.get('sub_hand', '無'), p.get('badge', '無'), p.get('cash_item1', '無'),
                p.get('cash_item2', '無'), p.get('cash_item3', '無'), enemy_str,
                p.get('strength', 10), p.get('agility', 10), p.get('intelligence', 10),
                p.get('vitality', 10), p.get('luck', 10), p.get('sprit', 10),
                p.get('job', '初心者'), p.get('attribute_points', 0), p.get('last_sign_in', 'None'),
                p.get('current_map', '主城'), p.get('current_city', '新手村'),
                inv_str, w_inv_str, p.get('tower_layer', 1), p.get('world_boss_damage', 0), p.get('forge_weapon_bonus', 0),
                user_id
            )
        )
        conn.commit()
    finally:
        cur.close()
        release_db_connection(conn)

def make_battle_card(title, p, enemy):
    import jobs
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    job_mod = jobs.JOBS_DATA.get(current_job, jobs.JOBS_DATA["初心者"])
    p_name = p.get("name", "新進勇者")

    vit_val = int(p.get("vitality", 10) * job_mod["vit_mod"])
    calculated_max_hp = 100 + (vit_val * 5) + (level * 15)
    men_val = int(p.get("sprit", 10) * job_mod["men_mod"])
    calculated_max_mp = 50 + (men_val * 4) + (level * 5)

    current_mp = p.get("mp", calculated_max_mp)
    if current_mp is None:
        current_mp = calculated_max_mp

    p_hp = p["hp"]
    p_pct = 0 if p_hp <= 0 else (100 if p_hp >= calculated_max_hp else int((p_hp / calculated_max_hp) * 100))
    mp_pct = 0 if current_mp <= 0 else (100 if current_mp >= calculated_max_mp else int((current_mp / calculated_max_mp) * 100))

    def get_bar(pct, color):
        return {
            "type": "box", "layout": "vertical", "backgroundColor": "#2A2A2A", "height": "10px", "cornerRadius": "5px", "margin": "xs",
            "contents": [{"type": "box", "layout": "vertical", "backgroundColor": color, "width": str(pct) + "%", "height": "10px", "cornerRadius": "5px", "contents": []}]
        }

    contents = []
    if p_hp <= 0:
        header_title = "☠️ 勇者不幸陣亡 ☠️"
    elif p.get("current_map") == "主城":
        header_title = "🏙️ 皇家安全區：" + p.get('current_city', '新手村')
    else:
        header_title = "🌲 副本/野外危險區：" + p.get('current_map', '未知領域')

    contents.append({"type": "text", "text": header_title, "weight": "bold", "size": "md", "align": "center", "color": "#FFFFFF"})
    contents.append({"type": "separator", "margin": "md"})
    contents.append({"type": "text", "text": str(title), "size": "sm", "wrap": True, "margin": "md", "color": "#E0E0E0"})

    if enemy:
        e_hp = enemy["hp"]
        e_max = enemy["max_hp"]
        e_pct = 0 if e_hp <= 0 else (100 if e_hp >= e_max else int((e_hp / e_max) * 100))
        is_wb = enemy.get("is_world_boss", False)
        boss_title_color = "#FF1F1F" if is_wb else "#FF3B30"
        contents.extend([
            {"type": "separator", "margin": "md"},
            {"type": "text", "text": str(enemy['name']), "weight": "bold", "size": "md", "margin": "md", "color": boss_title_color},
            {"type": "text", "text": "血量殘餘: " + str(e_hp) + " / " + str(e_max), "size": "xs", "color": "#FF8383" if is_wb else "#8E8E93", "margin": "xs", "weight": "bold" if is_wb else "regular"},
            get_bar(e_pct, "#FF1F1F" if is_wb else "#FF3B30")
        ])

    contents.extend([
        {"type": "separator", "margin": "md"},
        {"type": "text", "text": "👤 勇者：【 " + p_name + " 】 (" + current_job + " Lv." + str(p['level']) + ")", "weight": "bold", "size": "md", "margin": "md", "color": "#007AFF"},
        {"type": "text", "text": "血量: " + str(p_hp) + "/" + str(calculated_max_hp) + "  |  魔力: " + str(current_mp) + "/" + str(calculated_max_mp), "size": "xs", "color": "#8E8E93", "margin": "xs"},
        get_bar(p_pct, "#4CD964"), get_bar(mp_pct, "#34AADC")
    ])

    flex_bubble = {"type": "bubble", "styles": {"body": {"backgroundColor": "#1C1C1E"}}, "body": {"type": "box", "layout": "vertical", "contents": contents}}

    quick_items = []
    if p_hp <= 0:
        quick_items.append(QuickReplyItem(action=MessageAction(label="😇 祈求復活", text="復活")))
    elif enemy:
        quick_items.append(QuickReplyItem(action=MessageAction(label="⚔️ 普通攻擊", text="攻擊")))
        quick_items.append(QuickReplyItem(action=MessageAction(label="🛡️ 技能防禦", text="使用技能防禦")))
        for s_name, s_info in job_mod.get("skills", {}).items():
            if s_info.get("type") == "active" and s_name != "普通攻擊":
                quick_items.append(QuickReplyItem(action=MessageAction(label="🔮 " + s_name, text="使用技能 " + s_name)))
        quick_items.append(QuickReplyItem(action=MessageAction(label="🏃 轉身逃跑", text="逃跑")))
    elif p.get("current_map") == "主城":
        quick_items.extend([
            QuickReplyItem(action=MessageAction(label="📆 簽到", text="簽到")),
            QuickReplyItem(action=MessageAction(label="⚒️ 工坊", text="工坊")),
            QuickReplyItem(action=MessageAction(label="🏪 商店", text="冒險商店")),
            QuickReplyItem(action=MessageAction(label="🖤 黑市", text="黑市")),
            QuickReplyItem(action=MessageAction(label="🗼 爬塔", text="挑戰爬塔")),
            QuickReplyItem(action=MessageAction(label="🌋 世界Boss", text="挑戰世界Boss")),
            QuickReplyItem(action=MessageAction(label="🛡️ 裝備", text="我的裝備")),
            QuickReplyItem(action=MessageAction(label="🎒 背包", text="我的背包")),
            QuickReplyItem(action=MessageAction(label="🚪 出城", text="世界地圖"))
        ])
    else:
        quick_items.extend([
            QuickReplyItem(action=MessageAction(label="🔍 尋找怪物", text="尋怪")),
            QuickReplyItem(action=MessageAction(label="👤 狀態", text="我的狀態")),
            QuickReplyItem(action=MessageAction(label="🎒 背包", text="我的背包")),
            QuickReplyItem(action=MessageAction(label="🦅 回城", text="回城"))
        ])

    qr_dict = QuickReply(items=quick_items[:13]).to_dict()
    return {"flex": flex_bubble, "quick_reply": qr_dict}
# === END OF FILE ===
