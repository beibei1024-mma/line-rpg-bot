import random
from linebot.v3.messaging import QuickReply, QuickReplyItem, MessageAction
import db_core
import weapons

# 👑 世界 Boss 當前動態大數據（在雲端多人連線時，可改由資料庫全服累計）
WORLD_BOSS_TOTAL_HP = 10000000  # 全服共討千萬級血量
WORLD_BOSS_NAME = "🌋 【滅世魔神・毀滅終焉泰坦】"

def get_challenge_menu(p):
    """🤖 生成無痛橫滑的挑戰入口圖卡面板"""
    current_layer = p.get("tower_layer", 1)
    if current_layer is None: current_layer = 1
    
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
                    {"type": "text", "text": f"   ↳ 全服累積傷害！個人已貢獻：⚔️ {p.get('world_boss_damage', 0)} 點", "size": "xs", "color": "#8E8E93"}
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
    return flex_menu

def execute_tower_climb(p):
    """🗼 爬塔戰鬥計算核心 (不干擾原有尋怪，一次性拼勝負，適合速刷)"""
    layer = p.get("tower_layer", 1)
    if layer is None: layer = 1
    
    # 根據層數全自動動態公式生成怪物強度，無限增長
    monster_hp = 100 + (layer * 120)
    monster_atk = 15 + (layer * 18)
    monster_name = f"🔱 試煉塔第 {layer} 層・【守護石雕將軍】"
    
    # 計算勇者真實物傷 (包含新版神兵利器增幅)
    current_weapon = p.get("weapon", "赤手空拳")
    w_bonus = weapons.SHOP_WEAPONS[current_weapon]["atk_bonus"] if current_weapon in weapons.SHOP_WEAPONS else 0
    p_atk = 15 + (p.get("strength", 10) * 2) + w_bonus
    p_max_hp = 100 + (p.get("vitality", 10) * 5)
    
    if p["hp"] <= 0:
        return "❌ 勇者！你目前處於陣亡狀態，無法進入神聖試煉塔，請先復活！"
        
    log = f"⚔️ 歷練開啟！你隻身踏入試煉之塔第 {layer} 層！\n遭遇守關巨獸 ── {monster_name}\n─────────────────\n"
    
    # 模擬高階自動對戰回殺
    turns = 0
    m_current_hp = monster_hp
    p_current_hp = p["hp"]
    
    while m_current_hp > 0 and p_current_hp > 0 and turns < 10:
        turns += 1
        # 勇者重擊
        dmg = int(p_atk * random.uniform(0.9, 1.3))
        m_current_hp -= dmg
        log += f"💥 第 {turns} 回合：你對守衛造成 {dmg} 點重傷！\n"
        if m_current_hp <= 0: break
        
        # 怪物反擊
        m_dmg = max(1, monster_atk - (p.get("vitality", 10) // 2))
        p_current_hp -= m_dmg
        log += f"🩹 守衛長槍橫掃，反擊你 {m_dmg} 點生命！\n"
        
    if m_current_hp <= 0:
        reward_gold = 500 + (layer * 150)
        p["tower_layer"] = layer + 1
        p["gold"] += reward_gold
        p["hp"] = p_current_hp # 繼承殘餘血量
        db_core.save_player(p)
        return f"🏆 【試煉塔第 {layer} 層 挑戰大捷】 🏆\n─────────────────\n{log}\n🎉 奇蹟戰勝！你成功突破了此層防線！\n🪙 獲得層數通關獎勵：金幣 +{reward_gold}！\n🗼 試煉晉升：下一層解鎖第 {layer + 1} 層！"
    else:
        p["hp"] = max(0, p_current_hp)
        db_core.save_player(p)
        return f"☠️ 【試煉塔第 {layer} 層 挑戰兵敗】 ☠️\n─────────────────\n{log}\n❌ 守關者防禦太過堅固，你受傷過重狼狽撤退了...\n💡 提示：請先使用【加點】或擊敗普通怪物爆出更高階裝備後再來挑戰！"

def execute_world_boss_raid(p):
    """🌋 世界 Boss 討伐連動核心 (累積個人傷害，永不陣亡)"""
    if p["hp"] <= 0: return "❌ 你已陣亡，無法向世界魔神發起衝鋒！"
    
    current_weapon = p.get("weapon", "赤手空拳")
    w_bonus = weapons.SHOP_WEAPONS[current_weapon]["atk_bonus"] if current_weapon in weapons.SHOP_WEAPONS else 0
    p_atk = 20 + (p.get("strength", 10) * 2) + (p.get("intelligence", 10) * 2) + w_bonus
    
    # 瘋狂爆發一擊
    raid_damage = int(p_atk * random.uniform(1.5, 4.0))
    p["world_boss_damage"] = p.get("world_boss_damage", 0) + raid_damage
    
    # 承受魔神反噬餘波
    received_backlash = random.randint(20, 50)
    p["hp"] = max(1, p["hp"] - received_backlash) # 保留 1 血防暴斃
    
    db_core.save_player(p)
    return f"🌋 🔥 【世界 Boss 滅世突襲戰】 🔥 🌋\n─────────────────\n🛡️ 你點燃靈魂發動奧義，朝 {WORLD_BOSS_NAME} 揮出極限一擊！\n\n💥 本次對魔神灌入巨額總傷：【 ⚔️ {raid_damage} 】 點！\n🩹 承受滅世神能反噬：體力遭到灼傷扣減 -{received_backlash} 點。\n📈 個人全盛史詩戰功：目前累計總傷害已達 ── 【 🏆 {p['world_boss_damage']} 】 點！"
