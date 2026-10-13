import random
import json
from linebot.v3.messaging import QuickReply, QuickReplyItem, MessageAction
import db_core
import weapons

WORLD_BOSS_TOTAL_HP = 10000000  
WORLD_BOSS_NAME = "🌋 【滅世魔神・毀滅終焉泰坦】"

def get_challenge_menu(p):
    """🤖 生成挑戰入口圖卡面板 (附帶專屬 Quick Reply 導引)"""
    current_layer = p.get("tower_layer", 1)
    if current_layer is None: 
        current_layer = 1
        
    boss_dmg = p.get('world_boss_damage', 0)
    
    flex_menu = {
        "type": "bubble",
        "styles": {"body": {"backgroundColor": "#1A1A1A"}, "footer": {"backgroundColor": "#111111"}},
        "body": {
            "type": "box", "layout": "vertical", "spacing": "md",
            "contents": [
                {"type": "text", "text": "🎯 勇者至高皇家試煉場", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
                {"type": "separator", "color": "#333333"},
                {"type": "box", "layout": "vertical", "spacing": "xs", "contents": [
                    {"type": "text", "text": f"🗼 無盡試煉之塔：當前第 【 {current_layer} 】 層", "size": "sm", "color": "#AF52DE", "weight": "bold"},
                    {"type": "text", "text": "   ↳ 通關可獲得翻倍金幣、珍稀圖紙與永恆榮譽。", "size": "xs", "color": "#8E8E93"},
                    {"type": "text", "text": f"🌋 世界 Boss 討伐戰：{WORLD_BOSS_NAME}", "size": "sm", "color": "#FF3B30", "weight": "bold", "marginTop": "sm"},
                    {"type": "text", "text": f"   ↳ 全服累積傷害！個人已貢獻：⚔️ {boss_dmg} 點", "size": "xs", "color": "#8E8E93"}
                ]}
            ]
        },
        "footer": {
            "type": "box", "layout": "vertical", "spacing": "sm",
            "contents": [
                {"type": "button", "style": "primary", "color": "#AF52DE", "height": "sm", "action": {"type": "message", "label": "🗼 挑戰下一層試煉塔", "text": "挑戰爬塔"}},
                {"type": "button", "style": "primary", "color": "#FF3B30", "height": "sm", "action": {"type": "message", "label": "🌋 討伐全服世界Boss", "text": "挑戰世界Boss"}}
            ]
        }
    }
    
    quick_items = [
        QuickReplyItem(action=MessageAction(label="🗼 挑戰爬塔", text="挑戰爬塔")),
        QuickReplyItem(action=MessageAction(label="🌋 世界Boss", text="挑戰世界Boss")),
        QuickReplyItem(action=MessageAction(label="🏃 返回戰場", text="尋怪"))
    ]
    return {"flex": flex_menu, "quick_reply": QuickReply(items=quick_items)}

def execute_tower_climb(p):
    """🗼 爬塔戰鬥計算核心"""
    layer = p.get("tower_layer", 1)
    if layer is None: 
        layer = 1
    
    monster_hp = 100 + (layer * 120)
    monster_atk = 15 + (layer * 18)
    monster_name = f"🔱 試煉塔第 {layer} 層・【守護石雕將軍】"
    
    current_weapon = p.get("weapon", "赤手空拳")
    w_bonus = weapons.SHOP_WEAPONS[current_weapon]["atk_bonus"] if current_weapon in weapons.SHOP_WEAPONS else 0
    p_atk = 15 + (p.get("strength", 10) * 2) + w_bonus
    
    if p["hp"] <= 0:
        card = db_core.make_battle_card("❌ 勇者！你目前處於陣亡狀態，無法進入神聖試煉塔，請先復活！", p, None)
        return {"text": "❌ 你已陣亡！", "is_flex": True, "flex": card["flex"], "quick_reply": card["quick_reply"]}
        
    log = f"座落於虛空的時空法陣開啟！你獨自踏入試煉之塔第 {layer} 層！\n遭遇守關巨獸 ── {monster_name}\n─────────────────\n"
    
    turns = 0
    m_current_hp = monster_hp
    p_current_hp = p["hp"]
    p_defense_bonus = p.get("vitality", 10) // 2
    
    while m_current_hp > 0 and p_current_hp > 0 and turns < 5:
        turns += 1
        dmg = int(p_atk * random.uniform(0.9, 1.3))
        m_current_hp -= dmg
        log += f"💥 第 {turns} 回合：你轟出 {dmg} 點重傷！\n"
        if m_current_hp <= 0: 
            break
        
        m_dmg = max(1, monster_atk - p_defense_bonus)
        p_current_hp -= m_dmg
        log += f"🩹 守衛反擊你 {m_dmg} 點生命！\n"
        
    quick_items = [
        QuickReplyItem(action=MessageAction(label="🗡️ 繼續挑戰下一層", text="挑戰爬塔")),
        QuickReplyItem(action=MessageAction(label="📊 再看一次試煉場", text="挑戰")),
        QuickReplyItem(action=MessageAction(label="🏃 返回世界尋怪", text="尋怪"))
    ]
    qr_object = QuickReply(items=quick_items)
        
    if m_current_hp <= 0:
        reward_gold = 500 + (layer * 150)
        p["tower_layer"] = layer + 1
        p["gold"] += reward_gold
        p["hp"] = p_current_hp 
        db_core.save_player(p)
        
        reply_text = f"🏆 【試煉塔第 {layer} 層 挑戰大捷】 🏆\n─────────────────\n{log}\n🎉 奇蹟戰勝！你成功突破了此層防線！\n🪙 獲得層數通關獎勵：金幣 +{reward_gold}！\n🗼 試煉晉升：下一層解鎖第 {layer + 1} 層！"
        return {"text": reply_text, "is_flex": True, "flex": db_core.make_battle_card(reply_text, p, None)["flex"], "quick_reply": qr_object}
    else:
        p["hp"] = max(1, p_current_hp)
        db_core.save_player(p)
        
        reply_text = f"☠️ 【試煉塔第 {layer} 層 挑戰兵敗】 ☠️\n─────────────────\n{log}\n❌ 守關者防禦太過堅固，你受傷過重狼狽撤退了..."
        return {"text": reply_text, "is_flex": True, "flex": db_core.make_battle_card(reply_text, p, None)["flex"], "quick_reply": qr_object}

def execute_world_boss_raid(p):
    """世界 Boss 戰功結算，動態統計全服總傷害生成血條，並拉取前5名戰功排行榜"""
    if p["hp"] <= 0:
        card = db_core.make_battle_card("❌ 你已陣亡，無法向世界魔神發起衝鋒！", p, None)
        return {"text": "❌ 已陣亡！", "is_flex": True, "flex": card["flex"], "quick_reply": card["quick_reply"]}
        
    current_weapon = p.get("weapon", "赤手空拳")
    w_bonus = weapons.SHOP_WEAspects = weapons.SHOP_WEAPONS[current_weapon]["atk_bonus"] if current_weapon in weapons.SHOP_WEAPONS else 0
    p_atk = 20 + (p.get("strength", 10) * 2) + (p.get("intelligence", 10) * 2) + w_bonus
    
    raid_damage = int(p_atk * random.uniform(1.5, 4.0))
    p["world_boss_damage"] = p.get("world_boss_damage", 0) + raid_damage
    p["hp"] = max(1, p["hp"] - random.randint(20, 50))
    db_core.save_player(p)
    
    # 🌟 【排行榜與總血量核心管線】直接從 Supabase 即時加總全服所有勇者的傷害
    conn = db_core.get_db_connection()
    cur = conn.cursor()
    
    # 1. 撈取全服總傷害以動態換算 Boss 剩餘血量
    cur.execute("SELECT SUM(COALESCE(world_boss_damage, 0)) FROM players")
    server_total_damage = cur.fetchone()[0] or 0
    boss_current_hp = max(0, WORLD_BOSS_TOTAL_HP - server_total_damage)
    
    # 2. 🔥【排行榜實裝】撈取全服貢獻排名前 5 名的玩家
    cur.execute("SELECT user_id, job, level, COALESCE(world_boss_damage, 0) FROM players WHERE world_boss_damage > 0 ORDER BY world_boss_damage DESC LIMIT 5")
    leaderboard_rows = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # 3. 組合排行榜文字
    lb_lines = ["\n📊 【 🏆 皇家討伐戰功世界排行榜 🏆 】"]
    for idx, row in enumerate(leaderboard_rows, 1):
        uid, job, lvl, dmg = row
        # 隱碼保護 UID
        short_id = f"勇者*{str(uid)[-4:]}" if len(str(uid)) >= 4 else f"勇者{idx}"
        lb_lines.append(f" 🥇 第 {idx} 名：{short_id} ({job} Lv.{lvl}) ➡️ ⚔️ {dmg} 點")
    if len(leaderboard_rows) == 0:
        lb_lines.append("   (目前尚無勇者登榜，快拿測試神兵砍下一刀！)")
        
    leaderboard_text = "\n".join(lb_lines)
    
    reply_text = f"🌋 🔥 【世界 Boss 滅世突襲戰】 🔥 🌋\n─────────────────\n🛡️ 你發動全盛奧義，朝 {WORLD_BOSS_NAME} 揮出極限一擊！\n\n💥 本回合灌入傷害：【 ⚔️ {raid_damage} 點 】！\n🩹 承受魔神威壓反噬，體力扣減！\n{leaderboard_text}"
    
    # 封裝一個虛擬怪物包丟給 db_core，讓其強行渲染出 Boss 血條與數值
    boss_fake_monster = {
        "name": WORLD_BOSS_NAME,
        "hp": boss_current_hp,
        "max_hp": WORLD_BOSS_TOTAL_HP,
        "is_world_boss": True
    }
    
    quick_items = [
        QuickReplyItem(action=MessageAction(label="🌋 再次合力圍剿", text="挑戰世界Boss")),
        QuickReplyItem(action=MessageAction(label="📊 查看世界戰況", text="挑戰")),
        QuickReplyItem(action=MessageAction(label="🏃 返回普通尋怪", text="尋怪"))
    ]
    return {
        "text": reply_text, 
        "is_flex": True, 
        "flex": db_core.make_battle_card(reply_text, p, boss_fake_monster)["flex"], 
        "quick_reply": QuickReply(items=quick_items)
    }
