import random
import json
from linebot.v3.messaging import QuickReply, QuickReplyItem, MessageAction
import db_core
import weapons

WORLD_BOSS_TOTAL_HP = 10000000
WORLD_BOSS_NAME = "🌋 【滅世魔神・毀滅終焉泰坦】"

def get_challenge_menu(p):
    """🤖 生成挑戰入口圖卡面板 (展示即時千萬血量數值)"""
    current_layer = p.get("tower_layer", 1) or 1
    boss_dmg = p.get('world_boss_damage', 0) or 0
    boss_current_hp = check_boss_rebirth_and_get_hp()
    boss_status = "💀 已被擊殺！進入副本傳送陣將自動喚醒重生！" if boss_current_hp <= 0 else f"❤️ 剩餘生命：{boss_current_hp} / {WORLD_BOSS_TOTAL_HP}"

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
                {"type": "button", "style": "primary", "color": "#FF3B30", "height": "sm", "action": {"type": "message", "label": "🔮 傳送前往 Boss 獨立地圖", "text": "傳送 世界Boss"}}
            ]
        }
    }

    quick_items = [
        QuickReplyItem(action=MessageAction(label="🗼 挑戰爬塔", text="挑戰爬塔")),
        QuickReplyItem(action=MessageAction(label="🌋 世界Boss戰報", text="挑戰世界Boss")),
        QuickReplyItem(action=MessageAction(label="🔮 傳送世界Boss", text="傳送 世界Boss")),
        QuickReplyItem(action=MessageAction(label="🏃 出城冒險", text="世界地圖"))
    ]
    return {"flex": flex_menu, "quick_reply": QuickReply(items=quick_items).to_dict()}

def execute_tower_climb(p):
    """🗼 爬塔戰鬥計算核心"""
    layer = p.get("tower_layer", 1) or 1
    monster_hp = 100 + (layer * 120)
    monster_atk = 15 + (layer * 18)
    monster_name = f"🔱 試煉塔第 {layer} 層・【守護石雕將軍】"

    current_weapon = p.get("weapon", "赤手空拳")
    w_bonus = weapons.get_weapon_atk(current_weapon) + int(p.get("forge_weapon_bonus", 0))
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
        QuickReplyItem(action=MessageAction(label="🦅 返回主城", text="回城"))
    ]
    qr_dict = QuickReply(items=quick_items).to_dict()

    if m_current_hp <= 0:
        reward_gold = 500 + (layer * 150)
        p["tower_layer"] = layer + 1
        p["gold"] += reward_gold
        p["hp"] = p_current_hp
        db_core.save_player(p)
        reply_text = f"🏆 【試煉塔第 {layer} 層 挑戰大捷】 🏆\n─────────────────\n{log}\n🎉 奇蹟戰勝！你成功突破了此層防線！\n🪙 獲得層數通關獎勵：金幣 +{reward_gold}！\n🗼 試煉晉升：下一層解鎖第 {layer + 1} 層！"
        return {"text": reply_text, "is_flex": True, "flex": db_core.make_battle_card(reply_text, p, None)["flex"], "quick_reply": qr_dict}
    else:
        p["hp"] = max(1, p_current_hp)
        db_core.save_player(p)
        reply_text = f"☠️ 【試煉塔第 {layer} 層 挑戰兵敗】 ☠️\n─────────────────\n{log}\n❌ 守關者防禦太過堅固，你受傷過重狼狽撤退了..."
        return {"text": reply_text, "is_flex": True, "flex": db_core.make_battle_card(reply_text, p, None)["flex"], "quick_reply": qr_dict}

def check_boss_rebirth_and_get_hp():
    """🔄 檢查全服累積傷害，自動觸發滿血重生判定"""
    conn = db_core.get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT SUM(COALESCE(world_boss_damage, 0)) FROM players")
        res = cur.fetchone()
        server_total_damage = res[0] if res and res[0] is not None else 0
        if server_total_damage >= WORLD_BOSS_TOTAL_HP:
            cur.execute("UPDATE players SET world_boss_damage = 0")
            conn.commit()
            server_total_damage = 0
    finally:
        cur.close()
        db_core.release_db_connection(conn)
    return max(0, WORLD_BOSS_TOTAL_HP - server_total_damage)

def execute_world_boss_raid(p):
    """🌋 排行榜核心看板大腦：回傳標準 Flex + QuickReply 字典，也可供外部取文字"""
    boss_current_hp = check_boss_rebirth_and_get_hp()
    conn = db_core.get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT name, job, level, COALESCE(world_boss_damage, 0) FROM players WHERE world_boss_damage > 0 ORDER BY world_boss_damage DESC LIMIT 5")
        leaderboard_rows = cur.fetchall()
    finally:
        cur.close()
        db_core.release_db_connection(conn)

    lb_lines = [
        f"🌋 {WORLD_BOSS_NAME}",
        f"❤️ 剩餘生命：{boss_current_hp} / {WORLD_BOSS_TOTAL_HP}",
        "─────────────────",
        "📊 【 🏆 皇家討伐戰功世界排行榜 🏆 】"
    ]
    for idx, row in enumerate(leaderboard_rows, 1):
        real_name, job, lvl, dmg = row
        lb_lines.append(f" 👑 第 {idx} 名：【 {real_name} 】 ({job} Lv.{lvl}) ➡️ ⚔️ {dmg} 點")
    if len(leaderboard_rows) == 0:
        lb_lines.append("   (目前尚無勇者登榜，快傳送至世界Boss砸下第一刀！)")

    leaderboard_text = "\n".join(lb_lines)
    card = db_core.make_battle_card(leaderboard_text, p, p.get("enemy"))
    quick_items = [
        QuickReplyItem(action=MessageAction(label="🔮 傳送討伐世界Boss", text="傳送 世界Boss")),
        QuickReplyItem(action=MessageAction(label="🗼 挑戰試煉塔", text="挑戰爬塔")),
        QuickReplyItem(action=MessageAction(label="🦅 返回主城", text="回城"))
    ]
    return {"text": leaderboard_text, "flex": card["flex"], "quick_reply": QuickReply(items=quick_items).to_dict()}
