import db_core
import weapons
import equipment_core
import jobs
from linebot.v3.messaging import QuickReply, QuickReplyItem, MessageAction

def get_status_card(p):
    """👤 生成高質感 4 層橫向網格狀態面板 (完整計入全身 14 欄位防具與詞綴加成)"""
    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    job_mod = jobs.JOBS_DATA.get(current_job, jobs.JOBS_DATA["初心者"])

    # 統計全身 14 欄位裝備詞綴與攻防總和
    eq_bonus = equipment_core.get_player_total_equipment_bonus(p)

    str_val = int((p.get("strength", 10 + (level * 3)) + eq_bonus["strength"]) * job_mod["str_mod"])
    agi_val = int((p.get("agility", 10 + (level * 2)) + eq_bonus["agility"]) * job_mod["agi_mod"])
    int_val = int((p.get("intelligence", 10 + (level * 2)) + eq_bonus["intelligence"]) * job_mod["int_mod"])
    vit_val = int((p.get("vitality", 10 + (level * 3)) + eq_bonus["vitality"]) * job_mod["vit_mod"])
    luk_val = int((p.get("luck", 10 + (level * 1)) + eq_bonus["luck"]) * job_mod["luk_mod"])
    men_val = int((p.get("sprit", 10 + (level * 2)) + eq_bonus["sprit"]) * job_mod["men_mod"])

    free_pts = p.get("attribute_points", 0)
    current_weapon = p.get("weapon", "赤手空拳")

    p_atk_single = 12 + str_val + eq_bonus["atk"]
    m_atk_single = 10 + int_val
    p_def = (vit_val // 2) + eq_bonus["def"]
    m_def = (men_val // 2) + eq_bonus["mdef"]

    double_chance = min(60, 2 + (agi_val // 6))
    crit_chance = min(80, 10 + (luk_val // 5))
    calculated_max_hp = 100 + (vit_val * 5) + (level * 15)
    calculated_max_mp = 50 + (men_val * 4) + (level * 5)

    current_mp = p.get("mp")
    if current_mp in (None, "None"):
        current_mp = calculated_max_mp
        p["mp"] = calculated_max_mp

    status_color = "#FFCC00" if free_pts > 0 else "#8E8E93"

    flex_bubble = {
        "type": "bubble",
        "styles": {"body": {"backgroundColor": "#111111"}},
        "body": {
            "type": "box", "layout": "vertical", "spacing": "md",
            "contents": [
                {"type": "text", "text": f"👤 勇者狀態面板 (Lv.{level})", "weight": "bold", "size": "md", "color": "#FFFFFF", "align": "center"},
                {"type": "separator", "color": "#333333"},
                {"type": "box", "layout": "vertical", "spacing": "xs", "contents": [
                    {"type": "text", "text": f"🎭 目前職業：🔥【{current_job}】", "size": "sm", "color": "#007AFF", "weight": "bold"},
                    {"type": "text", "text": f"⚔️ 主手武器：【{current_weapon}】", "size": "xs", "color": "#4CD964", "wrap": True},
                    {"type": "text", "text": f"💰 擁有金幣：🪙 {p['gold']}", "size": "sm", "color": "#FFD700"},
                    {"type": "text", "text": f"🌟 經驗進度：{p['exp']} / {level * 50}", "size": "sm", "color": "#AF52DE"},
                    {"type": "text", "text": f"✨ 剩餘潛能點數：{free_pts} 點", "size": "sm", "color": status_color, "weight": "bold"}
                ]},
                {"type": "separator", "color": "#333333"},
                {"type": "text", "text": "🧬 【 角色素質 (含全身裝備詞綴加成) 】", "weight": "bold", "size": "xs", "color": "#8E8E93"},
                {"type": "box", "layout": "horizontal", "contents": [
                    {"type": "text", "text": f"💪 力量: {str_val}", "size": "xs", "color": "#FFFFFF", "flex": 1},
                    {"type": "text", "text": f"⚡ 敏捷: {agi_val}", "size": "xs", "color": "#FFFFFF", "flex": 1},
                    {"type": "text", "text": f"🔮 智力: {int_val}", "size": "xs", "color": "#FFFFFF", "flex": 1}
                ]},
                {"type": "box", "layout": "horizontal", "contents": [
                    {"type": "text", "text": f"🛡️ 體力: {vit_val}", "size": "xs", "color": "#FFFFFF", "flex": 1},
                    {"type": "text", "text": f"🍀 幸運: {luk_val}", "size": "xs", "color": "#FFFFFF", "flex": 1},
                    {"type": "text", "text": f"🌟 精神: {men_val}", "size": "xs", "color": "#FFFFFF", "flex": 1}
                ]},
                {"type": "separator", "color": "#222222", "margin": "sm"},
                {"type": "box", "layout": "horizontal", "contents": [
                    {"type": "text", "text": f"💥 物傷: {p_atk_single}", "size": "xs", "color": "#FF9500", "flex": 1},
                    {"type": "text", "text": f"🔮 魔傷: {m_atk_single}", "size": "xs", "color": "#5AC8FA", "flex": 1}
                ]},
                {"type": "box", "layout": "horizontal", "contents": [
                    {"type": "text", "text": f"🧱 物防: {p_def}", "size": "xs", "color": "#FF3B30", "flex": 1},
                    {"type": "text", "text": f"🌀 法防: {m_def}", "size": "xs", "color": "#AF52DE", "flex": 1}
                ]},
                {"type": "separator", "color": "#222222", "margin": "sm"},
                {"type": "box", "layout": "horizontal", "contents": [
                    {"type": "text", "text": f"💨 連擊率: {double_chance}%", "size": "xs", "color": "#E0E0E0", "flex": 1},
                    {"type": "text", "text": f"✨ 爆擊率: {crit_chance}%", "size": "xs", "color": "#FFCC00", "weight": "bold", "flex": 1}
                ]},
                {"type": "separator", "color": "#222222", "margin": "sm"},
                {"type": "box", "layout": "horizontal", "contents": [
                    {"type": "text", "text": f"💖 血量: {p['hp']} / {calculated_max_hp}", "size": "xs", "color": "#4CD964", "flex": 1},
                    {"type": "text", "text": f"🔷 魔力: {current_mp} / {calculated_max_mp}", "size": "xs", "color": "#007AFF", "flex": 1}
                ]}
            ]
        }
    }

    if free_pts > 0:
        flex_bubble["footer"] = {
            "type": "box", "layout": "vertical", "backgroundColor": "#1C1C1E",
            "contents": [{"type": "text", "text": "💡 提示：輸入【加點 屬性名稱 點數】配點。（例如：加點 力量 5）", "size": "xs", "color": "#8E8E93", "align": "center", "wrap": True}]
        }

    quick_items = [
        QuickReplyItem(action=MessageAction(label="🎒 我的背包", text="我的背包")),
        QuickReplyItem(action=MessageAction(label="🛡️ 我的裝備", text="我的裝備")),
        QuickReplyItem(action=MessageAction(label="🏪 補給商店", text="冒險商店")),
        QuickReplyItem(action=MessageAction(label="🦅 返回城鎮", text="回城"))
    ]
    return {"flex": flex_bubble, "quick_reply": QuickReply(items=quick_items).to_dict()}

def handle_resurrect(p):
    if p["hp"] > 0:
        card = db_core.make_battle_card("💡 提示：勇者！你目前明明生命值健全，不需要使用復活神術。", p, None)
        return {"flex": card["flex"], "quick_reply": card["quick_reply"]}

    level = p.get("level", 1)
    current_job = p.get("job", "初心者")
    job_mod = jobs.JOBS_DATA.get(current_job, jobs.JOBS_DATA["初心者"])
    eq_bonus = equipment_core.get_player_total_equipment_bonus(p)

    vit_val = int((p.get("vitality", 10 + (level * 3)) + eq_bonus["vitality"]) * job_mod["vit_mod"])
    men_val = int((p.get("sprit", 10 + (level * 2)) + eq_bonus["sprit"]) * job_mod["men_mod"])
    max_hp = 100 + (vit_val * 5) + (level * 15)
    max_mp = 50 + (men_val * 4) + (level * 5)

    p["hp"] = max_hp
    p["mp"] = max_mp
    p["current_map"] = "主城"
    p["enemy"] = None
    p["gold"] = max(0, p["gold"] - 20)
    db_core.save_player(p)

    log_text = (
        "😇 ✨ 👼 【 神聖天使・復活術成功 】 👼 ✨ 😇\n"
        "─────────────────\n"
        "世界樹的讚美詩響起！璀璨的光明法陣在虛空中張開，你被泉水聖光溫柔包覆！\n\n"
        "💖 狀態恢復：生命值與魔力值全數充滿爆表 ── 【 🟢 FULL HP/MP 】！\n"
        "🏙️ 時空轉移：靈魂已安穩重塑於皇家安全起點 ── 📍【 主城 】！\n"
        "🪙 公會稅收：修復靈魂扣除工本費 20 金幣。"
    )
    card = db_core.make_battle_card(log_text, p, None)
    return {"flex": card["flex"], "quick_reply": card["quick_reply"]}
