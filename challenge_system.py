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
    
    conn = db_core.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT SUM(COALESCE(world_boss_damage, 0)) FROM players")
    res = cur.fetchone()
    server_total_damage = res[0] if res and res[0] is not None else 0
    boss_current_hp = max(0, WORLD_BOSS_TOTAL_HP - server_total_damage)
    cur.close()
    conn.close()
    
    boss_status = "💀 已被擊殺！點擊下方按鈕將喚醒重生！" if boss_current_hp <= 0 else f"❤️ 剩餘生命：{boss_current_hp} / {WORLD_BOSS_TOTAL_HP}"
    
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
                    {"type": "text", "text": f"   ↳ {boss_status}", "size": "xs", "color": "#FF8383", "weight": "bold"},
                    {"type": "text", "text": f"   ↳ 全服累積貢獻！個人已輸出：⚔️ {boss_dmg} 點", "size": "xs", "color": "#8E8E93"}
                ]}
            ]
        },
        "footer": {
            "type": "box", "layout": "vertical", "spacing": "sm",
            "contents": [
                {"type": "button", "style": "primary", "color": "#AF52DE", "height": "sm", "action": {"type": "message", "label": "🗼 挑戰下一層試煉塔", "text": "挑戰爬塔"}},
                {"type": "button", "style": "primary", "color": "#FF3B30", "height": "sm", "action": {"type": "message", "label": "🌋 進入副本迎戰魔神", "text": "挑戰世界Boss"}}
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
    if layer is None: layer = 1
    
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
        if m_current_hp <= 0: break
        
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

def check_boss_rebirth_and_get_hp():
    """🔄 獨立大腦：檢查全服累積傷害，自動觸發滿血重生判定"""
    conn = db_core.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT SUM(COALESCE(world_boss_damage, 0)) FROM players")
    res = cur.fetchone()
    server_total_damage = res[0] if res and res[0] is not None else 0
    
    if server_total_damage >= WORLD_BOSS_TOTAL_HP:
        cur.execute("UPDATE players SET world_boss_damage = 0")
        conn.commit()
        server_total_damage = 0
        
    cur.close()
    conn.close()
    return max(0, WORLD_BOSS_TOTAL_HP - server_total_damage)

def execute_world_boss_raid(p):
    """🌋 副本進入陣：正式將 current_map 移動至世界Boss，強制解鎖小圖標與戰鬥核心"""
    if p["hp"] <= 0:
        card = db_core.make_battle_card("❌ 你已陣亡，無法向世界魔神發起衝鋒！", p, None)
        return {"text": "❌ 已陣亡！", "is_flex": True, "flex": card["flex"], "quick_reply": card["quick_reply"]}
        
    boss_current_hp = check_boss_rebirth_and_get_hp()
    
    # 📌 核心修正點：將玩家目前的所在地點切換成 "世界Boss"，以此跳出主城安全區按鈕的覆蓋魔咒！
    p["current_map"] = "世界Boss"
    
    p["enemy"] = {
        "name": WORLD_BOSS_NAME,
        "hp": boss_current_hp,
        "max_hp": WORLD_BOSS_TOTAL_HP,
        "atk": 160,                      
        "gold_range": (1000, 5000),
        "exp": 5000,
        "skill": "👁️ 邪神神格：承受全職業奧義轟炸！環境常駐【魔能潮汐】！",
        "drop_item": "舊神支配者之眼",
        "env": "🔮 魔能潮汐 (全屏大混戰，法術與技能增幅異常狂暴)",
        "is_world_boss": True            
    }
    
    db_core.save_player(p)
    
    title_text = f"⚔️ 踏入遠古禁忌副本！您已進入戰場！\n\n📢 魔神狀態：{p['enemy']['skill']}\n🛡️ 平衡機制：各職業神聖技能已全數解鎖！請點擊下方按鈕或施放【使用技能 技能名稱】朝魔神傾瀉火力！"
    card_data = db_core.make_battle_card(title_text, p, p["enemy"])
    
    return {
        "text": "已進入世界 Boss 戰場！",
        "is_flex": True,
        "flex": card_data["flex"],
        "quick_reply": card_data["quick_reply"]
    }
